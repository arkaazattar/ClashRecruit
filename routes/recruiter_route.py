from flask import Blueprint, request, session, jsonify
from datetime import datetime, timedelta, timezone
from ..api.recruiter_api import Recruiter
from ..config import headers
from ..services.mongo_db_client import clan_collection
from ..services.maxtownhall import refresh

recruiter_bp = Blueprint("recruiter", __name__)

@recruiter_bp.route("/recruiter", methods= ['GET', 'POST'])
def recruit():
    if not session.get("recruiter_status"):
        return jsonify({"message": "Forbidden"}), 403
 
    existing = clan_collection.find_one({"clan_tag": session.get("clan_tag")})
    
    user = Recruiter(session.get("player_tag"), session.get("clan_tag"), headers)
    user.pull_clan_requirements()
    if request.method == "GET":
        if existing:
            required_league = existing["requirements"][0]
            required_builder_league = existing["requirements"][1]
            required_townhall = existing["requirements"][2]
            clan_description = existing["clan_info"]["description"]
            status = existing["expires"]
        else:
            required_league = user.requirements[0]
            required_builder_league = user.requirements[1]
            required_townhall = user.requirements[2]
            clan_description = user.lookup_clan("description")["description"]
            status = None

        MAXTOWNHALL = refresh(headers)
        return jsonify({
            "oldRequiredLeague": required_league,
            "oldRequiredBuilderLeague": required_builder_league,
            "oldRequiredTownhall" : required_townhall,
            "MAXTOWNHALL" : MAXTOWNHALL,
            "clanDescription" : clan_description,
            "status" : status
        })
    
    data = request.get_json()    
    new_required_league = data.get("requiredLeague", None)
    new_required_builder_league = data.get("requiredBuilderLeague", None)
    new_required_townhall = data.get("requiredTownhall", None)
    user.requirements[0] = new_required_league
    user.requirements[1] = new_required_builder_league
    user.requirements[2] = new_required_townhall
    clan_info = user.lookup_clan()
    
    #may need to 403 error if existing
    if data.get("status") == "new":
        expiry = datetime.now(timezone.utc) + timedelta(days=7) 
        clan_info["description"] = data.get("description")
        data = {
            "requirements": user.requirements,
            "name": clan_info.get("name"),
            "clan_tag": session.get("clan_tag"),
            "player_tag": session.get("player_tag"),
            "clan_info": clan_info,
            "last_updated" : datetime.now(timezone.utc),
            "expires": expiry
        }
        render_data = data.copy()
        clan_collection.insert_one(data)
        render_data["status"] = expiry
        render_data["message"] = "Listing created successfully."

    elif data.get("status") == "update":
        render_data = {}
        query = {
            "requirements": user.requirements,
            "clan_info.description": data.get("description"),
            "last_updated": datetime.now(timezone.utc)
        }

        if data.get("updateExpiry") is True:
            expiry = datetime.now(timezone.utc) + timedelta(days=7)
            query["expires"] = expiry
            render_data["status"] = expiry
        else:
            render_data["status"] = data.get("expiry")

        clan_collection.update_one(
            {"clan_tag": session.get("clan_tag")},
            {"$set": query}
        )
        render_data["message"] = "Listing updated successfully."

    elif data.get("status") == "removeListing":
        deleted = clan_collection.delete_one({
            "clan_tag": session.get("clan_tag")
        })
        if deleted: message = "Successfully deleted entry."

        else: 
            message = "Failed to delete." 
            return jsonify(render_data ={"message" : message}), 404

        render_data = {
            "message" : message
        }

    return jsonify(render_data), 200
