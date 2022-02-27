from __future__ import print_function
import midi
import numpy as np

# this function extracts chords from MIDI files by looking for local maxima in polyphony.

def get_chords(filename):
    midi_obj = midi.read_midifile(filename)
    note_history = [] # list of note stacks
    note_stack = []
    for index, event in enumerate(midi_obj[-1]):
        if type(event) == midi.events.NoteOnEvent:
            # convert from midinote numbers to tidalcycles n; subtract 60
            note_stack.append(event.pitch - 60)
            note_history.append(tuple(note_stack))
        elif type(event) == midi.events.NoteOffEvent:
            note_stack.remove(event.pitch - 60)
            note_history.append(tuple(note_stack))

    return note_history


def local_maxima(note_history):
    chords = []
    for i, chord in enumerate(note_history):
        if (i > 1) & (i < len(note_history) - 1):
            prev_level = note_history[i - 1]
            next_level = note_history[i + 1]
            if (len(chord) > len(prev_level)) & (len(chord) > len(next_level)):
                chords.append(chord)
    return chords

def tc_snippet(chord_tuple):
    # in the familiar TidalCycles syntax n "[0, 3, 7, 10]"
    b = ", ".join([str(j) for j in chord_tuple])
    return "n \"[" + b + "]\""

def make_unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def chords_to_tc(chords, chord_prefix = 'choarde', unique = True):
    if unique:
        chords = make_unique(chords)
    output = ""
    for i, c in enumerate(chords):
        snippet = tc_snippet(c)
        if i == 0:
            # hehe cant believe i am still supporting python 2.
            # f-strings would make this so much more readable.
            output += 'let ' + chord_prefix + str(i) + ' = ' + snippet + '\n'
        else:
            output += '    ' + chord_prefix + str(i) + ' = ' + snippet + '\n'
    print(output)

def chords_to_tc_select(chords, name,  unique = True):
    """
    exports something like this (example showing two chords):
    ```let ssss p = select p [n "[0, 3, 7, 10]", n "[3, 6, 10, 13]"]```
    """
    if unique:
        chords = make_unique(chords)
    print('-- ' + str(len(chords)) + ' chords' )
    snippets = [tc_snippet(c) for c in chords ]
    string_head = 'let ' + name + ' p = select p [' 
    string_mid =  ', '.join(snippets)
    string_tail =  ']'
    out = string_head + string_mid + string_tail
    print(out)

def midi_to_tc_chords(input_midi_file, chord_prefix):
    chord_tuples = local_maxima(get_chords(input_midi_file))
    #chords_to_tc(chord_tuples, chord_prefix)
    chords_to_tc_select(chord_tuples, chord_prefix)

if __name__ == '__main__':
    import sys

    input_midi_file = sys.argv[1]

    if len(sys.argv) > 2:
        chord_prefix = sys.argv[2]
    else:
        chord_prefix = input_midi_file.split('/')[-1].split('.')[0].replace(' ', '-') 


    midi_to_tc_chords(input_midi_file = input_midi_file, chord_prefix = chord_prefix)

