import krpc
import os
import subprocess
from pathlib import Path
from decouple import config

CHECKPOINT_NAME = "checkpoint"


def is_ksp_running():
    try:
        # List processes and grep for KSP
        output = subprocess.check_output("tasklist", shell=True).decode("utf-8")
        return "KSP" in output
    except:
        return False


def launch_ksp(path: Path):
    subprocess.Popen([path], cwd=os.path.dirname(path))


def load_checkpoint(name: str, space_center):
    """Load the given game save state"""
    try:
        space_center.load(name)
    except ValueError as e:
        raise ValueError(
            f"No checkpoint named '{name}.sfs' was found. Please create one"
        )


if __name__ == "__main__":
    if not is_ksp_running():
        ksp_path = Path(str(config("KSP_PATH")))
        print(f"Launching KSP from '{ksp_path}'...")
        launch_ksp(path=ksp_path)

    input("Press any key once the KSP save is loaded to continue...")

    print("Connecting to KSP...")
    connection = krpc.connect(name="Simulator")
    assert 
    print(f"Loading '{CHECKPOINT_NAME}.sfs' checkpoint...")
    load_checkpoint(name=CHECKPOINT_NAME, space_center=connection.space_center)

    science = connection.space_center.science
    print(science)

    # connect through krpc

    # load the given saved game

    # load the given save point

    # pause the game

    input("Simulation complete. Press any key to quit...")
    # connection.close()
