import numpy as np
import tensorflow as tf

class SecondModel(object):

    def __init__(self, name='DefaultModel', board_size=19, model_path=None, layer_number=19):
        self.board_size = board_size
        self.model_path = model_path
        self.name = name
        self.layer_number = layer_number

        if model_path == None:
            self.is_new_model = True
        else:
            self.is_new_model = False

        self.session = tf.Session()

        self.input_x = tf.placeholder(tf.float32, name='input_x')
        self.input_y = tf.placeholder(tf.float32, name='input_y')

        self.output, self.loss = self.define_model(self.name, self.input_x, self.input_y)


        self.saver = tf.train.Saver()

        if self.is_new_model == True:
            
            init_g = tf.global_variables_initializer()
            init_l = tf.local_variables_initializer()
            self.session.run(init_g)
            self.session.run(init_l)
        else:
            self.saver.restore(self.session, model_path)


    def __del__(self):
        self.session.close()
        

        
    def define_model(self, name, input_x, input_y):

        print('# trying to define model in name scope:' + self.name)

        reshaped_input_x = tf.reshape(input_x, [-1, self.board_size, self.board_size, 1])
        reshaped_input_y = tf.reshape(input_y, [-1, 1])

        with tf.name_scope(self.name) as name_scope:
            # shape: [None,19,19,1]
            conv1 = tf.layers.conv2d(
                inputs=reshaped_input_x,
                filters=256,
                kernel_size=[3, 3],
                padding="same",
                # activation=tf.nn.relu,
                activation=tf.nn.tanh,
                name = name_scope + 'conv1')
            # shape: [None,19,19,256]

            # print ('----')
            # print (conv1.name)

            # short_cut = conv1 + reshaped_input_x

            short_cut = tf.concat([conv1, reshaped_input_x], 3)

            # shape: [None,19,19,257]

            for i in range(self.layer_number):

                conv_in = tf.layers.conv2d(
                    inputs=short_cut,
                    filters=256,
                    kernel_size=[3, 3],
                    padding="same",
                    # activation=tf.nn.relu,
                    activation=tf.nn.tanh,
                    name = name_scope + 'conv_in_'+str(i))

                # short_cut = conv_in + short_cut
                short_cut = tf.concat([conv_in, short_cut], 3)
            
            # shape: [None,19,19,257]

            last_conv = tf.layers.conv2d(
                inputs=short_cut,
                filters=1,
                kernel_size=[3, 3],
                padding="same",
                # activation=tf.nn.relu,
                activation=tf.nn.tanh,
                name = name_scope + 'last_conv')
            # shape: [None,19,19,1]

            flatten_layer = tf.contrib.layers.flatten(last_conv)

            move_number = self.board_size*self.board_size+1

            fully_connected = tf.layers.dense(inputs=flatten_layer, units=move_number, activation=tf.nn.tanh)
           
            fully_connected_output = tf.layers.dense(inputs=fully_connected, units=1, activation=tf.nn.tanh)

            sum_output = tf.reduce_sum(fully_connected_output, 1)

            loss = tf.reduce_mean(tf.squared_difference(fully_connected_output, reshaped_input_y))
            # sum_result = tf.reduce_sum(last_conv, [1,2,3])

            # round_result = tf.round(last_conv)

            # sum_result = tf.reduce_sum(round_result, [1,2,3])

        return sum_output, loss

    def predict(self, input_data):

        # if self.is_new_model:
        #     return

        

        result = self.session.run(self.output, feed_dict={self.input_x:input_data})

        # print('#' + str(result))
        # print('# -------------------------------')
        # print('#' + str(len(result)))

        return result

    def train(self, input_data, input_data_y, train_iter=100):
        

        # input_tensor = tf.convert_to_tensor(input_data, dtype=tf.float32)

        

        optimizer = tf.train.GradientDescentOptimizer(0.01)
        
        train = optimizer.minimize(self.loss)

        if self.is_new_model == True:
            init_g = tf.global_variables_initializer()
            init_l = tf.local_variables_initializer()
            self.session.run(init_g)
            self.session.run(init_l)
            self.is_new_model = False

        for i in range(train_iter):
            self.session.run(train, feed_dict={self.input_x:input_data, self.input_y:input_data_y})

        




    def save_model(self, model_path):
        self.saver = tf.train.Saver()
        self.model_path = model_path
        self.is_new_model = False
        self.saver.save(self.session, self.model_path)

    def load_model(self, model_path):
        self.saver = tf.train.Saver()
        self.model_path = model_path
        self.is_new_model = False
        self.saver.restore(self.session, self.model_path)