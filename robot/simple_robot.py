from go_core.goboard import GoBoard
from dnn.tensor_model import TensorModel


class SimpleRobot(object):

    def __init__(self):
        self.board_size = 19
        self.simulate_board_list = []
        self.max_play_move = 1024
        self.ColorBlackChar = 'b'
        self.ColorWhiteChar = 'w'
        

        # init board_size*board_size of simulating board
        for i in range (self.board_size*self.board_size):
            self.simulate_board_list.append(GoBoard(self.board_size))

        self.board = GoBoard(self.board_size)
        self.model = TensorModel(self.board_size)
        # self.model.load_model('./model/firstmodel.mdl')

    def reset_board(self):
        self.board.reset(self.board_size)

    def self_play(self):

        both_pass = False

        board_states = []

        for i in range(self.max_play_move):
            selected_black_move = self.select_move(self.ColorBlackChar)
            board_states.append(self.board.board)
            selected_white_move = self.select_move(self.ColorWhiteChar)
            board_states.append(self.board.board)
            if selected_black_move == None and selected_white_move == None:
                
                both_pass = True
                break

        if not both_pass:
            print ('Out of the max play move: ' + str(self.max_play_move))
            return False, None, None
        else:
            print ('Both play PASS!')
            self.board.update_score_board()

            print ('Result Score board:')
            # print (str(self.board))
            # print (self.board.get_score_only_debug_string())
            return True, board_states, self.board.score_board

    def self_train(self, iter_number = 10):

        for i in range(iter_number):
            self.board.reset(self.board_size)
            both_pass, board_states, score_board = self.self_play()
            if both_pass:
                print ('Both PASS: start to train the model')
                score_board_list = []
                for i in range(len(board_states)):
                    score_board_list.append(score_board)
                self.model.train(input_data=board_states, input_data_y=score_board_list, steps=10)



    def apply_move(self, color, pos):

        print ('aplying move:' + color + ' in the position ' + str(pos))

        self.board.apply_move(color, pos)

        # print(str(self.board))

    def showboard(self):
        self.board.update_score_board()
        return str(self.board)

    def select_move(self, color):
        move_and_result = {}

        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board.is_empty((row, col)):
                    board_index = row*self.board_size + col
                    self.simulate_board_list[board_index].copy_from(self.board)
                    is_valid = self.simulate_board_list[board_index].apply_move(color, (row,col))
                    if is_valid == True:
                        move_and_result[(row, col)] = self.simulate_board_list[board_index]

        # debug display of all the moves tried: 
        # for row in range(self.board_size):
        #     for col in range(self.board_size):
        #         pos = (row, col)
        #         if move_and_result.has_key(pos):
        #             print ('Result of :' + str(pos))
        #             print (str(move_and_result[pos]))
    
        selected_move = None

        all_moves = move_and_result.keys()

        # for pos in all_moves:
        #     if not self.board.is_solid_eye(color, pos):
        #         selected_move = pos
        #         break


        if len(all_moves) > 0:
            selected_move = all_moves[0]
            input_states = []
            input_pos = []
            for pos in all_moves:
                input_states.append(move_and_result.get(pos).board)
                input_pos.append(pos)

            predict_result = self.model.predict(input_states)

            move_and_predict = zip(input_pos, predict_result)

            
            move_and_predict.sort(key=lambda x:x[1])

            right_move = (None, -10000)

            color_value = self.board.get_color_value(color)

            if color_value == self.board.ColorBlack:
                right_move = move_and_predict[0]
            elif color_value == self.board.ColorWhite:
                right_move = move_and_predict[-1]


            print ('selected move:' + str(right_move[0]) + ' with value:' + str(right_move[1]))

            selected_move = right_move[0]

        #set the cursor to zero point and clean some space for display:
        print('\033[H\033[J')
        print('\x1b[0;0f')


        if selected_move == None:
            print('GenMove Result: PASS')
            print(str(self.board))
        else:
            self.board.apply_move(color, selected_move)
            print('Final Result:' + str(selected_move))
            print(str(self.board))

        return selected_move


                    

