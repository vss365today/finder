from datetime import date, datetime, timedelta

import sys_vars
from apscheduler.schedulers.blocking import BlockingScheduler
from httpx import HTTPError
from pytz import utc
from tweepy import Paginator

from src.core.api import v2
from src.helpers import tweet

__all__ = ["main", "schedule"]


# Connect to the Twitter API
TWITTER_API = tweet.twitter_v2_api()


def find_prompt(uid: str):
    found_tweet = None

    # Get the tweets from the Host for the prompt
    for response in Paginator(
        TWITTER_API.get_users_tweets,
        id=uid,
        max_results=50,
        exclude=["replies", "retweets"],
        tweet_fields=["entities"],
    ).flatten():
        # Found the prompt!
        if tweet.is_likely_prompt_tweet(response):
            found_tweet = response
            break

    # ...We never found the prompt. Sad face day :(
    if found_tweet is None:
        return None

    # ...OOOOORRRRRRRR we did, so return a proper Response object.
    # People these days. You just never know if they'll say what you want! /s
    return TWITTER_API.get_tweet(found_tweet.id, **tweet.fetch_fields())


def main() -> bool:
    # Start by getting today's date because it's surprising
    # how often we actually need this info
    today = datetime.now()

    # Get the latest recorded prompt to see if we need to do anything
    latest_tweet = v2.get("prompts/")[0]
    latest_tweet["date"] = date.fromisoformat(latest_tweet["date"])

    # We already have latest tweet, don't do anything
    # TODO: Can this be simplified by making `today` always a date and doing direct ==?
    if (
        latest_tweet["date"].year == today.year
        and latest_tweet["date"].month == today.month
        and latest_tweet["date"].day == today.day
    ):
        print(f"Prompt for {today} already found. Aborting...")
        return False

    # Hosts serve for 15 days (2 Hosts/mo). Ask the API who is currently hosting
    print("Identifying the current Host")
    try:
        current_host = v2.get("hosts", "current")

    # If that fails, we don't have an assigned Host for this period and must stop
    except HTTPError:
        print("No Host found for the current Hosting Period! Aborting...")
        return False

    # Attempt to find the prompt
    print(f"The current Host is {current_host['handle']}.")
    print("Searching for the latest Prompt")
    prompt_tweet = find_prompt(current_host["twitter_uid"])

    # The tweet was not found at all :(
    if prompt_tweet is None:
        print("Search limit reached without finding Prompt! Aborting...")
        return False

    # The found tweet date is yesterday's date, indicating a
    # time zone difference. Tweet datetimes are always expressed
    # in UTC, so attempt to get to tomorrow's date
    # and see if it matches the expected tweet date
    tweet_date: datetime = prompt_tweet.data.created_at
    if tweet_date.day - today.day < 0:
        next_day_hour_difference = 24 - prompt_tweet.data.created_at.hour
        tweet_date: datetime = prompt_tweet.data.created_at + timedelta(
            hours=next_day_hour_difference
        )

    # We already have the latest tweet, don't do anything
    # This condition is hit when it is _technically_ the next day
    # but the newest tweet hasn't been sent out
    # TODO: Can this be simplified by making `tweet_date` always a date and doing direct ==?
    if (
        tweet_date.year == latest_tweet["date"].year
        and tweet_date.month == latest_tweet["date"].month
        and tweet_date.day == latest_tweet["date"].day
    ):
        print(
            f"The latest Prompt for {tweet_date.date()} has already found. Aborting..."
        )
        return False

    # Attempt to extract the prompt word and back out if we can't
    prompt_word = tweet.get_prompt(prompt_tweet)
    if prompt_word is None:
        print(f"Cannot find Prompt word in tweet {prompt_tweet.data.id}")
        return False

    # Construct an API request object
    prompt = {
        "content": tweet.get_text(prompt_tweet),
        "date": tweet_date.date().isoformat(),
        "host_handle": prompt_tweet[1]["users"][0].username,
        "twitter_id": str(prompt_tweet.data.id),
        "word": prompt_word,
    }

    # Pull out any possible media
    media_alt_text = tweet.get_media_alt_text(prompt_tweet)
    media_url = tweet.get_media(prompt_tweet)
    prompt_media = {}
    if media_url is not None:
        prompt_media = {"items": [{"alt_text": media_alt_text, "url": media_url}]}

    try:
        # Add the tweet to the database
        print("Adding Prompt to database...")
        r = v2.post("prompts/", json=prompt)

        # Create any media that is attached to the tweet
        if prompt_media:
            print("Recording Prompt Media...")
            prompt_id = r["_id"]
            v2.post("prompts", str(prompt_id), "media/", json=prompt_media)

        # Send the email broadcast
        print("Sending out notification emails...")
        # v2.post("notifications", tweet_date.date().isoformat())

        # Generate a new Prompt archive
        print("Creating new Prompt archive...")
        v2.post("archive/")

    except HTTPError as exc:
        print(f"Cannot add Prompt for {tweet_date.date().isoformat()} to the database!")
        print(exc)
        return False
    return True


def schedule() -> None:
    """Schedule the Prompt fetch process."""
    scheduler = BlockingScheduler()

    # Get the scheduled times
    schedule_times: list[str] = sys_vars.get_json("SCHEDULE_TIMES")
    for time in schedule_times:
        minute, hour = time.split()

        # Create a job for each time
        scheduler.add_job(
            main,
            args=[],
            trigger="cron",
            hour=hour,
            minute=minute,
            day_of_week="*",
            timezone=utc,
        )

    # Start the scheduler
    scheduler.start()
