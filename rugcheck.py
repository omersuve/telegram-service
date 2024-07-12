import requests


def get_rugcheck_report(token_address):
    url = f"https://api.rugcheck.xyz/v1/tokens/{token_address}/report"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        report = response.json()  # Parse JSON response

        # Extract specific fields
        extracted_data = {
            "risks": [risk.get("name") for risk in report.get("risks", [])],
            "totalLPProviders": report.get("totalLPProviders"),
            "totalMarketLiquidity": report.get("totalMarketLiquidity")
        }
        return extracted_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching rugcheck report for {token_address}: {e}")
        return None
