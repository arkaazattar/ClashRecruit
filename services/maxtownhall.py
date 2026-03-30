"""
Caches the highest Townhall level for 24 hours into cache. 
"""

import requests
from diskcache import Cache

cache = Cache("cache")

def get_max_townhall(headers) -> int:
    """This function will return the current highest ranked player in the United States and pull their Townhall level.

    Args:
        headers (dict[str, str]): HTTP headers sent with the Clash of Clans API
            requests.

    Returns:
        int: The townhall level returned by the API.
    """    

    response = requests.get('https://api.clashofclans.com/v1/locations/32000249/rankings/players?limit=1', headers=headers)
    response = response.json()
    tag = response['items'][0]["tag"]
    tag = tag[1:]
    response = requests.get(f"https://api.clashofclans.com/v1/players/%23{tag}", headers=headers)
    response = response.json()
    MAXTOWNHALL = response.get("townHallLevel")
    cache.set("MAXTOWNHALL", MAXTOWNHALL, 86400)
    return MAXTOWNHALL


def get_max_townhall_cached(headers) -> int:
    """Returns the current highest Townhall level.
    Checks the cache first, and calls the API only if needed.

    Args:
        headers (dict[str, str]): HTTP headers sent with the Clash of Clans API
            requests.

    Returns:
        int: The townhall level returned by the API.
    """    

    if cache.get("MAXTOWNHALL") is None:
        get_max_townhall(headers)
    return cache.get("MAXTOWNHALL")
    
