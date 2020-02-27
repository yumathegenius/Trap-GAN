from __future__ import absolute_import, division, print_function, unicode_literals
import tensorflow as tf
import numpy as np
import re, os, sys
from midi_Data import*
import shutil

instruments = ['hihat',
               'kick',
               'snare']

class Midi_Generator:
  def __init__(self):
    # Define the training loop
    self.noise_dim = 100
    self.num_examples_to_generate = 1

    self.seed = tf.random.normal([self.num_examples_to_generate, self.noise_dim])

  def generate_midi_data(self, path, instrument):
    generator = tf.keras.models.load_model('{}/{}.h5'.format(path, instrument))
    predictions = generator(self.seed, training=False)
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


def main():
  script_home = os.path.dirname(os.path.realpath(__file__))
  os.makedirs('{}/output'.format(script_home), exist_ok = True)

  midi_generator = Midi_Generator()
  md = Midi_Data()
  
  for instrument in instruments:
    out_data = midi_generator.generate_midi_data('{}/h5model'.format(script_home), instrument)
    md.create_midi(out_data, instrument, '{}/output/{}.mid'.format(script_home, instrument))

if __name__ == '__main__':
  main()
