from go_core.goboard import GoBoard


class SimpleRobot(object):

    def __init__(self):
        self.board_size = 19
        self.board = GoBoard(self.board_size)

    def reset_board(self):
        self.board.reset(self.board_size)


    def apply_move(self, color, pos):

        print ('aplying move:' + color + ' in the position ' + str(pos))

        self.board.apply_move(color, pos)

        # print(str(self.board))

    def showboard(self):
        self.board.update_score_board()
        return str(self.board)
