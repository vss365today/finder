from argparse import Namespace
from datetime import datetime
from os import fspath

import py7zr
import sys_vars


__all__ = ["main"]


def main(_: Namespace) -> bool:
    """Create an archive backup of all Prompt static images."""
    print("Creating backup of Prompt images...")
    # Create the archive name
    now = datetime.now().isoformat().replace(":", "-")
    backup_file = (
        sys_vars.get_path("BACKUP_DIR") / f"vss365today_images_{now}.7z"
    ).resolve()

    try:
        # Attempt to create the archive
        with py7zr.SevenZipFile(fspath(backup_file), "w") as archive:
            # archname="" puts the files in the archive root
            archive.writeall(sys_vars.get_path("IMAGES_DIR").as_posix(), arcname="")

        print(f"{backup_file} successfully created")
        return True

    # Something happened and it failed
    except py7zr.exceptions.ArchiveErroras as exc:
        print("Unable to backup Prompt images!")
        print(exc)
        return False
