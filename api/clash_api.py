import requests
from typing import Literal

REQUESTOPTIONS = Literal[
    "expLevel",
    "leagueTier",
    "builderBaseLeague",
    "builderHallLevel",
    "clan"
]

class API:
    def __init__(self, user_tag, api, headers):
        self.headers = headers
        self.token = False
        self.user_tag = user_tag
        self.user_name = "Guest"
        self.json_data = {
            "token": api
        }
        self.clantag = ""
        self.recruiter_status = ""
        self.league = 0
        self.builder_trophies = 0
        self.townhall = 0
        self.townhallWeaponLevel = None
    def check_player_api(self):
        
        url = f"https://api.clashofclans.com/v1/players/%23{self.user_tag}/verifytoken"

        response = requests.post(url, headers=self.headers, json = self.json_data)
        self.apistorage = response.json() # Important!! this storage now holds whether the api key is valid or not

        status = self.apistorage.get("status")

        if status == "ok":
            self.token = True # set token value to 1 in boolean. this makes it easy to check if token info is correct

        elif status == "invalid":
            self.reason = "API Token is incorrect"

        else: self.reason = self.apistorage  
        return self.token 
    
    def check_player(self, request: list[REQUESTOPTIONS] | None = None):
        if self.user_tag == "Guest":
            self.reason = "User is a Guest"
            return False
        url = f"https://api.clashofclans.com/v1/players/%23{self.user_tag}"
        response = requests.get(url, headers=self.headers)
        self.storage = response.json()
        reason = self.storage.get("reason")
        
        if reason == "notFound":
            self.reason = "Player tag is incorrect"
            return False  
        
        if reason == "accessDenied.invalidIp":
             self.reason = "Invalid IP"
             return False
        
        if self.json_data["token"] and self.check_player_api() == False: 
            return False

        self.league = self.storage.get("leagueTier").get("name")
        if self.league != 'Unranked':
            self.league = int(self.league[-2:])
        else: self.league = 0
        self.townhall = self.storage.get("townHallLevel")
        self.builder_trophies = self.storage.get("builderBaseTrophies")
        
        if self.townhall <= 17:
            self.townhallWeaponLevel = self.storage.get("townHallWeaponLevel")
    
        self.recruiter_status = self.recruiting(self.storage)
        self.clantag = self.storage.get("clan", {}).get("tag", None)
        if self.clantag: 
            self.clantag = self.clantag[1:]            
        self.user_name = self.storage.get("name")

        if request:
            response = {
                "player_tag": self.user_tag
            }
            for request_key in request:
                response[request_key] = self.storage.get(request_key, None)

            if response.get("clan", None):
                response["clan"]["role"] = self.storage.get("role")
                
            return response

        return True
    
    def recruiting(self, data : dict): 
        roles = ["leader", "coleader", "admin"]
        
        clan_tag = data.get("clan", {}).get("tag", 0)
        if(clan_tag == 0):
            return False
        
        if(data["role"].lower() not in roles):
            return False
        
        return True  
