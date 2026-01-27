import sys
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from ..config import DBPASSWORD

uri = f"mongodb+srv://arkaazattar_db_user:{DBPASSWORD}@clashrecruit.poawkmg.mongodb.net/?appName=clashrecruit"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
clan_info_db = client["clan_info_db"]
player_info_db = client["player_info_db"]
clan_collection = clan_info_db["clans"]

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    sys.exit("Could not connect to DB. Check IP?")