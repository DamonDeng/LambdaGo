from go_core.goboard import GoBoard
from dnn.dual_head_model import DualHeadModel
from mcts.mcts_node import MTCSNode
import numpy as np

import time
import random


class MTCSRobot(object):

    def __init__(self, name='DefaultMTCSRobot', layer_number=19, old_model=None, search_time=100):
        self.name = name
        self.layer_number = layer_number
        self.search_time = search_time



        self.board_size = 19
        self.stone_number = self.board_size*self.board_size

        self.simulate_board_list = []
        self.max_play_move = 1024
        self.ColorBlackChar = 'b'
        self.ColorWhiteChar = 'w'

        self.BlackIdentify = np.ones((self.board_size, self.board_size), dtype=int)
        self.WhiteIdentify = np.ones((self.board_size, self.board_size), dtype=int) * -1

        self.komi = 7.5

        self.PosArray = []

        for row in range(self.board_size):
            for col in range(self.board_size):
                self.PosArray.append((row, col))

        self.PosArray.append(None)

        self.reset()
        
        if old_model is None:
            self.model = DualHeadModel(self.name, self.board_size, layer_number=self.layer_number)
        else:
            print ('Trying to load old model for continue training:' + './model/' + old_model)
            self.model = DualHeadModel(self.name, self.board_size, model_path='./model/' + old_model, layer_number=self.layer_number)

    def reset(self):
        self.root_node = MTCSNode()
        self.root_node.is_root = True
        self.root_node.is_leaf = True

        self.training_data = []
        self.training_score = []
        self.training_move = []

        self.simulate_board = GoBoard(self.board_size)

        self.go_board = GoBoard(self.board_size)



    def reset_board(self):
        self.go_board.reset(self.board_size)

    def apply_move(self, color, pos):

        # print ('aplying move:' + color + ' in the position ' + str(pos))

        current_data = []

        current_board = self.go_board.board

        current_data.append(current_board)

        if GoBoard.get_color_value(color) == GoBoard.ColorBlack:
            current_data.append(self.BlackIdentify)
        elif GoBoard.get_color_value(color) == GoBoard.ColorWhite:
            current_data.append(self.WhiteIdentify)
        else:
            raise Exception('Incorrect color character')

        self.training_data.append(current_data)

        if pos is None:
            current_move = np.zeros((self.board_size*self.board_size+1), dtype=int)
            current_move[self.board_size*self.board_size] = 1
            self.training_move.append(current_move)
        else:

            (row, col) = pos
            current_move = np.zeros((self.board_size*self.board_size+1), dtype=int)
            current_move[row*self.board_size+col] = 1
            self.training_move.append(current_move)

        is_valid, reason = self.go_board.apply_move(color, pos)

        # if not is_valid:
        #     print ('# incorrect move:' + color + '  pos:' + str(pos) + '  Reason:' + str(reason))
        # else:
        #     print ('#   correct move:' + color + '  pos:' + str(pos) + '                            ')

        # start_time = time.time()
        # self.board.update_score_board()
        # end_time = time.time()
        # print ('total update time:' + str(end_time - start_time))
        # print(str(self.board))

    def showboard(self):
        self.go_board.update_score_board()
        return str(self.go_board)



    def simulate_best_move(self, color, pos_filter=None):
        # create a new node as root node, we may need to reuse node from original tree in the future:
        self.root_node = MTCSNode()

        self.root_node.set_simulate_board(self.go_board)
        current_color = GoBoard.get_color_value(color)
        # root node is the node before current player play the stone, 
        # so the color of root node should be color of current color
        self.root_node.player_color = current_color
        self.root_node.is_root = True

        self.expand_mtcs_node(self.root_node, None)

        right_move = self.mcts_search(self.root_node, color)

        return right_move

    def mcts_search(self, root_node, color):

        right_move = (None, 0)

        for i in range(self.search_time):
            # node_visited = []
            # start_time = time.time()
            self.search_to_expand(root_node)
            # end_time = time.time()

            # print ('Search to Expand time:' + str(end_time - start_time))

            # print ('searching......, iter:' + str(i))
            # value = self.expand_mtcs_node(node_visited)
            # self.node_back_up(node_visited, value)

        right_node = self.lookup_right_node(self.root_node)

        right_move = (right_node.move, right_node.get_value())

        display_string = "# Player: "
        if GoBoard.get_color_value(color) == GoBoard.ColorBlack:
            display_string = display_string + "Black    "
        else:
            display_string = display_string + "White    "
        
        move_string = ' Move:' + str(right_move[0]) + '                   '
        value_string = ' Value:' + str(right_move[1]) + '                    '
        visit_count_string = '    Count:' + str(right_node.visit_count) + '                     '
        node_value_string = '   NodeValue:' + str(right_node.average_value) + '                    '
        policy_value_string = '   Policy:' + str(right_node.policy_value) + '                     '

        display_string = display_string + move_string[0:20] + visit_count_string[0:20]
        display_string = display_string + value_string[0:25] + node_value_string[0:25] + policy_value_string[0:25]

        if GoBoard.get_color_value(color) == GoBoard.ColorBlack:
            print (display_string)
            print ('# ')
        else:
            print ('# ')
            print (display_string)

        if abs(right_node.average_value) > 1:
            print('# incorrect node:')
            print (str(right_node))
            time.sleep(20)

        

        # print ('Found right move:' + str(right_move[0]) + 'with value:' + str(right_move[1]))
        # print ('Visited count: ' + str(right_node.visit_count))

        # time.sleep(5)

        return right_move

    def search_to_expand(self, current_node):

        # if not current_node.is_leaf:
        #     # it is not a leaf node, search the best one and call search_to_expand again
        best_value = -10000
        best_node = None
        for child in current_node.children:

            # print ('searching...........' + str(child.move))
            # print ('current value of best node:' + str(child.current_value))
            # print ('average value of best node:' + str(child.average_value))
            # print ('total value of best node:' + str(child.total_value))
            
            # print ('visit count of best node:' + str(child.visit_count))

            # print ('policy value of best node:' + str(child.policy_value))
            # print ('------------------------------------')

            node_value = child.get_value()
            if node_value > best_value:
                best_value = node_value
                best_node = child

        # print ('found best node:' + str(best_node.move) + '  with value:' + str(best_value))
        # print ('current value of best node:' + str(best_node.current_value))
        # print ('average value of best node:' + str(best_node.average_value))
        # print ('total value of best node:' + str(best_node.total_value))
        
        # print ('visit count of best node:' + str(best_node.visit_count))

        # print ('policy value of best node:' + str(best_node.policy_value))

        if best_node is None:
            raise Exception ('Node without valid child')
        else:
            if best_node.is_leaf:
                # print('trying to expand node.' + str(best_node.move))

                # start_time = time.time()

                value = self.expand_mtcs_node(best_node, current_node)

                # end_time = time.time()

                # print ('    node Expand time:' + str(end_time - start_time))

            else:
                # print('searching into best child:' + str(best_node.move) + '.........................................')
                value = self.search_to_expand(best_node)

            # print('value from child is:' + str(value))
            # print('number of children of current node:' +str(len(current_node.children)))
            current_node.visit_count = current_node.visit_count + 1
            current_node.total_value = current_node.total_value + value
            current_node.average_value = (current_node.total_value/current_node.visit_count) / self.stone_number
            current_node.current_value = current_node.average_value
            return value
        
        # else:
        #     value = self.expand_mtcs_node(current_node)
        #     return value




        

    def expand_mtcs_node(self, current_node, parent_node):

        # if parent_node is None:
        #     # no parent node, it is root node, we can use the value in current node, which is root node that was initialized.
        #     current_color = current_node.player_color
        # else:
        #     # copy data from parent node
        #     parent_color = parent_node.player_color
        #     current_color = GoBoard.reverse_color_value(parent_color)
        #     # enemy_color = parent_node.player_color

        #     current_node.player_color = current_color
        #     current_node.simulate_board = GoBoard(parent_node.simulate_board.board_size)
        #     current_node.simulate_board.copy_from(parent_node.simulate_board)

        #     current_node.simulate_board.apply_move(GoBoard.get_color_char(current_color), current_node.move)

        current_color = current_node.player_color
        child_color = GoBoard.reverse_color_value(current_color)

        # current_data_list = []

        current_data = []

        current_board = current_node.simulate_board.board

        current_data.append(current_board)
        if current_color == GoBoard.ColorBlack:
            current_data.append(self.BlackIdentify)
        elif current_color == GoBoard.ColorWhite:
            current_data.append(self.WhiteIdentify)
        else:
            raise Exception('Incorrect color character')

        # for i in range(361):
        #     current_data_list.append(current_data)

        # predict_start_time = time.time()

        result = self.model.predict(current_data)

        # predict_end_time = time.time()

        # print ('                Predict time:' + str(predict_end_time - predict_start_time))

        policy_array = result[0][0]

        current_value = result[1][0]
        
        move_and_policy_value = zip(self.PosArray, policy_array)

        # # need to consider whether sorting this array helps to improve the mtcs searching speed.
        # move_and_policy_value.sort(key=lambda x:x[1], reverse=True)

        # simulate_start_time = time.time()

        for single_move_and_policy in move_and_policy_value:
            
            move = single_move_and_policy[0]
            policy_value = single_move_and_policy[1]

            new_child = MTCSNode()

            new_child.simulate_board = GoBoard(self.board_size)
            new_child.simulate_board.copy_from(current_node.simulate_board)

            is_valid, reason = new_child.simulate_board.apply_move(GoBoard.get_color_char(current_color), move)

            if is_valid:
                new_child.move = move
                new_child.policy_value = policy_value
                new_child.player_color = child_color
                current_node.children.append(new_child)

        # simulate_end_time = time.time()

        # print ('              Simulating time:' + str(simulate_end_time - simulate_start_time))

        current_node.is_leaf = False
        current_node.visit_count = current_node.visit_count + 1
        current_node.total_value = current_node.total_value + current_value
        current_node.average_value = (current_node.total_value/current_node.visit_count) / self.stone_number
        current_node.current_value = current_node.average_value

        return current_value

    def lookup_right_node(self, current_node):

        most_visited_count = -1
        best_policy = -1
        most_visited_node = None

        for child in current_node.children:
            if child.visit_count > most_visited_count:
                most_visited_count = child.visit_count
                best_policy = child.policy_value
                most_visited_node = child
            elif child.visit_count == most_visited_count:
                if child.policy_value > best_policy:
                    best_policy = child.policy_value
                    most_visited_node = child

        return most_visited_node          


    def select_move(self, color):

        right_move = self.simulate_best_move(color)

        self.go_board.apply_move(color, right_move[0])

        # print ('# selected move:' + str(right_move))

        return right_move[0]


        
    def train(self, board_states, move_sequence, score_board):

        train_data_len = len(self.training_data)
        train_move_len = len(self.training_move)

        if not train_data_len == train_move_len:
            raise Exception('Inconsist state, training data and training move not in same length')

        self.go_board.update_score_board()

        result_score = self.get_score()

        if result_score > self.komi:
            for i in range(len(self.training_move)):
                if i%2 == 1:
                    # black win while current move is for white, revert it
                    self.training_move[i] = self.training_move[1] * -1 + 1
        else:
            for i in range(len(self.training_move)):
                if i%2 == 0:
                    # white win while current move is for black, revert it
                    self.training_move[i] = self.training_move[1] * -1 + 1

        result_score_board = self.go_board.score_board

        for i in range(train_data_len):
            self.training_score.append(result_score_board)

        print ('# robot ' + self.name + ' is in training.........')

        self.model.train(self.training_data, self.training_score, self.training_move, steps=2)

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


