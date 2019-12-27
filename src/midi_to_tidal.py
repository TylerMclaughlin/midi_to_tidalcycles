from __future__ import print_function
import midi
import numpy as np
import os


# NOTE NAMES c1 cs2 
# C4 (middle C) is midi note number 60.

def midinote_to_note_name(midi_note):
    if midi_note == 0.0:
        return "~"
    midi_note = int(midi_note)
    note_names_array = ["c", "cs", "d", "ds", "e", "f", "fs", "g", "gs", "a", "as", "b"]
    q, r = divmod(midi_note, 12) 
    note_name = note_names_array[r]
    octave_name = q - 1 
    full_note_name = str(note_name) + str(octave_name)
    return full_note_name


# test midinote_to_note_name
#for x in [35, 64, 123, 72]:
#    print(x,midinote_to_note_name(x))
    
def midi_to_array(filename,n_quanta = 64, quanta_per_qn = 4):
    pattern = midi.read_midifile(filename)
    ticks_per_quanta = pattern.resolution/quanta_per_qn  # ticks per quarter     note * quarter note per quanta
    last_event = pattern[-1][-1]
    assert type(last_event) == midi.events.EndOfTrackEvent
    cum_ticks = 0
    for index, event in enumerate(pattern[-1]):
    
        cum_ticks += event.tick
    n_quanta = cum_ticks/ticks_per_quanta
    note_vector = np.zeros(n_quanta) 

    cum_ticks = 0
    for event in pattern[-1]:
        print(event)
        cum_ticks += event.tick
        if type(event) == midi.events.NoteOnEvent:
            quanta_index = int(cum_ticks/ticks_per_quanta)
            note_vector[quanta_index] = event.pitch #- pitch_offset
  
    return(note_vector)


test_midi_dir = "/Volumes/SKYBLUE_128/tidal_code/midi_to_tidal/test_examples/"
#midi_file = "dorian-chromatic_16th-notes_monophonic_125bpm.mid"
midi_file = "insen_quarter-eighth-notes_duophonic_125bpm.mid"
test_midi = os.path.join(test_midi_dir,midi_file)

notes = midi_to_array(test_midi)

notes_names  = [midinote_to_note_name(x) for x in notes]

print(*notes_names, sep=' ')


