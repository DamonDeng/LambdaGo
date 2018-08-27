from go_core.lambda_goboard import LambdaGoBoard
import random
import time
import sys

def random_move_in_board(go_board,  step_to_run):

    move_step = 0
    is_both_pass = False

    black_pass = False
    white_pass = False

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

        if move_step >= step_to_run:
            break

        if black_pass and white_pass:
            is_both_pass = True
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

        if move_step >= step_to_run:
            break
        
        if black_pass and white_pass:
            is_both_pass = True
            break

    return move_step

def random_move_with_copy(go_board,  step_to_run):

    move_step = 0
    is_both_pass = False

    black_pass = False
    white_pass = False

    parallel_copy = go_board.copy()

    while True:

        black_pass = False
    
        valid_move = go_board.get_valid_move(LambdaGoBoard.ColorBlackChar)

        move_number = len(valid_move)

        move_and_result = go_board.simulate_all_valid_move(LambdaGoBoard.ColorBlackChar)

        copy_board = dict()
        has_exception = False
        incorrect_move = None

        for each_move in valid_move:
            copy_board[each_move] = go_board.copy()
            try:
                copy_board[each_move].apply_move(LambdaGoBoard.ColorBlackChar, each_move)
            except Exception, e:
                incorrect_move = each_move
                has_exception = True
                break

            copy_board_result = copy_board[each_move].output_board
            simulate_board_result = move_and_result[each_move]

            if (copy_board_result == simulate_board_result).all() :
                # print ('equal'),
                pass
            else:
                print ('Error, different')

        if has_exception:
            debug_copy_board(go_board, incorrect_move)

        if move_number < 1:
            black_pass = True
        else:
            random_index = random.randint(0,move_number-1)
            random_move = list(valid_move)[random_index]
            go_board.apply_move(LambdaGoBoard.ColorBlackChar, random_move)

            parallel_copy.apply_move(LambdaGoBoard.ColorBlackChar, random_move)

            original_board = go_board.output_board
            parallel_board = parallel_copy.output_board

            if (original_board == parallel_board).all():
                print ('.'),
                sys.stdout.flush()
            else:
                print (' !!!!!!!!! inconsisitant board of original board and parallel board')

            temp_board = parallel_board.copy()
            parallel_board = temp_board.copy()

        move_step += 1

        print (str(move_step)),
        sys.stdout.flush()

        if move_step >= step_to_run:
            break

        if black_pass and white_pass:
            is_both_pass = True
            break

        white_pass = False
        valid_move = go_board.get_valid_move(LambdaGoBoard.ColorWhiteChar)

        move_number = len(valid_move)

        move_and_result = go_board.simulate_all_valid_move(LambdaGoBoard.ColorWhiteChar)

        copy_board = dict()
        has_exception = False
        incorrect_move = None

        for each_move in valid_move:
            copy_board[each_move] = go_board.copy()

            try:
                copy_board[each_move].apply_move(LambdaGoBoard.ColorWhiteChar, each_move)
            except Exception, e:
                incorrect_move = each_move
                has_exception = True
                break

            copy_board_result = copy_board[each_move].output_board
            simulate_board_result = move_and_result[each_move]

            if (copy_board_result == simulate_board_result).all() :
                # print ('equal'),
                pass
            else:
                print ('Error, different')

        if has_exception:
            debug_copy_board(go_board, incorrect_move)

        if move_number < 1:
            white_pass = True
        else:

            random_index = random.randint(0,move_number-1)
            random_move = list(valid_move)[random_index]
            go_board.apply_move(LambdaGoBoard.ColorWhiteChar, random_move)

            parallel_copy.apply_move(LambdaGoBoard.ColorWhiteChar, random_move)

            original_board = go_board.output_board
            parallel_board = parallel_copy.output_board

            if (original_board == parallel_board).all():
                print ('.'),
                sys.stdout.flush()
            else:
                print (' !!!!!!!!! inconsisitant board of original board and parallel board')

            temp_board = parallel_board.copy()
            parallel_board = temp_board.copy()


        move_step += 1

        print (str(move_step)),
        sys.stdout.flush()

        if move_step >= step_to_run:
            break
        
        if black_pass and white_pass:
            is_both_pass = True
            break

    return move_step


def debug_copy_board(go_board, incorrect_move):
    print ('Got exception:' + str(incorrect_move))

    print ('Copy a new board to and apply again.')

    new_copy = go_board.copy()

    print ('==========================================')

    for row in range(new_copy.board_size):
        print_line = ''
        for col in range(new_copy.board_size):
            if new_copy.stone_group[row+1][col+1] == None:
                temp_id = -1
            else:
                temp_id = new_copy.stone_group[row+1][col+1].id

            print_line = print_line + '   '+ str(temp_id)
        print (print_line)

    print ('---------------------------')

    for row in range(go_board.board_size):
        print_line = ''
        for col in range(go_board.board_size):
            if go_board.stone_group[row+1][col+1] == None:
                temp_id = -1
            else:
                temp_id = go_board.stone_group[row+1][col+1].id
            print_line = print_line + '   '+ str(temp_id)
        print (print_line)


    print ('len of original groupdict: ' + str(len(go_board.stone_group_dict)))
    print ('len of copy groupdict: ' + str(len(new_copy.stone_group_dict)))
    
    for group in new_copy.stone_group_dict.values():
        original_group = go_board.stone_group_dict[group.id]

        stone_different1 = len(group.stones - original_group.stones)
        stone_different2 = len(original_group.stones - group.stones)

        liberty_different1 = len(group.liberties - original_group.liberties)
        liberty_different2 = len(original_group.liberties - group.liberties)


        if stone_different1 != 0 or \
            stone_different2 != 0 or \
            liberty_different1 != 0 or \
            liberty_different2 != 0:
            print ('Found different group!!!')

            print ('==============================================================')
            print ('Original stones: -----------')

            for each_stone in original_group.stones:
                print (str(each_stone))

            print ('Original libertys: -----------')
            for each_liberty in original_group.liberties:
                print (str(each_liberty))

            print ('------------------------------------------')
            print ('copy stones: -----------')

            for each_stone in group.stones:
                print (str(each_stone))
                
            print ('copy liberty: -----------')
            for each_liberty in group.liberties:
                print (str(each_liberty))

    new_copy.apply_move(LambdaGoBoard.ColorBlackChar, incorrect_move)

    print('Done!, work with new copied baord.')

    print ('Trying to apply the incorrect move to original board.')
    go_board.apply_move(LambdaGoBoard.ColorBlackChar, incorrect_move)
    print ('Done, original board is OK with the incorrect move.')
    print ('Trying to compare copy board and original board')

def display_board(go_board):
    clear_screen()
    print('\x1b[0;0f')
    print (str(go_board))

def clear_screen():
    # clear the screen
    print('\033[H\033[J')

def random_play():

    go_board = LambdaGoBoard(19)

    clear_screen()
    
    start_time = time.time()

    move_step = random_move_in_board(go_board, 800)

    end_time = time.time()

    display_board(go_board)

    print ('Total move steps: ' + str(move_step))

    print ('Time used: ' + str(end_time - start_time))

    print ('Time per move:' + str((end_time-start_time)/move_step))

def random_play_with_copy():

    go_board = LambdaGoBoard(19)

    # clear_screen()
    
    start_time = time.time()

    move_step = random_move_with_copy(go_board, 800)

    end_time = time.time()

    display_board(go_board)

    print ('Total move steps: ' + str(move_step))

    print ('Time used: ' + str(end_time - start_time))

    print ('Time per move:' + str((end_time-start_time)/move_step))
    


    
def copy_test():

    a_board = LambdaGoBoard(19)

    random_move_in_board(a_board, 200)

    start_time = time.time()
    b_board = LambdaGoBoard(19)

    b_board.copy_from(a_board)

    end_time = time.time()

    random_move_in_board(b_board, 400)

    print str(b_board)

    print ('time used to copy: ' + str(end_time - start_time))


def multiple_random_play_with_copy():
    for i in range(100):
        random_play_with_copy()
# random_play()
# copy_test()
# random_play_with_copy()
multiple_random_play_with_copy()