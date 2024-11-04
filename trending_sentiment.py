import asyncio
import os
from os.path import exists
import random
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta
from twikit import Client, Tweet
from discord_message import send_error_log_to_discord

# Load environment variables from the .env file
load_dotenv()

# Define credentials for multiple accounts
accounts = [
    {
        'username': os.environ.get('TW_USERNAME_6'),
        'email': os.environ.get('TW_MAIL_6'),
        'password': os.environ.get('TW_PASS_6'),
        'cookie_file': 'cookies6.json'
    },
    {
        'username': os.environ.get('TW_USERNAME'),
        'email': os.environ.get('TW_MAIL'),
        'password': os.environ.get('TW_PASS'),
        'cookie_file': 'cookies1.json'
    },
    {
        'username': os.environ.get('TW_USERNAME_2'),
        'email': os.environ.get('TW_MAIL_2'),
        'password': os.environ.get('TW_PASS_2'),
        'cookie_file': 'cookies2.json'
    },
    {
        'username': os.environ.get('TW_USERNAME_3'),
        'email': os.environ.get('TW_MAIL_3'),
        'password': os.environ.get('TW_PASS_3'),
        'cookie_file': 'cookies3.json'
    },
    {
        'username': os.environ.get('TW_USERNAME_4'),
        'email': os.environ.get('TW_MAIL_4'),
        'password': os.environ.get('TW_PASS_4'),
        'cookie_file': 'cookies4.json'
    },
    {
        'username': os.environ.get('TW_USERNAME_5'),
        'email': os.environ.get('TW_MAIL_5'),
        'password': os.environ.get('TW_PASS_5'),
        'cookie_file': 'cookies5.json'
    }
]

max_account_attempts = len(accounts)  # Track the number of total accounts tried

# Variable to track the index of the last used template
last_template_index = -1

current_account_index = 0

client = Client('en-US')


async def login_and_save_cookies(account):
    """Login and save cookies for the account."""
    try:
        await client.login(
            auth_info_1=account['username'],
            auth_info_2=account['email'],
            password=account['password']
        )
        client.save_cookies(account['cookie_file'])
        print(f"Logged in and saved new cookies for {account['username']}.")
    except Exception as e:
        print(f"Failed to log in for {account['username']}: {str(e)}")
        await send_error_log_to_discord(f"Failed to log in for {account['username']}: {str(e)}")
        return False
    return True


async def load_cookies(account):
    """Load cookies, or login if they don't exist."""
    if not exists(account['cookie_file']):
        print(f"Cookie file {account['cookie_file']} does not exist. Attempting login.")
        success = await login_and_save_cookies(account)
        if not success:
            return False  # Return False if login fails
    else:
        try:
            client.load_cookies(account['cookie_file'])
            print(f"Cookies loaded successfully for {account['username']}.")
        except Exception as e:
            print(f"Failed to load cookies for {account['username']}: {str(e)}")
            return False  # Return False if loading cookies fails
    return True


# Define thresholds
followers_threshold = 1000
favourites_threshold = 10000

# Define weights
weight_favorite = 2
weight_retweet = 5
weight_reply = 8
weight_followers = 0.01
weight_favourites = 0.005
weight_verified = 15

# Define maximum possible scores based on the weights and reasonable assumptions
max_tweet_count = 30
max_favorite_score = 150 * weight_favorite  # Assuming a max of 100
max_retweet_score = 100 * weight_retweet  # Assuming a max of 50
max_reply_score = 50 * weight_reply  # Assuming a max of 30
max_followers_score = 100000 * weight_followers  # Assuming a max of 100
max_favourites_score = 300000 * weight_favourites  # Assuming a max of 1000
max_verified_score = weight_verified * max_tweet_count  # Fixed value for verified users
max_tweet_count_weight = 1 + (max_tweet_count / 30)  # Max of 30 tweets

# print("max_favorite_score", max_favorite_score)
# print("max_retweet_score", max_retweet_score)
# print("max_reply_score", max_reply_score)
# print("max_followers_score", max_followers_score)
# print("max_favourites_score", max_favourites_score)
# print("max_verified_score", max_verified_score)
# print("max_tweet_count_weight", max_tweet_count_weight)

# Calculate the total maximum possible score
max_total_score = (
                          max_favorite_score +
                          max_retweet_score +
                          max_reply_score +
                          max_followers_score +
                          max_favourites_score +
                          max_verified_score
                  ) * max_tweet_count_weight


def calculate_score(tweet: Tweet):
    if tweet.user.followers_count < followers_threshold or tweet.user.favourites_count < favourites_threshold:
        return 0

    favorite_score = tweet.favorite_count * weight_favorite
    retweet_score = tweet.retweet_count * weight_retweet
    reply_score = tweet.reply_count * weight_reply
    followers_score = tweet.user.followers_count * weight_followers
    favourites_score = tweet.user.favourites_count * weight_favourites
    verified_score = tweet.user.is_blue_verified * weight_verified

    return (
            favorite_score +
            retweet_score +
            reply_score +
            followers_score +
            favourites_score +
            verified_score
    )


def scale_score_to_range(score, max_score, target_range=(0, 100)):
    min_target, max_target = target_range
    scaled_score = ((score / max_score) * (max_target - min_target)) + min_target
    return int(min(round(scaled_score), max_target))


def generate_tweet_content(ticker, token_address, dexscreener_url, telegram_url, blink_url):
    global last_template_index

    templates = [
        f"🚀 Trending Alert: {ticker} is on the rise! 💹\n\n📄 Contract: {token_address}\n📊 Check the chart: {dexscreener_url}\n💬 Join the chat: {telegram_url}\n\n{blink_url}",
        f"🌟 {ticker} just made waves! 🌊\n\n🔍 View contract: {token_address}\n📈 Chart it out: {dexscreener_url}\n👥 Telegram: {telegram_url}\n\n{blink_url}",
        f"🔥 Hot New Trend: {ticker}! 🚀\n\n📄 Contract Address: {token_address}\n📊 View chart: {dexscreener_url}\n💬 Telegram Group: {telegram_url}\n\n{blink_url}",
        f"🚨 Attention! {ticker} is gaining traction! 📈\n\n🔗 Contract: {token_address}\n📉 See the latest chart: {dexscreener_url}\n🗨️ Connect on Telegram: {telegram_url}\n\n{blink_url}",
        f"⚡️ {ticker} is trending now! ⚡️\n\n📜 Contract Info: {token_address}\n📊 Dive into the chart: {dexscreener_url}\n📣 Join the community: {telegram_url}\n\n{blink_url}",
        f"🚀 {ticker} is surging up the charts! 📈\n\n🔎 Contract: {token_address}\n📊 Check the performance: {dexscreener_url}\n💬 Join the conversation: {telegram_url}\n\n{blink_url}",
        f"🌐 Big Moves Alert: {ticker} is catching eyes! 👀\n\n📝 Contract Details: {token_address}\n📈 Analyze the chart: {dexscreener_url}\n🔊 Chat with the community: {telegram_url}\n\n{blink_url}",
        f"🔥 {ticker} is on fire! 🔥\n\n📝 Contract: {token_address}\n📊 Explore the chart: {dexscreener_url}\n👥 Join the discussion: {telegram_url}\n\n{blink_url}",
        f"⚠️ Trending Token: {ticker} is making headlines! 📈\n\n🔗 Contract Address: {token_address}\n📉 See the latest data: {dexscreener_url}\n💬 Connect on Telegram: {telegram_url}\n\n{blink_url}"
    ]

    # Generate a list of indices excluding the last used template
    available_indices = [i for i in range(len(templates)) if i != last_template_index]

    # Select a random index from the available options
    selected_index = random.choice(available_indices)

    # Update the last used template index
    last_template_index = selected_index

    # Return the selected template
    return templates[selected_index]


async def post_twitter(message_json):
    # Perform the synchronous POST request using requests
    try:
        response = requests.post(
            url="http://blinks-python.railway.internal:5001/post_tweet",
            json=message_json,
            timeout=20  # Set a timeout for the request
        )
        # Print the response from the server
        print(response.json())
    except requests.exceptions.RequestException as e:
        # Handle any exceptions (e.g., connection errors, timeouts)
        print(f"Failed to post the message to Twitter: {e}")


async def fetch_tweets_and_analyze(ticker: str, attempts=0):
    global current_account_index
    account = accounts[current_account_index]

    if attempts >= max_account_attempts:
        print(f"All accounts have been attempted. Stopping after {attempts} attempts.")
        return None  # You can return an error or log that all accounts failed.

    # Try to load cookies for the current account
    success = await load_cookies(account)
    if not success:
        print(f"Moving to next account due to cookie issue for {account['username']}.")
        current_account_index = (current_account_index + 1) % len(accounts)  # Move to next account
        return await fetch_tweets_and_analyze(ticker, attempts + 1)

    search_query = f"{ticker}"
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    formatted_yesterday = yesterday.strftime("%Y-%m-%d")

    try:
        print('{} since:{} min_retweets:2  min_faves:5'.format(search_query, formatted_yesterday))
        tweets = await client.search_tweet(
            '{} since:{} min_retweets:2  min_faves:5'.format(search_query, formatted_yesterday), 'Top', 10)

        total_score = 0
        tweet_count = 0

        for tweet in tweets:
            if ticker.lower() not in tweet.full_text.lower():
                continue
            sc = calculate_score(tweet)
            total_score += sc
            tweet_count += 1

        more_tweets = await tweets.next()  # Retrieve more tweets

        for tweet in more_tweets:
            if ticker.lower() not in tweet.full_text.lower():
                continue
            sc = calculate_score(tweet)
            total_score += sc
            tweet_count += 1

        much_more_tweets = await more_tweets.next()  # Retrieve more tweets

        for tweet in much_more_tweets:
            if ticker.lower() not in tweet.full_text.lower():
                continue
            sc = calculate_score(tweet)
            total_score += sc
            tweet_count += 1

        print("Found {} tweets".format(tweet_count))

        # Apply tweet count weight with increased importance
        weight_multiplier = 1 + (tweet_count / 20)
        weighted_score = total_score * weight_multiplier

        # Scale the score to a more meaningful range and cap it at the maximum target value
        print("weighted_score", weighted_score)
        final_score = scale_score_to_range(weighted_score, max_total_score)

        print("total_score", final_score)
        # Move to the next account for the next request
        current_account_index = (current_account_index + 1) % len(accounts)

        return final_score

    except Exception as err:
        print(f"Error fetching tweets for {ticker}: {err}")
        # Handle "Could not authenticate you" error by re-logging in
        if 'Could not authenticate you' in str(err):
            print(f"Re-logging in for {account['username']} due to authentication error.")
            await send_error_log_to_discord(f"Re-logging in for {account['username']} due to authentication error.")
            try:
                await login_and_save_cookies(account)  # Attempt to log in again
                return await fetch_tweets_and_analyze(ticker, attempts)  # Retry after login
            except Exception as login_err:
                # Handle login errors (e.g., "LoginFlow" error) and move to the next account
                if 'LoginFlow' in str(login_err):
                    print(f"LoginFlow error encountered for {account['username']}. Switching to next account.")
                    await send_error_log_to_discord(
                        f"LoginFlow error for {account['username']}. Moving to next account.")
                    current_account_index = (current_account_index + 1) % len(accounts)  # Move to next account
                    return await fetch_tweets_and_analyze(ticker, attempts + 1)
        else:
            print(f"Error: {str(err)}")
            await send_error_log_to_discord(f"Error fetching tweets for {ticker}: {str(err)}")
            # Move to next account
            current_account_index = (current_account_index + 1) % len(accounts)
            return await fetch_tweets_and_analyze(ticker, attempts + 1)

# asyncio.run(fetch_tweets_and_analyze("BTC"))
