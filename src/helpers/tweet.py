from typing import NewType, Optional

from tweepy import Status

from src.core import config


__all__ = ["confirm_prompt", "get_prompt"]


CONFIG = config.load()


Hashtags = NewType("Hashtags", list[dict])


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


def get_prompt(tweet: Status) -> Optional[str]:
    hts = Hashtags(tweet.entities["hashtags"])
    if not confirm_prompt(hts):
        return None
    return __get_hashtags(hts)[2]
