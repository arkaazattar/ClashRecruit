import requests
from ..services.maxtownhall import refresh

class Recruiter:

    def __init__(self, user_tag, clan_tag, headers):
        self.headers = headers
        self.user_tag = user_tag
        self.clan_tag = clan_tag
        self.requirements = []
        # this may need to change
        self.maxtownhall = refresh(self.headers)
    
    def pull_clan_requirements(self):

        response = requests.get(f"https://api.clashofclans.com/v1/clans?name=%23{self.clan_tag}", headers=self.headers)
        self.storage = response.json()
        long_list = self.storage.get("items")
        
        for i in range(len(long_list)):
            required_townhall = long_list[i].get('requiredTownhallLevel')
            required_builder_trophies = long_list[i].get('requiredBuilderBaseTrophies')
            required_league = 0

        
        self.new_clan_requirements(required_league, required_builder_trophies, required_townhall)

        return self.requirements

    def lookup_clan(self):
        """
        Used for looking up further clan stats
        """
        response = requests.get(f"https://api.clashofclans.com/v1/clans/%23{self.clan_tag}", headers=self.headers)
        response = response.json()  
        rsp = {}
        rsp['type'] = response.get("type")
        rsp['description'] = response.get("description")
        rsp['location']= response.get("location", {}).get("name", None)
        rsp['badge'] = response.get("badgeUrls").get("medium")
        rsp['clan_level'] = response.get("clanLevel")
        rsp['member_count'] = response.get("members")
        return rsp

        
    def set_townhall_requirement(self, required_townhall):
        self.required_townhall = required_townhall

    def set_builder_trophies_requirement(self, required_builder_trophies):
        self.required_builder_trophies = required_builder_trophies

    def set_league_requirement(self, required_league):
        self.required_league = required_league
     
    def new_clan_requirements(self, required_league, required_builder_trophies, required_townhall):
        self.required_league = required_league
        self.required_builder_trophies = required_builder_trophies 
        self.required_townhall = required_townhall
        self.requirements = [self.required_league, self.required_builder_trophies, self.required_townhall]
