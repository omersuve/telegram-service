import os
import requests
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()
API_KEY = os.getenv("AGENT_NODEJS_API_KEY")


def format_large_number(value):
    if isinstance(value, (int, float)):
        if value >= 1_000_000:
            return f"${round(value / 1_000_000)}M"
        elif value >= 1_000:
            return f"${round(value / 1_000)}K"
        else:
            return f"${int(value)}"
    return value


def generate_agent_knowledge(data):
    """
    Generates a formatted agent knowledge message from extracted data.
    """
    try:
        name = data.get("text", "").split("**")[1].split(" has ")[0].strip()
        token_name = data.get("text", "").split("Token: ")[1].split("\n")[0].strip()
        token_address = data.get("text", "").split("Dexscreener: [")[1].split("]")[0].split("(")[1].split(")")[0].split("/")[-1]
        total_liquidity = format_large_number(data.get("rugcheck", {}).get("totalMarketLiquidity", "N/A"))
        market_cap = format_large_number(data.get("marketCap", "N/A"))
        volume = format_large_number(data.get("volume1h", "N/A"))
        holders = data.get("holders", "N/A")
        score = data.get("scores", [0])[0]
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

        # Remove entries with None values
        knowledge = [line for line in knowledge if "None" not in line and "N/A" not in line]
        return "\n".join(knowledge)
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
    payload = {"trends": message}

    try:
        response = requests.post("https://agent-knowledge-gen-news-trends-production.up.railway.app/trends",
                                 json=payload, headers=headers)
        if response.status_code == 200:
            print(f"Successfully sent knowledge: {message}")
        else:
            print(f"Failed to send knowledge. Status code: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        print(f"Error sending knowledge to API: {e}")
