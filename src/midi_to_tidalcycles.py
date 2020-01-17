from __future__ import print_function
import midi
import numpy as np
import os
import argparse

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
   
     
def midi_to_array(filename, quanta_per_qn = 4, velocity_on = False, legato_on = False, print_events = False):
    pattern = midi.read_midifile(filename)
    ticks_per_quanta = pattern.resolution/quanta_per_qn  # ticks per quarter note * quarter note per quanta
    last_event = pattern[-1][-1]
    assert type(last_event) == midi.events.EndOfTrackEvent
    cum_ticks = 0
    for index, event in enumerate(pattern[-1]):
        cum_ticks += event.tick
    n_quanta = cum_ticks/ticks_per_quanta
    polyphony = infer_polyphony(pattern)
    print("inferred polyphony is ", end = "")
    print(polyphony)
    note_vector = np.zeros((n_quanta, polyphony)) 
    if velocity_on:
        velocity_vector = np.zeros((n_quanta, polyphony))
    if legato_on:
        legato_vector = np.zeros((n_quanta, polyphony))
        currently_active_notes = {} 
    cum_ticks = 0
    voice = -1 
    for event in pattern[-1]:
        if print_events:
            print(event)
        cum_ticks += event.tick
        if type(event) == midi.events.NoteOnEvent:
            voice += 1
            quanta_index = int(cum_ticks/ticks_per_quanta)
            print(voice)
            note_vector[quanta_index,voice] = event.pitch #- pitch_offset
            if legato_on: 
                currently_active_notes[event.pitch] = [quanta_index, voice]
            if velocity_on:
                velocity_vector[quanta_index,voice] = event.velocity #- pitch_offset
            #print(midinote_to_note_name(event.pitch))
            #print(event.velocity)
        elif (type(event) == midi.events.NoteOffEvent) & (legato_on):
            quanta_note_off_index = int(cum_ticks/ticks_per_quanta)
            note_length = quanta_note_off_index - currently_active_notes[event.pitch][0]
            legato_vector[currently_active_notes[event.pitch][0],currently_active_notes[event.pitch][1]] = note_length
            del currently_active_notes[event.pitch]
            voice = -1 #-= 1 
        else: # end of track
            # turn all notes off
            quanta_note_off_index = int(cum_ticks/ticks_per_quanta)
            if legato_on:
                for key in currently_active_notes.keys():
                    note_length = quanta_note_off_index - currently_active_notes[key][0]
                    legato_vector[currently_active_notes[key],voice] = note_length
            voice = -1
    if not legato_on and velocity_on:
        return note_vector, velocity_vector

    elif not velocity_on and legato_on:
        return note_vector, legato_vector

    elif velocity_on and legato_on:
        return note_vector, velocity_vector, legato_vector

    else:
        return note_vector


def vel_to_amp(vel):
    return round(vel/127., 2)

def print_midi_stack(notes, vels = None, legatos = None):
    print("stack [")
    # iterate over voices
    for j in range(0,len(notes[0,:])):
        notes_names  = [midinote_to_note_name(x) for x in notes[:,j]]
        print("    n \"", end = "")
        print(*notes_names, sep=' ', end = "")
        print("\"") 
        if vels is not None:
            print("    # amp \"", end = "")
            note_vels  = [vel_to_amp(x) for x in vels[:,j]]
            print(*note_vels, sep=' ', end = "")
            # add comma if it's not the last voice and if there are no legatos
            if legatos is None:
                if not j == len(notes[0,:]) - 1:
                    print("\",")
                # otherwise close the stack
                else:
                    print("\"\n]")
            else:  # if legatos is not None 
                print("\"")
        if legatos is not None:
            print("    # legato \"", end = "")
            note_legatos  = [x for x in legatos[:,j]]
            print(*note_legatos, sep=' ', end = "")
            # add comma if it's not the last voice
            if not j == len(notes[0,:]) - 1:
                print("\",")
            # otherwise close the stack
            else:
                print("\"\n]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("midi_files",nargs="*")
    parser.add_argument("--events","-e", const = True, default = False, help = "print midi event information", action = 'store_const')
    parser.add_argument("--dimensions","-d", const = True, default = False, help ="print midi dimensions", action = 'store_const')
    parser.add_argument("--resolution","-q", default = 4, type = int, help = "specify number of quanta per quarter note")
    parser.add_argument("--legato","-l", const = True, default = False, help = "print legato pattern", action = 'store_const')
    parser.add_argument("--amp","-a", const = True, default = False, help = "print amplitude pattern", action = 'store_const')
    args = parser.parse_args()
    for midi_file in args.midi_files:
         print(midi_file)
         print(args.events)
         data = midi_to_array(midi_file, quanta_per_qn = args.resolution, velocity_on = args.amp, legato_on = args.legato, print_events = args.events)
         vels = None
         legatos = None
         if args.amp:
             if args.legato:
                 notes, vels, legatos = data
             else:
                 notes, vels = data
         elif args.legato:
                 notes, legatos = data
         else:
             notes = data
         if args.dimensions:
             print('quanta: ',end = '')
             print(notes.shape[0])
             print('voices: ',end = '')
             print(notes.shape[1])
         print_midi_stack(notes, vels, legatos)
