import requests

from ..config import headers
from ..services.mongo_db_client import location_collection


def get_locations(headers=headers) -> list:
    """Returns a list of locations returned from the Clash of Clans API.

    Args:
        headers (dict[str, str], optional): HTTP headers sent with the Clash of
            Clans API request. Defaults to the module-level ``headers`` imported
            from ``config``.

    Returns:
        list: The list of all locations returned from the Clash of Clans API.
    """

    response = requests.get('https://api.clashofclans.com/v1/locations', headers=headers)
    list_of_locations = response.json().get("items", None)

    return list_of_locations

def update_location_collection() -> None:
    """Updates stored database locations on function call."""

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