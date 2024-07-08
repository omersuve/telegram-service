import os
import logging
import asyncio
from twikit import Client
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from dotenv import load_dotenv
from datetime import datetime, timedelta

# # Load environment variables from the .env file
load_dotenv()

# nltk.downloader.download('vader_lexicon')
vader = SentimentIntensityAnalyzer()

# tw_mail = os.environ.get('TW_MAIL')
# tw_pass = os.environ.get('TW_PASS')
# tw_username = os.environ.get('TW_USERNAME')

client = Client('en-US')
client.load_cookies("cookies.json")


def get_score(ticker_news: str) -> float:
    return vader.polarity_scores(ticker_news)['compound']


async def fetch_tweets_and_analyze(ticker: str):
    search_query = f"${ticker}"
    logging.info(f"Searching for tweets with query: {search_query}")

    now = datetime.utcnow()
    two_hours_ago = now - timedelta(hours=2)

    formatted_now = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    formatted_two_hours_ago = two_hours_ago.strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        tweets = client.search_tweet(
            '{} since:{} until:{} min_faves:20 min_retweets:10'.format(search_query, formatted_two_hours_ago,
                                                                       formatted_now), 'Top', 5)
        logging.info(f"Found {len(tweets)} tweets for ticker ${ticker}")

        total_score = 0
        for tweet in tweets:
            print(tweet.text)
            total_score = total_score + get_score(tweet.text)

        tweets.next()

        print("total_score", total_score)
        return total_score

    except Exception as e:
        logging.error(f"Error fetching tweets for {ticker}: {e}")


asyncio.run(fetch_tweets_and_analyze("BTC"))
