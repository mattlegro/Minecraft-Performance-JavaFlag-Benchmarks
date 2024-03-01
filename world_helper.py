import os, shutil, time


def restore_world(worldfolder, worldbackup):
    if os.path.isdir(worldfolder) and os.path.isdir(worldbackup):
        try:
            shutil.rmtree(worldfolder)
        except:
            time.sleep(7)  # Give the old server some time to close
            shutil.rmtree(worldfolder)
        os.rename(worldbackup, worldfolder)


def backup_world(worldfolder, worldbackup):
    try:
        # Backup existing world to restore later
        if os.path.isdir(worldfolder) and not os.path.isdir(worldbackup):
            try:
                shutil.copytree(worldfolder, worldbackup)
            except:
                time.sleep(3)
                shutil.copytree(worldfolder, worldbackup, dirs_exist_ok=True)
    except Exception as e:
        print("Could not create world backup")
        raise e
