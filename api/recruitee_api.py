import requests
class Recruitee:
    def __init__(self, user_tag, townhall, league, headers):
        self.headers = headers
        self.user_tag = user_tag

    
    def searchClan(self, filter, after):
        url = f"https://api.clashofclans.com/v1/clans"
        if after:
            filter["after"] = after
        
        response = requests.get(url, 
                                params = filter, 
                                headers = self.headers)
        
        return response.json()     
