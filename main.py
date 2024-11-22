import asyncio
import json
import os
import re
import uuid
import pusher
import redis.asyncio as redis
from dotenv import load_dotenv
from telethon import TelegramClient, events
from trending_sentiment import fetch_tweets_and_analyze
from rugcheck import get_rugcheck_report
import schedule
import time
from telegram_message import generate_telegram_content, send_message_to_telegram
import requests

# Load environment variables from .env file
load_dotenv()

api_id = int(os.environ.get("TELETHON_API_ID"))
api_hash = os.environ.get("TELETHON_API_HASH")

chat = 'dexscreener_trendings'

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
        # Check if the message indicates a "Golden Ticker" unlock event and skip it
        if "Golden Ticker" in message.text:
            print("Skipping 'Golden Ticker' unlock event.")
            return
        # Extract ticker symbol using regex
        match = re.search(r'Token: ([#$]\w+)', message.text)
        if match:
            ticker = match.group(1)
            print(f"Extracted ticker: {ticker}")

            # Extract token address using regex from Dexscreener URL
            address_match = re.search(r'dexscreener.com/solana/([a-zA-Z0-9]+)', message.text)
            token_address = address_match.group(1) if address_match else None

            if not token_address:
                print("Token address not found in the message text. Exiting handler.")
                return

            # Fetch token details from DexScreener API
            dex_api_url = f"https://api.dexscreener.io/latest/dex/tokens/{token_address}"
            response = await asyncio.to_thread(requests.get, dex_api_url)
            dex_data = response.json().get("pairs", [{}])[0]

            # Extract additional details from DexScreener
            market_cap = dex_data.get("marketCap", "N/A")
            created_at = dex_data.get("pairCreatedAt")
            volume_1h = dex_data.get("volume", {}).get("h1", "N/A")

            # Convert `pairCreatedAt` to a human-readable format
            if created_at:
                created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(created_at / 1000))

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

            # Extract Telegram handle or URL
            tg_match = re.search(r'Telegram: (@[a-zA-Z0-9_]+|https://t\.me/[a-zA-Z0-9_]+)', message.text)
            if tg_match:
                telegram_handle = tg_match.group(1)
                # Convert to a URL if it's a handle
                if telegram_handle.startswith('@'):
                    telegram_url = f"https://t.me/{telegram_handle[1:]}"
                else:
                    telegram_url = telegram_handle
            else:
                telegram_url = "N/A"

            # Fetch Twitter sentiment score
            score = await fetch_tweets_and_analyze(ticker)

            # Generate a unique ID for the message
            message_id = str(uuid.uuid4())

            # Format the Blink URL with the token address
            blink_url = f"https://dial.to/?action=solana-action%3Ahttps%3A%2F%2Factions.shotbots.app%2Fapi%2Fswap%3FtokenAddress%3D{token_address}&cluster=mainnet"
            # Generate the DexScreener URL
            dexscreener_url = f"https://dexscreener.com/solana/{token_address}"

            # tweet_content_random = generate_tweet_content(
            #     ticker=ticker,
            #     token_address=token_address,
            #     dexscreener_url=dexscreener_url,
            #     telegram_url=telegram_url,
            #     blink_url=blink_url
            # )
            #
            # # Send the formatted tweet to Twitter
            # await post_twitter({'text': tweet_content_random})

            # Generate Telegram content with RugCheck data
            telegram_msg = generate_telegram_content(
                ticker=ticker,
                token_address=token_address,
                dexscreener_url=dexscreener_url,
                telegram_url=telegram_url,
                score=score
            )

            telegram_msg += f"\n\n💰 Market Cap: ${market_cap}"
            telegram_msg += f"\n📅 Created At: {created_at}" if created_at else ""
            telegram_msg += f"\n📊 1 Hour Volume: ${volume_1h}"

            # Append RugCheck data to the message if available
            if rugcheck_data:
                telegram_msg += f"\n\n🛡️ Rug check report:\n\t- Risks: {', '.join(rugcheck_data['risks'])}\n\t- LP Providers: {rugcheck_data['totalLPProviders']}\n\t- Market Liquidity: ${int(rugcheck_data['totalMarketLiquidity'])}"

            # Send the message to Telegram
            await send_message_to_telegram(telegram_msg)
            print("Telegram message sent successfully.")

            data = {
                "id": message_id,
                "text": message.text,
                "date": message.date.isoformat(),
                "scores": [score, None, None],  # Initialize with the first score and placeholders
                "rugcheck": rugcheck_data,  # Possibly None
                "marketCap": market_cap,
                "createdAt": created_at,
                "volume1h": volume_1h,
                "blink_url": blink_url
            }
            print(data)

            await redis_client.lpush("latest_messages", json.dumps(data))
            await redis_client.ltrim("latest_messages", 0, 9)

            print("Redis pushed, trimmed!")
            await asyncio.sleep(3)  # Wait for 3 seconds

            pusher_client.trigger("my-channel", "my-event", {"message": "DATA CHANGED!"})
            print("Message published successfully")

            # Send message to Discord
            # await send_message_to_discord(data)

            # Start the Twitter sentiment analysis and schedule it to run every hour for total 4 times
            async def run_analysis():
                try:
                    for i in range(2):
                        await asyncio.sleep(1800)  # Wait for 0.5 hour
                        new_score = await fetch_tweets_and_analyze(ticker)
                        new_rugcheck_report = get_rugcheck_report(token_address) if token_address else None
                        # Retrieve the list of messages from Redis
                        messages = await redis_client.lrange("latest_messages", 0, -1)
                        for idx, msg in enumerate(messages):
                            msg_data = json.loads(msg)
                            if msg_data["id"] == message_id:
                                msg_data["scores"][i + 1] = new_score  # Update the scores array
                                msg_data["rugcheck"] = new_rugcheck_report  # Update rugcheck data
                                await redis_client.lset("latest_messages", idx,
                                                        json.dumps(msg_data))  # Update the message in Redis

                                await asyncio.sleep(3)  # Wait for 3 seconds

                                pusher_client.trigger("my-channel", "my-event", {"message": "NEW DATA CHANGED!"})
                                # Send log to Discord
                                # await send_log_to_discord(json.dumps(msg_data))
                                break

                except Exception as exception:
                    print(exception)
                    # await send_error_log_to_discord(str(exception))

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
            # start_discord_bot(),
            start_telegram_client()
        )
    except Exception as e:
        print(f"Error in Telegram client: {e}")
    # finally:
        # Stop the Discord bot if the Telegram client disconnects
        # await stop_discord_bot()


if __name__ == "__main__":
    asyncio.run(main())
