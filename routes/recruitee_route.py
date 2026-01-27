from flask import Blueprint, session, jsonify
from ..services.mongo_db_client import clan_collection

recruitee_bp = Blueprint("recruitee", __name__)

@recruitee_bp.route("/recruitee")
def recruitee():
    if session.get("db_user") != session.get("player_name"): # need new return
        if session.get("player_name") == "Guest":
            data = list(clan_collection.aggregate([
        { "$sample": { "size": 20 } },
        { "$project": { "_id": 0 } }  
    ]))

        else:
            data = list(clan_collection.find({
            "requirements.1": {"$lte" : session.get("player_builderbase_trophies")},
            "requirements.2": {"$lte" : session.get("player_townhall")},
            "requirements.0": {"$lte" : session.get("player_league")},
            },
            {"_id" : 0}        
            ).limit(20))

        session["db_return"] = data
        session["db_user"] = session.get("player_name")


    return jsonify(session.get("db_return"))
