from go_core.goboard import GoBoard
from dnn.tensor_model import TensorModel
from robot.simple_robot import SimpleRobot

import time
import random


class SelfTrainer(object):

    SwitchThreadhold = 0.8
    MinPlayTime = 10

    def __init__(self, teacher_robot, student_robot, layer_number=19):

        self.layer_number = layer_number

        self.board_size = 19

        self.max_play_move = 1024
        self.ColorBlackChar = 'b'
        self.ColorWhiteChar = 'w'

        self.current_black_player = 'student'

        self.komi = 7.5

        self.upgrade_times = 0

        self.reset_statistic()

        # use current time as prefix of saved model
        self.prefix = str(time.strftime("%Y_%m_%d_%H_%M",time.localtime(time.time())))
        self.model_dir = './model/'

        self.teacher = teacher_robot
        self.student = student_robot

    def reset_statistic(self):
        self.train_iter = 0
        self.black_win_times = 0
        self.white_win_times = 0
        self.teacher_win_as_black = 0
        self.teacher_win_as_white = 0
        self.student_win_as_black = 0
        self.student_win_as_white = 0
        self.different_score_times = 0
        self.game_played = 0
        self.win_percentage = 0

        

    def self_play(self, black_robot, white_robot):

        # return: is_both_pass?, score, board_states, score_board

        both_pass = False

        board_states = []
        move_sequence = []

        black_robot.new_game()
        white_robot.new_game()

        board_states.append(black_robot.get_current_state())

        for i in range(self.max_play_move):
            self.print_train_title()

            selected_black_move = black_robot.select_move(self.ColorBlackChar)
            white_robot.apply_move(self.ColorBlackChar, selected_black_move)

            move_sequence.append((self.ColorBlackChar, selected_black_move))
            # append current state into board_sates list
            # only add current state from one robot: black_robot, 
            # as white_robot is in same state if everything goes well.
            board_states.append(black_robot.get_current_state())
            
            black_robot.go_board.update_score_board()
            print (str(black_robot.go_board))
            # print (description)

            self.print_train_title()
            
            selected_white_move = white_robot.select_move(self.ColorWhiteChar)
            black_robot.apply_move(self.ColorWhiteChar, selected_white_move)

            move_sequence.append((self.ColorWhiteChar, selected_white_move))
            # append current state into board_sates list
            # only add current state from one robot: black_robot, 
            # as white_robot is in same state if everything goes well.
            board_states.append(black_robot.get_current_state())
            
            white_robot.go_board.update_score_board()
            print (str(white_robot.go_board))
            # print (description)

            if selected_black_move == None and selected_white_move == None:
                both_pass = True
                # add additional pass move in the move_sequence, 
                # so that the number of board_states and move_sequence are same
                move_sequence.append((self.ColorWhiteChar, None))
                break

        if not both_pass:
            print ('Out of the max play move: ' + str(self.max_play_move))
            return False, None, None, None, None
        else:
            # print ('Both play PASS!')
            black_score = black_robot.get_score()
            white_score = white_robot.get_score()
            
            if black_score != white_score:
                self.different_score_times = self.different_score_times + 1
                return False, None, None, None
            else:
                # black_score is equal to white_score
                # that means both player agree with the score
                # just return black_score as result

                score_board = black_robot.get_score_board()

                return True, black_score, board_states, move_sequence, score_board


    def self_train(self, iter_number = 10):

        self.reset_statistic()

        while self.upgrade_times < iter_number:

            self.train_iter = self.train_iter + 1

            # clear the screen while started to train
            print('\033[H\033[J')

            self.current_black_player = 'student'

            both_pass, score, board_states, move_sequence, score_board = self.self_play(self.student, self.teacher)

            if both_pass:
                if score > self.komi:
                    self.black_win_times = self.black_win_times + 1
                    self.student_win_as_black = self.student_win_as_black + 1
                elif score <= self.komi:
                    self.white_win_times = self.white_win_times + 1
                    self.teacher_win_as_white = self.teacher_win_as_white + 1

                print ('# Both pass, trying to train student as black.')
                self.student.train(board_states, move_sequence, score_board)
            else:
                print ('# reach max move, ignore this game')

            self.game_played = self.game_played + 1
            self.student.reset()
            self.teacher.reset()
                    
            self.current_black_player = 'teacher'
            both_pass, score, board_states, move_sequence, score_board = self.self_play(self.teacher, self.student)

            if both_pass:
                if score > self.komi:
                    self.black_win_times = self.black_win_times + 1
                    self.teacher_win_as_black = self.teacher_win_as_black + 1
                elif score <= self.komi:
                    self.white_win_times = self.white_win_times + 1
                    self.student_win_as_white = self.student_win_as_white + 1

                print ('# Both pass, trying to train student as white.')
                self.student.train(board_states, move_sequence, score_board)
            else:
                print ('# reach max move, ignore this game')

            self.game_played = self.game_played + 1
            self.student.reset()
            self.teacher.reset()

            self.win_percentage = (self.student_win_as_black + self.student_win_as_white)/self.game_played

            if self.game_played > self.MinPlayTime and self.win_percentage > self.SwitchThreadhold:
                # student win enough times, 
                # going to switch the model of student to teacher

                self.reset_statistic()

                model_path = self.model_dir + self.prefix + '__' + str(self.upgrade_times)

                self.student.save_model(model_path)
                self.teacher.load_model(model_path)

                self.upgrade_times = self.upgrade_times + 1

                


                    
    def print_train_title(self): 
        # moving the cursor to up left corner
        print('\x1b[0;0f')
        print ('# Self Train::::  Teacher upgrade times:' + str(self.upgrade_times) +'  Current iter:' + str(self.train_iter))

        win_string = '# Black Win:' + str(self.black_win_times) + '       White Win:' + str(self.white_win_times) 
        win_string = win_string + '   Student Win:' + str(self.student_win_as_black + self.student_win_as_white)
        win_string = win_string + '  GamePlayed:' + str(self.game_played)
        win_string = win_string + '  WinPercentage:' + str(self.win_percentage)
        print (win_string)
        print ('# Black Win as student:' + str(self.student_win_as_black) + '       White Win as teacher:' + str(self.teacher_win_as_white))
        print ('# Black Win as teacher:' + str(self.teacher_win_as_black) + '       White Win as student:' + str(self.student_win_as_white))
        print ('# Current Black Player:' + self.current_black_player)
        print ('#-------------------------------------------------------------#')

