import subprocess
import time
import os
import glob
import psutil
import json
import traceback
from benchmark import Benchmark


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


    def ClickPlay():
        _timeout = time.time() + 100

        while True:
            print("Searching for 'Play' button")
            time.sleep(0.3)
            if guibot.exists("Play1"):
                guibot.click("Play1")
                break
            elif guibot.exists("Play2"):
                guibot.click("Play2")
                break
            elif guibot.exists("Play3"):
                guibot.click("Play3")
                break
            elif guibot.exists("Play4"):
                guibot.click("Play4")
                break
            else:
                if focusclick:
                    middleclick()
                if time.time() > _timeout:
                    raise Exception(
                        "Cannot find 'Play' Button to click! This may be a machine vision issue if the start screen is modded."
                    )


    def ClickVersion():
        while True:
            print("Searching for 'Version' string")
            time.sleep(0.5)
            if guibot.exists("Version1"):
                guibot.click("Version1")
                ClickPlay()
                break
            elif guibot.exists("Version2"):
                guibot.click("Version2")
                ClickPlay()
                break
            elif guibot.exists("Version3"):
                guibot.click("Version3")
                ClickPlay()
                break
            elif guibot.exists("Version4"):
                guibot.click("Version4")
                ClickPlay()
                break
            else:
                if time.time() > _timeout:
                    raise Exception(
                        "Cannot find world to click! Please create a world before running the script. This may be a machine vision issue if the start screen is modded."
                    )


    def middleclick():
        pydirectinput.mouseDown(button="left")
        pydirectinput.mouseUp(button="left")



