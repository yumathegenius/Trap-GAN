from __future__ import absolute_import, division, print_function, unicode_literals
import tensorflow as tf
import numpy as np
from tensorflow.keras import layers
import os
import time

class Train_Instrument:
  def __init__(self, ckep_path, instrument, training_data):
    self.instrument              = instrument
    self.training_data           = training_data
    self.batch_size              = len(training_data)
    self.data_len                = len(training_data[0])
    self.generator               = self.make_generator_model()
    self.discriminator           = self.make_discriminator_model()
    self.generator_optimizer     = tf.keras.optimizers.Adam(1e-4)
    self.discriminator_optimizer = tf.keras.optimizers.Adam(1e-4)
    self.cross_entropy           = tf.keras.losses.BinaryCrossentropy(from_logits=True)
    self.checkpoint_dir          = '{}/{}/training_checkpoints'.format(ckep_path, instrument)
    self.checkpoint_prefix       = os.path.join(self.checkpoint_dir, "ckpt")
    self.checkpoint              = tf.train.Checkpoint(generator_optimizer=self.generator_optimizer,
                                                       discriminator_optimizer=self.discriminator_optimizer,
                                                       generator=self.generator,
                                                       discriminator=self.discriminator)
    # Define the training loop
    self.noise_dim = 100
    self.num_examples_to_generate = 1

    # We will reuse this seed overtime (so it's easier)
    # to visualize progress in the animated GIF)
    self.seed = tf.random.normal([self.num_examples_to_generate, self.noise_dim])

  def make_generator_model(self):
    model = tf.keras.Sequential()
    model.add(layers.Dense(1*int(self.data_len/2)*128, use_bias=False, input_shape=(100,)))
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())
  
    model.add(layers.Reshape((int(self.data_len/2), 1, 128)))
    assert model.output_shape == (None, int(self.data_len/2), 1, 128)
  
    model.add(layers.Conv2DTranspose(64, (5, 5), strides=(1, 1), padding='same', use_bias=False))
    assert model.output_shape == (None, int(self.data_len/2), 1, 64)
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())
  
    model.add(layers.Conv2DTranspose(1, (5, 5), strides=(2, 2), padding='same', use_bias=False, activation='tanh'))
    assert model.output_shape == (None, self.data_len, 2, 1)
  
    return model

  def make_discriminator_model(self):
    model = tf.keras.Sequential()
    model.add(layers.Conv2D(64, (5, 5), strides=(2, 2), padding='same',
                                     input_shape=[self.data_len, 2, 1]))
    model.add(layers.LeakyReLU())
    model.add(layers.Dropout(0.3))
  
    model.add(layers.Conv2D(128, (5, 5), strides=(2, 2), padding='same'))
    model.add(layers.LeakyReLU())
    model.add(layers.Dropout(0.3))
  
    model.add(layers.Flatten())
    model.add(layers.Dense(1))
  
    return model


  def discriminator_loss(self, real_output, fake_output):
    real_loss = self.cross_entropy(tf.ones_like(real_output), real_output)
    fake_loss = self.cross_entropy(tf.zeros_like(fake_output), fake_output)
    total_loss = real_loss + fake_loss
    return total_loss

  def generator_loss(self, fake_output):
    return self.cross_entropy(tf.ones_like(fake_output), fake_output)



  @tf.function
  def train_step(self, midi_data):
    noise = tf.random.normal([self.batch_size, self.noise_dim])

    with tf.GradientTape() as gen_tape, tf.GradientTape() as disc_tape:
      generated_midi = self.generator(noise, training=True)

      real_output = self.discriminator(midi_data, training=True)
      fake_output = self.discriminator(generated_midi, training=True)

      gen_loss = self.generator_loss(fake_output)
      disc_loss = self.discriminator_loss(real_output, fake_output)

    gradients_of_generator = gen_tape.gradient(gen_loss, self.generator.trainable_variables)
    gradients_of_discriminator = disc_tape.gradient(disc_loss, self.discriminator.trainable_variables)

    self.generator_optimizer.apply_gradients(zip(gradients_of_generator, self.generator.trainable_variables))
    self.discriminator_optimizer.apply_gradients(zip(gradients_of_discriminator, self.discriminator.trainable_variables))

  def train(self, epochs):
    print('start training {}'.format(self.instrument))
    for epoch in range(epochs):
      start = time.time()

      for data in self.training_data:
        data = np.array(data)
        data = data.reshape(1, self.data_len, 2, 1)
        self.train_step(data)

      # Save the model every 20 epochs
      if (epoch + 1) % 20 == 0:
        self.checkpoint.save(file_prefix = self.checkpoint_prefix)

        print ('Time for epoch {} is {} sec'.format(epoch + 1, time.time()-start))

  def generate_midi_data(self):
  # Notice `training` is set to False.
  # This is so all layers run in inference mode (batchnorm).
    predictions = self.generator(self.seed, training=False)
    return self.predictions_to_midi_data(np.array(predictions[0]).tolist())

  def predictions_to_midi_data(self, predictions):
    midi_data = []
    pre = None
    for note in predictions:
      if round(note[0][0]) == 1:
        on = 1
      else:
        on = 0
      if round(note[1][0]) == 1:
        if pre == on:
          con = 1
        else:
          con = 0
      else:
        if pre == 0 and on == 0:
          con = 1
        else:
          con = 0
      pre = on
      midi_data.append([on, con])
    
    return midi_data


