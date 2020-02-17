from __future__ import absolute_import, division, print_function, unicode_literals
from midi_Data import*
from gan import*
import re, os, sys
import shutil

instruments = ['hihat',
               'kick',
               'snare']

def chk_training_data(md, data_path, instrument):
  training_data = list()
  for root, dirs, files in os.walk('{}/{}'.format(data_path, instrument), topdown=True):
   for name in files:
      f = os.path.join(root, name)
      if f.endswith('.mid'):
        if md.chk_data(f, instrument) != True:
          print('Error : {} doesn\'t match the training data standard'.format(f))
          sys.exit(1)

def get_training_data(md, data_path, instrument):
  training_data = list()
  for root, dirs, files in os.walk('{}/{}'.format(data_path, instrument), topdown=True):
   for name in files:
      f = os.path.join(root, name)
      if f.endswith('.mid'):
        data = md.get_data(f, instrument)
        training_data.append(data)
  
  return training_data


def main():
  script_home = os.path.dirname(os.path.realpath(__file__))
  os.makedirs('{}/output'.format(script_home), exist_ok = True)

  epochs = 100

  md = Midi_Data()
  # Check Training data
  for instrument in instruments:
    chk_training_data(md, '{}/training_data'.format(script_home), instrument)

  # Train
  for instrument in instruments:
    training_data = get_training_data(md, '{}/training_data'.format(script_home), instrument)
    instrument_train = Train_Instrument('{}/chk_point'.format(script_home), instrument, training_data)
    instrument_train.train(epochs)
    out_data = instrument_train.generate_midi_data()
    md.create_midi(out_data, instrument, '{}/output/{}.mid'.format(script_home, instrument))

if __name__ == '__main__':
  main()
