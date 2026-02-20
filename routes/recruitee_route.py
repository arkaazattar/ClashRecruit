from flask import Blueprint, session, jsonify, request
from ..services.mongo_db_client import clan_collection

recruitee_bp = Blueprint("recruitee", __name__)

@recruitee_bp.route("/recruitee", methods=['GET', 'POST'])
def recruitee():

    if request.method == 'GET':
        if session.get("db_user") != session.get("player_name"): # need new return
            if session.get("player_name") == "Guest":
                data = list(clan_collection.aggregate([
            { "$sample": { "size": 20 } },
            { "$project": { "_id": 0 } }  
        ]))

            else:
                data = list(clan_collection.find({
                "requirements.0": {"$lte" : session.get("player_league")},
                "requirements.1": {"$lte" : session.get("player_builderbase_trophies")},
                "requirements.2": {"$lte" : session.get("player_townhall")},
                },
                {"_id" : 0}        
                ).limit(41))

            session["db_return"] = data
            session["db_user"] = session.get("player_name")
        return jsonify(session.get("db_return"))
    
    else:
        data = request.get_json() or {}
        clan_tag = data.get("clanTag")
        if not clan_tag:
            return jsonify({"error": "Missing clanTag"}), 400

        clan_info = clan_collection.find_one({"clan_tag": clan_tag}, {"_id": 0})
        if clan_info is None:
            return jsonify({"error": "Clan not found"}), 404
        return jsonify(clan_info)

