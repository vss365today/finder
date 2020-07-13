from typing import List

from apscheduler.schedulers.blocking import BlockingScheduler
import sys_vars

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
        )

    # Set the run time to be 5 minutes after the scheduled one
    minute, hour = schedule_times[-1].split()
    minute = str(int(minute) + 5)

    # Schedule the word archive generation
    scheduler.add_job(
        archive.main,
        args=[],
        trigger="cron",
        hour=hour,
        minute=minute,
        day_of_week="*",
    )

    # Start the scheduler
    scheduler.start()
