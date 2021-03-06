
from go_core.goboard import GoBoard


class MCTSNode(object):

    def __init__(self):

        self.simulate_board = None

        self.visit_count = 0
        # self.current_value = 0
        self.average_value = 0
        self.total_value = 0

        self.has_simulated = False

        self.is_valid = False

        self.move = (-1, -1)
        self.policy_value = 0

        self.children = []

        self.is_root = False

        self.is_leaf = True

        self.player_color = GoBoard.ColorWhite

    def set_simulate_board(self, current_board):
        self.simulate_board = GoBoard(current_board.board_size)
        self.simulate_board.copy_from(current_board)

    def get_value(self):

        # get value is called by parent,
        # so current node's player color is diffrent from parent's color
        # return negative value if current player color is Black, as that means parent's player color is white 
        if self.player_color == GoBoard.ColorBlack:
            return -self.average_value + self.policy_value/(self.visit_count+1)
        elif self.player_color == GoBoard.ColorWhite:
            return self.average_value + self.policy_value/(self.visit_count+1)
        else:
            raise Exception('Incorrect Color in MCTS Node')

    def __str__(self):
        result_string = ''
        result_string = result_string + 'IsRoot:' + str(self.is_root) + '\n'
        result_string = result_string + 'VisitCount:' + str(self.visit_count) + '\n'
        result_string = result_string + 'TotalValue:' + str(self.total_value) + '\n'
        result_string = result_string + 'AverageValue:' + str(self.average_value) + '\n'
        # result_string = result_string + 'CurrentValue:' + str(self.is_root) + '\n'
        result_string = result_string + 'Policy:' + str(self.policy_value) + '\n'

        return result_string
        
