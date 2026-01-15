"""
Caches the highest Townhall level for 24 hours into cache/. 

Important Note:
- If running this file standalone (not imported), you must provide the headers manually.
"""
import requests
from diskcache import Cache
from .config import headers 

cache = Cache("cache")

def get_max_townhall():
    """
    This function will return the current highest ranked player in the United States and pull their Townhall level.
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


def refresh():
    """
    Returns the current highest Townhall level.
    Checks the cache first, and calls the API only if needed.
    """
    if cache.get("MAXTOWNHALL") is None:
        get_max_townhall()
    return cache.get("MAXTOWNHALL")

if __name__ == "__main__":
    
    def check_cache():
        """
        This function is used to check the cache file for a value. If nothing is found, it will call get_max_townhall().
        get_max_townhall() will return the MAXTOWNHALL constant into a cache folder. Access using cache.get("MAXTOWNHALL").
        """
        if cache.get("MAXTOWNHALL") == None:
            get_max_townhall()
            return False
        return True
    
    cache_status = check_cache()
    if cache_status:
        print(f"Received from Cache. Maximum townhall = {cache.get('MAXTOWNHALL')}")
        exit()
    else:
        print(f"Checked highest ranked player in the United States. Maximum townhall = {cache.get('MAXTOWNHALL')}")
        exit()
    