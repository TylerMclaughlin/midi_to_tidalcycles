import midi

from midi_to_tidalcycles import vel_to_amp

def midinote_to_scale_degree(midi_note, scale_list, z = 12):
    #midi_note = int(midi_note) - 60
    # for non-12-TET scales, z may not be 12.
    q, r = divmod(midi_note, int(z)) 
    print(q,r)
    scale_degree = q*len(scale_list) + scale_list.index(r)
    return scale_degree


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

def tc_take_notation(pitches, amps, pname = 'notez', aname = 'ampz', scale = False, z = 12):
    """
    z only matters if scale is not False
    """
    pname = "\"" + pname + "\""
    aname = "\"" + aname + "\""
    amp_string = "\"" + " ".join([str(a) for a in amps]) + "\""
    out = " ".join(["aT",aname, str(len(amps)), amp_string, "$ "])   
    if scale is False:
        pitch_string = "\"" + " ".join([str(p) for p in pitches]) + "\""
        out += " ".join(["nT",pname, str(len(pitches)), pitch_string])   
    else:
        scale_list = sorted(list(set([x % int(z) for x in pitches]))) 
        print(scale_list)
        print(pitches)
        scale_pat = " ".join([str(int(x)) for x in scale_list])
        notes_degrees = " ".join([str(midinote_to_scale_degree(x, scale_list, z)) for x in pitches])
        out += "nT " + pname + " " + str(len(pitches)) 
        out +=  " (tScale\' " + str(z) +  " \"" + scale_pat + "\" (\""  + notes_degrees + "\")) "

    # i define the following in tidalcycles:
    # let aT name amt p = ampTake name (take amt (cycle (patternToList p)))
    return out


if __name__ == "__main__":
    import sys
    midi_in = sys.argv[1]
    p, v = get_melody(midi_in)
    if len(sys.argv) == 2:
        print(tc_take_notation(p,v))
    # scale mode
    elif len(sys.argv)  == 3:
        print(tc_take_notation(p,v, scale = True))
    # provide z for EDO 
    else:
        print(tc_take_notation(p,v, scale = True, z = sys.argv[3]))
