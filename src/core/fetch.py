from datetime import datetime, timedelta
from pprint import pprint
from typing import Optional

from requests.exceptions import HTTPError
import tweepy
from tweepy.tweet import Tweet

from src.helpers import get_tweet_media, get_tweet_text
from src.helpers import api, tweet2
from src.helpers.date import create_datetime


__all__ = ["main"]


# Connect to the Twitter API
TWITTER_API = tweet2.twitter_v2_api()


def find_prompt_tweet(
    uid: str, tweet_id: str = None, recur_count: int = 0
) -> Optional[Tweet]:
    # If we recurse too many times, stop searching
    if recur_count > 4:
        return None

    # Get the latest tweets from the prompt Host
    statuses = TWITTER_API.get_users_tweets(
        id=uid,
        until_id=tweet_id,
        max_results=30,
        exclude=["replies", "retweets"],
        expansions=["attachments.media_keys", "author_id"],
        tweet_fields=["created_at", "entities"],
        media_fields=["preview_image_url", "url"],
    )

    found_tweet = None
    for twt in statuses.data:
        # Try to find the prompt tweet among the pulled tweets
        if not tweet2.confirm_prompt(twt):
            continue

        # Found it!!
        found_tweet = twt
        break

    # We didn't find the prompt tweet, so we need to search again,
    # but this time, older than the oldest tweet we currently have
    if found_tweet is None:
        return find_prompt_tweet(uid, statuses.data[-1].data.id, recur_count + 1)
    return found_tweet


def main() -> bool:
    # Start by getting today's date because it's surprising
    # how often we actually need this info
    TODAY = datetime.now()

    # Get the latest recorded prompt to see if we need to do anything
    LATEST_TWEET = api.get("prompt")[0]
    LATEST_TWEET["date"] = create_datetime(LATEST_TWEET["date"])

    # We already have latest tweet, don't do anything
    if (
        LATEST_TWEET["date"].year == TODAY.year
        and LATEST_TWEET["date"].month == TODAY.month
        and LATEST_TWEET["date"].day == TODAY.day
    ):
        print(f"Prompt for {TODAY} already found. Aborting...")
        return False

    # Hosts serve for 15 days (2 Hosts/mo)
    # Determine which one is hosting right now
    # Start by searching for the Host for this exact day
    print("Identifying the current Host")
    try:
        CURRENT_HOST = api.get("host", "date", params={"date": TODAY})

    # If that fails, determine the Host for this hosting period
    except HTTPError:
        host_start_date = api.get("settings", "hosting", params={"date": TODAY})[0]
        hosting_period = datetime.now().replace(day=host_start_date)
        CURRENT_HOST = api.get("host", "date", params={"date": hosting_period})

    # Attempt to find the prompt
    print("Searching for the latest prompt")
    prompt_tweet = find_prompt_tweet(CURRENT_HOST["uid"])

    # The tweet was not found at all :(
    if prompt_tweet is None:
        print("Search limit reached without finding Prompt! Aborting...")
        return False

    # The found tweet date is yesterday's date, indicating a
    # time zone difference. Tweet datetimes are always expressed
    # in UTC, so attempt to get to tomorrow's date
    # and see if it matches the expected tweet date
    tweet_date = prompt_tweet.created_at
    if tweet_date.day - TODAY.day < 0:
        next_day_hour_difference = 24 - prompt_tweet.created_at.hour
        tweet_date = prompt_tweet.created_at + timedelta(hours=next_day_hour_difference)

    # We already have the latest tweet, don't do anything
    # This condition is hit when it is _technnically_ the next day
    # but the newest tweet hasn't been sent out
    if (
        tweet_date.year == LATEST_TWEET["date"].year
        and tweet_date.month == LATEST_TWEET["date"].month
        and tweet_date.day == LATEST_TWEET["date"].day
    ):
        print(f"The latest Prompt for {tweet_date} has already found. Aborting...")
        return False

    # Pull out the tweet media and text content
    # media_url, tweet_media = get_tweet_media(prompt_tweet)
    # tweet_text = get_tweet_text(prompt_tweet, media_url)
    # del media_url

    # Attempt to extract the prompt word and back out if we can't
    prompt_word = tweet2.get_prompt(prompt_tweet)
    if prompt_word is None:
        print(f"Cannot find Prompt word in tweet {prompt_tweet.id}")
        return False

    # Construct a dictionary with only the info we need
    prompt = {
        "id": str(prompt_tweet.id),
        "uid": str(prompt_tweet.author_id),
        "date": tweet_date.isoformat(),
        "word": prompt_word,
        "content": tweet2.get_text(prompt_tweet),
        # "media": tweet2.get_media(prompt_tweet),
    }
    pprint(prompt)
    print()
    try:
        # Add the tweet to the database
        print("Adding Prompt to database")
        #     api.post("prompt/", json=prompt)

        # Send the email broadcast
        print("Sending out notification emails")
    #     api.post("broadcast/", params={"date": tweet_date.isoformat()})

    except HTTPError:
        print(f"Cannot add Prompt for {tweet_date} to the database!")
    return True
