import numpy as np

class StoneGroup(object):

    def __init__(self, id, color_value):
        self.color_value = color_value
        self.id = id
        self.stones = set()
        self.liberties = set()

    def copy_from(self, source_group):
        self.color_value = source_group.color_value
        self.id = source_group.id
        self.stones = source_group.stones.copy()
        self.liberties = source_group.liberties.copy()

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

class LambdaGoBoard(object):

    ColorWhite = -1
    ColorBlack = 1
    ColorEmpty = 0
    ColorBorder = 3

    ColorWhiteChar = 'w'
    ColorBlackChar = 'b'

    # MoveResult_Normal = 0
    # MoveResult_SolidEye = 1
    # MoveResult_IsKo = 2
    # MoveResult_OutOfMax = 3
    # MoveResult_Pass = 4
    # MoveResult_NotEmpty = 5
    # MoveResult_IsSuicide = 6

    MaxMoveNumber = 1024

    def __init__(self, board_size=19):
        self.reset(board_size)

    def reset(self, board_size): 
        self.board_size = board_size

        # score_board_updated = False

        self.group_id = 0

        self.board = np.zeros((self.board_size+2, self.board_size+2), dtype=int)
        self.output_board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.simulate_board = np.zeros((self.board_size, self.board_size), dtype=int)


        self.score_board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.score_marker = np.zeros((self.board_size, self.board_size), dtype=int)

        self.empty_pos = set()
        # self.black_pos = set()
        # self.white_pos = set()


        self.black_suicide = set()
        self.white_suicide = set()

        self.black_eye = set()
        self.white_eye = set()

        self.single_empty_pos_index = set()

        self.ko_pos = set()

        self.stone_group = []
        self.stone_group_dict = dict()

        self.last_pos_index = None

        self.score_board_updated = False
        self.score = 0
        self.white_score = 0
        self.black_score = 0

        self.review_record = np.zeros((self.board_size, self.board_size), dtype=int)
        self.review_has_white = 0
        self.review_has_black = 0

        for row in range(self.board_size+2):
            temp_group = []
            for col in range(self.board_size+2):
                if row == 0 or col == 0 or row == self.board_size+1 or col == self.board_size+1:
                    self.board[row][col] = self.ColorBorder
                else:
                    self.empty_pos.add((row-1, col-1))
                temp_group.append(None)
            self.stone_group.append(temp_group)

        self.black_valid = self.empty_pos - self.black_suicide - self.black_eye
        self.white_valid = self.empty_pos - self.white_suicide - self.white_eye

    def get_board(self):
        return self.output_board

    def get_group_id(self):
        self.group_id = self.group_id + 1
        return self.group_id


    def copy_from(self, source_board):
        self.board_size = source_board.board_size
        self.group_id = source_board.group_id

        self.board = source_board.board.copy()
        self.output_board = source_board.output_board.copy()
        
        self.score_board = source_board.score_board.copy()
        self.score_marker = source_board.score_marker.copy()

        self.empty_pos = source_board.empty_pos.copy()
        # self.black_pos = source_board.black_pos.copy()
        # self.white_pos = source_board.white_pos.copy()

        self.black_valid = source_board.black_valid.copy()
        self.white_valid = source_board.white_valid.copy()

        self.score_board_updated = source_board.score_board_updated
        self.score_board = source_board.score_board.copy()
        self.score = source_board.score
        self.white_score = source_board.white_score
        self.black_score = source_board.black_score

        self.stone_group = []

        for row in range(self.board_size+2):
            temp_group = []
            for col in range(self.board_size+2):
                temp_group.append(None)
            self.stone_group.append(temp_group)

        self.stone_group_dict = dict()

        for inner_group_id in source_board.stone_group_dict.keys():
            temp_group = StoneGroup(1, 1)
            temp_group.copy_from(source_board.stone_group_dict[inner_group_id])
            self.stone_group_dict[inner_group_id] = temp_group

            for inner_stone in temp_group.stones:
                (inner_row_index, inner_col_index) = inner_stone
                self.stone_group[inner_row_index][inner_col_index] = temp_group

    def copy(self):
        new_board = LambdaGoBoard(self.board_size)
        new_board.copy_from(self)
        return new_board
        
    def get_valid_move(self, color):
        if color == LambdaGoBoard.ColorBlackChar:
            return self.black_valid
        elif color == LambdaGoBoard.ColorWhiteChar:
            return self.white_valid
        return None

    def apply_move(self, color, pos):
        color_value = LambdaGoBoard.get_color_value(color)
        self.apply_move_value(color_value, pos)
        self.score_board_updated = False


    def apply_move_value(self, color_value, pos):

        if pos is None:
            # it is a pass move
            self.last_pos_index = None
            return True

        (row_index, col_index) = self.get_index(pos)

        if self.board[row_index][col_index] != self.ColorEmpty:
            # it is not empty, failed
            return False

        #########################
        ## handling the neighbour with same color
        current_neighbour = self.get_neighbour_group(color_value, row_index, col_index)

        neighbour_number = len(current_neighbour)

        # print ('# neighbour number is:' + str(neighbour_number))

        if neighbour_number == 0:
            target_group = StoneGroup(self.get_group_id(), color_value)
            self.stone_group_dict[target_group.id] = target_group
        else:
            target_group = current_neighbour[0]
            target_group.remove_liberty((row_index, col_index))

        target_group.add_stone((row_index, col_index))
        
        liberty_index = self.get_surrounded_empty(row_index, col_index)
        for pos_index in liberty_index:
            target_group.add_liberty(pos_index)

        # print ('# before merging, the liberty of current group is:' + str(target_group.get_liberty_number()))

        # print ('# liberties:')
        # for pos in target_group.liberties:
        #     print ('# ' + str(pos))

        if neighbour_number > 1:
            # need to merge other surrounded neighbour group, and update the pointer in self.stone_group
            for i in range (1, neighbour_number):
                current_neighbour[i].remove_liberty((row_index, col_index))
                target_group.merge_from(current_neighbour[i])
            
            for i in range (1, neighbour_number):
                self.update_stone_group(current_neighbour[i], target_group)

            for i in range (1, neighbour_number):
                self.stone_group_dict.pop(current_neighbour[i].id)

            # print ('# after merging, the liberty of current group is:' + str(target_group.get_liberty_number()))

            # print ('# liberties:')
            # for pos in target_group.liberties:
            #     print ('# ' + str(pos))
        
        self.stone_group[row_index][col_index] = target_group

        self.board[row_index][col_index] = color_value
        self.output_board[row_index-1][col_index-1] = color_value
        

        if (row_index, col_index) in self.single_empty_pos_index:
            self.single_empty_pos_index.remove((row_index, col_index))
        else:

            surrounded_single_empty = self.get_surrounded_single_empty((row_index, col_index))

            for each_item in surrounded_single_empty:
                # pos = self.get_pos(each_item)
                self.single_empty_pos_index.add(each_item)

        # if color_value == LambdaGoBoard.ColorBlack:
        #     self.black_pos.add((row_index,col_index))
        # elif color_value == LambdaGoBoard.ColorWhite:
        #     self.white_pos.add((row_index, col_index))

        self.empty_pos.remove((row_index-1, col_index-1))


        # print ('# current group has ' + str(target_group.get_stone_number()) + ' stones')
        # for t_pos_index in target_group.stones:
        #     (t_row_index, t_col_index) = t_pos_index
        #     inner_group = self.stone_group[t_row_index][t_col_index]
        #     print ('# id of the group:' + str(t_pos_index) + ' is:' + str(inner_group.id))

        #     for pos in inner_group.liberties:
        #         print ('#                  ' + str(pos))

        #########################
        ## handling the neighbour with enemy color

        enemy_color_value = self.reverse_color_value(color_value)

        enemy_neighbour = self.get_neighbour_group(enemy_color_value, row_index, col_index)

        neighbour_number = len(enemy_neighbour)

        remove_enemy_group_num = 0
        last_single_remove_pos_index = None

        if neighbour_number > 0:
            for i in range(neighbour_number):

                # print ('# trying to remove liberty ' + str((row_index, col_index)) + ' from the following neighbour:')

                # print ('# group id:' + str(enemy_neighbour[i].id))

                # for pos in enemy_neighbour[i].liberties:
                #     print ('#                  ' + str(pos))

                enemy_neighbour[i].remove_liberty((row_index, col_index))
                # print ('# liberty_number of neighbour:' + str(i) + ' is:' + str(enemy_neighbour[i].get_liberty_number()))
                if enemy_neighbour[i].get_liberty_number() == 0:
                    remove_enemy_group_num += 1
                    if enemy_neighbour[i].get_stone_number() == 1:
                        last_single_remove_pos_index = list(enemy_neighbour[i].stones)[0]
                    # remove all the stones in the enemy group which has no liberty left
                    self.remove_all_in_group(enemy_neighbour[i])
                    # remove the group in the stone_group_dict record
                    self.stone_group_dict.pop(enemy_neighbour[i].id)

        # if current move remove just one stone, remember the location of that stone
        # so that we can check whether there is a ko move.
        if remove_enemy_group_num == 1 and last_single_remove_pos_index != None:
            pass
        else:
            last_single_remove_pos_index = None


        self.black_suicide = set()
        self.white_suicide = set()
        self.black_eye = set()
        self.white_eye = set()
        self.ko_pos = set()

        for each_pos_index in self.single_empty_pos_index:
            (single_row_index, single_col_index) = each_pos_index
            all_neighbour = self.get_all_neighbour_group(single_row_index, single_col_index)

            if len(all_neighbour) == 1:
                # only one group around this single empty point, that means it is an eye of that group
                neighbour_group = list(all_neighbour)[0]
                if neighbour_group.color_value == LambdaGoBoard.ColorBlack:
                    # it is an eye of black
                    self.black_eye.add((single_row_index-1, single_col_index-1))
                    if neighbour_group.get_liberty_number() > 1:
                        # the group around this empty point has more than one liberties
                        # so this empty point is suicide point of white.
                        self.white_suicide.add((single_row_index-1, single_col_index-1))

                elif neighbour_group.color_value == LambdaGoBoard.ColorWhite:
                    # it is an eye of white
                    self.white_eye.add((single_row_index-1, single_col_index-1))
                    if neighbour_group.get_liberty_number() > 1:
                        # the group around this empty point has more than one liberties
                        # so this empty point is suicide point of black.
                        self.black_suicide.add((single_row_index-1, single_col_index-1))
            elif len(all_neighbour) > 1:
                # more than one group around this empty point.
                black_group_bad = 0
                black_group_good = 0
                white_group_bad = 0
                white_group_good = 0

                the_bad_black_group = None
                the_bad_white_group = None

                for each_neighbour in all_neighbour:
                    if each_neighbour.get_liberty_number() == 1:
                        if each_neighbour.color_value == LambdaGoBoard.ColorBlack:
                            black_group_bad += 1
                            the_bad_black_group = each_neighbour
                        elif each_neighbour.color_value == LambdaGoBoard.ColorWhite:
                            white_group_bad += 1
                            the_bad_white_group = each_neighbour
                    elif each_neighbour.get_liberty_number() > 1:
                        if each_neighbour.color_value == LambdaGoBoard.ColorBlack:
                            black_group_good += 1
                        elif each_neighbour.color_value == LambdaGoBoard.ColorWhite:
                            white_group_good += 1
                
                if black_group_good > 0:
                    # at least one black group has more than 1 liberties
                    # this empty point couldn't be suicide point of black
                    if white_group_good > 0:
                        # at least one white group has more than 1 liberties
                        # this empty point couldn't be suicide point of white either.
                        pass
                    elif white_group_good == 0:
                        # no white group has more than 1 liberties
                        # if white player can't kill any of black group, it is a suicide point of white
                        if black_group_bad == 0:
                            self.white_suicide.add((single_row_index-1, single_col_index-1))
                        elif black_group_bad == 1:
                            # checking ko
                            # if black group only has one liberty and one stone,
                            # and it is the right stone we play this time, 
                            # current point is the right point we remove
                            if last_single_remove_pos_index != None:
                                if the_bad_black_group.get_stone_number() == 1:
                                    if list(the_bad_black_group.stones)[0] == (row_index, col_index):
                                        if (single_row_index, single_col_index) == last_single_remove_pos_index:
                                            self.ko_pos.add((single_row_index-1, single_col_index-1))

                elif black_group_good == 0:
                    # no black group has more than 1 liberties
                    # if white group has more than 1 liberties, 
                    # meybe this empty point is suicide point for black

                    if white_group_good > 0:
                        # at least one white group has more than 1 libeties
                        # if black player can't kill any of white group, this empty point is suicide point of black
                        if white_group_bad == 0:
                            self.black_suicide.add((single_row_index-1, single_col_index-1))
                        elif white_group_bad == 1:
                            # checking ko
                            # if white group only has one liberty and one stone,
                            # and it is the right stone we play this time, 
                            # current point is the right point we remove
                            if last_single_remove_pos_index != None:
                                if the_bad_white_group.get_stone_number() == 1:
                                    if list(the_bad_white_group.stones)[0] == (row_index, col_index):
                                        if (single_row_index, single_col_index) == last_single_remove_pos_index:
                                            self.ko_pos.add((single_row_index-1, single_col_index-1))
                    elif white_group_good == 0:
                        # no white group has more than 1 liberties
                        # white no black group has more than 1 liberties either
                        # need to check whether there is any white group or black group which can be killed

                        if black_group_bad > 0 and white_group_bad > 0:
                            # both side can kill each other, it is a save point for each side 
                            pass
                        elif black_group_bad > 0 and white_group_bad == 0:
                            # no white group around atall, and black group can be killed
                            # it is valid point for white, while it is suicide point for black
                            self.black_suicide.add((single_row_index-1, single_col_index-1))
                        elif black_group_bad == 0 and white_group_bad > 0:
                            # no black group around at all, and white group can be killed
                            # it is valid point for black, while it is suicide point for white
                            self.white_suicide.add((single_row_index-1, single_col_index-1))
                        else:
                            # no black group around, and no white group around, 
                            # it is in inconsistant state, raise error
                            raise Exception('Invalid situation, no stones around a single empty point')
                            
        
        self.black_valid = self.empty_pos - self.black_suicide - self.black_eye - self.ko_pos
        self.white_valid = self.empty_pos - self.white_suicide - self.white_eye - self.ko_pos

        self.last_pos_index = (row_index, col_index)

    def simulate_all_valid_move(self, color):
        move_and_result = dict()

        color_value = LambdaGoBoard.get_color_value(color)

        if color == LambdaGoBoard.ColorBlackChar:
            valid_set = self.black_valid
        elif color == LambdaGoBoard.ColorWhiteChar:
            valid_set = self.white_valid
        else:
            return None

        for pos in valid_set:
            self.simulate_move_value(color_value, pos)
            move_and_result[pos] = self.simulate_board.copy()

        move_and_result[None] = self.output_board

        return move_and_result


    def simulate_move_value(self, color_value, pos):

        self.simulate_board = self.output_board.copy()

        if pos is None:
            # it is a pass move
            # simuate board is same with last output board
            return True

        (row_index, col_index) = self.get_index(pos)

        if self.board[row_index][col_index] != self.ColorEmpty:
            # it is not empty, failed
            return False

        # as the simulating move is a valid move, so there is no suicide, we can just add current stone in simulating board
        self.simulate_board[row_index-1, col_index-1] = color_value

        # check whether we need to remove enemy around
        enemy_color_value = self.reverse_color_value(color_value)

        enemy_neighbour = self.get_neighbour_group(enemy_color_value, row_index, col_index)

        neighbour_number = len(enemy_neighbour)

        if neighbour_number > 0:
            for i in range(neighbour_number):
                if enemy_neighbour[i].get_liberty_number() == 1:
                    # the enemy neighbour only has one liberty left, 
                    # it shoule be remove, as current liberty will be remove
                    for each_neighbour_stone in enemy_neighbour[i].stones:
                        (row_index, col_index) = each_neighbour_stone
                        self.simulate_board[row_index-1][col_index-1] = LambdaGoBoard.ColorEmpty


    


        


    def get_neighbour_group(self, color_value, row_index, col_index):
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

    def get_all_neighbour_group(self, row_index, col_index):
        result = []
        all_gounp_id = set()

        if self.board[row_index-1][col_index] != LambdaGoBoard.ColorEmpty and \
           self.board[row_index-1][col_index] != LambdaGoBoard.ColorBorder:
            result.append(self.stone_group[row_index-1][col_index])
            group_id = self.stone_group[row_index-1][col_index].id
            all_gounp_id.add(group_id)

        if self.board[row_index][col_index-1] != LambdaGoBoard.ColorEmpty and \
           self.board[row_index][col_index-1] != LambdaGoBoard.ColorBorder:
            group_id = self.stone_group[row_index][col_index-1].id
            if not group_id in all_gounp_id:
                result.append(self.stone_group[row_index][col_index-1])
                all_gounp_id.add(group_id)
        
        if self.board[row_index+1][col_index] != LambdaGoBoard.ColorEmpty and \
            self.board[row_index+1][col_index] != LambdaGoBoard.ColorBorder:
            group_id = self.stone_group[row_index+1][col_index].id
            if not group_id in all_gounp_id:
                result.append(self.stone_group[row_index+1][col_index])
                all_gounp_id.add(group_id)
        
        if self.board[row_index][col_index+1] != LambdaGoBoard.ColorEmpty and \
            self.board[row_index][col_index+1] != LambdaGoBoard.ColorBorder:
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

        if len(target_group.stones) == 1:
            # only one stone was removed, it should be added into single empty set:
            
            # pos = self.get_pos(list(target_group.stones)[0])
            self.single_empty_pos_index.add(list(target_group.stones)[0])

    def remove_stone(self, pos_index):

        (row_index, col_index) = pos_index

        original_color_value = self.board[row_index][col_index]

        enemy_color_value = self.reverse_color_value(original_color_value)

        all_neighbour = self.get_neighbour_group(enemy_color_value, row_index, col_index)

        for neighbour in all_neighbour:
            neighbour.add_liberty((row_index, col_index))

        self.board[row_index][col_index] = self.ColorEmpty
        self.output_board[row_index-1][col_index-1] = self.ColorEmpty

        # if original_color_value == LambdaGoBoard.ColorBlack:
        #     self.black_pos.remove((row_index,col_index))
        # elif original_color_value == LambdaGoBoard.ColorWhite:
        #     self.white_pos.remove((row_index, col_index))

        self.empty_pos.add((row_index-1, col_index-1))



    def get_index(self, pos):
        (row, col) = pos
        return (row+1, col+1)

    def get_pos(self, pos_index):
        (row_index, col_index) = pos_index
        return (row_index-1, col_index-1)

    def is_single_empty(self, pos_index):
        (row_index, col_index) = pos_index
        
        if self.board[row_index][col_index] != LambdaGoBoard.ColorEmpty:
            return False

        surrounded_empty = self.get_surrounded_empty(row_index, col_index)

        if len(surrounded_empty) == 0:
            return True
        else:
            return False


    def get_surrounded_single_empty(self, pos_index):

        (row_index, col_index) = pos_index

        result = []

        if self.is_single_empty((row_index-1, col_index)):
            result.append((row_index-1, col_index))

        if self.is_single_empty((row_index, col_index-1)):
            result.append((row_index, col_index-1))

        if self.is_single_empty((row_index+1, col_index)):
            result.append((row_index+1, col_index))

        if self.is_single_empty((row_index, col_index+1)):
            result.append((row_index, col_index+1))

        return result



    def update_score_board(self):

        if self.score_board_updated:
            return True

        
        self.score_board = self.output_board.copy()
        self.score_marker = abs(self.output_board)

        for row in range(0, self.board_size):
            for col in range(0, self.board_size):
                if self.score_marker[row][col] != 1:
                    self.score_empty_point(row, col)
        
        self.score = self.score_board.sum()
        self.white_score = (abs(self.score_board).sum() - self.score)/2
        self.black_score = self.score + self.white_score

        self.score_board_updated = True
        return True

    def score_empty_point(self, row, col):

        self.review_record = np.zeros((self.board_size, self.board_size), dtype=int)
        self.review_has_white = 0
        self.review_has_black = 0

        review_result = []

        # print ('review_result:' + str(review_result))

        review_result = self.empty_score_review(row, col, review_result)

        # print ('review_result:' + str(review_result))

        for single_review_pos in review_result:
            (i, j) = single_review_pos
            self.score_marker[i][j] = 1
            if self.review_has_black == 1 and self.review_has_white == 1:
                self.score_board[i][j] = self.ColorEmpty
            elif self.review_has_black == 1:
                self.score_board[i][j] = self.ColorBlack
            elif self.review_has_white == 1:
                self.score_board[i][j] = self.ColorWhite


    def empty_score_review(self, row, col, review_result):

        # print('# reviewing: ' + str(row) + ',' + str(col))
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            # current location is out of board, return
            return review_result

        if self.review_record[row][col] == 1:
            # this point has been reviewed, return
            return review_result

        if self.output_board[row][col] == self.ColorEmpty:
            # color of current stone is empty point, need to check the location around.

            # set current location as reviewd
            self.review_record[row][col] = 1
            review_result.append((row, col))

            # start to check the location around
            review_result = self.empty_score_review(row+1, col, review_result)

            review_result = self.empty_score_review(row, col+1, review_result)
            
            review_result = self.empty_score_review(row-1, col, review_result)
            
            review_result = self.empty_score_review(row, col-1, review_result)

            # beside the point in review history, all the neighbours are dead, return True
            # print('# stone around are dead')
            return review_result

        elif self.output_board[row][col] == self.ColorBlack:

            self.review_has_black = 1
            # current location is black, this empty space has black around.
            return review_result

        elif self.output_board[row][col] == self.ColorWhite:

            self.review_has_white = 1
            # current location is black, this empty space has white around.
            return review_result

    def get_score(self):
        if self.score_board_updated:
            return self.score
        else:
            self.update_score_board()
            return self.score


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

    def get_score_debug_string(self):

        result = '# GoBoard\n'
        row_string = '#      '
        char_string = 'A B C D E F G H J K L M N O P Q R S T '
        row_char_string = char_string[0:self.board_size*2]

        row_string = row_string + row_char_string + '\n'
        
        result =  result + row_string
        
        for i in range(self.board_size - 1, -1, -1):
            line_number = '  ' + str(i+1) + '   '
            line = '# ' + line_number[-5:]
            for j in range(0, self.board_size):
                if self.output_board[i][j] == self.ColorBlack:
                    line = line + '\033[1;31mx\033[0m'
                if self.output_board[i][j] == self.ColorWhite:
                    line = line + '\033[1;32mo\033[0m'
                if self.output_board[i][j] == self.ColorEmpty:
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

        score_string = '#'

        if self.score_board_updated:
            total_score_string = '          ' + str(self.score) + '       '
            # black_score_string = '          ' + str(self.score_board_sum_black) + '       '
            # white_score_string = '          ' + str(self.score_board_sum_white) + '       '

            score_string = score_string + ' Score: ' + total_score_string[-11:]
            # score_string = score_string + ',  Black: ' + black_score_string[-11:]
            # score_string = score_string + ', White: ' + white_score_string[-11:]
            score_string = score_string + '\n'
            
        else:

            score_string = score_string + ' Score: NotCounted,  Black: NotCounted, White: NotCounted\n' 
        
        result = result + score_string

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


    def get_single_empty_debug_string(self):
        result = '# GoBoard Single Empty\n'
        row_string = '#      A B C D E F G H J K L M N O P Q R S T \n'
        
        result =  result + row_string
        
        for row in range(self.board_size, 0, -1):
            line_number = '  ' + str(row) + '   '
            line = '# ' + line_number[-5:]
            for col in range(1, self.board_size+1):
                if (row, col) in self.single_empty_pos_index:
                    line = line + '\033[1;32mo\033[0m'
                else:
                    line = line + '.'

                line = line + ' '

            line = line + line_number[:4]

            result = result + line + '\n'

        result = result + row_string
        
        return result


    def get_valid_debug_string(self):
        result = '# GoBoard Valid pionts:\n'
        row_string = '#      A B C D E F G H J K L M N O P Q R S T \n'
        
        result =  result + row_string
        
        for row in range(self.board_size, 0, -1):
            line_number = '  ' + str(row) + '   '
            line = '# ' + line_number[-5:]
            for col in range(1, self.board_size+1):
                pos = (row-1, col-1)

                if pos in self.black_valid and pos in self.white_valid:
                    line = line + '.'
                elif pos not in self.black_valid and pos in self.white_valid:
                    line = line + '\033[1;31mx\033[0m'
                elif pos in self.black_valid and pos not in self.white_valid:
                    line = line + '\033[1;32mo\033[0m'
                else:
                    line = line + 'E'

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
        
        # result = result + self.get_standard_debug_string()

        result = result + self.get_score_debug_string()
        
        # result = result + self.get_border_debug_string()

        # result = result + self.get_single_empty_debug_string()
        
        # result = result + self.get_valid_debug_string()
        
        return result