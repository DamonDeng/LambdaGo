from go_core.goboard import GoBoard
from dnn.tensor_model import TensorModel

import time
import random


class SimpleRobot(object):

    def __init__(self, name='DefaultSimpleRobot', layer_number=19, old_model=None, boardsize=19, komi=7.5):
        self.name = name
        self.layer_number = layer_number

        self.board_size = boardsize
        self.komi = komi

        self.simulate_board_list = []
        self.max_play_move = 1024
        self.ColorBlackChar = 'b'
        self.ColorWhiteChar = 'w'

        

        # self.for_repeat_move = [(-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6)]

        # # init board_size*board_size of simulating board
        # for i in range (self.board_size*self.board_size):
        #     self.simulate_board_list.append(GoBoard(self.board_size))

        # self.go_board = GoBoard(self.board_size)

        self.reset()

        if old_model is None:
            self.model = TensorModel(self.name, self.board_size, layer_number=self.layer_number)
        else:
            print ('Trying to load old model for continue training:' + old_model)
            self.model = TensorModel(self.name, self.board_size, model_path=old_model, layer_number=self.layer_number)
        
    def reset(self):
        
        self.for_repeat_move = [(-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7), (-8, -8)]

        # init board_size*board_size of simulating board
        for i in range (self.board_size*self.board_size):
            self.simulate_board_list.append(GoBoard(self.board_size))

        self.go_board = GoBoard(self.board_size)

    def reset_board(self):
        self.go_board.reset(self.board_size)

    def apply_move(self, color, pos):

        # print ('aplying move:' + color + ' in the position ' + str(pos))

        self.go_board.apply_move(color, pos)
        self.record_repeat(pos)

        # start_time = time.time()
        # self.board.update_score_board()
        # end_time = time.time()
        # print ('total update time:' + str(end_time - start_time))
        # print(str(self.board))

    def record_repeat(self, pos):
        self.for_repeat_move.append(pos)
        self.for_repeat_move.pop(0)

    def is_repeating(self):
        if self.for_repeat_move[5] == self.for_repeat_move[2] and \
            self.for_repeat_move[4] == self.for_repeat_move[1] and \
            self.for_repeat_move[3] == self.for_repeat_move[0]:

            return True
            
        elif self.for_repeat_move[7] == self.for_repeat_move[3] and \
            self.for_repeat_move[6] == self.for_repeat_move[2] and \
            self.for_repeat_move[5] == self.for_repeat_move[1] and \
            self.for_repeat_move[4] == self.for_repeat_move[0]:

            return True

        else:
            return False

    def showboard(self):
        # start_time = time.time()
        self.go_board.update_score_board()
        # end_time = time.time()
        # print ('# time used:' + str(end_time - start_time))
        return str(self.go_board)


    def simulate_all_move(self, color, pos_filter=None):
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
        
        return move_and_result, forbidden_moves


    def simulate_best_move(self, color, pos_filter=None):

        move_and_result , forbidden_moves = self.simulate_all_move(color)

        all_moves = move_and_result.keys()

        right_move = (None, 0)

        best_move_is_lossing = False

        if len(all_moves) <= 0:
            # no available move left, just return PASS, and current score board sum as value
            if not self.go_board.score_board_updated:
                self.go_board.update_score_board()

            right_move = (None, self.go_board.score_board_sum)

            # best_move_is_lossing = False
            lossing_right_move = (None, 0)

            self.display_result(color, right_move, best_move_is_lossing, lossing_right_move)

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
            # start_time = time.time()

            predict_result = self.model.predict(input_states)

            # time debug for prediction
            # end_time = time.time()
            # print('# time used for prediction:' + str(end_time - start_time) + '         ')

            move_and_predict = zip(input_pos, predict_result)

            color_value = self.go_board.get_color_value(color)

            if color_value == self.go_board.ColorBlack:
                move_and_predict.sort(key=lambda x:x[1], reverse=True)
                if move_and_predict[0][1] > self.komi:
                    best_move_is_lossing = False
                else:
                    best_move_is_lossing = True
                    
            else:
                move_and_predict.sort(key=lambda x:x[1])
                if move_and_predict[0][1] < self.komi:
                    best_move_is_lossing = False
                else:
                    best_move_is_lossing = True
                    

            

            right_move = move_and_predict[0]

            # if the robot is repeating in three ko, select the second one
            if self.is_repeating() and len(move_and_predict) > 1:
                right_move = move_and_predict[1]

            
            

            # print ('# right move:' + str(right_move[0]) + ' with valueprediction:' + str(right_move[1]) + '       ')

        lossing_right_move = (None, 0)

        if best_move_is_lossing:

            if len(move_and_predict) == 1:
                lossing_right_move = move_and_predict[0]
            else:
                # if best move is lossing, chossing random one from the first two moves.

                move_to_select = min(len(move_and_predict), 10)

                random_index = random.randint(0,move_to_select-1)
                lossing_right_move = move_and_predict[random_index]


        # if best_move_is_lossing:
        #     # if best move of current color is lossing, 
        #     # try to get the best move of enemy and occupy it to block the best move of enemy

        #     # enemy_color = GoBoard.other_color(color)

        #     all_moves = move_and_result.keys()

        #     move_and_score = []

        #     for single_move in all_moves:
        #         (score_row, score_col) = single_move

        #         board_index = score_row*self.board_size + score_col
        #         self.simulate_board_list[board_index].update_score_board()
        #         current_score = self.simulate_board_list[board_index].score_board_sum
        #         move_and_score.append((single_move, current_score))

                

        #     if color_value == self.go_board.ColorBlack:
        #         move_and_score.sort(key=lambda x:x[1], reverse=True)
                

                    
        #     elif color_value == self.go_board.ColorWhite: 
        #             move_and_score.sort(key=lambda x:x[1])

            
        #     first_value = move_and_score[0][1]
        #     number_of_best = 0
        #     for inner_iter in move_and_score:
        #         if abs(abs(first_value) - abs(inner_iter[1])) > 1:
        #             break
        #         number_of_best += 1

        #     random_index = random.randint(0, number_of_best-1)
        #     lossing_right_move = move_and_score[random_index]

        
        self.display_result(color, right_move, best_move_is_lossing, lossing_right_move)
        
        
        if best_move_is_lossing:
            return lossing_right_move, forbidden_moves
        else:
            return right_move, forbidden_moves

    def simulate_best_move_both_side(self, color, pos_filter=None):
        move_and_result , forbidden_moves = self.simulate_all_move(color)

        all_moves = move_and_result.keys()

        right_move = (None, 0)

        best_move_is_lossing = False

        if len(all_moves) <= 0:
            # no available move left, just return PASS, and current score board sum as value
            if not self.go_board.score_board_updated:
                self.go_board.update_score_board()

            right_move = (None, self.go_board.score_board_sum)

            # best_move_is_lossing = False
            lossing_right_move = (None, 0)

            self.display_result(color, right_move, best_move_is_lossing, lossing_right_move)

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
            # start_time = time.time()

            predict_result = self.model.predict(input_states)

            # time debug for prediction
            # end_time = time.time()
            # print('# time used for prediction:' + str(end_time - start_time) + '         ')

            move_and_predict = zip(input_pos, predict_result)

            
            move_and_predict.sort(key=lambda x:x[1], reverse=True)

            color_value = self.go_board.get_color_value(color)

            if color_value == self.go_board.ColorBlack:
                # print ('# black top move:' + str(move_and_predict[0][0]) + ' with prediction:' + str(move_and_predict[0][1]) + '         ')
                right_move = move_and_predict[0]

                # if the robot is repeating in three ko, select the second one
                if self.is_repeating() and len(move_and_predict) > 1:
                    right_move = move_and_predict[1]

                if move_and_predict[0][1] > self.komi:
                    best_move_is_lossing = False
                else:
                    best_move_is_lossing = True
                    
            elif color_value == self.go_board.ColorWhite:
                # print ('# white top move:' + str(move_and_predict[-1][0]) + ' with prediction:' + str(move_and_predict[-1][1]) + '         ')
                right_move = move_and_predict[-1]

                # if the robot is repeating in three ko, select the second one
                if self.is_repeating() and len(move_and_predict) > 1:
                    right_move = move_and_predict[-2]

                if move_and_predict[-1][1] < self.komi:
                    best_move_is_lossing = False
                else:
                    best_move_is_lossing = True

            # print ('# right move:' + str(right_move[0]) + ' with valueprediction:' + str(right_move[1]) + '       ')

        lossing_right_move = (None, 0)

        if best_move_is_lossing:
            # if best move of current color is lossing, 
            # try to get the best move of enemy and occupy it to block the best move of enemy

            enemy_color = GoBoard.other_color(color)

            lossing_move_and_result , lossing_forbidden_moves = self.simulate_all_move(enemy_color, forbidden_moves)

            lossing_all_moves = lossing_move_and_result.keys()

            if len(lossing_all_moves) <= 0:
                # none of the enemy moves can be used.
                # set the best_move_is_lossing back to False, to use the best one current player has
                best_move_is_lossing = False
            else:
                input_states = []
                input_pos = []
                for pos in lossing_all_moves:

                    temp_board = lossing_move_and_result.get(pos)
                    # temp_board.update_score_board()

                    input_states.append(temp_board.board)
                    # input_score.append(temp_board.score_board_sum)
                    input_pos.append(pos)

                # time debug for prediction
                # start_time = time.time()

                predict_result = self.model.predict(input_states)

                # time debug for prediction
                # end_time = time.time()
                # print('# time used for prediction:' + str(end_time - start_time) + '         ')

                move_and_predict = zip(input_pos, predict_result)

                
                move_and_predict.sort(key=lambda x:x[1], reverse=True)

                enemy_color_value = self.go_board.get_color_value(enemy_color)

                if enemy_color_value == self.go_board.ColorBlack:
                    lossing_right_move = move_and_predict[0]

                    if self.is_repeating() and len(lossing_move_and_result) > 1:
                        lossing_right_move = move_and_predict[1]
                    
                        
                elif enemy_color_value == self.go_board.ColorWhite: 
                    lossing_right_move = move_and_predict[-1]

                    if self.is_repeating() and len(lossing_move_and_result) > 1:
                        lossing_right_move = move_and_predict[-2]
                    

        
        self.display_result(color, right_move, best_move_is_lossing, lossing_right_move)
        
        
        if best_move_is_lossing:
            return lossing_right_move, forbidden_moves
        else:
            return right_move, forbidden_moves
    
    def display_result(self, color, right_move, best_move_is_lossing, lossing_right_move):
        display_string = '#'
        if GoBoard.get_color_value(color) == GoBoard.ColorBlack:
            display_string = display_string + ' Black Player: ' + self.name + '    '
        else:
            display_string = display_string + ' White Player: ' + self.name + '    '
        
        move_string = ' Move:' + str(right_move[0]) + '                   '
        value_string = ' Value:' + str(right_move[1]) + '                    '
        # visit_count_string = '    Count:' + str(right_node.visit_count) + '                     '
        # node_value_string = '   NodeValue:' + str(right_node.average_value) + '                    '
        # policy_value_string = '   Policy:' + str(right_node.policy_value) + '                     '

        lossing_move_string = ' Move:                                                '
        lossing_value_string = ' Value:                                              '

        if best_move_is_lossing:
            lossing_string = '--Lossing-------------      '

            # \033[1;32mo\033[0m
            lossing_move_string = ' Move:' + str(lossing_right_move[0]) + '                   '

            if lossing_right_move[0] == right_move[0]:
                lossing_value_string = ' Value:\033[1;32m' + str(lossing_right_move[1]) + '\033[0m                    '
            else:
                lossing_value_string = ' Value:' + str(lossing_right_move[1]) + '                    '
           
            
        else:
            lossing_string = '-----Not-----Lossing--      '

        display_string = display_string + move_string[0:20] + value_string[0:25] 
        display_string = display_string + lossing_string  + lossing_move_string[0:30] + lossing_value_string[0:30] 
        # display_string = display_string + visit_count_string[0:20]
        # display_string = display_string + value_string[0:25] + node_value_string[0:25] + policy_value_string[0:25]

        if GoBoard.get_color_value(color) == GoBoard.ColorBlack:
            print (display_string)
            print ('# ')
        else:
            print ('# ')
            print (display_string)



    def select_move(self, color):

        right_move, forbidden_moves = self.simulate_best_move(color)

        self.go_board.apply_move(color, right_move[0])

        # print ('# selected move:' + str(right_move))

        return right_move[0]


        
    def train(self, board_states, move_sequence, score_board):

        print (' Starting to train the model')

        training_length = len(board_states)

        training_y = []

        for i in range(training_length):
            training_y.append(score_board)

        # set the batch_size to half of the max stone number
        # to make sure that the model can be train only if the robot can be used to play.

        batch_size = self.board_size*self.board_size/2
        total_train_sample = len(board_states)

        batch_number = 0

        while (batch_number+1)*batch_size < total_train_sample:

            s_index = batch_number*batch_size
            e_index = (batch_number+1)*batch_size

            self.model.train(board_states[s_index:e_index], training_y[s_index:e_index], steps=10)

            batch_number += 1

        s_index = batch_number*batch_size
        self.model.train(board_states[s_index:], training_y[s_index:], steps=10)


        # reverse_training_states = []
        # reverse_training_y = []

        # reverse_score_board = -score_board

        # for i in range(training_length):
        #     reverse_training_states.append( -board_states[i])
        #     reverse_training_y.append(reverse_score_board)

        

        # self.model.train(reverse_training_states, reverse_training_y, steps=10)




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


    def save_model(self, model_path):
        self.model.save_model(model_path)

    def load_model(self, model_path):
        self.model.load_model(model_path)


