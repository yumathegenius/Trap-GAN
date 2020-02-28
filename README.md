# Trap-GAN
This is a python base machine learning trap beats generator.
<br><br>For Demo :<br>https://trapgan.yumathegenius.com/


## Instroments 
 - hihat
 - kick
 - snare

## Getting Started

### Requirements

- python3-midi<br>
  https://github.com/louisabraham/python3-midi

- TensorFlow<br>
  https://www.tensorflow.org/install

### Sample

run the sample program

```
python sample.py
```

The midi file will be generated 

```
./output/hihat.mid
./output/kick.mid
./output/snare.mid
```

## Training

### Training data
Here are the setting for default program
- Time Signture : 4/4
- Lenth : 4 bars
- Shortest Note : <br>  hihat : thirtysecond note
                  <br>  kick : eighth note
                  <br>  snare : eighth note
- Pitch : As long as they are all same pitch

### Midi_Data()
#### Initialize

```
from midi_Data import*

md = Midi_Data()
```

#### list get_data(midi_path, instrument)
Convert single midi file into training data for the machine learning

```
md.get_data(midi_path, instrument)
```

#### create_midi(data, instrument, output_path)
Create midi from generated data

```
md.create_midi(data, instrument, output_path)
```

#### boolean chk_data(midi_path, instrument)
Check if the midi file match the training standard. Return True if the file match 

```
md.chk_data(midi_path, instrument)
```

### Train_Instrument()

#### Initialize

```
from gan import*

instrument_train = Train_Instrument(Check_point_path, instrument, training_data)
```

#### train(epochs)
Check point will be saved every 20 epochs

```
instrument_train.train(epochs)
```

#### list generate_midi_data()
Generate midi data

```
instrument_train.checkpoint.restore(tf.train.latest_checkpoint(instrument_train.checkpoint_dir))
data = instrument_train.generate_midi_data()
```

## SEND ME UR BEATS!!!!
send me your beats, help me develope this thing!!!<br>
yumathegenius@gmail.com

## Donation!!!!
PayPal :<br>
https://paypal.me/pools/campaign/113237164948464442<br>

## APP COMING SOON
