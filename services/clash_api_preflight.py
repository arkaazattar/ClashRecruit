"""Development preflight check for Clash API reachability."""

import requests

from ..config import headers


def run_clash_api_preflight(headers=headers) -> None:
    """Call a lightweight Clash endpoint and raise if the API rejects this IP.


    Args:
        headers (dict[str, str], optional): HTTP headers sent with the Clash of
            Clans API request. Defaults to the module-level ``headers``
            imported
            from ``config``.

    Raises:
        Exception: Raised when the Clash API responds with an HTTP error
            status.
    """
    response = requests.get(
        (
            "https://api.clashofclans.com/v1/locations/32000249/"
            "rankings/players?limit=1"
        ),
        headers=headers,
    )
    status_code = response.status_code

    if status_code >= 400:
        reason = response.json().get("reason", "unknown")
        raise Exception(f"HTTP {status_code}: {reason}")

    return

if __name__ == "__main__":
    run_clash_api_preflight()
