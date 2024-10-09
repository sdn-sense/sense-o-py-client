#!/usr/bin/env python3
import os
from yaml import safe_load as yload


def parse_timing(timesin):
    """Parse timing data"""
    keys = ["CREATE", "PENDING", "COMPILED", "COMMITTING", "COMMITTED", "READY"]
    schedkeys = ["SCHEDULED", "UNSTABLE", "STABLE"]
    out = []
    outkeys = []
    # first entry we get create details
    tmpline = []
    outkeys.append("create")
    prevtime = 0
    for key in keys:
        if key in timesin['create']:
            ntime = timesin['create'][key]["entertime"]*-1
            tmpline.append(ntime - prevtime)
            prevtime = ntime
        elif str("CREATE - " + key) in timesin['create']:
            ntime = timesin['create'][str("CREATE - " + key)]["entertime"]*-1
            tmpline.append(ntime - prevtime)
            prevtime = ntime
        else:
            tmpline.append(0)
        # Need to add also scheduling data
        if key == "READY" and str("CREATE - " + key) in timesin['create']:
            for skey in schedkeys:
                if skey in timesin['create']["CREATE - " + key]['configStatus']:
                    ntime = timesin['create']["CREATE - " + key]['configStatus'][skey]*-1
                    tmpline.append(ntime - prevtime)
                    prevtime = ntime
                else:
                    tmpline.append(0)
    out.append(tmpline)
    # now we need to loop from 0 to 100 (we will not do more than 100 retries)
    for i in range(100):
        for rtype in ['cancel', 'reprovision']:
            prevtime = 0
            tmpline = []
            linelook = f"{rtype}{i}"
            if linelook not in timesin:
                continue
            outkeys.append(linelook)
            for key in keys:
                if key in timesin[linelook]:
                    ntime = timesin[linelook][key]["entertime"]*-1
                    tmpline.append(ntime - prevtime)
                    prevtime = ntime
                elif str("CANCEL - " + key) in timesin[linelook]:
                    ntime = timesin[linelook]["CANCEL - " + key]["entertime"]*-1
                    tmpline.append(ntime - prevtime)
                    prevtime = ntime
                elif str("REPROVISION - " + key) in timesin[linelook]:
                    ntime = timesin[linelook]["REPROVISION - " + key]["entertime"]*-1
                    tmpline.append(ntime - prevtime)
                    prevtime = ntime
                elif str("REINSTATE - " + key) in timesin[linelook]:
                    ntime = timesin[linelook]["REINSTATE - " + key]["entertime"]*-1
                    tmpline.append(ntime - prevtime)
                    prevtime = ntime
                else:
                    tmpline.append(0)
                # Need to add also scheduling data
                if key == "READY":
                    bkey = str("REINSTATE - " + key)
                    if bkey not in timesin[linelook]:
                        bkey = str("CANCEL - " + key)
                    if bkey not in timesin[linelook]:
                        continue
                    for skey in schedkeys:
                        if skey in timesin[linelook][bkey]['configStatus']:
                            ntime = timesin[linelook][bkey]['configStatus'][skey]*-1
                            tmpline.append(ntime - prevtime)
                            prevtime = ntime
                        else:
                            tmpline.append(0)
            out.append(tmpline)
    print("TYPE," + ",".join(keys + schedkeys))
    for ct in range(len(out)):
        print(f"{outkeys[ct]}," +  ",".join(str(num) for num in out[ct]))


if __name__ == "__main__":
    # for all files in timing directory
    # read the file
    for file in os.listdir('timings'):
        with open(f'timings/{file}', 'r', encoding="utf-8") as fd:
            timing = yload(fd.read())
            parse_timing(timing)
    #with open('timings1', 'r', encoding="utf-8") as fd:
    #    timing = yload(fd.read())
    #    parse_timing(timing)
