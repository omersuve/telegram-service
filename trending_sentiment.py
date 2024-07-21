import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from twikit import Client, Tweet, TooManyRequests
from discord_message import send_error_log_to_discord

# Load environment variables from the .env file
load_dotenv()

# Define credentials for multiple accounts
accounts = [
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

current_account_index = 0

client = Client('en-US')


def login_and_save_cookies(account):
    client.login(
        auth_info_1=account['username'],
        auth_info_2=account['email'],
        password=account['password']
    )
    client.save_cookies(account['cookie_file'])
    print(f"Logged in and saved new cookies for {account['username']}.")


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

print("max_total_score", max_total_score)


def calculate_score(tweet: Tweet):
    if tweet.user.followers_count < followers_threshold or tweet.user.favourites_count < favourites_threshold:
        return 0

    favorite_score = tweet.favorite_count * weight_favorite
    retweet_score = tweet.retweet_count * weight_retweet
    reply_score = tweet.reply_count * weight_reply
    followers_score = tweet.user.followers_count * weight_followers
    favourites_score = tweet.user.favourites_count * weight_favourites
    verified_score = tweet.user.is_blue_verified * weight_verified

    print("favorite_count:", tweet.favorite_count, "-> favorite_score:", favorite_score)
    print("retweet_count:", tweet.retweet_count, "-> retweet_score:", retweet_score)
    print("reply_count:", tweet.reply_count, "-> reply_score:", reply_score)
    print("followers_count:", tweet.user.followers_count, "-> followers_score:", followers_score)
    print("favourites_count:", tweet.user.favourites_count, "-> favourites_score:", favourites_score)
    print("is_blue_verified:", tweet.user.is_blue_verified, "-> verified_score:", verified_score)

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


async def fetch_tweets_and_analyze(ticker: str, retries=1):
    global current_account_index
    account = accounts[current_account_index]

    # Load cookies for the current account
    client.load_cookies(account['cookie_file'])
    print(f"Cookies loaded successfully for {account['username']}.")

    search_query = f"${ticker}"
    print("search_query", search_query)

    now = datetime.now()
    yesterday = now - timedelta(days=1)

    formatted_yesterday = yesterday.strftime("%Y-%m-%d")

    try:
        print('{} since:{} min_retweets:2  min_faves:5'.format(search_query, formatted_yesterday))
        tweets = client.search_tweet(
            '{} since:{} min_retweets:2  min_faves:5'.format(search_query, formatted_yesterday), 'Top', 10)

        total_score = 0
        tweet_count = 0
        for tweet in tweets:
            print(tweet.full_text)
            if ticker.lower() not in tweet.full_text.lower():
                continue
            sc = calculate_score(tweet)
            print("sc", sc)
            print("-----------------")
            total_score += sc
            tweet_count += 1

        more_tweets = tweets.next()  # Retrieve more tweets

        for tweet in more_tweets:
            if ticker.lower() not in tweet.full_text.lower():
                continue
            sc = calculate_score(tweet)
            print("sc", sc)
            print("-----------------")
            total_score += sc
            tweet_count += 1

        much_more_tweets = more_tweets.next()  # Retrieve more tweets

        for tweet in much_more_tweets:
            if ticker.lower() not in tweet.full_text.lower():
                continue
            sc = calculate_score(tweet)
            print("sc", sc)
            print("-----------------")
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

        # Handle authentication error by logging in and saving new cookies
        if 'Could not authenticate you' in str(err) and retries > 0:
            print(f"Re-logging in for {account['username']} due to authentication error.")
            await send_error_log_to_discord(f"Re-logging in for {account['username']} due to authentication error.")
            login_and_save_cookies(account)
            return await fetch_tweets_and_analyze(ticker, retries - 1)
        else:
            print(str(err))
            await send_error_log_to_discord(str(err))
        current_account_index = (current_account_index + 1) % len(accounts)
        return await fetch_tweets_and_analyze(ticker)

# asyncio.run(fetch_tweets_and_analyze("BTC"))
