import os, glob


def mod_check(blist):

    # Try to find Spark and/or Carpet mods
    if os.path.isdir("mods"):
        mods = glob.glob("mods/*.jar")
        spark = any("spark" in s for s in mods)
        if spark:
            self.blist["Average_TPS_Values"] = []  # initialize lists
            self.blist["GC_Stop_MS"] = []
            self.blist["GC_Stops"] = []
            self.blist["Oldgen_GCs"] = []
            self.blist["Memory_Usage"] = []
            self.blist["CPU_Usage"] = []
        hascarpet = any("fabric-carpet" in s for s in mods)
        if hascarpet:
            self.blist["Player_Spawn_Times"] = []

    return has_spark, has_carpet


def add_spark_stats(blist):
    self.blist["Average_TPS_Values"] = []  # initialize lists
    self.blist["GC_Stop_MS"] = []
    self.blist["GC_Stops"] = []
    self.blist["Oldgen_GCs"] = []
    self.blist["Memory_Usage"] = []
    self.blist["CPU_Usage"] = []
    return blist


def add_carpet_stats(blist):
    self.blist["Player_Spawn_Times"] = []
    return blist


def qw(blist, s):
    print("Startup error, please check the server log: " + s)
    self.blist["Startup_Times"].append(s)
    self.blist["Chunkgen_Times"].append(s)
    return blist
