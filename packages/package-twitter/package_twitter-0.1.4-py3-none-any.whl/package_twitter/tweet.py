import os

import tweepy


class TwitterBot:

    def __init__(self):
        # Load credentials from environment variables
        self.consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
        self.consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

        if not all(
            [
                self.consumer_key,
                self.consumer_secret,
                self.access_token,
                self.access_token_secret,
            ]
        ):
            raise ValueError(
                "Twitter API credentials not found in environment variables. "
                "Please set TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, "
                "TWITTER_ACCESS_TOKEN, and TWITTER_ACCESS_TOKEN_SECRET."
            )

        # Authenticate with Twitter API v2 (recommended by Twitter)
        self.client = tweepy.Client(
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
        )

    def post_tweet(self, text: str) -> dict:
        """
        Posts a tweet to Twitter.

        Args:
            text: The text content of the tweet.

        Returns:
            A dictionary containing information about the posted tweet.
            Raises a tweepy.TweepyException on API errors.
        """
        if not text:
            raise ValueError("Tweet text cannot be empty.")
        if len(text) > 280:
            raise ValueError(f"Tweet text exceeds 280 characters ({len(text)}).")

        try:
            response = self.client.create_tweet(text=text)
            if response.data:
                print(f"Tweet posted successfully! ID: {response.data['id']}")
                print(f"Text: {response.data['text']}")
            else:
                print("Tweet failed with no data in response.")
            return response.data
        except tweepy.TweepyException as e:
            print(f"Error posting tweet: {e}")
            raise  # Re-raise the exception to be handled by the caller


# You might want to expose a simple function from __init__.py
# src/twitter_bot_cli/__init__.py:
from .tweet import TwitterBot


# Optional: if you want to expose a direct function for convenience
def tweet_now(text: str):
    """
    Convenience function to post a tweet directly.
    Initializes TwitterBot internally.
    """
    bot = TwitterBot()
    return bot.post_tweet(text)
