"""Service for caching the highest Townhall level for 24 hours into cache."""

from functools import lru_cache

import requests
from diskcache import Cache


@lru_cache(maxsize=1)
def get_cache() -> Cache:
    """Return a cached diskcache handle initialized on first use."""
    return Cache("cache")


def get_max_townhall(headers) -> int:
    """Fetch and cache the current highest observed Town Hall level.

    Args:
        headers (dict[str, str]): HTTP headers sent with Clash of Clans API
            requests.

    Returns:
        int: The highest Town Hall level from the top-ranked U.S. player.

    Raises:
        ValueError: If the API response does not include a valid
            ``townHallLevel`` value.
    """
    response = requests.get(
        "https://api.clashofclans.com/v1/locations/32000249/"
        "rankings/players?limit=1",
        headers=headers,
    )
    response = response.json()
    tag = response['items'][0]["tag"]
    tag = tag[1:]
    response = requests.get(
        f"https://api.clashofclans.com/v1/players/%23{tag}",
        headers=headers,
    )
    response = response.json()
    max_townhall = response.get("townHallLevel")
    if max_townhall is None:
        raise ValueError("Missing 'townHallLevel' in Clash API response.")

    max_townhall = int(max_townhall)
    get_cache().set("MAXTOWNHALL", max_townhall, 86400)
    return max_townhall


def refresh(headers) -> int:
    """Return the cached maximum Town Hall level, refreshing when absent.

    Args:
        headers (dict[str, str]): HTTP headers sent with Clash of Clans API
            requests when a refresh is needed.

    Returns:
        int: The cached maximum Town Hall level.

    Raises:
        ValueError: If a valid Town Hall level cannot be resolved.
    """
    cached_value = get_cache().get("MAXTOWNHALL")
    if cached_value is None:
        return get_max_townhall(headers)

    return int(cached_value)
