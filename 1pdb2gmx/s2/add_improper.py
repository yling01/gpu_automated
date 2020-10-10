import optparse

def get_improper_atom(gro):
    fi = open(gro)
    lines = fi.readlines()
    fi.close()
    length = lines[-2][0:5].strip()
    target = ["CA", "C", "N", "H", "O"]
    mem = {}
    for line in lines:
        resID = line[0:5].strip()

        atomName = line[10:15].strip()
        if atomName not in target:
            continue

        atomID = line[15:20].strip()
        entryID = atomName + resID
        mem[entryID] = atomID
    return length, mem

def add_improper(topOri, topOut, improper_list):
    fi = open(topOri)
    lines = fi.readlines()
    fi.close()
    with open(topOut, "w+") as fo:
        for i in range(1, len(lines)):
            if lines[i] == "; Include Position restraint file\n":
                for improper in improper_list:
                    fo.write(improper)
                    fo.write("\n")
            fo.write(lines[i - 1])
        fo.write(lines[-1])


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('--gro', dest = 'gro', default = 'prot.gro')
    parser.add_option('--ori', dest = 'topOri', default = 'cx_amber99sbMod_tip3p_temp.top')
    parser.add_option('--out', dest = 'topOut', default = 'cx_amber99sbMod_tip3p.top')
    parser.add_option('--extra', dest = 'extra', default = 'False')


    (options, args) = parser.parse_args()
    gro = options.gro
    topOri = options.topOri
    topOut = options.topOut
    extra = options.extra
    extra = True if extra[0].upper() == "T" else False

    length, improper_dic = get_improper_atom(gro)
    improper_list = []
    improper1 = "%5s %5s %5s %5s %5s     ; added by TL" % (improper_dic["CA" + length],
                                                           improper_dic["N1"],
                                                           improper_dic["C" + length],
                                                           improper_dic["O" + length],
                                                           4)
    improper2 = "%5s %5s %5s %5s %5s     ; added by TL" % (improper_dic["C" + length],
                                                           improper_dic["CA1"],
                                                           improper_dic["N1"],
                                                           improper_dic["H1"],
                                                           4)
    improper_list.append(improper1)
    improper_list.append(improper2)
    if extra:
        length = int(length)
        for i in range(1, length + 1):
            j = i + 1
            if j > length:
                j = j % length
            improper = "%5s %5s %5s %5s %5s     ; added by TL" % (improper_dic["H" + str(j)],
                                                                  improper_dic["N" + str(j)],
                                                                  improper_dic["C" + str(i)],
                                                                  improper_dic["O" + str(i)],
                                                                  4)
            improper_list.append(improper)

    add_improper(topOri, topOut, improper_list)
