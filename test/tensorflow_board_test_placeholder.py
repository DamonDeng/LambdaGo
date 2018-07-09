import numpy as np
import tensorflow as tf
 
# Declare list of features. We only have one numeric feature. There are many
# other types of columns that are more complicated and useful.
feature_columns = [tf.feature_column.numeric_column("x", shape=[1])]
 
# An estimator is the front end to invoke training (fitting) and evaluation
# (inference). There are many predefined types like linear regression,
# linear classification, and many neural network classifiers and regressors.
# The following code provides an estimator that does linear regression.
estimator = tf.estimator.LinearRegressor(feature_columns=feature_columns)
 
# TensorFlow provides many helper methods to read and set up data sets.
# Here we use two data sets: one for training and one for evaluation
# We have to tell the function how many batches
# of data (num_epochs) we want and how big each batch should be.

board_size = 19

input_x = np.zeros((1, board_size, board_size, 1), dtype=int)
random_x = np.random.rand(1, board_size, board_size, 1) * 2 - 1

for i in range(board_size):
    for j in range(board_size):
        if random_x[0][i][j][0] < -0.6:
            input_x[0][i][j][0] = -1
        elif random_x[0][i][j][0] > 0.6:
            input_x[0][i][j][0] = 1
        else:
            input_x[0][i][j][0] = 0



random_y = np.random.rand(board_size,board_size) * 2 - 1

print(input_x)
print(random_y)

input_tensor = tf.convert_to_tensor(input_x, dtype=tf.float32)
input_y = tf.convert_to_tensor(random_y, dtype=tf.float32)

# shape: [None,19,19,1]
conv1 = tf.layers.conv2d(
    inputs=input_tensor,
    filters=32,
    kernel_size=[3, 3],
    padding="same",
    activation=tf.nn.relu,
    name = 'conv1')
# shape: [None,19,19,32]
conv2 = tf.layers.conv2d(
    inputs=conv1,
    filters=1,
    kernel_size=[3, 3],
    padding="same",
    activation=tf.nn.tanh,
    name = 'conv2')
# shape: [None,19,19,1]

loss = tf.reduce_mean(tf.squared_difference(conv2, input_y))

tf_session = tf.Session()

init_g = tf.global_variables_initializer()
init_l = tf.local_variables_initializer()

with tf_session:
    tf_session.run(init_g)
    tf_session.run(init_l)
    result = tf_session.run(conv2)

    print(result)

# np.zeros((self.board_size, self.board_size), dtype=int)

# x_train = np.array([1., 2., 3., 4.])
# y_train = np.array([0., -1., -2., -3.])
# x_eval = np.array([2., 5., 8., 1.])
# y_eval = np.array([-1.01, -4.1, -7, 0.])
# input_fn = tf.estimator.inputs.numpy_input_fn(
#     {"x": x_train}, y_train, batch_size=4, num_epochs=None, shuffle=True)
# train_input_fn = tf.estimator.inputs.numpy_input_fn(
#     {"x": x_train}, y_train, batch_size=4, num_epochs=1000, shuffle=False)
# eval_input_fn = tf.estimator.inputs.numpy_input_fn(
#     {"x": x_eval}, y_eval, batch_size=4, num_epochs=1000, shuffle=False)
 
# # We can invoke 1000 training steps by invoking the  method and passing the
# # training data set.
# estimator.train(input_fn=input_fn, steps=1000)
 
# # Here we evaluate how well our model did.
# train_metrics = estimator.evaluate(input_fn=train_input_fn)
# eval_metrics = estimator.evaluate(input_fn=eval_input_fn)
# print("train metrics: %r"% train_metrics)
# print("eval metrics: %r"% eval_metrics)
 
 
# print("------------------------------------3")

# predict_input_fn = tf.estimator.inputs.numpy_input_fn(
#     x={"x": x_train},
#     num_epochs=1,
#     shuffle=False)

# y_predict = list(estimator.predict(input_fn=predict_input_fn))

# for predict_item in y_predict:
#     print(predict_item.get('predictions'))


