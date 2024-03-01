import os, glob


def mod_check(blist):

    # Try to find Spark and/or Carpet mods
    if os.path.isdir("mods"):
        mods = glob.glob("mods/*.jar")
        spark = any("spark" in s for s in mods)
        if spark:
            blist["Average_TPS_Values"] = []  # initialize lists
            blist["GC_Stop_MS"] = []
            blist["GC_Stops"] = []
            blist["Oldgen_GCs"] = []
            blist["Memory_Usage"] = []
            blist["CPU_Usage"] = []
        hascarpet = any("fabric-carpet" in s for s in mods)
        if hascarpet:
            blist["Player_Spawn_Times"] = []

    return has_spark, has_carpet


def add_spark_stats(blist):
    blist["Average_TPS_Values"] = []  # initialize lists
    blist["GC_Stop_MS"] = []
    blist["GC_Stops"] = []
    blist["Oldgen_GCs"] = []
    blist["Memory_Usage"] = []
    blist["CPU_Usage"] = []
    return blist


def add_carpet_stats(blist):
    blist["Player_Spawn_Times"] = []
    return blist


def qw(blist, s):
    print("Startup error, please check the server log: " + s)
    blist["Startup_Times"].append(s)
    blist["Chunkgen_Times"].append(s)
    return blist
