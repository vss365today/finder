import argparse
import logging
import sys

from src.core import archive, email, fetch, manual, schedule


# Create a logger to print all logging output to stdout
logger = logging.getLogger("vss365today-finder")
logger.setLevel(logging.INFO)
LOG_FORMAT = logging.Formatter("[%(asctime)s - %(levelname)s]: %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(LOG_FORMAT)
logger.addHandler(handler)


def handle_prompt_command(args: argparse.Namespace) -> bool:
    if args.schedule:
        logging.info("Starting scheduled Prompt...")
        return schedule.main()

    if args.manual:
        logging.info("Running manual Prompt...")
        return manual.main()

    logging.info("Running fetch Prompt...")
    return fetch.main()


# Handle app arguments
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

# Archive file generation
parser_archive = subparsers.add_parser("archive", help="archive help")
parser_archive.add_argument(
    "-r",
    "--regenerate",
    help="regenerate an existing word archive",
    action="store_true",
)
parser_archive.set_defaults(func=archive.main)

# Notif email sending
parser_email = subparsers.add_parser("email", help="email help")
parser_email.set_defaults(func=email.main)

# Prompt recording actions
parser_prompt = subparsers.add_parser("prompt", help="prompt help")
group_prompt = parser_prompt.add_mutually_exclusive_group()
group_prompt.add_argument(
    "-m",
    "--manual",
    help="manually record a specific prompt.",
    action="store_true",
)
group_prompt.add_argument(
    "-s",
    "--schedule",
    help="schedule recording the latest prompt according to ENV values.",
    action="store_true",
)
parser_prompt.set_defaults(func=handle_prompt_command)

# Run the proper commands
try:
    args = parser.parse_args()
    args.func(args)
except AttributeError:
    parser.print_help()
