import os
import discord
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DISCORD_CHANNEL_ID = int(os.environ.get('DISCORD_CHANNEL_ID'))
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

# Discord bot setup
intents = discord.Intents.default()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')


async def send_message_to_discord(message):
    await client.wait_until_ready()  # Ensure the client is ready before trying to send a message
    channel = client.get_channel(DISCORD_CHANNEL_ID)
    if channel:
        await channel.send(message)
    else:
        print("Channel not found")


# Run the bot
client.run(DISCORD_BOT_TOKEN)
