import midi

from midi_to_tidalcycles import vel_to_amp

def get_melody(filename):
    midi_obj = midi.read_midifile(filename)
    pitches = []
    vels = []
    #suss = []
    note_stack = []
    for index, event in enumerate(midi_obj[-1]):
        #print(event)
        if type(event) == midi.events.NoteOnEvent:
            # convert from midinote numbers to tidalcycles n; subtract 60
            pitches.append(event.pitch - 60)
            vels.append(event.velocity)
            #suss.append(event.)

    amps = [vel_to_amp(v) for v in vels ]
    return pitches, amps 

def tc_take_notation(pitches, amps, pname = 'notez', aname = 'ampz'):
    pname = "\"" + pname + "\""
    aname = "\"" + aname + "\""
    pitch_string = "\"" + " ".join([str(p) for p in pitches]) + "\""
    amp_string = "\"" + " ".join([str(a) for a in amps]) + "\""
    out = " ".join(["nT",pname, str(len(pitches)), pitch_string])   
    # i define the following in tidalcycles:
    # let aT name amt p = ampTake name (take amt (cycle (patternToList p)))
    out += '\n'
    out += " ".join(["# aT",aname, str(len(amps)), amp_string])   
    return out


if __name__ == "__main__":
    import sys
    midi_in = sys.argv[1]
    p, v = get_melody(midi_in)
    print(tc_take_notation(p,v))
