import requests


def get_holder_count(token_address):
    url = f"https://holderscan.com/api/tokens/holders?ca={token_address}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # Extract the holder count from the first element in token_holders_historical
        holder_count = data.get("data", {}).get("token_holders_historical", [{}])[0].get("holder_count")
        return holder_count
    except requests.exceptions.RequestException as e:
        print(f"Error fetching holder count for {token_address}: {e}")
        return None
