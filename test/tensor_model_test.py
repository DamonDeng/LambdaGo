from dnn.tensor_model import TensorModel
import numpy as np
import time

board_size = 19

input_x = np.zeros((180, board_size, board_size, 1), dtype=int)
random_x = np.random.rand(180, board_size, board_size, 1) * 2 - 1

random_y = np.random.rand(180, board_size, board_size, 1) * 2 - 1


for index in range(180):
    for i in range(board_size):
        for j in range(board_size):
            if random_x[index][i][j][0] < -0.6:
                input_x[index][i][j][0] = -1
            elif random_x[index][i][j][0] > 0.6:
                input_x[index][i][j][0] = 1
            else:
                input_x[index][i][j][0] = 0




model = TensorModel()

# model.train(input_x, random_y)

# model.save_model('./model/firstmodel.mdl')

model.load_model('./model/firstmodel.mdl')

time_start=time.time()



model.predict(input_x)

time_end=time.time()
print 'time used:' + str(time_end-time_start)

