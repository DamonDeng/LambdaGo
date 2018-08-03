import numpy as np

class StoneGroup(object):

    def __init__(self, id, color):
        self.color = color
        self.id = id
        self.stones = set()
        self.liberties = set()

    def add_stone(self, pos_index):
        self.stones.add(pos_index)

    def add_liberty(self, pos_index):
        self.liberties.add(pos_index)

    def remove_liberty(self, pos_index):
        self.liberties.remove(pos_index)

    def merge_from(self, target_group):
        self.stones.update(target_group.stones)
        self.liberties.update(target_group.liberties)


    def get_stone_number(self):
        return len(self.stones)

    def get_liberty_number(self):
        return len(self.liberties)

class DeltaGoBoard(object):

    ColorWhite = -1
    ColorBlack = 1
    ColorEmpty = 0
    ColorBorder = 3

    ColorWhiteChar = 'w'
    ColorBlackChar = 'b'

    MoveResult_Normal = 0
    MoveResult_SolidEye = 1
    MoveResult_IsKo = 2
    MoveResult_OutOfMax = 3
    MoveResult_Pass = 4
    MoveResult_NotEmpty = 5
    MoveResult_IsSuicide = 6

    MaxMoveNumber = 2048

    def __init__(self, board_size=19):
        self.reset(board_size)

    def reset(self, board_size): 
        self.board_size = board_size
        self.group_id = 0
        self.board = np.zeros((self.board_size+2, self.board_size+2), dtype=int)
        self.score_board = np.zeros((self.board_size+2, self.board_size+2), dtype=int)
        self.score_marker = np.zeros((self.board_size+2, self.board_size+2), dtype=int)

        self.empty_pos = set()
        self.black_pos = set()
        self.white_pos = set()

        self.stone_group = []

        for row in range(self.board_size+2):
            temp_group = []
            for col in range(self.board_size+2):
                if row == 0 or col == 0 or row == self.board_size+1 or col == self.board_size+1:
                    self.board[row][col] = self.ColorBorder
                self.empty_pos.add((row, col))
                temp_group.append(None)
            self.stone_group.append(temp_group)
                

    def get_group_id(self):
        self.group_id = self.group_id + 1
        return self.group_id


    def copy_from(self, source_board):
        self.board_size = source_board.board_size
        self.board = source_board.board.copy()
        self.score_board = source_board.score_board.copy()
        self.score_marker = source_board.score_marker.copy()

        self.empty_pos = source_board.empty_pos.copy()
        self.black_pos = source_board.black_pos.copy()
        self.white_pos = source_board.white_pos.copy()
        

    def apply_move(self, color, pos):
        color_value = DeltaGoBoard.get_color_value(color)
        self.apply_move_value(color_value, pos)


    def apply_move_value(self, color_value, pos):

        if pos is None:
            # it is a pass move
            return True

        (row_index, col_index) = self.get_index(pos)

        if self.board[row_index][col_index] != self.ColorEmpty:
            # it is not empty, failed
            return False

        #########################
        ## handling the neighbour with same color
        current_neighbour = self.get_neighbour(color_value, row_index, col_index)

        neighbour_number = len(current_neighbour)

        print ('# neighbour number is:' + str(neighbour_number))

        if neighbour_number == 0:
            target_group = StoneGroup(self.get_group_id(), color_value)
        else:
            target_group = current_neighbour[0]
            target_group.remove_liberty((row_index, col_index))

        target_group.add_stone((row_index, col_index))
        
        liberty_index = self.get_surrounded_empty(row_index, col_index)
        for pos_index in liberty_index:
            target_group.add_liberty(pos_index)

        print ('# before merging, the liberty of current group is:' + str(target_group.get_liberty_number()))

        print ('# liberties:')
        for pos in target_group.liberties:
            print ('# ' + str(pos))

        if neighbour_number > 1:
            # need to merge other surrounded neighbour group, and update the pointer in self.stone_group
            for i in range (1, neighbour_number):
                current_neighbour[i].remove_liberty((row_index, col_index))
                target_group.merge_from(current_neighbour[i])
            
            for i in range (1, neighbour_number):
                self.update_stone_group(current_neighbour[i], target_group)

            print ('# after merging, the liberty of current group is:' + str(target_group.get_liberty_number()))

            print ('# liberties:')
            for pos in target_group.liberties:
                print ('# ' + str(pos))
        
        self.stone_group[row_index][col_index] = target_group
        self.board[row_index][col_index] = color_value

        print ('# current group has ' + str(target_group.get_stone_number()) + ' stones')
        for t_pos_index in target_group.stones:
            (t_row_index, t_col_index) = t_pos_index
            inner_group = self.stone_group[t_row_index][t_col_index]
            print ('# id of the group:' + str(t_pos_index) + ' is:' + str(inner_group.id))

            for pos in inner_group.liberties:
                print ('#                  ' + str(pos))

        #########################
        ## handling the neighbour with enemy color

        enemy_color_value = self.reverse_color_value(color_value)

        enemy_neighbour = self.get_neighbour(enemy_color_value, row_index, col_index)

        neighbour_number = len(enemy_neighbour)

        if neighbour_number > 0:
            for i in range(neighbour_number):

                print ('# trying to remove liberty ' + str((row_index, col_index)) + ' from the following neighbour:')

                print ('# group id:' + str(enemy_neighbour[i].id))

                for pos in enemy_neighbour[i].liberties:
                    print ('#                  ' + str(pos))

                enemy_neighbour[i].remove_liberty((row_index, col_index))
                print ('# liberty_number of neighbour:' + str(i) + ' is:' + str(enemy_neighbour[i].get_liberty_number()))
                if enemy_neighbour[i].get_liberty_number() == 0:
                    self.remove_all_in_group(enemy_neighbour[i])




    def get_neighbour(self, color_value, row_index, col_index):
        result = []
        all_gounp_id = set()

        if self.board[row_index-1][col_index] == color_value:
            result.append(self.stone_group[row_index-1][col_index])
            group_id = self.stone_group[row_index-1][col_index].id
            all_gounp_id.add(group_id)

        if self.board[row_index][col_index-1] == color_value:
            group_id = self.stone_group[row_index][col_index-1].id
            if not group_id in all_gounp_id:
                result.append(self.stone_group[row_index][col_index-1])
                all_gounp_id.add(group_id)
        
        if self.board[row_index+1][col_index] == color_value:
            group_id = self.stone_group[row_index+1][col_index].id
            if not group_id in all_gounp_id:
                result.append(self.stone_group[row_index+1][col_index])
                all_gounp_id.add(group_id)
        
        if self.board[row_index][col_index+1] == color_value:
            group_id = self.stone_group[row_index][col_index+1].id
            if not group_id in all_gounp_id:
                result.append(self.stone_group[row_index][col_index+1])
                all_gounp_id.add(group_id)

        return result

    def get_surrounded_empty(self, row_index, col_index):
        result = []

        if self.board[row_index-1][col_index] == self.ColorEmpty:
            result.append((row_index-1,col_index))

        if self.board[row_index][col_index-1] == self.ColorEmpty:
            result.append((row_index,col_index-1))
        
        if self.board[row_index+1][col_index] == self.ColorEmpty:
            result.append((row_index+1,col_index))
        
        if self.board[row_index][col_index+1] == self.ColorEmpty:
            result.append((row_index,col_index+1))

        return result


    def update_stone_group(self, group_to_update, target_group):

        for pos_index in group_to_update.stones:
            (row_index, col_index) = pos_index
            self.stone_group[row_index][col_index] = target_group

    def remove_all_in_group(self, target_group):

        for pos_index in target_group.stones:
            self.remove_stone(pos_index)

    def remove_stone(self, pos_index):

        (row_index, col_index) = pos_index

        original_color_value = self.board[row_index][col_index]

        enemy_color_value = self.reverse_color_value(original_color_value)

        all_neighbour = self.get_neighbour(enemy_color_value, row_index, col_index)

        for neighbour in all_neighbour:
            neighbour.add_liberty((row_index, col_index))

        self.board[row_index][col_index] = self.ColorEmpty


    def get_index(self, pos):
        (row, col) = pos
        return (row+1, col+1)


        


    # convert the color letter to color value
    @classmethod
    def get_color_value(cls, color):
        if color == 'b':
            color_value = 1
        elif color == 'w':
            color_value = -1
        else:
            raise ValueError

        return color_value

    # convert the color letter to enemy's color value
    @classmethod
    def get_enemy_color_value(cls, color):
        if color == 'b':
            color_value = -1
        elif color == 'w':
            color_value = 1
        else:
            raise ValueError
        return color_value

    # convert the color letter to color value
    @classmethod
    def get_color_char(cls, color_value):
        if color_value == 1:
            color = 'b'
        elif color_value == -1:
            color = 'w'
        else:
            raise ValueError

        return color

    # convert the color letter to enemy's color value
    @classmethod
    def get_enemy_color_char(cls, color_value):
        if color_value == -1:
            color = 'b'
        elif color_value == 1:
            color = 'w'
        else:
            raise ValueError
        return color

    # reverse the color letter
    @classmethod
    def other_color(cls, color):
        '''
        Color of other player
        '''
        if color == 'b':
            return 'w'
        if color == 'w':
            return 'b'

    # reverse the color_value 
    @classmethod
    def reverse_color_value(cls, color_value):
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
        row_string = '#      A B C D E F G H J K L M N O P Q R S T \n'
        
        result =  result + row_string
        
        for row in range(self.board_size, 0, -1):
            line_number = '  ' + str(row) + '   '
            line = '# ' + line_number[-5:]
            for col in range(1, self.board_size+1):
                if self.board[row][col] == self.ColorBlack:
                    line = line + '\033[1;31mx\033[0m'
                if self.board[row][col] == self.ColorWhite:
                    line = line + '\033[1;32mo\033[0m'
                if self.board[row][col] == self.ColorEmpty:
                    line = line + '.'

                line = line + ' '

            line = line + line_number[:4]

            result = result + line + '\n'

        result = result + row_string
        
        return result

    def get_border_debug_string(self):
        result = '# GoBoard\n'
        row_string = '#        A B C D E F G H J K L M N O P Q R S T \n'
        
        result =  result + row_string
        
        for row in range(self.board_size+1, -1, -1):
            line_number = '  ' + str(row) + '   '
            line = '# ' + line_number[-5:]
            for col in range(0, self.board_size+2):
                if self.board[row][col] == self.ColorBlack:
                    line = line + '\033[1;31mx\033[0m'
                if self.board[row][col] == self.ColorWhite:
                    line = line + '\033[1;32mo\033[0m'
                if self.board[row][col] == self.ColorEmpty:
                    line = line + '.'
                if self.board[row][col] == self.ColorBorder:
                    line = line + 'H'

                line = line + ' '

            line = line + line_number[:4]

            result = result + line + '\n'

        result = result + row_string
        
        return result


    # def get_score_only_debug_string(self):
    #     result = '# GoBoard\n'
    #     row_string = '#      A B C D E F G H J K L M N O P Q R S T \n'
        
    #     result =  result + row_string
        
    #     for i in range(self.board_size - 1, -1, -1):
    #         line_number = '  ' + str(i+1) + '   '
    #         line = '# ' + line_number[-5:]
    #         for j in range(0, self.board_size):
    #             if self.score_board[i][j] == self.ColorBlack:
    #                 line = line + '\033[1;31mx\033[0m'
    #             if self.score_board[i][j] == self.ColorWhite:
    #                 line = line + '\033[1;32mo\033[0m'
    #             if self.score_board[i][j] == self.ColorEmpty:
    #                 line = line + '.'

    #             line = line + ' '

    #         line = line + line_number[:4]

    #         result = result + line + '\n'

    #     result = result + row_string
        
    #     return result

    # def get_score_debug_string(self):

    #     result = '# GoBoard\n'
    #     row_string = '#      A B C D E F G H J K L M N O P Q R S T \n'
        
    #     result =  result + row_string
        
    #     for i in range(self.board_size - 1, -1, -1):
    #         line_number = '  ' + str(i+1) + '   '
    #         line = '# ' + line_number[-5:]
    #         for j in range(0, self.board_size):
    #             if self.board[i][j] == self.ColorBlack:
    #                 line = line + '\033[1;31mx\033[0m'
    #             if self.board[i][j] == self.ColorWhite:
    #                 line = line + '\033[1;32mo\033[0m'
    #             if self.board[i][j] == self.ColorEmpty:
    #                 if self.score_board[i][j] == self.ColorBlack:
    #                     line = line + '\033[1;31m*\033[0m'
    #                 elif self.score_board[i][j] == self.ColorWhite:
    #                     line = line + '\033[1;32m*\033[0m'
    #                 else:
    #                     line = line + '.'

    #             line = line + ' '

    #         line = line + line_number[:4]

    #         result = result + line + '\n'

    #     result = result + row_string

    #     score_string = '#'

    #     if self.score_board_updated:
    #         total_score_string = '          ' + str(self.score_board_sum) + '       '
    #         black_score_string = '          ' + str(self.score_board_sum_black) + '       '
    #         white_score_string = '          ' + str(self.score_board_sum_white) + '       '

    #         score_string = score_string + ' Score: ' + total_score_string[-10:]
    #         score_string = score_string + ',  Black: ' + black_score_string[-10:]
    #         score_string = score_string + ', White: ' + white_score_string[-10:]
    #         score_string = score_string + '\n'
            
    #     else:

    #         score_string = score_string + ' Score: NotCounted,  Black: NotCounted, White: NotCounted\n' 
        
    #     result = result + score_string

    #     return result


    # debuging function: return string representing current board
    ##############################
    def __str__(self):
        result = ''
        
        result = result + self.get_standard_debug_string()
        
        # result = result + self.get_border_debug_string()
        
        
        return result