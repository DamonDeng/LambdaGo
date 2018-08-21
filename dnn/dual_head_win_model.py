import numpy as np
import tensorflow as tf

class DualHeadModel(object):

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
        self.input_policy_y = tf.placeholder(tf.float32, name='input_policy_y')

        self.policy_output, self.value_output, self.loss = self.define_model(self.name, self.input_x, self.input_y, self.input_policy_y)


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
        

        
    def define_model(self, name, input_x, input_y, input_policy_y):

        print('# trying to define model in name scope:' + self.name)

        reshaped_input_x = tf.reshape(input_x, [-1, self.board_size, self.board_size, 2])
        reshaped_input_y = tf.reshape(input_y, [-1, self.board_size, self.board_size, 1])
        reshaped_input_policy_y = tf.reshape(input_policy_y, [-1, (self.board_size*self.board_size+1)])

        with tf.name_scope(self.name) as name_scope:
            # shape: [None,19,19,1]
            conv1 = tf.layers.conv2d(
                inputs=reshaped_input_x,
                filters=256,
                kernel_size=[3, 3],
                padding="same",
                activation=tf.nn.tanh,
                name = name_scope + 'conv1')
            # shape: [None,19,19,256]

            print ('----')
            print (conv1.name)

            short_cut = tf.concat([conv1, reshaped_input_x], 3)   # conv1 + reshaped_input_x

            # shape: [None,19,19,258]

            for i in range(self.layer_number):

                conv_in = tf.layers.conv2d(
                    inputs=short_cut,
                    filters=256,
                    kernel_size=[3, 3],
                    padding="same",
                    activation=tf.nn.tanh,
                    name = name_scope + 'conv_in_'+str(i))

                short_cut = tf.concat([conv_in, short_cut], 3) # short_cut = conv_in + short_cut
            
            # shape: [None,19,19,258]

            value_short_cut = short_cut
            policy_short_cut = short_cut

            value_head_layer_number = 2
            policy_head_layer_number = 2

            for i in range(value_head_layer_number):
                conv_in = tf.layers.conv2d(
                    inputs=value_short_cut,
                    filters=256,
                    kernel_size=[3, 3],
                    padding="same",
                    activation=tf.nn.tanh,
                    name = name_scope + 'value_conv_in_'+str(i))

                value_short_cut = tf.concat([conv_in, value_short_cut], 3)  #value_short_cut = conv_in + value_short_cut

            for i in range(policy_head_layer_number):
                conv_in = tf.layers.conv2d(
                    inputs=policy_short_cut,
                    filters=256,
                    kernel_size=[3, 3],
                    padding="same",
                    activation=tf.nn.tanh,
                    name = name_scope + 'policy_conv_in_'+str(i))

                policy_short_cut = tf.concat([conv_in, policy_short_cut], 3) # policy_short_cut = conv_in + policy_short_cut

            policy_last_conv = tf.layers.conv2d(
                inputs=policy_short_cut,
                filters=1,
                kernel_size=[3, 3],
                padding="same",
                activation=tf.nn.tanh,
                name = name_scope + 'policy_last_conv')

            flatten_layer = tf.contrib.layers.flatten(policy_last_conv)

            last_conv = tf.layers.conv2d(
                inputs=value_short_cut,
                filters=1,
                kernel_size=[3, 3],
                padding="same",
                activation=tf.nn.tanh,
                name = name_scope + 'last_conv')
            # shape: [None,19,19,1]

            move_number = self.board_size*self.board_size+1

            policy_fully_connected = tf.layers.dense(inputs=flatten_layer, units=move_number, activation=tf.nn.tanh)
            policy_result = tf.nn.softmax(logits=policy_fully_connected)
            
            cross_entropy = tf.nn.softmax_cross_entropy_with_logits(labels=reshaped_input_policy_y, logits=policy_fully_connected, name='cross_entropy')
            policy_loss = tf.reduce_mean(cross_entropy, name='loss')
            
            value_loss = tf.reduce_mean(tf.squared_difference(last_conv, reshaped_input_y))
            value_result = tf.reduce_sum(last_conv, [1,2,3])

            total_loss = policy_loss + value_loss

        return policy_result, value_result, total_loss

    def predict(self, input_data):

        # if self.is_new_model:
        #     return

        

        result = self.session.run([self.policy_output, self.value_output], feed_dict={self.input_x:input_data})

        # print('#' + str(result))
        # print('# -------------------------------')
        # print('#' + str(len(result)))

        return result

    def train(self, input_data, input_data_y, input_data_policy_y, steps=100):
        

        # input_tensor = tf.convert_to_tensor(input_data, dtype=tf.float32)

        

        optimizer = tf.train.GradientDescentOptimizer(0.01)
        
        train = optimizer.minimize(self.loss)

        if self.is_new_model == True:
            init_g = tf.global_variables_initializer()
            init_l = tf.local_variables_initializer()
            self.session.run(init_g)
            self.session.run(init_l)
            self.is_new_model = False

        for i in range(steps):
            self.session.run(train, feed_dict={self.input_x:input_data, self.input_y:input_data_y, self.input_policy_y:input_data_policy_y})

        




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