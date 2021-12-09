from argparse import Namespace
from datetime import datetime
from os import fspath

import py7zr
import sys_vars
from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import utc


__all__ = ["main", "schedule"]


def main(*args: Namespace) -> bool:
    """Create an archive backup of all Prompt images."""
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
    except py7zr.exceptions.ArchiveError as exc:
        print("Unable to backup Prompt images!")
        print(exc)
        return False


def schedule() -> None:
    """Schedule the Prompt images backup."""
    scheduler = BlockingScheduler()
    scheduler.add_job(
        main,
        args=[],
        trigger="cron",
        hour="0",
        minute="0",
        day_of_week="0",
        timezone=utc,
    )
    scheduler.start()
