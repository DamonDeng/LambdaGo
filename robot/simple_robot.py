from go_core.goboard import GoBoard
from dnn.tensor_model import TensorModel

import time
import random


class SimpleRobot(object):

    def __init__(self, name='DefaultSimpleRobot', layer_number=19, old_model=None):
        self.name = name
        self.layer_number = layer_number

        self.board_size = 19
        self.simulate_board_list = []
        self.max_play_move = 1024
        self.ColorBlackChar = 'b'
        self.ColorWhiteChar = 'w'

        self.komi = 7.5

        # init board_size*board_size of simulating board
        for i in range (self.board_size*self.board_size):
            self.simulate_board_list.append(GoBoard(self.board_size))

        self.go_board = GoBoard(self.board_size)

        if old_model is None:
            self.model = TensorModel(self.name, self.board_size, layer_number=self.layer_number)
        else:
            print ('Trying to load old model for continue training:' + './model/' + old_model)
            self.model = TensorModel(self.name, self.board_size, model_path='./model/' + old_model, layer_number=self.layer_number)
        

    def reset_board(self):
        self.go_board.reset(self.board_size)

    def apply_move(self, color, pos):

        # print ('aplying move:' + color + ' in the position ' + str(pos))

        self.go_board.apply_move(color, pos)

        # start_time = time.time()
        # self.board.update_score_board()
        # end_time = time.time()
        # print ('total update time:' + str(end_time - start_time))
        # print(str(self.board))

    def showboard(self):
        self.go_board.update_score_board()
        return str(self.go_board)



    def simulate_best_move(self, color, pos_filter=None):
        move_and_result = {}

        forbidden_moves = []

        # time debug for prediction
        # start_time = time.time()

        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.go_board.is_empty((row, col)):
                    board_index = row*self.board_size + col
                    self.simulate_board_list[board_index].copy_from(self.go_board)
                    is_valid, reason = self.simulate_board_list[board_index].apply_move(color, (row,col))
                    if is_valid == True:
                        if pos_filter != None:
                            if not (row, col) in pos_filter:
                                move_and_result[(row, col)] = self.simulate_board_list[board_index]
                        else:
                            move_and_result[(row, col)] = self.simulate_board_list[board_index]
                    else:
                        if reason == self.go_board.MoveResult_IsKo or \
                           reason == self.go_board.MoveResult_IsSuicide or \
                           reason == self.go_board.MoveResult_SolidEye:
                            forbidden_moves.append((row, col))

        all_moves = move_and_result.keys()

        right_move = (None, 0)

        best_move_is_lossing = False

        if len(all_moves) <= 0:
            # no available move left, just return PASS, and current score board sum as value
            if not self.go_board.score_board_updated:
                self.go_board.update_score_board()

            right_move = (None, self.go_board.score_board_sum)

            return right_move, forbidden_moves
        else:
            # selected_move = all_moves[0]
            input_states = []
            input_pos = []
            for pos in all_moves:

                temp_board = move_and_result.get(pos)
                # temp_board.update_score_board()

                input_states.append(temp_board.board)
                # input_score.append(temp_board.score_board_sum)
                input_pos.append(pos)

            # time debug for prediction
            start_time = time.time()

            predict_result = self.model.predict(input_states)

            # time debug for prediction
            # end_time = time.time()
            # print('# time used for prediction:' + str(end_time - start_time) + '         ')

            move_and_predict = zip(input_pos, predict_result)

            
            move_and_predict.sort(key=lambda x:x[1], reverse=True)

            color_value = self.go_board.get_color_value(color)

            if color_value == self.go_board.ColorBlack:
                print ('# black top move:' + str(move_and_predict[0][0]) + ' with prediction:' + str(move_and_predict[0][1]) + '         ')

                if move_and_predict[0][1] > self.komi:
                    right_move = move_and_predict[0]
                    best_move_is_lossing = False
                else:
                    right_move = move_and_predict[0]
                    best_move_is_lossing = True
                    
            elif color_value == self.go_board.ColorWhite:
                print ('# white top move:' + str(move_and_predict[-1][0]) + ' with prediction:' + str(move_and_predict[-1][1]) + '         ')

                if move_and_predict[-1][1] < self.komi:
                    right_move = move_and_predict[-1]
                    best_move_is_lossing = False
                else:
                    right_move = move_and_predict[-1]
                    best_move_is_lossing = True

            # print ('# right move:' + str(right_move[0]) + ' with valueprediction:' + str(right_move[1]) + '       ')

        if not best_move_is_lossing:
            print ('#----not----lossing-----')
            print ('#                                                                     ')
                   
            return right_move, forbidden_moves

        print ('#-lossing---------------')


        # just using random selection while it is lossing:

        

        random_int = random.randint(0, len(move_and_predict)-1)

        right_move = move_and_predict[random_int]

        print ('# random move:' + str(right_move[0]) + ' with prediction:' + str(right_move[1]) + '    ')
        

        return right_move, forbidden_moves


    def select_move(self, color):

        right_move, forbidden_moves = self.simulate_best_move(color)

        self.go_board.apply_move(color, right_move[0])

        # print ('# selected move:' + str(right_move))

        return right_move[0]


        
    def train(self, board_states, move_sequence, score_board):

        print ('# pretent to be in training state....')

    def new_game(self):
        self.reset_board()

        self.simulate_board_list = []
        for i in range (self.board_size*self.board_size):
            self.simulate_board_list.append(GoBoard(self.board_size))

    def get_current_state(self):
        return self.go_board.board

    def get_score_board(self):

        if not self.go_board.score_board_updated:
            self.go_board.update_score_board()
        
        return self.go_board.score_board

    def get_score(self):

        if not self.go_board.score_board_updated:
            self.go_board.update_score_board()
        
        return self.go_board.score_board_sum


