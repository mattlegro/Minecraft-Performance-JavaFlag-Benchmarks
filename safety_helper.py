import time, statistics


def waitforlogline(lfile, key, ldelay=1, ltimeout=1800):
    lt = float(time.time() + float(ltimeout))
    with open(lfile, "r") as t:
        while True:
            for line in t.readlines():
                if key in line:
                    return
            time.sleep(ldelay)
            if time.time() > lt:
                raise Exception("Cannot find " + key + " in log!")


def safemean(l):  # average lists while ignoring strings in them
    l = [x for x in l if not isinstance(x, str)]
    if len(l) > 1:
        return round(statistics.mean(l), 2)
    elif len(l) == 1:
        return l[0]
    else:
        return "-"


def safevar(l):  # pvariance lists while ignoring strings in them
    l = [x for x in l if not isinstance(x, str)]
    if len(l) > 1:
        return round(statistics.pvariance(l), 2)
    else:
        return "-"
