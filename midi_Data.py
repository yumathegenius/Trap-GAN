from __future__ import absolute_import, division, print_function, unicode_literals
import midi

class Midi_Data:
  def __init__(self):
    self.whole_lenth       = 7680
    self.whole_note        = 480
    self.half_note         = 240
    self.quarter_note      = 120
    self.eighth_note       = 60
    self.sixteenth_note    = 30
    self.thirsecond_note   = 15
    self.resolution        = 480
    self.pitch             = {'hihat' : 60,
                              'kick'  : 36,
                              'snare' : 37}
    self.min_note          = {'hihat' : self.thirsecond_note,
                              'kick'  : self.eighth_note,
                              'snare' : self.eighth_note}
    self.name_data         = {'hihat' : [72, 105, 72, 97, 116],
                              'kick'  : [75, 105, 99, 107],
                              'snare' : [83, 110, 97, 114, 101]}    
  def get_data(self, file, instrument):
    min_note = self.min_note[instrument]

    events = self.get_events(file)
    data = list()

    for i in range(0, len(events), 2):
      #first
      if events[i].tick != 0:
        data.append([0.0,0.0])
      
      if events[i].tick > min_note:
        for x in range(1, int(events[i].tick/min_note)):
          data.append([0.0,1.0])
      #second
      if events[i+1].tick != 0:
        data.append([1.0,0.0])
      
      if events[i+1].tick > min_note:
        for x in range(1, int(events[i+1].tick/min_note)):
          data.append([1.0,1.0])

    r = int((self.whole_lenth/min_note) - len(data))
    if r > 0:
      data.append([0.0,0.0])
      for i in range(1, r):
        data.append([0.0,1.0])

    return data


  def get_events(self, file):
    pattern = midi.read_midifile(file)
    lenth = 0
    events = list()
    
    for track in pattern:
      for event in track:
        if type(event) is midi.events.NoteOnEvent or type(event) is midi.events.NoteOffEvent:
          events.append(event)

    return events

  def create_midi(self, data, instrument, gen_path):
    min_note = self.min_note[instrument]
    self.pattern = midi.Pattern(resolution=self.resolution)
    self.track = midi.Track()
    self.track.append(midi.TrackNameEvent(tick=0, text=instrument, data=self.name_data[instrument]))
    self.track.append(midi.InstrumentNameEvent(tick=0, text=instrument, data=self.name_data[instrument]))
    self.event_i = 0

    #trim tail
    if data[-1][0] == 0:
      while True:
        r = data.pop(-1)
        if r == [0,0]:
          break

    #gen event 
    on = data[0][0]
    x = 1
    for i in range(1, len(data)):
      if data[i][1] == 1:
        x += 1
      elif  data[i][1] == 0:
        on_next = data[i][0] 
        self.add_event(on, on_next, x* min_note, self.pitch[instrument])
        on = on_next
        x = 1
    
    self.add_event(on, 0, x* min_note, self.pitch[instrument])
    if (self.event_i % 2) == 1:
      self.track.insert(2, midi.NoteOnEvent(tick=0, channel=0, data=[self.pitch[instrument], 79]))   


    self.track.append(midi.EndOfTrackEvent(tick=0, data=[]))
    self.pattern.append(self.track)
    midi.write_midifile(gen_path, self.pattern)

  def add_event(self, on, on_next, lenth, pitch):
    if on == 1:
      if on_next == 1:
        self.track.append(midi.NoteOnEvent(tick=lenth, channel=0, data=[pitch, 79]))
        self.track.append(midi.NoteOffEvent(tick=0, channel=0, data=[pitch, 64]))
        self.event_i+=2
      else:
        self.track.append(midi.NoteOffEvent(tick=lenth, channel=0, data=[pitch, 64]))
        self.event_i+=1
    else:
      self.track.append(midi.NoteOnEvent(tick=lenth,  channel=0, data=[pitch, 64]))
      self.event_i+=1

  def chk_data(self, file, instrument):
    min_note = self.min_note[instrument]
    events = self.get_events(file)

    for event in events:
      if event.tick % min_note != 0:
        return False

    return True

