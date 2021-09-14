from pprint import pprint

from requests.exceptions import HTTPError

from src.helpers import api, tweet
from src.helpers.date import create_datetime


__all__ = ["main"]


def main() -> bool:
    """Manually specify and record a Prompt."""
    # Get the information we need
    tweet_date = create_datetime(input("Enter the Prompt date (YYYY-MM-DD): "))
    tweet_url = input("Enter the Prompt url: ")
    tweet_duplicate_date = input(
        "Has a Prompt already been recorded for this day? (y/N) "
    ).strip()
    should_send_emails = input(
        "Should notification emails be sent for this Prompt? (y/N) "
    ).strip()

    # It's not a Twitter URL
    if not tweet.is_url(tweet_url):
        return False

    # Connect to the Twitter API to get the prompt tweet
    twitter_api = tweet.twitter_v2_api()
    print("Successfully connected to the Twitter API")
    prompt_tweet = twitter_api.get_tweet(
        tweet.get_id(tweet_url), **tweet.fetch_fields()
    )

    # Construct an API request object
    prompt = {
        "id": str(prompt_tweet.data.id),
        "uid": str(prompt_tweet.data.author_id),
        "date": tweet_date.isoformat(),
        "word": tweet.get_prompt(prompt_tweet),
        "content": tweet.get_text(prompt_tweet),
        "media": tweet.get_media(prompt_tweet),
        "media_alt_text": tweet.get_media_alt_text(prompt_tweet),
        "is_duplicate_date": tweet_duplicate_date.lower() == "y",
    }
    pprint(prompt)

    try:
        # Add the tweet to the database
        print("Adding Prompt to database")
        api.post("prompt/", json=prompt)

        # Send the email broadcast if desired
        if should_send_emails.lower() == "y":
            print("Sending out notification emails")
            api.post("broadcast/", params={"date": tweet_date})

    except HTTPError:
        print(f"Cannot add Prompt for {tweet_date} to the database!")
        return False
    return True
