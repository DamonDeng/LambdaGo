from dnn.value_confidence_model import ValueConfidenceModel
import numpy as np

def simple_test():

    testing_model = ValueConfidenceModel(layer_number=1)

    testing_input_data = np.zeros((19,19), dtype=int)

    testing_input_data[1][1] = 1
    testing_input_data[2][1] = 1
    testing_input_data[3][1] = 1
    testing_input_data[4][1] = 1
    testing_input_data[11][15] = -1
    testing_input_data[12][15] = -1
    testing_input_data[13][15] = -1
    testing_input_data[14][15] = -1

    testing_y = np.zeros((19,19), dtype=int)

    testing_y[1][1] = 1
    testing_y[2][1] = 1
    testing_y[3][1] = 1
    testing_y[4][1] = 1
    testing_y[1][2] = 1
    testing_y[2][2] = 1
    testing_y[3][2] = 1
    testing_y[4][2] = 1
    testing_y[11][15] = -1
    testing_y[12][15] = -1
    testing_y[13][15] = -1
    testing_y[14][15] = -1
    testing_y[11][16] = -1
    testing_y[12][16] = -1
    testing_y[13][16] = -1
    testing_y[14][16] = -1
    

    
    print('before training:')
    result = testing_model.predict(testing_input_data)

    print (result)

    result = testing_model.predict_score(testing_input_data)

    print_board(result)

    print('after training------------')

    train_data_list = []
    train_y_list = []

    for i in range(100):
        train_data_list.append(testing_input_data)
        train_y_list.append(testing_y)

    testing_model.train(train_data_list, testing_y, steps=40)

    print('train finished')

    result = testing_model.predict(testing_input_data)

    print (result)

    result = testing_model.predict_score(testing_input_data)

    print_board(result)





def print_board(input_data):

    for row in range(19):
        line_string = ''
        for col in range(19):
            temp_string = '___________________' + str(round(input_data[0][row][col], 3)) + '|'
            line_string = line_string + temp_string[-8:]
        print (line_string)


simple_test()