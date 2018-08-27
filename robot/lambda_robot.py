from go_core.lambda_goboard import LambdaGoBoard
from network.simple_model import SimpleModel

import numpy as np

import time
import random


class LambdaRobot(object):

    def __init__(self, name='DefaultLambdaRobot', layer_number=19, old_model=None, board_size=19, komi=7.5, train_iter=2):
        self.name = 'Lambda_' + name
        self.layer_number = layer_number

        self.board_size = board_size
        
        self.max_play_move = 1024
        self.ColorBlackChar = 'b'
        self.ColorWhiteChar = 'w'

        self.komi = komi

        self.train_iter = train_iter

        self.go_board = LambdaGoBoard(self.board_size)

        self.model = SimpleModel(self.name, self.board_size, layer_number=self.layer_number)

        self.move_record = []
        self.in_repeat_checking = False
        self.repeat_check_move = None
        self.board_snapshot = np.zeros((self.board_size, self.board_size))
        self.repeat_move_number = 0
        

    def reset_board(self):
        self.go_board.reset(self.board_size)

    def apply_move(self, color, pos):

        # print ('aplying move:' + color + ' in the position ' + str(pos))

        self.go_board.apply_move(color, pos)

        self.move_record.append((color, pos))

        # start_time = time.time()
        # self.board.update_score_board()
        # end_time = time.time()
        # print ('total update time:' + str(end_time - start_time))
        # print(str(self.board))

    def showboard(self):
        # self.go_board.update_score_board()
        return str(self.go_board)




    def select_move(self, color):

        right_move = self.simulate_best_move(color)

        self.go_board.apply_move(color, right_move[0])

        self.move_record.append((color, right_move[0]))

        # print ('# selected move:' + str(right_move))

        return right_move[0]


    def simulate_best_move(self, color):

        move_and_result = self.go_board.simulate_all_valid_move(color)

        # move_and_result[None] = self.go_board

        all_moves = move_and_result.keys()

        right_move = (None, 0)

        best_move_is_lossing = False

        # if len(all_moves) <= 0:
        #     # no available move left, just return PASS, and current score board sum as value
        #     if not self.go_board.score_board_updated:
        #         self.go_board.update_score_board()

        #     right_move = (None, self.go_board.score_board_sum)

        #     # best_move_is_lossing = False
        #     lossing_right_move = (None, 0)

        #     self.display_result(color, right_move, best_move_is_lossing, lossing_right_move)

        #     return right_move, forbidden_moves
        # else:
            # selected_move = all_moves[0]
        input_states = []
        input_pos = []
        for pos in all_moves:

            temp_board = move_and_result.get(pos)
            # temp_board.update_score_board()

            input_states.append(temp_board)
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

        is_repeat = False

        if (color, right_move[0]) in self.move_record:
            if not self.in_repeat_checking:
                # it is the first time we found a move we play before
                self.repeat_check_move = (color, right_move[0])
                self.in_repeat_checking = True
            else:
                # it is more than one time we found a move we play before
                if (color, right_move[0]) != self.repeat_check_move:
                    # current repeating move is not the one we found before
                    # increase the repeat_move_number
                    # stop repeating checking after (24) moves
                    # as we think it wouldn't be necessary to check it 
                    # if there are 24 continued repeating moves without seeing the first one we remember
                    self.repeat_move_number += 1
                    if self.repeat_move_number > 24:
                        self.in_repeat_checking = False
                        self.repeat_move_number = 0
                else:
                    #current repeating move is the right one we found before
                    if not (self.go_board.output_board == self.board_snapshot).all():
                        # the board we remember for the last repeating move is different from current board
                        # remember current board.
                        self.board_snapshot = self.go_board.output_board.copy() 
                    else:
                        # it is same move with same board state
                        is_repeat = True
        else:
            # it is a brand new move. reset the repeating checking setting
            self.in_repeat_checking = False
            self.repeat_move_number = 0

        if is_repeat:
            if len(move_and_predict) > 1:
                right_move = move_and_predict[1]

                
            
                

        # if the robot is repeating in three ko, select the second one
        # if self.is_repeating() and len(move_and_predict) > 1:
        #     right_move = move_and_predict[1]

            
            

            # print ('# right move:' + str(right_move[0]) + ' with valueprediction:' + str(right_move[1]) + '       ')

        # use the right move even if it is lossing
        lossing_right_move = right_move

        # # random move choossing for lossing move:
        # lossing_right_move = (None, 0)

        # if best_move_is_lossing:

        #     if len(move_and_predict) == 1:
        #         lossing_right_move = move_and_predict[0]
        #     else:
        #         # if best move is lossing, chossing random one from the first two moves.

        #         move_to_select = min(len(move_and_predict), 10)

        #         random_index = random.randint(0,move_to_select-1)
        #         lossing_right_move = move_and_predict[random_index]


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
            return lossing_right_move
        else:
            return right_move

    def display_result(self, color, right_move, best_move_is_lossing, lossing_right_move):
        display_string = '#'
        if LambdaGoBoard.get_color_value(color) == LambdaGoBoard.ColorBlack:
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

        if LambdaGoBoard.get_color_value(color) == LambdaGoBoard.ColorBlack:
            print (display_string)
            print ('# ')
        else:
            print ('# ')
            print (display_string)



    
        
    def train(self, board_states, move_sequence, score_board):
        print (' Starting to train the model:' + self.name)

        training_length = len(board_states)

        # print (' training length:' + str(training_length))
        # print (' score board is: ' + str(score_board))

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

            # print ('len of current batch:' + str(len(board_states[s_index:e_index])))

            self.model.train(board_states[s_index:e_index], training_y[s_index:e_index], steps=self.train_iter)

            batch_number += 1

        s_index = batch_number*batch_size
        self.model.train(board_states[s_index:], training_y[s_index:], steps=self.train_iter)

    def new_game(self):
        self.reset_board()


    def get_current_state(self):
        return self.go_board.output_board

    def get_score(self):
        return self.go_board.get_score()

    def get_score_board(self):
        return self.go_board.score_board

    def reset(self):
        self.go_board = LambdaGoBoard(self.board_size)

    def save_model(self, model_path):
        self.model.save_model(model_path)

    def load_model(self, model_path):
        self.model.load_model(model_path)

  


