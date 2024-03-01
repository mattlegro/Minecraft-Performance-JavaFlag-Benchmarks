import time, guibot, pydirectinput


# Try to find matches PNGs in CV_Images and click on them:
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
