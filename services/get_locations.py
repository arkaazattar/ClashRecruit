import requests
from ..config import headers
from ..services.mongo_db_client import location_collection

def get_locations(headers):
    response = requests.get('https://api.clashofclans.com/v1/locations', headers=headers)
    list_of_locations = response.json().get("items", None)

    return list_of_locations

def update_location_collection():
    list_of_locations = get_locations(headers)

    for location in list_of_locations:
        if location["name"] == "":
            continue
        if not location_collection.find_one({"id" : location.get("id")}):
            location_collection.insert_one(            
                location
                )

if __name__ == "__main__":
    update_location_collection()