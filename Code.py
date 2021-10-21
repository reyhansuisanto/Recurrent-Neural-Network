# -*- coding: utf-8 -*-
"""Quiz 2 ANN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1AuDLzAO7FBxFw7GurgPtVQUoa0f93kbG
"""

import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

dataset = pd.read_csv('dataset.csv')
dataset = dataset.drop(['Year','Quarter'],axis = 1)

split = int(len(dataset) * 0.25)
training_dataset =  dataset[ : split]
testing_dataset = dataset[ split : ]

scaler = MinMaxScaler()
scaler = scaler.fit(dataset)

normalized_training_dataset = scaler.transform(training_dataset)
normalized_testing_dataset =scaler.transform(testing_dataset)

layer = {
    'input':1,
    'output':1
}

context_count = 4
time_steps = 2
batch_size = 4

cell = tf.contrib.rnn.BasicRNNCell(context_count, activation = tf.nn.sigmoid)

tf.contrib.rnn.OutputProjectionWrapper(cell, output_size = layer['output'], activation=tf.nn.sigmoid)

x = tf.placeholder(tf.float32, [None, time_steps, layer['input']])
y = tf.placeholder(tf.float32, [None, time_steps, layer['output']])

output, _ = tf.nn.dynamic_rnn(cell, x, dtype = tf.float32)

loss = tf.reduce_mean(0.5 * (y - output)**2)
learning_rate = 0.01
train = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss)

def next_batch(dataset, batch_size, time_steps):
  x_batch = np.zeros( shape = (batch_size, time_steps, layer['input']))
  y_batch = np.zeros( shape = (batch_size, time_steps, layer['output']))
  for i in range(batch_size):
      start = np.random.randint(0, len(dataset)- time_steps)
      x_batch[i] = dataset[start : start + time_steps]
      y_batch[i] = dataset[start + 1: start + time_steps + 1]

  return x_batch, y_batch

saver = tf.train.Saver()

epoch = 1000
with tf.Session() as sess:
  sess.run(tf.global_variables_initializer())

  for i in range(1, epoch + 1):
    x_batch, y_batch = next_batch(normalized_training_dataset,batch_size, time_steps)
    feed_train = {
        x: x_batch,
        y: y_batch
    }
    sess.run(train, feed_dict = feed_train)

    if i % 200 == 0:
      print('Epoch: ', i, 'Loss: ', end = "")
      print( sess.run(loss, feed_dict = feed_train))


  saver.save(sess, 'rnn-kelas/model.ckpt')

with tf.Session() as sess:
  seed_data = list(normalized_testing_dataset)
  saver.restore(sess, 'rnn-kelas/model.ckpt')

  for i in range( len(testing_dataset)):
    x_batch = np.array(seed_data[-time_steps: ]).reshape(1,time_steps,layer['input'])

    y_prediction = sess.run(output, feed_dict = {x: x_batch})

    seed_data.append(y_prediction[0, -1, 0])

result = scaler.inverse_transform(np.array(seed_data[-len(testing_dataset):]).reshape([len(testing_dataset),1]))
testing_dataset['Prediction'] = result
testing_dataset.plot()
plt.show()