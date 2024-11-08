import os
import requests
import random
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

base_url = f"https://api.telegram.org/bot{os.environ.get('TELEGRAM_BOT_TOKEN')}/sendMessage"
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

last_template_index = -1


def generate_telegram_content(ticker, token_address, dexscreener_url, telegram_url, score):
    global last_template_index

    templates = [
        f"🚀 Trending Alert: {ticker} is on the rise! 💹\n\n📄 Contract: {token_address}\n\n📊 Check the chart: {dexscreener_url}\n\n💬 Join the chat: {telegram_url}\n\n💯 Sentimental Score: {score}/100",
        f"🌟 {ticker} just made waves! 🌊\n\n🔍 View contract: {token_address}\n\n📈 Chart it out: {dexscreener_url}\n\n👥 Telegram: {telegram_url}\n\n💯 Sentimental Score: {score}/100",
        f"🔥 Hot New Trend: {ticker}! 🚀\n\n📄 Contract Address: {token_address}\n\n📊 View chart: {dexscreener_url}\n\n💬 Telegram Group: {telegram_url}\n\n💯 Sentimental Score: {score}/100",
        f"🚨 Attention! {ticker} is gaining traction! 📈\n\n🔗 Contract: {token_address}\n\n📉 See the latest chart: {dexscreener_url}\n\n🗨️ Connect on Telegram: {telegram_url}\n\n💯 Sentimental Score: {score}/100",
        f"⚡️ {ticker} is trending now! ⚡️\n\n📜 Contract Info: {token_address}\n\n📊 Dive into the chart: {dexscreener_url}\n\n📣 Join the community: {telegram_url}\n\n💯 Sentimental Score: {score}/100",
        f"🚀 {ticker} is surging up the charts! 📈\n\n🔎 Contract: {token_address}\n\n📊 Check the performance: {dexscreener_url}\n\n💬 Join the conversation: {telegram_url}\n\n💯 Sentimental Score: {score}/100",
        f"🌐 Big Moves Alert: {ticker} is catching eyes! 👀\n\n📝 Contract Details: {token_address}\n\n📈 Analyze the chart: {dexscreener_url}\n\n🔊 Chat with the community: {telegram_url}\n\n💯 Sentimental Score: {score}/100",
        f"🔥 {ticker} is on fire! 🔥\n\n📝 Contract: {token_address}\n\n📊 Explore the chart: {dexscreener_url}\n\n👥 Join the discussion: {telegram_url}\n\n💯 Sentimental Score: {score}/100",
        f"⚠️ Trending Token: {ticker} is making headlines! 📈\n\n🔗 Contract Address: {token_address}\n\n📉 See the latest data: {dexscreener_url}\n\n💬 Connect on Telegram: {telegram_url}\n\n💯 Sentimental Score: {score}/100"
    ]

    # Generate a list of indices excluding the last used template
    available_indices = [i for i in range(len(templates)) if i != last_template_index]

    # Select a random index from the available options
    selected_index = random.choice(available_indices)

    # Update the last used template index
    last_template_index = selected_index

    # Return the selected template
    return templates[selected_index]


async def send_message_to_telegram(text: str):
    requests.get(base_url, data={
        "chat_id": chat_id,
        "disable_web_page_preview": True,
        "text": text
    })
