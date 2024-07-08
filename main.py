import asyncio
import json
import os
import pusher
import redis.asyncio as redis
from dotenv import load_dotenv
from telethon import TelegramClient, events
from discord_message import start_discord_bot, stop_discord_bot, send_message_to_discord  # Import functions

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


@client_telegram.on(events.NewMessage(chats=chat))
async def handler(event):
    message = event.message
    data = {
        "group": chat,
        "sender": message.sender_id,
        "text": message.text,
        "date": message.date.isoformat()
    }
    print(data)
    # Publish message to Redis
    try:
        await redis_client.lpush("latest_messages", json.dumps(data))
        await redis_client.ltrim("latest_messages", 0, 9)

        print("redis pushed and trimmed")

        pusher_client.trigger("my-channel", "my-event", {"message": json.dumps(data)})
        print("Message published successfully")

        # Send message to Discord
        await send_message_to_discord(json.dumps(data))

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
