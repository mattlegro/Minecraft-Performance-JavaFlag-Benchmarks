import time
import os
import psutil
import json
import traceback
import pexpect
import signal
from glob import glob
from benchmark import Benchmark


class ServerBenchmark(Benchmark):

    def __init__(self, config=None):

        super().__init__(self, config)
        self.command = config.get(
            "Command", ""
        )  # Full java command to launch the server, except for forge/fabric arguments
        self.server_path = config.get("Path", "")  # Full path to the server
        self.nogui = config.get(
            "nogui", True
        )  # Whether to run the dedicated server GUI or not
        self.num_fake_players = config.get(
            "num_fake_players", 2
        )  # Number of simulated players if the "Carpet" fabric mod is present
        self.fabric_chunkgen_command = config.get(
            "fabric_chunkgen_command", "chunky start"
        )  # Chunk generation command to use in fabric packs
        self.fabric_chunkgen_expect = config.get(
            "fabric_chunkgen_expect", "[Chunky] Task finished for"
        )  # String to look for when chunk generation is finished
        self.forge_chunkgen_command = config.get(
            "forge_chunkgen_command", "forge generate 0 0 0 3000"
        )  # Chunk generation command to use in forge packs
        self.forge_chunkgen_expect = config.get(
            "forge_chunkgen_expect", "Finished generating"
        )  # String to look for when chunk generation is finished
        self.startuptimeout = config.get(
            "startuptimeout", 350
        )  # Number of seconds to wait before considering the server to be dead/stuck
        self.chunkgentimeout = config.get(
            "chunkgentimeout", 600
        )  # Number of seconds to wait for chunk generation before considering the server to be dead/stuck
        self.totaltimeout = config.get(
            "totaltimeout", 1200
        )  # Number of seconds the whole server can run before timing out
        self.forceload_cmd = config.get(
            "forceload_cmd", "forceload add -120 -120 120 120"
        )  # Command to forceload a rectangle. Can also be some other server console command
        # self.plat
        # self.worldfolder
        # self.worldbackup

    def run(self):
        try:

            # Initialize lists
            self.blist["Startup_Times"] = []
            self.blist["Chunkgen_Times"] = []

            # TO DO
            # Try to find server start.bat file

            # See if there isn't better path to initiate search from
            # Try to find Fabric
            d = glob("*.jar")
            for f in d:
                if "fabric-" in os.path.basename(
                    f
                ) and "fabric-installer" not in os.path.basename(f):
                    chunkgen_command = self.fabric_chunkgen_command
                    chunkgen_expect = self.fabric_chunkgen_expect
                    command = command + " -jar " + os.path.basename(f)
                    if self.nogui:
                        command = command + "--nogui"
                    break

            # Try to find Forge
            d = glob(r"libraries/net/minecraftforge/forge/*/win_args.txt")
            if len(d) == 1:
                if self.debug:
                    print("Found Forge" + d[0])
                chunkgen_command = self.forge_chunkgen_command
                chunkgen_expect = self.forge_chunkgen_expect
                if self.plat == "Linux":
                    command = (
                        command
                        + " @"
                        + os.path.normpath(
                            os.path.join(os.path.dirnamme(d[0]), r"unix_args.txt")
                        )
                        + " --nogui"
                        + r' "$@"'
                    )
                else:
                    command = command + " @" + os.path.normpath(d[0]) + r" %*"
                    if self.nogui:
                        command = command + " --nogui"

            has_spark, has_carpet = mod_check()
            if has_spark:
                add_spark_stats(self.blist)
            if has_carpet:
                add_spark_stats(self.blist)

            # Helper function for crash notification

            # Bench Minecraft for # of iterations
            for n in range(1, self.iterations + 1):
                # Backup existing world to restore later
                if os.server_path.isdir("world") and not os.server_path.isdir(
                    "_world_backup"
                ):
                    backup_world(self.worldfolder, self.worldbackup)

                try:
                    # Delete chunky config if found, as it stores jobs there
                    if os.server_path.isfile(r"config/chunky.json"):
                        if self.debug:
                            print("Removing chunky config")
                        os.remove(r"config/chunky.json")

                    # Start Minecraft
                    print("Running '" + self.blist["Name"] + "' iteration " + str(n))
                    start = time.time()
                    try:
                        mcserver = pexpect.popen_spawn.PopenSpawn(
                            command, timeout=self.totaltimeout, maxread=20000000
                        )  # Start Minecraft server
                    except Exception as e:
                        print("Error running the command:")
                        print(command)
                        raise e

                    time.sleep(0.01)

                    if self.plat == "Windows":
                        try:
                            for proc in psutil.process_iter(["name"]):
                                if "java" in str(proc.name):
                                    if self.debug:
                                        print("Setting Priority")
                                    proc.nice(psutil.HIGH_PRIORITY_CLASS)
                        except:
                            print(
                                "Failed to set process priority, please run this benchmark as an admin!"
                            )

                    crash = False
                    index = mcserver.expect_exact(
                        pattern_list=[
                            r'''! For help, type "help"''',
                            "Minecraft Crash Report",
                            pexpect.EOF,
                            pexpect.TIMEOUT,
                        ],
                        timeout=self.startuptimeout,
                    )

                    if index == 0:
                        if self.debug:
                            print("Server started")
                    elif index == 1:
                        mcserver.sendline("stop")
                        time.sleep(0.01)
                        mcserver.kill(signal.SIGTERM)
                        qw("CRASH")
                        crash = True
                    elif index == 2:
                        qw("STOPPED")
                        crash = True
                    elif index == 3:
                        mcserver.sendline("stop")
                        mcserver.kill(signal.SIGTERM)
                        qw("TIMEOUT")
                        crash = True

                    if not crash:
                        self.blist["Startup_Times"].append(
                            round(time.time() - start, 2)
                        )
                        time.sleep(6)  # Let the server "settle"

                        if has_carpet:
                            if self.debug:
                                print("Spawning players")
                        start = time.time()
                        for x in range(1, self.num_fake_players + 1):
                            mcserver.sendline("player " + str(x) + " spawn")
                            mcserver.expect_exact(str(x) + " joined the game")
                            mcserver.sendline(
                                "player "
                                + str(x)
                                + " look 30 "
                                + str(int(round(360 * x / self.num_fake_players)))
                            )
                            mcserver.sendline("player " + str(x) + " jump continuous")
                            mcserver.sendline("player " + str(x) + " move forward")
                            mcserver.sendline("player " + str(x) + " sprint")
                            mcserver.sendline("player " + str(x) + " attack continuous")
                        self.blist["Player_Spawn_Times"].append(
                            round(time.time() - start, 3)
                        )

                        mcserver.sendline(self.forceload_cmd)
                        time.sleep(1)  # Let it settle some more

                        if self.debug:
                            print("Generating chunks...")

                        start = time.time()
                        mcserver.sendline(chunkgen_command)  # Generate chunks

                        index = mcserver.expect_exact(
                            pattern_list=[
                                chunkgen_expect,
                                "Minecraft Crash Report",
                                pexpect.EOF,
                                pexpect.TIMEOUT,
                            ],
                            timeout=self.chunkgentimeout,
                        )

                        if index == 0:
                            if self.debug:
                                print("Chunks finished. Stopping server...")
                            self.blist["Chunkgen_Times"].append(
                                round(time.time() - start, 2)
                            )
                            if has_spark:
                                mcserver.sendline("spark health --memory")
                                mcserver.expect_exact("TPS from last 5")
                                mcserver.sendline("spark gc")
                                mcserver.expect_exact("Garbage Collector statistics")
                                time.sleep(0.5)  # make sure log is flushed to disk
                                with open(
                                    "logs/latest.log", "r"
                                ) as f:  # Get spark info from the log
                                    lines = f.readlines()
                                    iter = 0
                                    for l in lines:
                                        if "TPS from last 5" in l:
                                            self.blist["Average_TPS_Values"].append(
                                                float(
                                                    lines[iter + 1]
                                                    .split(",")[-1][1:-1]
                                                    .split("*")[-1]
                                                )
                                            )  # TPS
                                        if "Memory usage:" in l:
                                            self.blist["Memory_Usage"].append(
                                                float(
                                                    lines[iter + 1]
                                                    .split("GB")[0]
                                                    .strip()
                                                )
                                            )  # Memory
                                        if "CPU usage" in l:
                                            self.blist["CPU_Usage"].append(
                                                float(
                                                    lines[iter + 2]
                                                    .split(",")[-1]
                                                    .split(r"%")[0]
                                                    .strip()
                                                )
                                            )  # CPU
                                        if (
                                            ("G1 Young Generation" in l)
                                            or ("ZGC Pauses collector:" in l)
                                            or ("Shenandoah Pauses collector" in l)
                                        ):
                                            self.blist["GC_Stop_MS"].append(
                                                float(
                                                    lines[iter + 1]
                                                    .split("ms avg")[0]
                                                    .strip()
                                                )
                                            )
                                            self.blist["GC_Stops"].append(
                                                int(
                                                    lines[iter + 1]
                                                    .split("ms avg,")[-1]
                                                    .split("total")[0]
                                                    .strip()
                                                )
                                            )  # GC Stop-the-world info
                                        if "G1 Old Generation" in l:
                                            g1gc = True
                                            self.blist["Oldgen_GCs"].append(
                                                int(
                                                    lines[iter + 1]
                                                    .split("collections")[0]
                                                    .strip()
                                                )
                                            )  # G1GC Old Gen collections
                                        iter = iter + 1

                        elif index == 1:
                            self.blist["Chunkgen_Times"].append("CRASH")
                        elif index == 2:
                            self.blist["Chunkgen_Times"].append("STOPPED")
                        elif index == 3:
                            self.blist["Chunkgen_Times"].append("TIMEOUT")
                        mcserver.kill(signal.SIGTERM)

                        if self.debug:
                            json.pprint.pprint(self.config)
                        with open(self.benchlog, "w") as f:
                            json.dump(
                                self.blist, f, indent=4
                            )  # Write current data to the benchmark log

                except Exception as e:
                    print(f"Error in ServerBenchmark Iteration {n}:")
                    print(traceback.format_exc())
                    try:
                        mcserver.kill(signal.SIGTERM)
                        time.sleep(2)
                    except:
                        pass

                try:
                    restore_world()  # Restore the world backup
                except:
                    try:
                        mcserver.kill(signal.SIGTERM)
                    except:
                        pass
                    time.sleep(5)
                    restore_world()  # Sometimes shutil fails if the server is still up, so try again.

            # End of iteration loop
            try:  # Dont let funky data kill the benchmark
                if self.blist["Iterations"] >= 2:
                    self.blist["Average_Chunkgen_Time"] = safemean(
                        self.blist["Chunkgen_Times"]
                    )
                    self.blist["Average_Startup_Time"] = safemean(
                        self.blist["Startup_Times"]
                    )
                    self.blist["PVariance_Chunkgen_Time"] = safevar(
                        self.blist["Chunkgen_Times"]
                    )
                    self.blist["Pvariance_Startup_Time"] = safevar(
                        self.blist["Startup_Times"]
                    )
                    if spark:
                        self.blist["Average_TPS"] = safemean(
                            self.blist["Average_TPS_Values"]
                        )
                        self.blist["PVariance_TPS"] = safevar(
                            self.blist["Average_TPS_Values"]
                        )
                        self.blist["Average_GC_Stop_MS"] = safemean(
                            self.blist["GC_Stop_MS"]
                        )
                        self.blist["PVariance_GC_Stop_MS"] = safevar(
                            self.blist["GC_Stop_MS"]
                        )
                        self.blist["Average_GC_Stops"] = safemean(
                            self.blist["GC_Stops"]
                        )
                        self.blist["Average_Memory_Usage_GB"] = safemean(
                            self.blist["Memory_Usage"]
                        )
                        self.blist["Average_CPU_Usage"] = safemean(
                            self.blist["CPU_Usage"]
                        )
                        if g1gc:
                            if len(self.blist["Oldgen_GCs"]) > 1:
                                self.blist["Average_Oldgen_GCs"] = safemean(
                                    self.blist["Oldgen_GCs"]
                                )
                    if hascarpet:
                        self.blist["Average_Spawn_Time"] = safemean(
                            self.blist["Player_Spawn_Times"]
                        )
                        self.blist["Player_Spawn_Variance"] = safevar(
                            self.blist["Player_Spawn_Times"]
                        )
            except Exception as e:
                print("Error saving benchmark data!")
                print(traceback.format_exc())

            with open(self.benchlog, "w") as f:
                json.dump(self.blist, f, indent=4)

        except:
            print("Error in ServerBenchmark!")
            print(traceback.format_exc())
