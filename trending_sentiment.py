from twikit import Client, Tweet
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables from the .env file
load_dotenv()

# tw_mail = os.environ.get('TW_MAIL')
# tw_pass = os.environ.get('TW_PASS')
# tw_username = os.environ.get('TW_USERNAME')

client = Client('en-US')
client.load_cookies("cookies.json")

# Define thresholds
followers_threshold = 1000
favourites_threshold = 10000

# Define weights
weight_favorite = 0.3
weight_retweet = 0.5
weight_reply = 0.2
weight_followers = 0.05
weight_favourites = 0.01
weight_verified = 15

# Define maximum possible scores based on the weights and reasonable assumptions
max_tweet_count = 30
max_favorite_score = 100 * weight_favorite  # Assuming a max of 100
max_retweet_score = 50 * weight_retweet  # Assuming a max of 50
max_reply_score = 30 * weight_reply  # Assuming a max of 30
max_followers_score = 100 * weight_followers  # Assuming a max of 100
max_favourites_score = 100000 * weight_favourites  # Assuming a max of 1000
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

    print("favorite_count", tweet.favorite_count)
    print("retweet_count", tweet.retweet_count)
    print("reply_count", tweet.reply_count)
    print("followers_count", tweet.user.followers_count)
    print("favourites_count", tweet.user.favourites_count)
    print("is_blue_verified", tweet.user.is_blue_verified)
    print("url", tweet.media)

    # Calculate the score
    return (
            (tweet.favorite_count * weight_favorite) +
            (tweet.retweet_count * weight_retweet) +
            (tweet.reply_count * weight_reply) +
            (tweet.user.followers_count * weight_followers) +
            (tweet.user.favourites_count * weight_favourites) +
            (tweet.user.is_blue_verified * weight_verified)
    )


def scale_score_to_range(score, max_score, target_range=(0, 100)):
    min_target, max_target = target_range
    scaled_score = ((score / max_score) * (max_target - min_target)) + min_target
    return int(min(round(scaled_score), max_target))


async def fetch_tweets_and_analyze(ticker: str):
    search_query = f"${ticker}"
    print("search_query", search_query)

    now = datetime.now()
    two_hours_ago = now - timedelta(hours=2)

    formatted_now = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    formatted_two_hours_ago = two_hours_ago.strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        tweets = client.search_tweet(
            '{} since:{} until:{} min_faves:10 min_retweets:5'.format(search_query, formatted_two_hours_ago,
                                                                      formatted_now), 'Top', 10)

        total_score = 0
        tweet_count = 0
        for tweet in tweets:
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
