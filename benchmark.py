from abc import ABC, abstractmethod
from os import path, rename
from glob import glob
import time
import statistics
import shutil


class Benchmark(ABC):
    def __init__(self, config):
        if config is None:
            config = {}
        self.warmup = config.get("warmup", 90)
        self.benchtime = config.get("benchtime", 90)
        self.benchlog = config.get("benchlog", "default_benchlog_path")
        self.blist = config.get("blist", [])
        self.iterations = config.get("iterations", 1)
        self.debug = config.get("debug", 1)
        self.loadedstring = config.get("loadedstring", 1)

    @abstractmethod
    def run(self):
        pass

    def mod_check():

        # Try to find Spark and/or Carpet mods

        # TO DO
        # need to make path search better than isdir('mods')
        if path.isdir("mods"):
            mods = glob("mods/*.jar")
            has_spark = any("spark" in s for s in mods)
            has_carpet = any("fabric-carpet" in s for s in mods)

        return has_spark, has_carpet

    def add_spark_stats(self):

        self.blist["Average_TPS_Values"] = []  # initialize lists
        self.blist["GC_Stop_MS"] = []
        self.blist["GC_Stops"] = []
        self.blist["Oldgen_GCs"] = []
        self.blist["Memory_Usage"] = []
        self.blist["CPU_Usage"] = []

        return self.blist

    def add_carpet_stats(self):

        self.blist["Player_Spawn_Times"] = []

        return self.blist

    def qw(self, s):

        print("Startup error, please check the server log: " + s)
        self.blist["Startup_Times"].append(s)
        self.blist["Chunkgen_Times"].append(s)

        return self.blist

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

    def restore_world(worldfolder, worldbackup):
        if path.isdir(worldfolder) and path.isdir(worldbackup):
            try:
                shutil.rmtree(worldfolder)
            except:
                time.sleep(7)  # Give the old server some time to close
                shutil.rmtree(worldfolder)
            rename(worldbackup, worldfolder)

    def backup_world(worldfolder, worldbackup):
        try:
            # Backup existing world to restore later
            if path.isdir(worldfolder) and not path.isdir(worldbackup):
                try:
                    shutil.copytree(worldfolder, worldbackup)
                except:
                    time.sleep(3)
                    shutil.copytree(worldfolder, worldbackup, dirs_exist_ok=True)
        except Exception as e:
            print("Could not create world backup")
            raise e
