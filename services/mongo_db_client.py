import sys
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from ..config import DBURI

uri = DBURI
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    sys.exit("Could not connect to DB. Check IP?")

clan_info_db = client["clan_info_db"]
location_collection = clan_info_db["locations"]
clan_collection = clan_info_db["clans"]
user_collection = clan_info_db["users"]
import_state_collection = clan_info_db["import_state"]

clan_collection.create_index("expires", expireAfterSeconds=0)
user_collection.create_index("player_tag", unique=True)

try:
    clan_collection.create_index([("clan_tag", 1), ("source", 1)], unique=True)
except Exception:
    pass

clan_collection.create_index("source")
clan_collection.create_index("last_updated")
clan_collection.create_index([("last_updated", -1), ("clan_tag", 1)])
clan_collection.create_index("requirements.0")
clan_collection.create_index("requirements.1")
clan_collection.create_index("requirements.2")
clan_collection.create_index("last_discovered")
clan_collection.create_index("last_enriched")
clan_collection.create_index("detail_status")
clan_collection.create_index("clan_info.location.id")
clan_collection.create_index("clan_info.location.name")
clan_collection.create_index("clan_info.member_count")
clan_collection.create_index("clan_info.clan_level")
clan_collection.create_index("clan_info.clanPoints")
clan_collection.create_index("clan_info.warFrequency")

import_state_collection.create_index("seed_key", unique=True)
