# import os
# import discord
# from dotenv import load_dotenv
#
# # Load environment variables from .env file
# load_dotenv()
#
# DISCORD_CHANNEL_ID = int(os.environ.get('DISCORD_CHANNEL_ID'))
# DISCORD_CHANNEL_ID_2 = int(os.environ.get('DISCORD_CHANNEL_ID_2'))
# DISCORD_CHANNEL_ID_3 = int(os.environ.get('DISCORD_CHANNEL_ID_3'))
# DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
#
# # Discord bot setup
# intents = discord.Intents.default()
# dc_client = discord.Client(intents=intents)
#
#
# @dc_client.event
# async def on_ready():
#     print(f'Logged in as {dc_client.user}')
#
#
# def prepare_message(message_json):
#     text = message_json['text']
#     date = message_json['date']
#     risks = message_json['rugcheck'].get('risks', []) if message_json.get('rugcheck') else []
#
#     formatted_risks = ', '.join(risks) if risks else 'No risks reported'
#
#     # Extract the necessary details from the text
#     lines = [line for line in text.split('\n') if line]
#
#     print("lines", lines)
#
#     # Default values
#     token = 'Unknown'
#     telegram = 'Not Provided'
#     dexscreener = 'Unknown'
#
#     # Parse header
#     header = "🎯 " + lines[0].replace('🔥 ', '').replace('** has just entered Dexscreener hot pairs**', '**') + " 🍾"
#
#     # Explicitly look for each keyword to find the correct data
#     for line in lines:
#         if line.startswith("Token:"):
#             token = line.split(": ")[1]
#         elif line.startswith("Telegram:"):
#             telegram_handle = line.split(": ")[1]
#             # Convert to URL if it is a handle
#             if telegram_handle.startswith('@'):
#                 telegram = f"[{telegram_handle}](https://t.me/{telegram_handle[1:]})"
#             else:
#                 telegram = telegram_handle  # In case it's already a full URL
#         elif line.startswith("Dexscreener:"):
#             dexscreener = line.split(": ")[1]
#
#     formatted_message = f"""
#     {header}
#
#     **Token:** {token}
#     **Telegram:** {telegram}
#     **Dexscreener:** {dexscreener}
#     **Date:** {date}
#     **Risks:** {formatted_risks}
#
#     """
#     return formatted_message
#
#
# async def send_message_to_discord(message):
#     await dc_client.wait_until_ready()  # Ensure the client is ready before trying to send a message
#     channel = dc_client.get_channel(DISCORD_CHANNEL_ID)
#     if channel:
#         await channel.send(prepare_message(message))
#     else:
#         print("Channel not found")
#
#
# async def send_log_to_discord(message):
#     await dc_client.wait_until_ready()  # Ensure the client is ready before trying to send a message
#     channel = dc_client.get_channel(DISCORD_CHANNEL_ID_2)
#     if channel:
#         await channel.send(message)
#     else:
#         print("Channel not found")
#
#
# async def send_error_log_to_discord(message):
#     await dc_client.wait_until_ready()  # Ensure the client is ready before trying to send a message
#     channel = dc_client.get_channel(DISCORD_CHANNEL_ID_3)
#     if channel:
#         await channel.send(message)
#     else:
#         print("Channel not found")
#
#
# async def start_discord_bot():
#     await dc_client.start(DISCORD_BOT_TOKEN)
#
#
# async def stop_discord_bot():
#     await dc_client.close()
