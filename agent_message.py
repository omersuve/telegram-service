import os
import requests
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()
API_KEY = os.getenv("AGENT_NODEJS_API_KEY")


def generate_agent_knowledge(data):
    """
    Generates a formatted agent knowledge message from extracted data.
    """
    try:
        name = data.get("text", "").split("**")[1].strip()
        token_name = data.get("tokenName")
        token_address = data.get("tokenAddress")
        score = data.get("scores", [0])[0]
        total_liquidity = data.get("rugcheck", {}).get("totalMarketLiquidity", "N/A")
        market_cap = data.get("marketCap", "N/A")
        volume = data.get("volume1h", "N/A")
        holders = data.get("holders", "N/A")
        created_at = data.get("createdAt", "N/A")

        knowledge = (
            f"Name: {name}\n"
            f"Token Name: {token_name}\n"
            f"Token Address: {token_address}\n"
            f"Score: {score}\n"
            f"Total Market Liquidity: ${total_liquidity}\n"
            f"Market Cap: ${market_cap}\n"
            f"1 Hour Volume: ${volume}\n"
            f"Created At: {created_at}\n"
            f"Holders: {holders}"
        )

        return knowledge.strip()
    except Exception as e:
        print(f"Error generating agent knowledge: {e}")
        return None


def send_agent_knowledge_to_api(message):
    """
    Sends the agent knowledge message to the Node.js API.
    """
    if not message:
        print("No valid message to send.")
        return

    headers = {"x-api-key": API_KEY}
    payload = {"news": message}

    try:
        response = requests.post("https://agent-knowledge-gen-news-trends-production.up.railway.app/trends",
                                 json=payload, headers=headers)
        if response.status_code == 200:
            print(f"Successfully sent knowledge: {message}")
        else:
            print(f"Failed to send knowledge. Status code: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        print(f"Error sending knowledge to API: {e}")
