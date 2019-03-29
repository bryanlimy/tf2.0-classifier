import tensorflow as tf
import tensorflow.keras as keras

from utils import HParams, Logger, get_dataset


def get_hparams():
  hparams = HParams()
  hparams.epochs = 10
  hparams.batch_size = 32
  hparams.learning_rate = 0.001
  hparams.dataset = 'mnist'
  return hparams


class Model(keras.Model):

  def __init__(self):
    super().__init__()
    self.flatten = keras.layers.Flatten()
    self.dense1 = keras.layers.Dense(
        units=128, activation=keras.activations.relu)
    self.dense2 = keras.layers.Dense(
        units=64, activation=keras.activations.relu)
    self.dense3 = keras.layers.Dense(
        units=10, activation=keras.activations.softmax)

  def call(self, inputs):
    output = self.flatten(inputs)
    output = self.dense1(output)
    output = self.dense2(output)
    output = self.dense3(output)
    return output


@tf.function
def train_step(features, labels, model, loss_function, optimizer):
  with tf.GradientTape() as tape:
    predictions = model(features)
    loss = loss_function(labels, predictions)
  gradients = tape.gradient(loss, model.trainable_variables)
  optimizer.apply_gradients(zip(gradients, model.trainable_variables))
  return loss, predictions


@tf.function
def test_step(features, labels, model, loss_function):
  predictions = model(features)
  loss = loss_function(labels, predictions)
  return loss, predictions


@tf.function
def predict(features, model):
  return model(features)


def main():
  hparams = get_hparams()

  train_dataset, test_dataset = get_dataset(hparams)

  model = Model()

  loss_function = keras.losses.SparseCategoricalCrossentropy()
  optimizer = keras.optimizers.Adam(lr=0.001)

  logger = Logger()

  for epoch in range(hparams.epochs):
    for images, labels in train_dataset:
      loss, predictions = train_step(images, labels, model, loss_function,
                                     optimizer)
      logger.log_progress(loss, labels, predictions, mode='train')

    for images, labels in test_dataset:
      loss, predictions = test_step(images, labels, model, loss_function)
      logger.log_progress(loss, labels, predictions, mode='test')

    logger.print_progress(epoch)


if __name__ == "__main__":
  main()