# -*- coding: utf-8 -*-

import pandas as pd
import DATA_CONSTANTS as DC
import HullRsiWin_Parameter as Parameter


def set_generator():
    setlist = []
    i = 0
    for n1 in range(23, 33, 2):
        for m1 in range(7, 13, 1):
            #   for m2 in range(3, 15, 3):
            for m2 in [3, 4, 5 ]:
                #for n in range(3, 16, 3):
                for n in [7, 8, 9, 10,11]:
                    #for ma_n in range(20, 51, 10):
                    for ma_n in [15, 25, 35]:
                        setname = "Set%d N1_%d M1_%d M2_%d N_%d MaN_%d" % (i, n1, m1, m2, n, ma_n)
                        l = [setname, n1, m1, m2, n, ma_n]
                        setlist.append(l)
                        i += 1

    setpd = pd.DataFrame(setlist, columns=['Setname', 'N1', 'M1', 'M2', 'N', 'MaN'])
    #setpd['RSI1_UP'] = 70
    #setpd['RSI1_DOWN'] = 30

    upperpath = DC.getUpperPath(Parameter.folderLevel)
    resultpath = upperpath + Parameter.resultFolderName
    setpd.to_csv(resultpath + Parameter.parasetname)


if __name__ == "__main__":
    set_generator()
    pass
