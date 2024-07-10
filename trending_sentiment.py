import asyncio
import os

from twikit import Client, Tweet
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables from the .env file
load_dotenv()

# tw_mail = os.environ.get('TW_MAIL')
# tw_pass = os.environ.get('TW_PASS')
# tw_username = os.environ.get('TW_USERNAME')

client = Client('en-US')
# client.login(auth_info_1=tw_username, auth_info_2=tw_mail, password=tw_pass)
# client.save_cookies("cookies.json")
client.load_cookies("cookies.json")

# Define thresholds
followers_threshold = 1000
favourites_threshold = 10000

# Define weights
weight_favorite = 2
weight_retweet = 3
weight_reply = 5
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

print("max_favorite_score", max_favorite_score)
print("max_retweet_score", max_retweet_score)
print("max_reply_score", max_reply_score)
print("max_followers_score", max_followers_score)
print("max_favourites_score", max_favourites_score)
print("max_verified_score", max_verified_score)
print("max_tweet_count_weight", max_tweet_count_weight)

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
    print("url:", tweet.media)

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


async def fetch_tweets_and_analyze(ticker: str):
    search_query = f"${ticker}"
    print("search_query", search_query)

    now = datetime.now()
    yesterday = now - timedelta(days=1)

    formatted_yesterday = yesterday.strftime("%Y-%m-%d")

    try:
        print('{} since:{} min_retweets:5  min_faves:10'.format(search_query, formatted_yesterday))
        tweets = client.search_tweet(
            '{} since:{} min_retweets:5  min_faves:10'.format(search_query, formatted_yesterday), 'Top', 10)

        total_score = 0
        tweet_count = 0
        for tweet in tweets:
            print(tweet.full_text)
            if search_query not in tweet.full_text:
                continue
            sc = calculate_score(tweet)
            print("sc", sc)
            print("-----------------")
            total_score += sc
            tweet_count += 1

        more_tweets = tweets.next()  # Retrieve more tweets

        for tweet in more_tweets:
            if search_query not in tweet.full_text:
                continue
            sc = calculate_score(tweet)
            print("sc", sc)
            print("-----------------")
            total_score += sc
            tweet_count += 1

        much_more_tweets = more_tweets.next()  # Retrieve more tweets

        for tweet in much_more_tweets:
            if search_query not in tweet.full_text:
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
        return final_score

    except Exception as e:
        print(f"Error fetching tweets for {ticker}: {e}")

# asyncio.run(fetch_tweets_and_analyze("BOB"))
