from argparse import Namespace

import sys_vars
from httpx import HTTPError

from src.core.api import v2

__all__ = ["main"]


def main(args: Namespace) -> bool:
    """Generate a Prompt archive file."""
    try:
        v2.post("archive/")

    # The generation failed. We don't need to move on
    except HTTPError as exc:
        print("Unable to create archive file!")
        print(exc)
        return False

    # Get the downloads directory content
    dir_contents = sorted(
        sys_vars.get_path("DOWNLOADS_PATH").glob("*.xlsx"), reverse=True
    )

    # Determine what old archive file(s) should be deleted
    # We only ever want 2 files at a time: yesterday and today
    files_to_delete = []
    if len(dir_contents) >= 3:
        files_to_delete.extend(dir_contents[2:])

    # Delete all the old archive files
    for old_file in files_to_delete:
        print(f"Deleting old file {old_file}")
        old_file.unlink()

    print(f"Successfully created Archive file {dir_contents[0]}")
    return True
