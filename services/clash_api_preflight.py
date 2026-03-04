"""
Development preflight check for Clash API reachability.
"""

import requests
from ..config import headers

def run_clash_api_preflight(headers=headers) -> None:
    """
    Call a lightweight Clash endpoint and raise if the API rejects this IP.
    """
    response = requests.get(
        "https://api.clashofclans.com/v1/locations/32000249/rankings/players?limit=1",
        headers=headers,
    )
    status_code = response.status_code

    if status_code >= 400:
        reason = response.json().get("reason", "unknown")
        raise Exception(f"HTTP {status_code}: {reason}")
    
    return

if __name__ == "__main__":
    run_clash_api_preflight()
