import numpy as np
import copy

class GoBoard(object):

    def __init__(self, board_size=19):
        self.ColorBlack = 1
        self.ColorWhite = -1
        self.ColorEmpty = 0
        self.reset(board_size)

    def reset(self, board_size): 
        self.board_size = board_size
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.score_board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.score_marker = np.zeros((self.board_size, self.board_size), dtype=int)
        
        self.review_has_white = 0
        self.review_has_black = 0

        self.move_number = 0
        self.max_move_number = 2048
        self.potential_ko = False
        self.ko_remove = (-1, -1)
        self.last_move_pos = (-1, -1)

    def copy_from(self, source_board):
        self.board_size = source_board.board_size
        self.board = source_board.board.copy()
        self.move_number = source_board.move_number
        self.max_move_number = source_board.max_move_number
        self.potential_ko = source_board.potential_ko
        self.ko_remove = source_board.ko_remove
        self.last_move_pos = source_board.last_move_pos

    def is_empty(self, pos):
        (row, col) = pos
        if self.board[row][col] == self.ColorEmpty:
            return True
        else:
            return False

    def is_solid_eye(self, color, pos):
        if pos is None:
            return False

        color_value = self.get_color_value(color)
        (row, col) = pos

        if row < 1:
            if col < 1:
                if self.board[row][col + 1] != color_value:
                    return False
                elif self.board[row + 1][col] != color_value:
                    return False
                elif self.board[row + 1][col + 1] != color_value:
                    return False
                else:
                    return True
            
            elif col == self.board_size - 1:
                if self.board[row][col - 1] != color_value:
                    return False
                elif self.board[row + 1][col - 1] != color_value:
                    return False
                elif self.board[row + 1][col] != color_value:
                    return False
                else:
                    return True

            else:
                if self.board[row][col - 1] != color_value:
                    return False
                elif self.board[row][col + 1] != color_value:
                    return False
                elif self.board[row + 1][col - 1] != color_value:
                    return False
                elif self.board[row + 1][col] != color_value:
                    return False
                elif self.board[row + 1][col + 1] != color_value:
                    return False
                else:
                    return True


        elif row == self.board_size - 1:
            if col < 1:
                if self.board[row - 1][col] != color_value:
                    return False
                elif self.board[row - 1][col + 1] != color_value:
                    return False
                elif self.board[row][col + 1] != color_value:
                    return False
                else:
                    return True
            
            elif col == self.board_size - 1:

                if self.board[row - 1][col - 1] != color_value:
                    return False
                elif self.board[row - 1][col] != color_value:
                    return False
                elif self.board[row][col - 1] != color_value:
                    return False
                else:
                    return True

            else:
                if self.board[row - 1][col - 1] != color_value:
                    return False
                elif self.board[row - 1][col] != color_value:
                    return False
                elif self.board[row - 1][col + 1] != color_value:
                    return False
                elif self.board[row][col - 1] != color_value:
                    return False
                elif self.board[row][col + 1] != color_value:
                    return False
                else:
                    return True

        else:
            if col < 1:
                if self.board[row - 1][col] != color_value:
                    return False
                elif self.board[row - 1][col + 1] != color_value:
                    return False
                elif self.board[row][col + 1] != color_value:
                    return False
                elif self.board[row + 1][col] != color_value:
                    return False
                elif self.board[row + 1][col + 1] != color_value:
                    return False
                else:
                    return True
                    
            
            elif col == self.board_size - 1:

                if self.board[row - 1][col - 1] != color_value:
                    return False
                elif self.board[row - 1][col] != color_value:
                    return False
                elif self.board[row][col - 1] != color_value:
                    return False
                elif self.board[row + 1][col - 1] != color_value:
                    return False
                elif self.board[row + 1][col] != color_value:
                    return False
                else:
                    return True
                    

            else:

                if self.board[row - 1][col] != color_value:
                    return False
                elif self.board[row][col - 1] != color_value:
                    return False
                elif self.board[row][col + 1] != color_value:
                    return False
                elif self.board[row + 1][col] != color_value:
                    return False
                else:
                    corner_number = 0

                    if self.board[row - 1][col - 1] != color_value:
                        corner_number = corner_number + 1
                    
                    if self.board[row - 1][col + 1] != color_value:
                        corner_number = corner_number + 1
                    
                    if self.board[row + 1][col - 1] != color_value:
                        corner_number = corner_number + 1
                    
                    if self.board[row + 1][col + 1] != color_value:
                        corner_number = corner_number + 1
                    
                    if corner_number > 1:
                        return False
                    else:
                        return True
                    


    def apply_move(self, color, pos):

        current_move_is_ko = False

        if pos is None:
        # current player pass, just return
            return True

        # apply move to position
        # print('# applying move: ' + color + "  " + str(pos))
        last_move_number = self.move_number
        cur_move_number = self.move_number + 1

        if cur_move_number >= self.max_move_number:
            # this board has more than 1024 moves, it is full, just return
            print('#warning: reach max move number')
            return False

        (row, col) = pos
        color_value = self.get_color_value(color)
        enemy_color_value = self.get_enemy_color_value(color)

        if self.board[row][col] != 0:
            # current point is not empty, return
            return False
    

        self.board[row][col] = color_value
    
        up_removed = self.remove_if_enemy_dead(row+1, col, enemy_color_value)
        right_removed = self.remove_if_enemy_dead(row, col+1, enemy_color_value)
        down_removed = self.remove_if_enemy_dead(row-1, col, enemy_color_value)
        left_removed = self.remove_if_enemy_dead(row, col-1, enemy_color_value)

        if not (up_removed > 0 or right_removed >0 or down_removed > 0 or left_removed > 0):
            suicide = self.remove_if_dead(row, col)
            if suicide:
                return False

        if up_removed+right_removed+down_removed+left_removed > 1:
            # more than one stones were removed, it could not be a potential_ko
            self.potential_ko = False
        else:

            if self.potential_ko == True:
                # last move just remove one stone, it is a potential ko
                if self.ko_remove == pos:
                    # current move is right in the position of the removed stone by last move
                    # need to check whether current move just remove the last stone.
                    if up_removed == 1:
                        if self.last_move_pos == (row+1, col):
                            current_move_is_ko = True
                    elif right_removed == 1:
                        if self.last_move_pos == (row, col+1):
                            current_move_is_ko = True
                    elif down_removed == 1:
                        if self.last_move_pos == (row-1, col):
                            current_move_is_ko = True
                    elif left_removed == 1:
                        if self.last_move_pos == (row, col-1):
                            current_move_is_ko = True

            self.potential_ko = True
            if up_removed == 1:
                self.ko_remove = (row+1, col)
            elif right_removed == 1:
                self.ko_remove = (row, col+1)
            elif down_removed == 1:
                self.ko_remove = (row-1, col)
            elif left_removed == 1:
                self.ko_remove = (row, col-1)

        self.move_number = self.move_number + 1
        self.last_move_pos = pos

        if current_move_is_ko == True:
            return False
        else:
            if self.is_solid_eye(color, pos):
                return False
            else:
                return True



    def remove_if_enemy_dead(self, row, col, enemy_color_value):
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            return 0

        if self.board[row][col] == enemy_color_value:
            return self.remove_if_dead(row, col)
        else:
            return 0
    
    def remove_if_dead(self, row, col):
        # print('# trying to remove if it is dead: ' + str(row) + ',' +str(col))
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            return 0

        target_color_value = self.board[row][col]
        if target_color_value == 0:
            # it is empty, return 0
            # print('# move of: '+ str(cur_move_number) + ' is: ' + str(self.board[cur_move_number][row][col]))
            return 0

        self.review_record = np.zeros((self.board_size, self.board_size), dtype=int)

        # print('# trying to call dead review: ' + str(row) + ',' +str(col))
        is_dead = self.dead_review(row, col, target_color_value)
        # print('# after calling dead review: is dead: ' + str(is_dead))

        if is_dead:
            removed_number = 0
            for i in range(self.board_size):
                for j in range(self.board_size):
                    if self.review_record[i][j] == 1:
                        self.board[i][j] = 0
                        removed_number = removed_number + 1
            return removed_number

        return 0
    
    def dead_review(self, row, col, target_color_value):
        # print('# reviewing: ' + str(row) + ',' + str(col))
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            # current location is out of board, return True
            return True

        if self.review_record[row][col] == 1:
            # this point has been reviewed, return True
            return True

        if self.board[row][col] == target_color_value:
            # color of current stone is target_color_value, need to check the location around.

            # set current location as reviewd
            self.review_record[row][col] = 1

            # start to check the location around
            is_dead = self.dead_review(row+1, col, target_color_value)
            if not is_dead:
                return False

            is_dead = self.dead_review(row, col+1, target_color_value)
            if not is_dead:
                return False
            
            is_dead = self.dead_review(row-1, col, target_color_value)
            if not is_dead:
                return False
            
            is_dead = self.dead_review(row, col-1, target_color_value)
            if not is_dead:
                return False

            # beside the point in review history, all the neighbours are dead, return True
            # print('# stone around are dead')
            return True

        elif self.board[row][col] == 0:
            # current location is empty, target is not dead
            return False
        else:
            # current location has stone with enemy's color, return True
            # print('# current point has enemy stone')
            return True


    def update_score_board(self):

        self.score_marker = np.zeros((self.board_size, self.board_size), dtype=int)

        for i in range(0, self.board_size):
            for j in range(0, self.board_size):
                if self.board[i][j] == self.ColorBlack or self.board[i][j] == self.ColorWhite:
                    self.score_marker[i][j] = 1
                    self.score_board[i][j] = self.board[i][j]
                elif self.board[i][j] == self.ColorEmpty:
                    if self.score_marker[i][j] != 1:
                        self.score_empty_point(i, j)

    def score_empty_point(self, row, col):

        self.review_record = np.zeros((self.board_size, self.board_size), dtype=int)
        self.review_has_white = 0
        self.review_has_black = 0

        self.empty_score_review(row, col)

        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.review_record[i][j] == 1:
                    self.score_marker[i][j] = 1
                    if self.review_has_black == 1 and self.review_has_white == 1:
                        self.score_board[i][j] = 0
                    elif self.review_has_black == 1:
                        self.score_board[i][j] = self.ColorBlack
                    elif self.review_has_white == 1:
                        self.score_board[i][j] = self.ColorWhite



    def empty_score_review(self, row, col):

        # print('# reviewing: ' + str(row) + ',' + str(col))
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            # current location is out of board, return
            return

        if self.review_record[row][col] == 1:
            # this point has been reviewed, return
            return

        if self.board[row][col] == self.ColorEmpty:
            # color of current stone is empty point, need to check the location around.

            # set current location as reviewd
            self.review_record[row][col] = 1

            # start to check the location around
            self.empty_score_review(row+1, col)

            self.empty_score_review(row, col+1)
            
            self.empty_score_review(row-1, col)
            
            self.empty_score_review(row, col-1)

            # beside the point in review history, all the neighbours are dead, return True
            # print('# stone around are dead')
            return

        elif self.board[row][col] == self.ColorBlack:

            self.review_has_black = 1
            # current location is black, this empty space has black around.
            return

        elif self.board[row][col] == self.ColorWhite:

            self.review_has_white = 1
            # current location is black, this empty space has white around.
            return


        else:
            
            return True



    # convert the color letter to color value
    def get_color_value(self, color):
        if color == 'b':
            color_value = 1
        elif color == 'w':
            color_value = -1
        else:
            raise ValueError

        return color_value

    # convert the color letter to enemy's color value
    def get_enemy_color_value(self, color):
        if color == 'b':
            color_value = -1
        elif color == 'w':
            color_value = 1
        else:
            raise ValueError
        return color_value

    # reverse the color letter
    def other_color(self, color):
        '''
        Color of other player
        '''
        if color == 'b':
            return 'w'
        if color == 'w':
            return 'b'

    # reverse the color_value 
    def reverse_color_value(self, color_value):
        if color_value == 0:
            return 0
        elif color_value == 1:
            return -1
        elif color_value == -1:
            return 1
        else:
            raise ValueError


    def get_standard_debug_string(self):
        result = '# GoBoard\n'
        row_string = '#     A B C D E F G H J K L M N O P Q R S T \n'
        
        result =  result + row_string
        
        for i in range(self.board_size - 1, -1, -1):
            line_number = '  ' + str(i+1) + '   '
            line = '#' + line_number[-5:]
            for j in range(0, self.board_size):
                if self.board[i][j] == self.ColorBlack:
                    line = line + '\033[1;31mx\033[0m'
                if self.board[i][j] == self.ColorWhite:
                    line = line + '\033[1;32mo\033[0m'
                if self.board[i][j] == self.ColorEmpty:
                    line = line + '.'

                line = line + ' '

            line = line + line_number[:4]

            result = result + line + '\n'

        result = result + row_string
        
        return result

    def get_score_only_debug_string(self):
        result = '# GoBoard\n'
        row_string = '#     A B C D E F G H J K L M N O P Q R S T \n'
        
        result =  result + row_string
        
        for i in range(self.board_size - 1, -1, -1):
            line_number = '  ' + str(i+1) + '   '
            line = '#' + line_number[-5:]
            for j in range(0, self.board_size):
                if self.score_board[i][j] == self.ColorBlack:
                    line = line + '\033[1;31mx\033[0m'
                if self.score_board[i][j] == self.ColorWhite:
                    line = line + '\033[1;32mo\033[0m'
                if self.score_board[i][j] == self.ColorEmpty:
                    line = line + '.'

                line = line + ' '

            line = line + line_number[:4]

            result = result + line + '\n'

        result = result + row_string
        
        return result

    def get_score_debug_string(self):

        result = '# GoBoard\n'
        row_string = '#     A B C D E F G H J K L M N O P Q R S T \n'
        
        result =  result + row_string
        
        for i in range(self.board_size - 1, -1, -1):
            line_number = '  ' + str(i+1) + '   '
            line = '#' + line_number[-5:]
            for j in range(0, self.board_size):
                if self.board[i][j] == self.ColorBlack:
                    line = line + '\033[1;31mx\033[0m'
                if self.board[i][j] == self.ColorWhite:
                    line = line + '\033[1;32mo\033[0m'
                if self.board[i][j] == self.ColorEmpty:
                    if self.score_board[i][j] == self.ColorBlack:
                        line = line + '\033[1;31m*\033[0m'
                    elif self.score_board[i][j] == self.ColorWhite:
                        line = line + '\033[1;32m*\033[0m'
                    else:
                        line = line + '.'

                line = line + ' '

            line = line + line_number[:4]

            result = result + line + '\n'

        result = result + row_string
        
        return result


    # debuging function: return string representing current board
    ##############################
    def __str__(self):
        result = ''
        
        # result = result + self.get_standard_debug_string()
        
        result = result + self.get_score_debug_string()
        
        
        return result
