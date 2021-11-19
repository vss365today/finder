from argparse import Namespace
from typing import List

import sys_vars
from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import utc

from src.core import archive, fetch


__all__ = ["main"]


def main():
    scheduler = BlockingScheduler()

    # Get the scheduled times
    schedule_times: List[str] = sys_vars.get_json("SCHEDULE_TIMES")
    for time in schedule_times:
        minute, hour = time.split()

        # Create a job for each time
        scheduler.add_job(
            fetch.main,
            args=[],
            trigger="cron",
            hour=hour,
            minute=minute,
            day_of_week="*",
            timezone=utc,
        )

    # Start the scheduler
    scheduler.start()
