from argparse import Namespace
from contextlib import suppress
from datetime import date

from httpx import HTTPError, RemoteProtocolError

from src.core.api import v2

__all__ = ["main"]


def main(_: Namespace) -> bool:
    # Cutoff date
    if date.today() >= date(2024, 1, 1):
        print("Today is on or after January 1, 2024. Refusing to run.")
        return True

    # Ask for the prompt date
    prompt_date = date.fromisoformat(
        input("Enter the Prompt date (YYYY-MM-DD): ").strip()
    )

    try:
        # Fetch all Prompts for this date
        available_prompts = v2.get("prompts", "date", prompt_date.isoformat())

        # By default, select the first/latest Prompt
        prompt_index = -1

        # There's > 1 recorded Prompt for the day. Ask which should be sent out
        num_of_prompts = len(available_prompts)
        if num_of_prompts >= 2:
            print(
                f"\nThere are {num_of_prompts} Prompts for {prompt_date}.",
                "Which would you like to send a notification for?",
            )
            for i, prompt in enumerate(available_prompts):
                print(f"[{i + 1}] {prompt['word']}")

            # Ask for a prompt until we get a valid selection
            while True:
                selected_prompt = input("> ")

                # Make sure we have a number input and it's within range
                # This check has the advantage of automatically disallowing
                # a negative index
                if (
                    not selected_prompt.isnumeric()
                    or int(selected_prompt) > num_of_prompts
                ):
                    print("Please enter a prompt number")
                    continue
                break

            # Properly index the selected Prompt
            prompt_index = int(selected_prompt) - 1

        # Send the email broadcast.
        # For some reason, this exception keeps getting raised
        # despite the emails actually sending out, so suppress it
        with suppress(RemoteProtocolError):
            v2.post(
                "notifications",
                prompt_date.isoformat(),
                params={"which": prompt_index},
            )
        print(f"Email broadcast for {prompt_date} successfully sent")
        return True

    # A broadcast for that day couldn't be sent
    except HTTPError as exc:
        print(f"Unable to send email broadcast for {prompt_date}!")
        print(f"{exc.__class__.__name__}: {exc}")
    return False
