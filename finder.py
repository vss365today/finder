import argparse
import logging
from importlib import import_module
from typing import Callable

from src.helpers import logger


# Create a logger
log = logging.getLogger("vss365today-finder")
log.addHandler(logger.file_handler())


def get_task_main(module_name: str) -> Callable:
    """Get a task's entrypoint function."""
    return import_module(f"src.core.{module_name}").main  # type: ignore


def handle_prompt_command(args: argparse.Namespace) -> bool:
    if args.schedule:
        logging.info("Starting scheduled Prompt...")
        return get_task_main("schedule")()

    if args.manual:
        logging.info("Running manual Prompt...")
        return get_task_main("schedule")()

    logging.info("Running fetch Prompt...")
    return get_task_main("fetch")()


# Handle app arguments
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

# Archive file generation
parser_archive = subparsers.add_parser("archive", help="archive help")
parser_archive.add_argument(
    "-r",
    "--regenerate",
    help="regenerate an existing Prompt archive",
    action="store_true",
)
parser_archive.set_defaults(func=get_task_main("archive"))

parser_backup = subparsers.add_parser("backup", help="backup help")
parser_backup.set_defaults(func=get_task_main("backup"))

# Notif email sending
parser_email = subparsers.add_parser("email", help="email help")
parser_email.set_defaults(func=get_task_main("email"))

# Prompt recording actions
parser_prompt = subparsers.add_parser("prompt", help="prompt help")
group_prompt = parser_prompt.add_mutually_exclusive_group()
group_prompt.add_argument(
    "-m",
    "--manual",
    help="manually record a specific Prompt.",
    action="store_true",
)
group_prompt.add_argument(
    "-s",
    "--schedule",
    help="schedule recording the latest Prompt according to ENV values.",
    action="store_true",
)
parser_prompt.set_defaults(func=handle_prompt_command)

# Run the proper commands
try:
    args = parser.parse_args()
    args.func(args)
except AttributeError:
    parser.print_help()
