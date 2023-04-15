from datetime import date

from requests.exceptions import HTTPError

from src.core.api import v2
from src.helpers import tweet


__all__ = ["main"]


def main() -> bool:
    """Manually specify and record a Prompt."""
    # Get the information we need
    tweet_date = date.fromisoformat(
        input("Enter the Prompt date (YYYY-MM-DD): ").strip()
    )
    tweet_url = input("Enter the Prompt url: ")
    tweet_duplicate_date = input(
        "Has a Prompt already been recorded for this day? (y/N) "
    ).strip()
    should_send_emails = input(
        "Should notification emails be sent for this Prompt? (y/N) "
    ).strip()
    should_generate_archive = input(
        "Should an archive spreadsheet be generated with this Prompt? (y/N) "
    ).strip()
    tweet_is_additional = tweet_duplicate_date.lower() == "y"

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
        "content": tweet.get_text(prompt_tweet),
        "date": tweet_date.isoformat(),
        "host_handle": prompt_tweet[1]["users"][0].username,
        "twitter_id": str(prompt_tweet.data.id),
        "word": tweet.get_prompt(prompt_tweet),
        "is_additional": tweet_is_additional,
    }

    # Pull out any possible media
    media_alt_text = tweet.get_media_alt_text(prompt_tweet)
    media_url = tweet.get_media(prompt_tweet)
    prompt_media = {}
    if media_url is not None:
        prompt_media = {"items": [{"alt_text": media_alt_text, "url": media_url}]}

    try:
        # Add the tweet to the database
        print("Adding Prompt to database...")
        r = v2.post("prompts/", json=prompt)

        # Create any media that is attached to the tweet
        if prompt_media:
            print("Recording Prompt Media...")
            prompt_id = r["_id"]
            v2.post("prompts", str(prompt_id), "media", json=prompt_media)

        # Send the email broadcast if desired
        if should_send_emails.lower() == "y":
            print("Sending out notification emails...")
            v2.post("notifications", tweet_date.date().isoformat())

        # Generate an archive file if desired
        if should_generate_archive.lower() == "y":
            # Handle if this is a newly recorded tweet
            print("Generating new archive spreadsheet...")
            v2.post("archive/")

    except HTTPError:
        print(f"Cannot add Prompt for {tweet_date} to the database!")
        return False
    return True
