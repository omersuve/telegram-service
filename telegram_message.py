import os
import requests
import random
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

base_url = f"https://api.telegram.org/bot{os.environ.get('TELEGRAM_BOT_TOKEN')}/sendMessage"
chat_id = os.environ.get('TELEGRAM_CHAT_ID')
trendings_topic_id = os.environ.get('TELEGRAM_TOPIC_ID')

last_template_index = -1


def generate_telegram_content(ticker, token_address, dexscreener_url, telegram_url, score, holders):
    global last_template_index

    templates = [
        f"🚀 Trending Alert: {ticker} is on the rise! 💹\n\n📄 Contract: {token_address}\n\n📊 Check the chart: {dexscreener_url}\n\n💬 Join the chat: {telegram_url}\n\n💯 Sentimental Score: {score}/100",
    ]

    # Append holder count if available
    holder_text = f"\n\n👥 Holder Count: {holders}" if holders is not None else ""

    # Generate a list of indices excluding the last used template
    available_indices = [i for i in range(len(templates)) if i != last_template_index]

    # Select a random index from the available options
    selected_index = random.choice(available_indices)

    # Update the last used template index
    last_template_index = selected_index

    # Return the selected template
    return templates[selected_index] + holder_text


async def send_message_to_telegram(text: str):
    requests.get(base_url, data={
        "chat_id": chat_id,
        "message_thread_id": trendings_topic_id,
        "disable_web_page_preview": True,
        "text": text
    })
