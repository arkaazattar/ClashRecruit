import requests


class Recruitee:
    def __init__(self, user_tag, townhall, league, headers):
        self.headers = headers
        self.user_tag = user_tag

    
    def searchClan(self, filter, after = None):
        url = f"https://api.clashofclans.com/v1/clans"
        if after:
            filter["after"] = after
      
        response = requests.get(url, 
                                params = filter, 
                                headers = self.headers)
        
        storage = response.json()

        error = None
        if response.status_code >= 400:
            error = {
                "reason": storage.get("reason"),
                "message": storage.get("message"),
                "status": response.status_code,
            }

        return {
        "items": storage.get("items", []),
        "after": storage.get("paging", {}).get("cursors", {}).get("after"),
        "error": error,
    }
