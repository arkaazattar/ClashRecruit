import requests
import apiKey
import time 

headers = {

    "Content-Type" : "application/json",
    "Authorization" : apiKey.api 
    }

class API:
    def __init__(self, user_tag, api):
        self.token = False
        self.user_tag = user_tag
        self.reason = 0 # should be string but wtv
        self.user_name = "Guest"
        self.json_data = {
            "token": str(api)
        }
        self.clantag = ""
        #api is one time use, no point of storing it 
    def check_player(self):
        url = f"https://api.clashofclans.com/v1/players/%23{self.user_tag}"
        response = requests.get(url, headers=headers)
        self.storage = response.json()

        if self.storage.get("reason") == "notFound":
            self.reason = "Player tag is incorrect"
            return False  

        self.clantag = self.storage.get("clan", {}).get("tag", None)
        self.clantag = self.clantag[1:]
        self.user_name = self.storage.get("name")
        return True
    
    def check_player_api(self):

        if (self.check_player() == False):
            return False

        url = f"https://api.clashofclans.com/v1/players/%23{self.user_tag}/verifytoken"

        response = requests.post(url, headers=headers, json = self.json_data)
        self.storage = response.json() # Important!! this storage now holds whether the api key is valid or not

        if self.storage.get("status") == "invalid":
            self.reason = "API Token is incorrect"


        elif self.storage.get("status") == "ok":
            self.token = True # set token value to 1 in boolean. this makes it easy to check if token info is correct

        else: self.reason = self.storage  
        
        return self.token #dont really need to store token in class, as its being returned anyways. keeping for now in the case that we need it for error checking.

class Advertisement:

    def __init__(self, requirements, Recruiter):
        self.requirements = requirements

    
class Recruiter: # error checking needs to be done out of class
    
    def __init__(self, user_tag, clan_tag):
        self.user_tag = user_tag
        self.clan_tag = clan_tag
        self.requirements = []

    def print_info(self): # idk why we would need this 
        print(self.user_tag + " " + self.clan_tag)

    def pull_clan_requirements(self):
        
       # params = {
       #     "name" : self.clan_tag,
       # }

        response = requests.get(f"https://api.clashofclans.com/v1/clans?name=%23{self.clan_tag}", headers=headers)
        self.storage = response.json()
        long_list = self.storage.get("items")
        
        for i in range(len(long_list)):
            required_townhall = long_list[i].get('requiredTownhallLevel')
            required_builder_trophies = long_list[i].get('requiredBuilderBaseTrophies')
            required_league = 0

        
        self.new_clan_requirements(required_league, required_builder_trophies, required_townhall)

        #need to pull, required trophies, required builder base trophies, required townhall level,
        #required trophies doesnt work till api is changed
        #leaving blank for now

  
        # invalid = True
        # while invalid:
        #     change_requirements = input(f"Do you want to change the townhall requirements from clans default requirements ({required_townhall})? Yes or no: ").lower()
        #     if change_requirements == "yes":
        #         required_townhall = int(input("New Townhall requirement: ")) #error handling later
        #         self.set_townhall_requirement(required_townhall)
        #         invalid = False
        #     elif change_requirements == "no":
        #         invalid = False
        #     else: 
        #         print("Invalid input")
                
        # invalid = True
        # while invalid:
        #     change_requirements = input(f"Do you want to change the builder trophy requirements from clans default requirements ({required_builder_trophies})? Yes or no: ").lower()
        #     if change_requirements == "yes":

        #         required_builder_trophies = int(input("New builder trophies requirement: ")) #error handling later

        #         self.set_builder_trophies_requirement(required_builder_trophies)
        #         invalid = False
        #     elif change_requirements == "no":
        #         invalid = False
        #     else: 
        #         print("Invalid input")

        # print("Set required league") #ts will go away
        # self.set_league_requirement(required_league)

        
        # self.new_clan_requirements(required_league, required_builder_trophies, required_townhall)
        
        # valid_input = False
        # while(False):
        #     if (input("Do you want to post an ad? (Yes/No)").lower) == "yes" or "no":
        #         self.post_ad()
        #         valid_input = True
        #     else:  
        #         (print("Invalid Input"))

        
        
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

    def post_ad(self):
        print(self.requirements)

    def get_requirements(self):
        return self.requirements


class Recruitee:
    # everything here now needs to call back to api request

    def __init__(self, user_tag):
        self.user_tag = user_tag




        

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

def recruiting(user_tag): # this should automatically load their clan, no need to type in clan tag
    roles = ["leader", "coleader", "admin"] #admin is elder r we 
    response = requests.get(f"https://api.clashofclans.com/v1/players/%23{user_tag}", headers=headers)
    data = response.json()
    clan_tag = data.get("clan", {}).get("tag", 0)
    if(clan_tag == 0):
        print("not in clan")
        return(False)
    
    if(data["role"].lower() not in roles):
        print("not a leader")
        return(False)
    
    return(True)

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


