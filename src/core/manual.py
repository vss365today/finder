from pprint import pprint
from typing import Optional
from urllib3.util.url import parse_url

from requests.exceptions import HTTPError

from src.helpers import (
    connect_to_twitter,
    find_prompt_word,
    get_tweet_media,
    get_tweet_text,
)
from src.helpers import api
from src.helpers.date import create_datetime


__all__ = ["main"]


def __get_tweet_id(url: str) -> Optional[str]:
    # Parse the URL into its components
    parsed = parse_url(url.strip())

    # This is not a Twitter URL or an individual tweet
    if "twitter.com" not in parsed.host and "status" not in parsed.path:
        return None

    # Break up the URL path and pull out the tweet id
    url_path = parsed.path.split("/")
    return url_path[3]


def main() -> bool:
    """Manually specify and record a Prompt."""
    # Get the tweet date and url info from the url
    tweet_date = input("Enter the Prompt date (YYYY-MM-DD): ")
    tweet_url = input("Enter the Prompt url: ")
    tweet_duplicate_date = input(
        "Has a Prompt already been recored for this day? (y/N) "
    ).strip()
    tweet_id = __get_tweet_id(tweet_url)

    # It's not a Twitter URL
    if not tweet_id:
        return False

    # Connect to the Twitter API to get the tweet itself
    twitter_api = connect_to_twitter()
    print("Successfully connected to the Twitter API")
    prompt_tweet = twitter_api.get_status(
        tweet_id, include_my_retweet=False, tweet_mode="extended"
    )

    # Extract the tweet content
    media_url, tweet_media = get_tweet_media(prompt_tweet)
    tweet_text = get_tweet_text(prompt_tweet, media_url)

    # Determine if this has been explictly marked as a duplicate Prompt
    is_duplicate_date = (
        tweet_duplicate_date.upper() == "Y" if tweet_duplicate_date else False
    )

    # Construct a tweet object
    prompt = {
        "id": tweet_id,
        "uid": prompt_tweet.author.id_str,
        "date": str(prompt_tweet.created_at),
        "word": find_prompt_word(tweet_text),
        "content": tweet_text,
        "media": tweet_media,
        "is_duplicate_date": is_duplicate_date,
    }
    pprint(prompt)

    try:
        # Add the tweet to the database
        print("Adding tweet to database")
        api.post("prompt", json=prompt)

        # Send the email broadcast
        print("Sending out notification emails")
        api.post("broadcast", params={"date": create_datetime(tweet_date)})

    except HTTPError:
        print(f"Cannot add prompt for {tweet_date} to the database!")
        return False
    return True
