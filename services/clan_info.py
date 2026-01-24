"""
Pull clan information from database and return the json
"""
from .mongo_db_client import clan_collection

def clan_info(clantag):
    """
    Returns JSON information received from the database on the input clan tag
    """
    info = clan_collection.find_one({"clan_tag" : clantag}, {"_id" : 0})
    if info is None:
        return {"error": "Clan not found"}, 404
    return info