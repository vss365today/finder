import tweepy
import sys_vars


__all__ = ["twitter_v2_api"]


def twitter_v2_api() -> tweepy.Client:
    """Connect to Twitter API v2 using a Bearer token."""
    return tweepy.Client(bearer_token=sys_vars.get("TWITTER_BEARER"))
