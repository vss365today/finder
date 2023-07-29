import argparse
import logging
from importlib import import_module
from types import ModuleType

from src.helpers import logger


# Create a logger
log = logging.getLogger("vss365today-finder")
log.addHandler(logger.file_handler())


def get_task_main(module_name: str) -> ModuleType:
    """Import a task module."""
    return import_module(f"src.core.{module_name}")


def handle_prompt_command(args: argparse.Namespace) -> bool:
    if args.manual:
        logging.info("Running manual Prompt...")
        return get_task_main("manual").main()  # type: ignore

    logging.info("Running fetch Prompt...")
    return get_task_main("fetch").main()  # type: ignore


def handle_schedule_command(args: argparse.Namespace) -> bool:
    if args.prompt:
        logging.info("Starting scheduled Prompt fetch...")
        return get_task_main("fetch").schedule()  # type: ignore

    if args.backup:
        logging.info("Starting scheduled Prompt images backup...")
        return get_task_main("backup").schedule()  # type: ignore

    return False


# Handle app arguments
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

# Archive file generation
parser_archive = subparsers.add_parser("archive", help="archive help")
parser_archive.set_defaults(func=get_task_main("archive").main)  # type: ignore

# Static file backup
parser_backup = subparsers.add_parser("backup", help="backup help")
parser_backup.set_defaults(func=get_task_main("backup").main)  # type: ignore

# Notif email sending
parser_email = subparsers.add_parser("email", help="email help")
parser_email.set_defaults(func=get_task_main("email").main)  # type: ignore

# Prompt recording actions
parser_prompt = subparsers.add_parser("prompt", help="prompt help")
group_prompt = parser_prompt.add_mutually_exclusive_group()
group_prompt.add_argument(
    "-m",
    "--manual",
    help="manually record a specific Prompt.",
    action="store_true",
)
parser_prompt.set_defaults(func=handle_prompt_command)

# Scheduled tasks
parser_schedule = subparsers.add_parser("schedule", help="schedule help")
group_schedule = parser_schedule.add_mutually_exclusive_group()
group_schedule.add_argument(
    "-p",
    "--prompt",
    help="schedule recording the latest Prompt according to ENV values.",
    action="store_true",
)
group_schedule.add_argument(
    "-b",
    "--backup",
    help="schedule a backup of Prompt images.",
    action="store_true",
)
parser_schedule.set_defaults(func=handle_schedule_command)

# Run the proper commands
try:
    args = parser.parse_args()
    args.func(args)
except AttributeError:
    parser.print_help()
