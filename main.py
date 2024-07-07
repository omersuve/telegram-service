import json
from telethon import TelegramClient, events
import os
from dotenv import load_dotenv
import redis.asyncio as redis

try:
    # Load environment variables from .env file
    load_dotenv()

    api_id = int(os.environ.get("TELETHON_API_ID"))
    api_hash = os.environ.get("TELETHON_API_HASH")

    print(api_hash)

    # chat = 'dexscreener_trendings'
    chat = 'maomaomaocat'

    # Use 'session_name' for the session file
    client = TelegramClient("session_name", api_id, api_hash)

    # Connect to Redis
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    print(redis_url)
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
        # Publish message to Redis
        try:
            await redis_client.publish('telegram_messages', json.dumps(data))
            # print("Message published successfully")
        except Exception as e:
            print(f"Failed to publish message to Redis: {e}")

except Exception as e:
    print(e)


def main():
    try:
        client.start()
        print("Telegram client started successfully")
        client.run_until_disconnected()
    except Exception as e:
        print(f"Error in Telegram client: {e}")


if __name__ == "__main__":
    main()
