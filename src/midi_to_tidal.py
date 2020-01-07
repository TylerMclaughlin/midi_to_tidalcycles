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
    octave_name = q  # q - 1  <- this is correct but tidal is off by an octave I think.
    full_note_name = str(note_name) + str(octave_name)
    return full_note_name


# test midinote_to_note_name
#for x in [35, 64, 123, 72]:
#    print(x,midinote_to_note_name(x))

def infer_polyphony(midi_pattern):
    last_event = midi_pattern[-1][-1]
    assert type(last_event) == midi.events.EndOfTrackEvent
    n_adjacent_on_events = 0
    inferred_polyphony = 0
    for index, event in enumerate(midi_pattern[-1]):
        if type(event) == midi.events.NoteOnEvent: # starting note off
            n_adjacent_on_events += 1
            inferred_polyphony = max(inferred_polyphony, n_adjacent_on_events)
        elif type(event) == midi.events.NoteOffEvent:
            n_adjacent_on_events = 0
    return inferred_polyphony
   
     
def midi_to_array(filename,n_quanta = 64, quanta_per_qn = 4, velocity_on = False):
    pattern = midi.read_midifile(filename)
    ticks_per_quanta = pattern.resolution/quanta_per_qn  # ticks per quarter     note * quarter note per quanta
    last_event = pattern[-1][-1]
    assert type(last_event) == midi.events.EndOfTrackEvent
    cum_ticks = 0
    for index, event in enumerate(pattern[-1]):
        cum_ticks += event.tick
    n_quanta = cum_ticks/ticks_per_quanta
    polyphony = infer_polyphony(pattern)
    print("inferred polyphony is :")
    print(polyphony)
    note_vector = np.zeros((n_quanta, polyphony)) 
    if velocity_on:
        velocity_vector = np.zeros((n_quanta, polyphony))

    cum_ticks = 0
    voice = -1 
    for event in pattern[-1]:
        print(event)
        cum_ticks += event.tick
        if type(event) == midi.events.NoteOnEvent:
            voice += 1
            quanta_index = int(cum_ticks/ticks_per_quanta)
            note_vector[quanta_index,voice] = event.pitch #- pitch_offset
            if velocity_on:
                velocity_vector[quanta_index,voice] = event.velocity #- pitch_offset
            #print(midinote_to_note_name(event.pitch))
            #print(event.velocity)
        else:
            voice = -1 
    if velocity_on:
        return note_vector, velocity_vector
    else:
        return note_vector

def vel_to_amp(vel):
    return round(vel/127., 2)

def print_midi_stack(notes, vels):
    print("stack [")
    for j in range(0,len(notes[0,:])):
        notes_names  = [midinote_to_note_name(x) for x in notes[:,j]]
        print("    n \"", end = "")
        print(*notes_names, sep=' ', end = "")
        print("\"") 
        print("    # amp \"", end = "")
        note_vels  = [vel_to_amp(x) for x in vels[:,j]]
        print(*note_vels, sep=' ', end = "")
        if not j == len(vels[0,:]) - 1:
            print("\",")
        else:
            print("\"\n]")



test_midi_dir = "/Volumes/SKYBLUE_128/tidal_code/midi_to_tidal/test_examples/"
#midi_file = "dorian-chromatic_16th-notes_monophonic_125bpm.mid"
#midi_file = "insen_quarter-eighth-notes_duophonic_125bpm.mid"
#midi_file = "jazz-chords_played-live_quadraphonic_125bpm.mid"
#midi_file = "bass_tresillo_monophonic_125bpm.mid"
#midi_file = "/Volumes/SKYBLUE_128/reason_songs/tidal_midi_dec29_2019/minor_chords_eleventh_ninth_ninth.mid"
#midi_file = "/Volumes/SKYBLUE_128/reason_songs/tidal_midi_dec29_2019/melody_eleventh_ninth_ninth.mid"
#midi_file = "/Volumes/SKYBLUE_128/reason_songs/tidal_midi_dec29_2019/bass_eleventh_ninth_ninth.mid"
#midi_file = "/Volumes/SKYBLUE_128/reason_songs/tidal_midi_jan01_2020/midis/green_aug_1.mid"
#midi_file = "/Volumes/SKYBLUE_128/reason_songs/tidal_midi_jan01_2020/midis/blue_sakamoto_1_6bars.mid"
midi_file = "/Volumes/SKYBLUE_128/reason_songs/tidal_midi_jan01_2020/midis/blue_sakamoto_2_6bars.mid"
test_midi = os.path.join(test_midi_dir,midi_file)

#notes = midi_to_array(test_midi)
notes, vels  = midi_to_array(test_midi, velocity_on = True)
print(notes.shape)
#for j in range(0,len(notes[0,:])):
#    notes_names  = [midinote_to_note_name(x) for x in notes[:,j]]
#    print(*notes_names, sep=' ')

print_midi_stack(notes, vels)
