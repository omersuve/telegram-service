import json
import os
import pusher
import redis.asyncio as redis
from dotenv import load_dotenv
from telethon import TelegramClient, events
from discord_message import send_message_to_discord, client  # Import the function and client

try:
    # Load environment variables from .env file
    load_dotenv()

    api_id = int(os.environ.get("TELETHON_API_ID"))
    api_hash = os.environ.get("TELETHON_API_HASH")

    chat = 'dexscreener_trendings'
    # chat = 'maomaomaocat'

    # Use 'session_name' for the session file
    client = TelegramClient("session_name", api_id, api_hash)

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
            await redis_client.lpush("latest_messages", json.dumps(data))
            await redis_client.ltrim("latest_messages", 0, 9)

            print("redis pushed and trimmed")

            pusher_client.trigger("my-channel", "my-event", {"message": json.dumps(data)})
            print("Message published successfully")

            # Send message to Discord
            await send_message_to_discord(json.dumps(data))

        except Exception as err:
            print(f"Failed to sending message to Redis: {err}")
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
