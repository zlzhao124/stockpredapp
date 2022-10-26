

import tensorflow as tf
from tensorflow.keras import models, layers, optimizers, metrics
import numpy as np
from functions import evaluate_on_ticker, evaluate, get_last_step_predictions # custom-made helper functions

X_train = np.load('data/train_data.npy')
y_train = np.load('data/train_targets.npy')
X_test = np.load('data/test_data.npy')
y_test = np.load('data/test_targets.npy')


# Shuffle and split the data set
# tot_size = data.shape[0]
# np.random.seed(42)
# indexes = np.random.permutation(tot_size)
# train_ix_threshold = int(0.7*tot_size)
# val_ix_threshold = train_ix_threshold + int(0.2*tot_size)

# train_indexes = indexes[:train_ix_threshold]
# val_indexes = indexes[train_ix_threshold:val_ix_threshold]
# test_indexes = indexes[val_ix_threshold:]

# X_train, y_train = data[train_indexes], targets[train_indexes]
# X_val, y_val = data[val_indexes], targets[val_indexes]
# X_test, y_test = data[test_indexes], targets[test_indexes]




# Create model 
num_neurons = 20
model = models.Sequential([
    layers.LSTM(num_neurons, return_sequences=True, input_shape=[None, 5]),
    layers.LSTM(num_neurons, return_sequences=True),
    layers.LSTM(num_neurons, return_sequences=True),
    layers.TimeDistributed(layers.Dense(3, activation='softmax'))
    ])

def last_step_accuracy(Y_true, Y_pred):
    last_step_labels = tf.dtypes.cast(Y_true[:, -1], tf.int32)
    last_step_preds = Y_pred[:,-1]
    last_step_preds = tf.math.argmax(last_step_preds, axis=1, output_type=tf.int32)
    compare = tf.dtypes.cast(tf.equal(last_step_preds, last_step_labels), tf.int32)
    tot_correct = tf.reduce_sum(compare)
    tot_size = tf.size(last_step_labels)
    accuracy = tf.divide(tot_correct, tot_size)
    return accuracy

optimizer = optimizers.Adam(lr=0.01)
model.compile(loss='sparse_categorical_crossentropy', optimizer=optimizer, metrics=[last_step_accuracy])

# Train the model
history = model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=15)

# Model evaluation
evaluate(model, X_test, y_test)

# Save model as JSON and weights as h5
model_as_json = model.to_json()
with open("trained_model/model.json", "w") as model_file:
    model_file.write(model_as_json)
model.save_weights("trained_model/weights.h5")


