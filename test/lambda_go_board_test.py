from go_core.lambda_goboard import LambdaGoBoard
import random
import time

def display_board(go_board):
    print('\x1b[0;0f')
    print (str(go_board))

def clear_screen():
    # clear the screen
    print('\033[H\033[J')

def random_play():

    go_board = LambdaGoBoard(19)

    move_step = 0

    black_pass = False
    white_pass = False

    clear_screen()
    
    start_time = time.time()

    while True:

        black_pass = False
    
        valid_move = go_board.get_valid_move(LambdaGoBoard.ColorBlackChar)

        move_number = len(valid_move)

        if move_number < 1:
            black_pass = True
        else:
            random_index = random.randint(0,move_number-1)
            random_move = list(valid_move)[random_index]
            go_board.apply_move(LambdaGoBoard.ColorBlackChar, random_move)

        move_step += 1

        # display_board(go_board)

        # print ('Move number: ' + str(move_number))

        if black_pass and white_pass:
            break

        white_pass = False
        valid_move = go_board.get_valid_move(LambdaGoBoard.ColorWhiteChar)

        move_number = len(valid_move)

        if move_number < 1:
            white_pass = True
        else:

            random_index = random.randint(0,move_number-1)
            random_move = list(valid_move)[random_index]
            go_board.apply_move(LambdaGoBoard.ColorWhiteChar, random_move)

        move_step += 1

        # display_board(go_board)

        # print ('Move number: ' + str(move_number))
        
        if black_pass and white_pass:
            break

    end_time = time.time()

    display_board(go_board)

    print ('Total move steps: ' + str(move_step))

    print ('Time used: ' + str(end_time - start_time))

    print ('Time per move:' + str((end_time-start_time)/move_step))
    

random_play()
