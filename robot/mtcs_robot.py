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
        self.simulate_board_list = []
        self.max_play_move = 1024
        self.ColorBlackChar = 'b'
        self.ColorWhiteChar = 'w'

        self.BlackIdentify = np.ones((self.board_size, self.board_size), dtype=int)
        self.WhiteIdentify = np.ones((self.board_size, self.board_size), dtype=int) * -1

        self.komi = 7.5

        self.PosArray = []

        self.root_node = MTCSNode()
        self.root_node.is_root = True
        self.root_node.is_leaf = True

        for row in range(self.board_size):
            for col in range(self.board_size):
                self.PosArray.append((row, col))

        self.PosArray.append(None)

        # init board_size*board_size of simulating board
        for i in range (self.board_size*self.board_size):
            self.simulate_board_list.append(GoBoard(self.board_size))

        self.simulate_board = GoBoard(self.board_size)

        self.go_board = GoBoard(self.board_size)

        if old_model is None:
            self.model = DualHeadModel(self.name, self.board_size, layer_number=self.layer_number)
        else:
            print ('Trying to load old model for continue training:' + './model/' + old_model)
            self.model = DualHeadModel(self.name, self.board_size, model_path='./model/' + old_model, layer_number=self.layer_number)
        

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
        # create a new node as root node, we may need to reuse node from original tree in the future:
        self.root_node = MTCSNode()

        self.root_node.set_simulate_board(self.go_board)
        self.root_node.player_color = GoBoard.get_color_value(color)
        self.root_node.is_root = True

        self.expand_mtcs_node(self.root_node, None)

        right_move = self.mcts_search(self.root_node)

        return right_move

    def mcts_search(self, root_node):

        right_move = (None, 0)

        for i in range(self.search_time):
            # node_visited = []
            start_time = time.time()
            self.search_to_expand(root_node)
            end_time = time.time()

            print ('Search to Expand time:' + str(end_time - start_time))

            # print ('searching......, iter:' + str(i))
            # value = self.expand_mtcs_node(node_visited)
            # self.node_back_up(node_visited, value)

        right_node = self.lookup_right_node(self.root_node)

        right_move = (right_node.move, right_node.current_value)

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

                start_time = time.time()

                value = self.expand_mtcs_node(best_node, current_node)

                end_time = time.time()

                print ('    node Expand time:' + str(end_time - start_time))

            else:
                # print('searching into best child:' + str(best_node.move) + '.........................................')
                value = self.search_to_expand(best_node)

            # print('value from child is:' + str(value))
            # print('number of children of current node:' +str(len(current_node.children)))
            current_node.visit_count = current_node.visit_count + 1
            current_node.total_value = current_node.total_value + value
            current_node.average_value = current_node.average_value/current_node.visit_count
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

        current_data = []

        current_board = current_node.simulate_board.board

        current_data.append(current_board)
        if current_color == GoBoard.ColorBlack:
            current_data.append(self.BlackIdentify)
        elif current_color == GoBoard.ColorWhite:
            current_data.append(self.WhiteIdentify)
        else:
            raise Exception('Incorrect color character')


        predict_start_time = time.time()

        result = self.model.predict(current_data)

        predict_end_time = time.time()

        print ('                Predict time:' + str(predict_end_time - predict_start_time))

        policy_array = result[0][0]

        current_value = result[1][0]
        
        move_and_policy_value = zip(self.PosArray, policy_array)

        # # need to consider whether sorting this array helps to improve the mtcs searching speed.
        # move_and_policy_value.sort(key=lambda x:x[1], reverse=True)

        simulate_start_time = time.time()

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
                current_node.children.append(new_child)

        simulate_end_time = time.time()

        print ('              Simulating time:' + str(simulate_end_time - simulate_start_time))

        current_node.is_leaf = False
        current_node.visit_count = current_node.visit_count + 1
        current_node.total_value = current_node.total_value + current_value
        current_node.average_value = current_node.total_value/current_node.visit_count
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
            

        # print (move_and_policy_value)


        # move_and_result = {}

        # forbidden_moves = []

        # # time debug for prediction
        # # start_time = time.time()

        # for row in range(self.board_size):
        #     for col in range(self.board_size):
        #         if self.go_board.is_empty((row, col)):
        #             board_index = row*self.board_size + col
        #             self.simulate_board_list[board_index].copy_from(self.go_board)
        #             is_valid, reason = self.simulate_board_list[board_index].apply_move(color, (row,col))
        #             if is_valid == True:
        #                 if pos_filter != None:
        #                     if not (row, col) in pos_filter:
        #                         move_and_result[(row, col)] = self.simulate_board_list[board_index]
        #                 else:
        #                     move_and_result[(row, col)] = self.simulate_board_list[board_index]
        #             else:
        #                 if reason == self.go_board.MoveResult_IsKo or \
        #                    reason == self.go_board.MoveResult_IsSuicide or \
        #                    reason == self.go_board.MoveResult_SolidEye:
        #                     forbidden_moves.append((row, col))

        # all_moves = move_and_result.keys()

        # right_move = (None, 0)

        # best_move_is_lossing = False

        # if len(all_moves) <= 0:
        #     # no available move left, just return PASS, and current score board sum as value
        #     if not self.go_board.score_board_updated:
        #         self.go_board.update_score_board()

        #     right_move = (None, self.go_board.score_board_sum)

        #     return right_move, forbidden_moves
        # else:
        #     # selected_move = all_moves[0]
        #     input_states = []
        #     input_pos = []
        #     for pos in all_moves:

        #         temp_board = move_and_result.get(pos)
        #         # temp_board.update_score_board()

        #         input_states.append(temp_board.board)
        #         # input_score.append(temp_board.score_board_sum)
        #         input_pos.append(pos)

        #     # time debug for prediction
        #     start_time = time.time()

        #     predict_result = self.model.predict(input_states)

        #     # time debug for prediction
        #     # end_time = time.time()
        #     # print('# time used for prediction:' + str(end_time - start_time) + '         ')

        #     move_and_predict = zip(input_pos, predict_result)

            
        #     move_and_predict.sort(key=lambda x:x[1], reverse=True)

        #     color_value = self.go_board.get_color_value(color)

        #     if color_value == self.go_board.ColorBlack:
        #         print ('# black top move:' + str(move_and_predict[0][0]) + ' with prediction:' + str(move_and_predict[0][1]) + '         ')

        #         if move_and_predict[0][1] > self.komi:
        #             right_move = move_and_predict[0]
        #             best_move_is_lossing = False
        #         else:
        #             right_move = move_and_predict[0]
        #             best_move_is_lossing = True
                    
        #     elif color_value == self.go_board.ColorWhite:
        #         print ('# white top move:' + str(move_and_predict[-1][0]) + ' with prediction:' + str(move_and_predict[-1][1]) + '         ')

        #         if move_and_predict[-1][1] < self.komi:
        #             right_move = move_and_predict[-1]
        #             best_move_is_lossing = False
        #         else:
        #             right_move = move_and_predict[-1]
        #             best_move_is_lossing = True

        #     # print ('# right move:' + str(right_move[0]) + ' with valueprediction:' + str(right_move[1]) + '       ')

        # if not best_move_is_lossing:
        #     print ('#----not----lossing-----')
        #     print ('#                                                                     ')
                   
        #     return right_move, forbidden_moves

        # print ('#-lossing---------------')


        # # just using random selection while it is lossing:

        

        # random_int = random.randint(0, len(move_and_predict)-1)

        # right_move = move_and_predict[random_int]

        # print ('# random move:' + str(right_move[0]) + ' with prediction:' + str(right_move[1]) + '    ')
        

        # return right_move


    def select_move(self, color):

        right_move = self.simulate_best_move(color)

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


