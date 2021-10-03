from collections import namedtuple
from typing import Optional

import sys_vars
import tweepy
from urllib3.util.url import parse_url

from src.core import config


__all__ = [
    "confirm_prompt",
    "fetch_fields",
    "get_id",
    "get_media",
    "get_prompt",
    "get_text",
    "is_url",
    "twitter_v2_api",
]


CONFIG = config.load()


def __filter_hashtags(hts: set[str]) -> list[str]:
    """Filter out any hashtags that should not be considered a prompt."""
    return list(hts - set(CONFIG["filter"]))


def __get_hashtags(hts: list[dict]) -> set[str]:
    """Extract all hashtags from the tweet."""
    return set(ht["tag"] for ht in hts)


def __get_media_obj(tweet: namedtuple) -> Optional[dict]:
    """Get the media object from the tweet."""
    # This tweet has no media in it
    if tweet.data.attachments is None:
        return None

    # Shortcut to the media (because it's pretty buried in the response)
    return tweet.includes["media"][0].data


def confirm_prompt(tweet: namedtuple) -> bool:
    """Confirm this is the Prompt tweet."""
    hts = tweet.data.get("entities", {}).get("hashtags")
    hts = __get_hashtags(hts)
    return hts is not None and len(hts) >= 3 and set(CONFIG["identifiers"]) <= set(hts)


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
    parsed = parse_url(url.strip())

    # Break up the URL path and pull out the tweet id
    url_path = parsed.path.split("/")
    return url_path[3]


def get_media(tweet: namedtuple) -> Optional[str]:
    """Get any media in the tweet."""
    if not (media := __get_media_obj(tweet)):
        return None

    # Single, still image
    if media["type"] == "photo":
        return media["url"]

    # Animated gif/video
    elif media["type"] in ("animated_gif", "video"):
        return media["preview_image_url"]


def get_media_alt_text(tweet: namedtuple) -> Optional[str]:
    """Get the alt text for a tweet's media."""
    if media := __get_media_obj(tweet):
        return media.get("alt_text")
    return None


def get_prompt(tweet: namedtuple) -> Optional[str]:
    """Get the prompt word from the tweet."""
    if not confirm_prompt(tweet):
        return None

    hts = tweet.data.entities["hashtags"]
    hts = __filter_hashtags(__get_hashtags(hts))
    return hts[CONFIG["prompt_index"]]


def get_text(tweet: namedtuple) -> str:
    """Get the full tweet text."""
    return tweet.data.text


def is_url(url: str) -> bool:
    """Determine if this is a tweet URL."""
    url = url.lower()
    return "twitter.com/" in url and "/status/" in url


def twitter_v2_api() -> tweepy.Client:
    """Connect to Twitter API v2 using a Bearer token."""
    return tweepy.Client(bearer_token=sys_vars.get("TWITTER_BEARER"))
