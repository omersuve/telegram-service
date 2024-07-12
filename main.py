import asyncio
import json
import os
import re
import pusher
import redis.asyncio as redis
from dotenv import load_dotenv
from telethon import TelegramClient, events
from discord_message import start_discord_bot, stop_discord_bot, send_message_to_discord
from trending_sentiment import fetch_tweets_and_analyze
from rugcheck import get_rugcheck_report
import schedule
import time

# Load environment variables from .env file
load_dotenv()

api_id = int(os.environ.get("TELETHON_API_ID"))
api_hash = os.environ.get("TELETHON_API_HASH")

chat = 'dexscreener_trendings'
# chat = 'maomaomaocat'

# Use 'session_name' for the session file
client_telegram = TelegramClient("session_name", api_id, api_hash)

# Connect to Redis
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(redis_url)

# Initialize Pusher
pusher_client = pusher.Pusher(
    app_id=os.environ.get("PUSHER_APP_ID"),
    key=os.environ.get("PUSHER_KEY"),
    secret=os.environ.get("PUSHER_SECRET"),
    cluster=os.environ.get("PUSHER_CLUSTER"),
    ssl=True
)


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


@client_telegram.on(events.NewMessage(chats=chat))
async def handler(event):
    message = event.message
    try:
        # Extract ticker symbol using regex
        match = re.search(r'Token: \$(\w+)', message.text)
        if match:
            ticker = match.group(1)
            print(f"Extracted ticker: {ticker}")

            print("message", message)

            # Extract token address using regex from Dexscreener URL
            address_match = re.search(r'dexscreener.com/solana/([a-zA-Z0-9]+)', message.text)
            token_address = address_match.group(1) if address_match else None

            rugcheck_data = None

            if token_address:
                print(f"Extracted token address: {token_address}")

                # Fetch RugCheck report
                rugcheck_report = get_rugcheck_report(token_address)
                if rugcheck_report:
                    rugcheck_data = {
                        "risks": rugcheck_report.get("risks"),
                        "totalLPProviders": rugcheck_report.get("totalLPProviders"),
                        "totalMarketLiquidity": rugcheck_report.get("totalMarketLiquidity")
                    }

            # Fetch Twitter sentiment score
            score = await fetch_tweets_and_analyze(ticker)

            data = {
                "text": message.text,
                "date": message.date.isoformat(),
                "score": score,
                "rugcheck": rugcheck_data  # Possibly None
            }
            print(data)

            await redis_client.lpush("latest_messages", json.dumps(data))
            await redis_client.ltrim("latest_messages", 0, 9)

            print("redis pushed and trimmed")

            pusher_client.trigger("my-channel", "my-event", {"message": json.dumps(data)})
            print("Message published successfully")

            # Send message to Discord
            await send_message_to_discord(json.dumps(data))

            # Start the Twitter sentiment analysis and schedule it to run every hour for total 4 times
            async def run_analysis():
                for _ in range(3):
                    await asyncio.sleep(5400)  # Wait for 1.5 hour
                    new_score = await fetch_tweets_and_analyze(ticker)
                    await send_message_to_discord(ticker + ": " + str(new_score))  # DELETE LATER!

            await asyncio.create_task(run_analysis())

    except Exception as err:
        print(f"Failed to sending message to Redis: {err}")


async def start_telegram_client():
    await client_telegram.connect()
    print("Telegram client connected successfully")
    await client_telegram.run_until_disconnected()


async def main():
    try:
        # Start the Discord bot and Telegram client concurrently
        await asyncio.gather(
            start_discord_bot(),
            start_telegram_client()
        )
    except Exception as e:
        print(f"Error in Telegram client: {e}")
    finally:
        # Stop the Discord bot if the Telegram client disconnects
        await stop_discord_bot()


if __name__ == "__main__":
    asyncio.run(main())
