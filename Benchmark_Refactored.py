import subprocess
import time
import os
import glob
import psutil
import shutil
import json
import traceback
from safety_helper import waitforlogline, safemean, safevar
from world_helper import restore_world, backup_world
from abc import ABC, abstractmethod


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


class ClientBenchmark(Benchmark):
    def __init__(self, config=None):
        super().__init__(config)
        self.prismpath = config.get(
            "prismpath", "C:/Benchmark/PrismLauncherPortable/Prism.exe"
        )  # Full path to Prism executable file
        self.prisminstances = config.get(
            "prisminstances", ""
        )  # Full path to Prism instance folder. Normally in %appdata%/roaming/Prism on windows, but you can leave this blank if using Prism portable
        self.presentmonpath = config.get(
            "presentmonpath", "C:/Benchmark/presentmon.exe"
        )  # Full path to Intel presentmon executable file
        self.warmup = config.get(
            "warmup", 90
        )  # Seconds to wait after hitting the "singleplayer" button before starting the benchmark. Give enough time for the world to load, and java to "warm up"
        self.benchtime = config.get("benchtime", 90)  # Seconds to run the benchmark
        self.focusclick = config.get(
            "focusclick", True
        )  # Middle click before searching for buttons, only really necessary for fullscreen Minecraft
        self.cvpath
        self.csvpath

    def run(self):
        try:
            # Extract configuration parameters

            # Client branch logic
            if "PrismInstance" in self.config:
                prismfolder = os.path.normpath(
                    os.path.join(
                        os.path.dirname(prismpath), "instances", prism_instance
                    )
                )
                if not os.path.isdir(prismfolder):
                    prismfolder = os.path.join(prisminstances, prism_instance)
                    if not os.path.isdir(prismfolder):
                        raise Exception(
                            "Either your Prism instance path or your selected instance is incorrect: "
                            + prismfolder
                        )
                prismfolder = glob.glob(os.path.join(prismfolder, "minecraft"))[0]
                if not os.path.isdir(prismfolder):
                    raise Exception("Prism instance not valid!")
                plog = os.path.join(prismfolder, "logs", "latest.log")
                worldfolder = glob.glob(os.path.join(prismfolder, "saves", "*"))[0]
                try:
                    worldbackup = os.path.join(prismfolder, "world_backup")
                except:
                    raise Exception(
                        "Please create a world in this instance before running the benchmark!"
                    )

                os.chdir(prismfolder)

                # Initialize lists
                self.blist["Average_FPS"] = []
                self.blist[r"1%_Frametime_ms"] = []
                self.blist[r"5%_Frametime_ms"] = []

                # Try to find Spark and/or Carpet mods
                if os.path.isdir("mods"):
                    mods = glob.glob("mods/*.jar")
                    spark = any("spark" in s for s in mods)
                    if spark:
                        self.blist["GC_Stop_MS"] = []
                        self.blist["GC_Stops"] = []
                        self.blist["Oldgen_GCs"] = []
                        self.blist["Memory_Usage"] = []
                        self.blist["CPU_Usage"] = []

                # Restore world backup
                atexit.register(self.restore_world)
                restore_world(worldfolder, worldbackup)

                for n in range(1, self.config["Iterations"] + 1):
                    backup_world(worldfolder, worldbackup)

                    for proc in psutil.process_iter(["name"]):
                        if "javaw" in str(proc.name):
                            raise Exception(
                                "Please kill all existing 'javaw' processes"
                            )
                    if os.path.exists(plog):
                        os.remove(plog)

                    try:
                        subprocess.run(
                            [presentmonpath, "-terminate_existing"],
                            creationflags=subprocess.CREATE_NEW_CONSOLE,
                            shell=True,
                        )
                    except:
                        pass

                    try:
                        clientprocess = subprocess.Popen(
                            [prismpath, "--launch", prism_instance],
                            creationflags=subprocess.HIGH_PRIORITY_CLASS
                            | subprocess.CREATE_NEW_CONSOLE,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            shell=True,
                        )
                    except Exception as e:
                        print("Error starting client:")
                        raise e

                    time.sleep(15)
                    self.waitforlogline(plog, loadedstring)
                    title = None
                    for t in gw.getAllTitles():
                        if "Minecraft" or "minecraft" in t:
                            title = t
                    mcwindow = gw.getWindowsWithTitle(title)[0]
                    mcwindow.maximize()
                    mcwindow.activate()
                    time.sleep(4)
                    if debug:
                        print("Starting machine vision search")
                    GlobalConfig.smooth_mouse_drag = False
                    GlobalConfig.delay_after_drag = 0
                    ctl = PyAutoGUIController()
                    gfinder = TemplateFinder()
                    guibot = GuiBot(ctl, gfinder)
                    guibot.add_path(cvpath)

                    while True:
                        time.sleep(1)
                        if guibot.exists("Singleplayer1"):
                            guibot.click("Singleplayer1")
                            ClickVersion()
                            break
                        elif guibot.exists("Singleplayer2"):
                            guibot.click("Singleplayer2")
                            ClickVersion()
                            break
                        elif guibot.exists("Singleplayer3"):
                            guibot.click("Singleplayer3")
                            ClickVersion()
                            break
                        elif guibot.exists("Singleplayer4"):
                            guibot.click("Singleplayer4")
                            ClickVersion()
                            break
                        else:
                            if time.time() > _timeout:
                                raise Exception(
                                    "Cannot find 'Singleplayer' button to click! This may be a machine vision issue if the start screen is modded."
                                )

                    time.sleep(warmup)

                    pydirectinput.keyDown("space")
                    pydirectinput.keyDown("w")
                    pydirectinput.mouseDown(button="left")

                    if os.path.isfile(csvpath):
                        os.remove(csvpath)
                    pmonprocess = subprocess.Popen(
                        [
                            presentmonpath,
                            "-process_name",
                            "javaw.exe",
                            "-output_file",
                            csvpath,
                            "-terminate_on_proc_exit",
                        ],
                        creationflags=subprocess.CREATE_NEW_CONSOLE,
                        shell=True,
                    )

                    time.sleep(benchtime)

                    try:
                        subprocess.run(
                            [presentmonpath, "-terminate_existing"],
                            creationflags=subprocess.CREATE_NEW_CONSOLE,
                            shell=True,
                        )
                    except:
                        pass
                    pmonprocess.terminate()
                    pydirectinput.keyUp("w")
                    pydirectinput.keyUp("space")
                    pydirectinput.mouseUp(button="left")
                    if spark:
                        pydirectinput.press(r"/")
                        pydirectinput.typewrite("sparkc health --memory")
                        pydirectinput.press(r"enter")
                        pydirectinput.press(r"/")
                        pydirectinput.typewrite("sparkc gc")
                        pydirectinput.press(r"enter")
                        time.sleep(0.3)

                        with open(plog, "r") as f:
                            lines = f.readlines()
                            iter = 0
                            for l in lines:
                            if "Memory usage:" in l:
                                blist["Memory_Usage"].append(
                                    float(
                                        lines[iter]
                                        .split(r"Memory usage:\n")[-1]
                                        .split("GB")[0]
                                        .strip()
                                    )
                                )  # Memory
                            if "CPU usage" in l:
                                blist["CPU_Usage"].append(
                                    float(
                                        lines[iter]
                                        .split(r"(process)\n\n>")[0]
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
                                blist["GC_Stop_MS"].append(
                                    float(
                                        lines[iter]
                                        .split("ms avg")[0]
                                        .split(r"\n")[-1]
                                        .strip()
                                    )
                                )
                                blist["GC_Stops"].append(
                                    int(
                                        lines[iter]
                                        .split("ms avg,")[1]
                                        .split("total")[0]
                                        .strip()
                                    )
                                )  # GC Stop-the-world info
                            if "G1 Old Generation" in l:
                                g1gc = True
                                blist["Oldgen_GCs"].append(
                                    int(
                                        lines[iter]
                                        .split(r"G1 Old Generation collector:\n")[-1]
                                        .split("collections")[0]
                                        .strip()
                                    )
                                )  # G1GC Old Gen collections
                            iter = iter + 1

                    # close presentmon and kill the minecraft client
                    clientprocess.terminate()
                    time.sleep(1)
                    try:
                        for proc in psutil.process_iter(
                            ["name"]
                        ):  # Make sure the java client is really dead, as it likes to hang
                            if "javaw" in str(proc.name):
                                if debug:
                                    print("Killing client")
                                proc.kill()
                    except:
                        print("Failed to run psutil loop to kill Minecraft")

                    # Clean up for sure
                    try:
                        subprocess.run(
                            [presentmonpath, "-terminate_existing"],
                            creationflags=subprocess.CREATE_NEW_CONSOLE,
                            shell=True,
                        )
                    except:
                        pass
                    try:
                        clientprocess.terminate()
                        pmonprocess.terminate()
                    except:
                        pass

                    time.sleep(10)

                    frametimes = []
                    with open(csvpath, "r") as f:
                        csv_reader = csv.DictReader(f, delimiter=",")
                        for line in csv_reader:
                            if line["msBetweenPresents"] is not None:
                                frametimes.append(float(line["msBetweenPresents"]))
                    
                    blist["Average_FPS"].append(
                        round(1000 / statistics.mean(frametimes), 2)
                    )  # Average FPS
                    blist[r"1%_Frametime_ms"].append(
                        round(
                            statistics.mean(
                                sorted(frametimes)[round(len(frametimes) * 0.99 - 1) :]
                            ),
                            2,
                        )
                    )  # Slowest 1% of frametimes average
                    blist[r"5%_Frametime_ms"].append(
                        round(
                            statistics.mean(
                                sorted(frametimes)[round(len(frametimes) * 0.95 - 1) :]
                            ),
                            2,
                        )
                    )  # Slowest 5% of frametimes average                    

                    restore_world()

                    with open(benchlog, "w") as f:
                        json.dump(
                            blist, f, indent=4
                        )  # Write current data to the benchmark log                    

                    print("Iteration " + str(n) + " completed.")
                
                try:
                    if blist["Iterations"] >= 2:
                        blist["Net_Average_FPS"] = safemean(blist["Average_FPS"])
                        blist["Average_FPS_Variance"] = safevar(blist["Average_FPS"])
                        blist[r"Average_1%_Frametime_ms"] = safemean(
                            blist[r"1%_Frametime_ms"]
                        )
                        blist[r"PVariance_1%_Frametime_ms"] = safevar(
                            blist[r"1%_Frametime_ms"]
                        )
                        blist[r"Average_5%_Frametime_ms"] = safemean(
                            blist[r"5%_Frametime_ms"]
                        )
                        blist[r"PVariance_5%_Frametime_ms"] = safevar(
                            blist[r"5%_Frametime_ms"]
                        )
                        if spark:
                            blist["Average_GC_Stop_MS"] = safemean(blist["GC_Stop_MS"])
                            blist["PVariance_GC_Stop_MS"] = safevar(blist["GC_Stop_MS"])
                            blist["Average_GC_Stops"] = safemean(blist["GC_Stops"])
                            blist["Average_Memory_Usage_GB"] = safemean(
                                blist["Memory_Usage"]
                            )
                            blist["Average_CPU_Usage"] = safemean(blist["CPU_Usage"])
                            if g1gc:
                                if len(blist["Oldgen_GCs"]) > 1:
                                    blist["Average_Oldgen_GCs"] = safemean(
                                        blist["Oldgen_GCs"]
                                    )
                except Exception as e:
                    print("Error saving client benchmark data!")
                    print(traceback.format_exc())

        except Exception as e:
            print("Error in ClientBenchmark run:")
            print(traceback.format_exc())


class ServerBenchmark(Benchmark):
    def __init__(self, config=None):
        super().__init__(config)
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

            # Try to find Fabric
            d = glob.glob("*.jar")
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
            d = glob.glob(r"libraries/net/minecraftforge/forge/*/win_args.txt")
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

            has_spark, has_carpet = mod_check(self.blist)
            if has_spark:
                add_spark_stats(blist)
            if has_carpet:
                add_spark_stats(blist)
            
            else:
                if self.debug:
                    print("No mods folder found")

            # Helper function for crash notification

            # Bench Minecraft for # of iterations
            for n in range(1, self.iterations + 1):
                # Backup existing world to restore later
                if os.server_path.isdir("world") and not os.server_path.isdir("_world_backup"):
                    backup_world(self.worldfolder,self.worldbackup)

                try:
                    # Delete chunky config if found, as it stores jobs there
                    if os.server_path.isfile(r"config/chunky.json"):
                        if self.debug:
                            print("Removing chunky config")
                        os.remove(r"config/chunky.json")

                    # Start Minecraft
                    print(
                        "Running '" + self.blist["Name"] + "' iteration " + str(n)
                    )
                    start = time.time()
                    try:
                        mcserver = popen_spawn.PopenSpawn(
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
                                + str(int(round(360 * x / carpet)))
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
                                                    lines[iter + 1].split("GB")[0].strip()
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
                    self.blist["Average_Chunkgen_Time"] = safemean(self.blist["Chunkgen_Times"])
                    self.blist["Average_Startup_Time"] = safemean(self.blist["Startup_Times"])
                    self.blist["PVariance_Chunkgen_Time"] = safevar(
                        self.blist["Chunkgen_Times"]
                    )
                    self.blist["Pvariance_Startup_Time"] = safevar(self.blist["Startup_Times"])
                    if spark:
                        self.blist["Average_TPS"] = safemean(self.blist["Average_TPS_Values"])
                        self.blist["PVariance_TPS"] = safevar(self.blist["Average_TPS_Values"])
                        self.blist["Average_GC_Stop_MS"] = safemean(self.blist["GC_Stop_MS"])
                        self.blist["PVariance_GC_Stop_MS"] = safevar(self.blist["GC_Stop_MS"])
                        self.blist["Average_GC_Stops"] = safemean(self.blist["GC_Stops"])
                        self.blist["Average_Memory_Usage_GB"] = safemean(
                            self.blist["Memory_Usage"]
                        )
                        self.blist["Average_CPU_Usage"] = safemean(self.blist["CPU_Usage"])
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
                json.dump(
                    self.blist, f, indent=4)
        
        except:
            print("Error in ServerBenchmark!")
            print(traceback.format_exc())
