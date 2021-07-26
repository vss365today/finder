from typing import NewType, Optional

import tweepy
import sys_vars

from src.core import config


__all__ = ["confirm_prompt", "get_prompt", "twitter_v1_api"]


CONFIG = config.load()


Hashtags = NewType("Hashtags", list[dict])


def __filter_hashtags(hts: list[str]) -> list[str]:
    """Filter out any hashtags that should not be considered a prompt."""
    return [ht for ht in hts if ht not in CONFIG["filter"]]


def __get_hashtags(hashtags: Hashtags) -> list[str]:
    """Extract all hashtags from the tweet."""
    return [ht["text"] for ht in hashtags]


def confirm_prompt(hts: Hashtags) -> bool:
    """Confirm this is the Prompt tweet."""
    return (
        len(hts) >= 3
        and hts[0]["text"] == CONFIG["identifiers"][0]
        and hts[1]["text"] == CONFIG["identifiers"][1]
    )


def get_prompt(tweet: tweepy.Status) -> Optional[str]:
    hts = Hashtags(tweet.entities["hashtags"])
    if not confirm_prompt(hts):
        return None
    return __filter_hashtags(__get_hashtags(hts))[CONFIG["prompt_index"] + 2]


def twitter_v1_api() -> tweepy.API:
    """Connect to Twitter API v1 using OAuth 2."""
    auth = tweepy.AppAuthHandler(
        sys_vars.get("TWITTER_CONSUMER_KEY"), sys_vars.get("TWITTER_CONSUMER_SECRET")
    )
    return tweepy.API(auth)
