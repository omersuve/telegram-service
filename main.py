import json
from telethon import TelegramClient, events
import datetime
import os
from dotenv import load_dotenv
import redis.asyncio as redis

# Load environment variables from .env file
load_dotenv()

try:
    api_id = int(os.getenv("TELETHON_API_ID"))
    api_hash = os.getenv("TELETHON_API_HASH")

    # chat = 'maomaomaocat'
    chat = 'dexscreener_trendings'

    print("api_id", api_id)
    print("api_hash", api_hash)

    # Use 'session_name' for the session file
    client = TelegramClient("session_name", api_id, api_hash)

    # Connect to Redis
    redis_url = os.getenv("REDIS_PUBLIC_URL", "redis://localhost:6379/0")
    redis_client = redis.from_url(redis_url)


    @client.on(events.NewMessage(chats=chat))
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
            await redis_client.publish('telegram_messages', json.dumps(data))
            print("Message published successfully")
        except Exception as e:
            print(f"Failed to publish message to Redis: {e}")


except Exception as e:
    print(f"Error in Beginning: {e}")


def main():
    try:
        client.start()
        print("Telegram client started successfully")
        client.run_until_disconnected()
    except Exception as e:
        print(f"Error in Telegram client: {e}")


if __name__ == "__main__":
    main()
