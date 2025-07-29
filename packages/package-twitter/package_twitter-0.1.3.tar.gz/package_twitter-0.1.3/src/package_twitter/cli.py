import argparse
import sys

from package_twitter import TwitterBot, tweet_now


def main():
    parser = argparse.ArgumentParser(
        description="Programmatically create tweets on Twitter."
    )
    parser.add_argument("tweet_text", type=str, help="The text content of your tweet.")
    args = parser.parse_args()

    try:
        # Using the convenience function
        tweet_now(args.tweet_text)
        # Or directly using the class:
        # bot = TwitterBot()
        # bot.post_tweet(args.tweet_text)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
