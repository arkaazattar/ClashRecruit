import requests
from .config import headers
from .maxtownhall import refresh
MAXTOWNHALL = refresh()

class API:
    def __init__(self, user_tag, api):
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
    def check_player_api(self):
        
        url = f"https://api.clashofclans.com/v1/players/%23{self.user_tag}/verifytoken"

        response = requests.post(url, headers=headers, json = self.json_data)
        self.apistorage = response.json() # Important!! this storage now holds whether the api key is valid or not

        status = self.apistorage.get("status")

        if status == "ok":
            self.token = True # set token value to 1 in boolean. this makes it easy to check if token info is correct

        elif status == "invalid":
            self.reason = "API Token is incorrect"

        else: self.reason = self.apistorage  
        return self.token 
    
    def check_player(self):
        url = f"https://api.clashofclans.com/v1/players/%23{self.user_tag}"
        response = requests.get(url, headers=headers)
        self.storage = response.json()
        self.league = self.storage.get("leagueTier").get("name")
        if self.league != 'Unranked':
            self.league = int(self.league[-2:])
        self.townhall = self.storage.get("townHallLevel")
        self.builder_trophies = self.storage.get("builderBaseTrophies")


        reason = self.storage.get("reason")
        
        if reason == "notFound":
            self.reason = "Player tag is incorrect"
            return False  
        
        if reason == "accessDenied.invalidIp":
             self.reason = "Invalid IP"
             return False
        
        if self.check_player_api() == False: 
            return False
        self.townhall = self.storage.get("townHallLevel")
        self.builder_trophies = self.storage.get("builderBaseTrophies")
     

        self.recruiter_status = self.recruiting(self.storage)
        self.clantag = self.storage.get("clan", {}).get("tag", None)
        self.clantag = self.clantag[1:]
        self.user_name = self.storage.get("name")
        return True
    
    def recruiting(self, data : dict): 
        roles = ["leader", "coleader", "admin"] #admin is elder r we 
        
        clan_tag = data.get("clan", {}).get("tag", 0)
        if(clan_tag == 0):
            print("not in clan")
            return False
        
        if(data["role"].lower() not in roles):
            print("not a leader")
            return False
        
        return True

class Recruiter: # error checking needs to be done out of class
    
    def __init__(self, user_tag, clan_tag):
        self.user_tag = user_tag
        self.clan_tag = clan_tag
        self.requirements = []

    def pull_clan_requirements(self):

        response = requests.get(f"https://api.clashofclans.com/v1/clans?name=%23{self.clan_tag}", headers=headers)
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
        response = requests.get(f"https://api.clashofclans.com/v1/clans/%23{self.clan_tag}", headers=headers)
        response = response.json()  
        rsp = {}
        rsp['type'] = response.get("type")
        rsp['description'] = response.get("description")
        rsp['location']= response.get("location", {}).get("name", None)
        rsp['badge'] = response.get("badgeUrls").get("medium")
        rsp['clan_level'] = response.get("clanLevel")
        return rsp

        
#setters
    def set_townhall_requirement(self, required_townhall):
        self.required_townhall = required_townhall

    def set_builder_trophies_requirement(self, required_builder_trophies):
        self.required_builder_trophies = required_builder_trophies

    def set_league_requirement(self, required_league):
        self.required_league = required_league

#change list of requirements        
    def new_clan_requirements(self, required_league, required_builder_trophies, required_townhall):
        self.required_league = required_league
        self.required_builder_trophies = required_builder_trophies 
        self.required_townhall = required_townhall
        self.requirements = [self.required_league, self.required_builder_trophies, self.required_townhall]


class Recruitee:
    def __init__(self, user_tag, townhall, league):
        self.user_tag = user_tag

if __name__ == "__main":

    def ask_if_recruiting():
        invalid_input = True
        while invalid_input:
            recruiting = input("Are you recuiting? Yes or no: ").lower()
            if recruiting == "yes" or  recruiting == "no" or recruiting == 'test':
                invalid_input = False
            else: print("Invalid input")
        return recruiting # returns yes, no, or test

    def check_api():
        valid_api = False
        while valid_api == False:
            user_tag = input("Please enter your player tag: #")
            tag_check = API(user_tag, "")
            if tag_check.check_player() == False:
                print(f"{tag_check.reason}, try again.")
                continue
            api = input("Please enter your API token: ")
            user = API(user_tag, api)
            user.check_player_api()
            if user.token == True:
                valid_api = True
            else: print(f"{user.reason}, try again") 
        return(user_tag)



    def recruitee():
        invalid_input = True
        while invalid_input:
            looking_for_clan = input("Are you looking for a clan? Yes or no: ").lower()
            if looking_for_clan == "yes" or  looking_for_clan == "no":
                if looking_for_clan == "no":
                    exit() # kill program ? prob wont be needed when made into website
                else: invalid_input = False
            else: print("Invalid input")
        return


    def get_user():
        response = ask_if_recruiting()
        user_tag = check_api()
        if response == "yes":
            if recruiting(user_tag) == False:
                return # this return might be bad, not a graceful exit
            else: 
                pass
                # need to figure out how to call a clan tag for that function, basically need to store the clan tag and then call new_clan_requirements() to store parameters for that clan

        if response == "no":
            recruitee()




            
        
# get_user()
#jon was here
#arkaaz was here
#testing for jon


