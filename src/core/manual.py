from html import escape
from pprint import pprint
from typing import Optional
from urllib.parse import urlparse

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
    parsed = urlparse(url.strip())

    # This is not a Twitter URL
    if "twitter.com" not in parsed.netloc:
        return None

    # Break up the URL path and pull out the tweet id
    url_path = parsed.path.split("/")
    return url_path[3]


def main() -> bool:
    """Manually specify and record a Prompt."""
    # Get the tweet date and url info from the url
    tweet_date = input("Enter the tweet date (YYYY-MM-DD): ")
    tweet_url = input("Enter the tweet url: ")
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

    # Construct a tweet object
    prompt = {
        "id": tweet_id,
        "date": str(prompt_tweet.created_at),
        "uid": prompt_tweet.author.id_str,
        "content": escape(tweet_text),
        "word": find_prompt_word(tweet_text),
        "media": tweet_media,
    }
    pprint(prompt)

    try:
        # Add the tweet to the database
        print("Adding tweet to database")
        api.post("prompt", json=prompt)

        # Send the email broadcast
        print("Sending out notification emails")
        api.post(
            "subscription", "broadcast", params={"date": create_datetime(tweet_date)}
        )

    except HTTPError:
        print(f"Cannot add prompt for {tweet_date} to the database!")
        return False
    return True
