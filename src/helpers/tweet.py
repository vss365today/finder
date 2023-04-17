from json import loads
from pathlib import Path
from typing import TypedDict

import sys_vars
import tweepy
from urllib3.util.url import Url, parse_url


__all__ = [
    "is_prompt_tweet",
    "fetch_fields",
    "get_id",
    "get_media",
    "get_prompt",
    "get_text",
    "is_url",
    "twitter_v2_api",
]


class Hashtags(TypedDict):
    start: int
    end: int
    tag: str


CONFIG = loads((Path("configuration") / "default.json").read_text())


def __filter_hashtags(hts: list[str]) -> list[str]:
    """Filter out any hashtags that should not be considered a prompt."""
    # This cannot use set math as it will change the order of the hashtags,
    # which makes it impossible to determine the prompt word
    return [ht for ht in hts if ht.lower() not in CONFIG["filter"]]


def __get_media_obj(tweet: tweepy.Response) -> dict | None:
    """Get the media object from the tweet."""
    # This tweet has no media in it
    if tweet.data.attachments is None:
        return None

    # Shortcut to the media (because it's pretty buried in the response)
    return tweet.includes["media"][0].data


def __extract_hashtags(tweet: tweepy.Tweet) -> list[str]:
    """Extract the hashtags from a tweet, if present."""
    # There are no entities (whatever that means) in this tweet at all
    if tweet.entities is None:
        return []

    # There are no hashtags in this tweet
    if "hashtags" not in tweet.entities:
        return []

    hts: list[Hashtags] = tweet.entities["hashtags"]
    return [ht["tag"] for ht in hts]


def is_prompt_tweet(hts: list[str]) -> bool:
    """Confirm this is the Prompt tweet."""
    # No hashtags were provided
    if not hts:
        return False

    # Make sure at least hashtags are present in the tweet AND
    # the prompt identifying hashtags are present (via subset set math)
    hts = [ht.lower() for ht in hts]
    return len(hts) >= 3 and set(CONFIG["identifiers"]) <= set(hts)


def fetch_fields() -> dict[str, list[str]]:
    """Specify the expansions and fields for needed information."""
    return {
        "expansions": ["attachments.media_keys", "author_id"],
        "tweet_fields": ["created_at", "entities"],
        "media_fields": ["alt_text", "preview_image_url", "url"],
    }


def get_id(url: str) -> str:
    """Confirm this is a tweet url and get its ID."""
    # Parse the URL into its components
    parsed: Url = parse_url(url.strip())

    # Break up the URL path and pull out the tweet id
    url_path = parsed.path.split("/")
    return url_path[3]


def get_media(tweet: tweepy.Response) -> str | None:
    """Get any media in the tweet."""
    if not (media := __get_media_obj(tweet)):
        return None

    # Single, still image
    if media["type"] == "photo":
        return media["url"]

    # Animated gif/video
    elif media["type"] in ("animated_gif", "video"):
        return media["preview_image_url"]
    return None


def get_media_alt_text(tweet: tweepy.Response) -> str | None:
    """Get the alt text for a tweet's media."""
    if media := __get_media_obj(tweet):
        return media.get("alt_text")
    return None


def get_prompt(tweet: tweepy.Response) -> str | None:
    """Get the prompt word from the tweet."""
    # Pull out any hashtags from the tweet
    hts = __extract_hashtags(tweet.data)

    # This is not the prompt tweet
    if not is_prompt_tweet(hts):
        return None

    # Remove any hashtags that cannot be prompt words
    hts = __filter_hashtags(hts)

    # According to the #vss365 charter, a Prompt must contain the hashtags
    # `#vss365 #prompt #[prompt]`, in that order. Confirm that those hashtags
    # are in that order and if they are, use that ordering to extract the word
    vss_idx = hts.index("vss365")
    try:
        if hts[vss_idx + 1].lower() != "prompt":
            return None
        return hts[vss_idx + 2]
    except (IndexError, ValueError):
        return None


def get_text(tweet: tweepy.Response) -> str:
    """Get the full tweet text."""
    return tweet.data.text


def is_url(url: str) -> bool:
    """Determine if this is a tweet URL."""
    url = url.lower()
    return "twitter.com/" in url and "/status/" in url


def twitter_v2_api() -> tweepy.Client:
    """Connect to Twitter API v2 using a Bearer token."""
    return tweepy.Client(bearer_token=sys_vars.get("TWITTER_BEARER"))
