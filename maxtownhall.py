import requests
from diskcache import Cache
import apiKey
headers = {

    "Content-Type" : "application/json",
    "Authorization" : apiKey.api 
    }
cache = Cache("cache")

def get_max_townhall():
    """
    This function will return the current highest ranked player in the United States and pull their Townhall level. 
    """
    cached = cache.get("MAXTOWNHALL")
    if cached is not None:
        return cached

    response = requests.get('https://api.clashofclans.com/v1/locations/32000249/rankings/players?limit=1', headers=headers)
    response = response.json()
    tag = response["items"][0]["tag"]
    tag = tag[1:]
    response = requests.get(f"https://api.clashofclans.com/v1/players/%23{tag}", headers=headers)
    response = response.json()
    MAXTOWNHALL = response.get("townHallLevel")
    cache.set("MAXTOWNHALL", MAXTOWNHALL, 86400)
    return MAXTOWNHALL

if __name__ == "__main__":
    townhall = get_max_townhall()
    print(f"{townhall}")