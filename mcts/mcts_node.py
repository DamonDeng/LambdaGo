
from go_core.goboard import GoBoard


class MTCSNode(object):

    def __init__(self):

        self.simulate_board = None

        self.visit_count = 0
        self.current_value = 0
        self.average_value = 0
        self.total_value = 0

        self.has_simulated = False

        self.is_valid = False

        self.move = (-1, -1)
        self.policy_value = 0

        self.children = []

        self.is_root = False

        self.is_leaf = True

        self.player_color = GoBoard.ColorBlack

    def set_simulate_board(self, current_board):
        self.simulate_board = GoBoard(current_board.board_size)
        self.simulate_board.copy_from(current_board)

    def get_value(self):

        if self.player_color == GoBoard.ColorBlack:
            return self.current_value + self.policy_value/(self.visit_count+1)
        elif self.player_color == GoBoard.ColorWhite:
            return -self.current_value + self.policy_value/(self.visit_count+1)
        else:
            raise Exception('Incorrect Color in MCTS Node')
