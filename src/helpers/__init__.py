from typing import Tuple

import tweepy

from src.core import config


__all__ = [
    "get_tweet_media",
    "get_tweet_text",
]


CONFIG = config.load()


def get_tweet_media(tweet: tweepy.models.Status) -> Tuple[str, None]:
    """Get the tweet's media if it exists."""
    media_url = ""
    tweet_media = None

    # If we have media in our tweet
    if hasattr(tweet, "extended_entities"):
        media = tweet.extended_entities.get("media")
        if media:
            # We only need a static image, and it's the same route
            # to get one regardless if the media is an image
            # or an "animated GIF"
            media_url = media[0]["url"]
            tweet_media = media[0]["media_url_https"]
    return (media_url, tweet_media)


def get_tweet_text(tweet: tweepy.models.Status, media_url: str) -> str:
    """Get the tweet's complete text."""
    # Because we're accessing "extended" tweets (> 140 chars),
    # we need to be sure to access the full_text property
    # that holds the non-truncated text
    return tweet.full_text.replace(media_url, "").strip()
