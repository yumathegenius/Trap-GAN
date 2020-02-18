from __future__ import absolute_import, division, print_function, unicode_literals
from midi_Data import*
from gan import*
import re, os, sys
import shutil

instruments = ['hihat',
               'kick',
               'snare']

def get_dummy_data(md, instrument):
  training_data = list()
  data = list()
  for i in range(int(md.whole_lenth/md.min_note[instrument])):
    data.append([0.0,0.0])
  training_data.append(data)
  return training_data
               
def main():
  script_home = os.path.dirname(os.path.realpath(__file__))
  os.makedirs('{}/output'.format(script_home), exist_ok = True)

  md = Midi_Data()
  # Train
  for instrument in instruments:
    training_data = get_dummy_data(md, instrument)
    instrument_train = Train_Instrument('{}/chk_point'.format(script_home), instrument, training_data)
    out_data = instrument_train.generate_midi_data()
    md.create_midi(out_data, instrument, '{}/output/{}.mid'.format(script_home, instrument))

if __name__ == '__main__':
  main()
