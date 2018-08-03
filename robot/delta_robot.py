from go_core.delta_goboard import DeltaGoBoard
# from dnn.tensor_model import TensorModel

import time
import random


class SimpleRobot(object):

    def __init__(self, name='DefaultDeltaRobot', layer_number=19, old_model=None):
        self.name = name
        self.layer_number = layer_number

        self.board_size = 19
        
        self.max_play_move = 1024
        self.ColorBlackChar = 'b'
        self.ColorWhiteChar = 'w'

        self.komi = 7.5

        self.go_board = DeltaGoBoard(self.board_size)

        

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
        # self.go_board.update_score_board()
        return str(self.go_board)




    def select_move(self, color):

        return (0,0)


        
    def train(self, board_states, move_sequence, score_board):

        print ('# pretent to be in training state....')

    def new_game(self):
        self.reset_board()


    def get_current_state(self):
        return self.go_board.board

  


