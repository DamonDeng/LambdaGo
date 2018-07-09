import numpy as np
import tensorflow as tf

class TensorModel(object):

    def __init__(self, model_path=None):
        self.model_path = model_path

        if model_path == None:
            self.is_new_model = True
        else:
            self.is_new_model = False

        self.session = tf.Session()

        self.input_x = tf.placeholder(tf.float32, name='input_x')
        self.input_y = tf.placeholder(tf.float32, name='input_y')

        self.output, self.loss = self.define_model(self.input_x, self.input_y)


        self.saver = None

        if self.is_new_model == True:
            
            init_g = tf.global_variables_initializer()
            init_l = tf.local_variables_initializer()
            self.session.run(init_g)
            self.session.run(init_l)
        else:
            self.saver.restore(self.session, model_path)


    def __del__(self):
        self.session.close()
        

        
    def define_model(self, input_x, input_y):

        reshaped_input_x = tf.reshape(input_x, [-1, 19, 19, 1])
        reshaped_input_y = tf.reshape(input_y, [-1, 19, 19, 1])


        # shape: [None,19,19,1]
        conv1 = tf.layers.conv2d(
            inputs=reshaped_input_x,
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

        loss = tf.reduce_mean(tf.squared_difference(conv2, reshaped_input_y))

        return conv2, loss

    def predict(self, input_data):

        if self.is_new_model:
            return

        

        result = self.session.run(self.output, feed_dict={self.input_x:input_data})

        print(result)

    def train(self, input_data, input_data_y, steps=100):
        

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