# 🐦 Package-Twitter: Programmatic Tweeting with Python

![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)
[![PyPI version](https://img.shields.io/pypi/v/package-twitter.svg)](https://pypi.org/project/package-twitter/)
[![License](https://img.shields.io/github/license/Nivesh03/package-twitter.svg)](LICENSE)
[![Tests](https://github.com/Nivesh03/package-twitter/actions/workflows/main.yml/badge.svg)](https://github.com/Nivesh03/package-twitter/actions/workflows/main.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 📖 Table of Contents

- [🐦 Package-Twitter: Programmatic Tweeting with Python](#-package-twitter-programmatic-tweeting-with-python)
  - [📖 Table of Contents](#-table-of-contents)
  - [📖 About](#-about)
  - [✨ Features](#-features)
  - [🚀 Installation](#-installation)
  - [🔑 Twitter API Setup (Crucial!)](#-twitter-api-setup-crucial)
  - [🚀 Quick Start](#-quick-start)
    - [Using the Command-Line Interface (CLI)](#using-the-command-line-interface-cli)
    - [Using Programmatically in Python](#using-programmatically-in-python)
  - [📄 License](#-license)
  - [👤 Author](#-author)

---

## 📖 About

`Package-Twitter` is a lightweight Python package designed to simplify programmatic tweeting on Twitter (now X). It provides a user-friendly command-line interface (CLI) for quick tweets and a robust Python API for integration into larger applications, bots, or automated workflows. Built on top of `tweepy`, it offers a straightforward way to interact with the Twitter API v2.

## ✨ Features

* **Simple CLI:** Post tweets directly from your terminal.
* **Pythonic API:** Easily integrate tweeting functionality into your Python applications.
* **Secure Credential Handling:** Utilizes environment variables to keep your sensitive API keys out of your codebase.
* **Robust Error Handling:** Provides clear feedback on common Twitter API issues.

## 🚀 Installation

You can install `Package-Twitter` directly from PyPI:

```bash
pip install package-twitter
```

NOTE: `package-twitter` supports python versions 3.11 or later.

## 🔑 Twitter API Setup (Crucial!)
To use `package-twitter`, you must obtain Twitter API credentials from the Twitter Developer Portal.

* **Apply for a Developer Account:** If you don't have one, apply and explain your use case.

* **Create a Project and App:** Once approved, create a new project and then an app within it.

* **Generate API Keys and Tokens:** For this app, you will need:

  * `Consumer Key (API Key)`
  * `Consumer Secret (API Secret Key)`
  * `Access Token`
  * `Access Token Secret`
  
* **Enable "Read and Write" Permissions:** Crucially, ensure your app's permissions are set to "Read and Write" in the Developer Portal. Without write permissions, you won't be able to post tweets.

* **Set Environment Variables:** Create a new python environment or activate a already created environment with python version >=3.11. Then install `package-twitter` in this environment. Set the API keys as environment variables using the following methods.

  * **Using `python-dotenv`**
    * Create a `.env` file
  
        Create a new file named `.env`. This file contains key-value pairs of environment variables. Make sure to provide the following names to the keys. Copy these values and change the placeholders with actual keys.
        ``` bash
        TWITTER_CONSUMER_KEY="your_consumer_key_here"
        TWITTER_CONSUMER_SECRET="your_consumer_secret_here"
        TWITTER_ACCESS_TOKEN="your_access_token_here"
        TWITTER_ACCESS_TOKEN_SECRET="your_access_token_secret_here"
        ```
    * Install the `python-dotenv` package

        `python-dotenv` reads key-value pairs from a `.env` file and can set them as environment variables.
        ```bash
        pip install python-dotenv
        ```
    * Load `.env` values in your Python code

        Once the `python-dotenv` package is installed and the `.env` file has been created, use the dotenv module along with os.environ to load them into the environment:

        ```python
        from dotenv import load_dotenv
        import os
        
        # Load environment variables from .env file
        load_dotenv()
        ```
  * **Using `shell`**

    Add these lines to your shell's configuration file (e.g., ~/.bashrc, ~/.zshrc, ~/.profile for macOS/Linux, or system environment variables for Windows) for persistence.

    ```bash
    export TWITTER_CONSUMER_KEY="your_consumer_key_here"
    export TWITTER_CONSUMER_SECRET="your_consumer_secret_here"
    export TWITTER_ACCESS_TOKEN="your_access_token_here"
    export TWITTER_ACCESS_TOKEN_SECRET="your_access_token_secret_here"
    ```
    Remember to replace the placeholder values with your actual keys and tokens.

## 🚀 Quick Start
Once installed and your environment variables are set, you can start tweeting!

### Using the Command-Line Interface (CLI)
---
The package provides a tweet command for quick usage:

```bash
tweet "Hello Twitter! This tweet was sent using the Package-Twitter CLI."
```
If you installed from source using Poetry, make sure you're in the project directory and inside the Poetry shell:

```bash
cd /path/to/your/package-twitter
poetry shell
tweet "Another tweet via Poetry shell!"
```
### Using Programmatically in Python
---
You can import TwitterBot or tweet_now into your Python scripts:

```python
# my_awesome_bot.py
from package_twitter import TwitterBot, tweet_now
import sys

def post_my_tweet():
    try:
        # Option 1: Using the TwitterBot class directly
        bot = TwitterBot()
        tweet_text_class = "This is a tweet posted using the TwitterBot class directly in Python. #Automation"
        print(f"Attempting to post (class): '{tweet_text_class}'")
        response_class = bot.post_tweet(tweet_text_class)
        if response_class:
            print(f"Tweet posted! ID: {response_class.get('id')}")

        # Option 2: Using the convenience function
        tweet_text_func = "This is another tweet posted using the package_twitter.tweet_now() function. #PythonDev"
        print(f"Attempting to post (function): '{tweet_text_func}'")
        response_func = tweet_now(tweet_text_func)
        if response_func:
            print(f"Tweet posted! ID: {response_func.get('id')}")

    except ValueError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    post_my_tweet()
```

To run this script:

```bash
py my_awesome_bot.py
```

## 📄 License
This project is licensed under the MIT License - see the [LICENCE](LICENSE) file for details.

## 👤 Author
Github Profile: [Nivesh03](https://github.com/Nivesh03)

Email: niveshsharma67@gmail.com