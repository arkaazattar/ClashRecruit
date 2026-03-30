from flask import Blueprint, request, session, jsonify
from ..api.recruiter_api import Recruiter
from ..config import headers
from ..services.mongo_db_client import clan_collection
from datetime import datetime, timedelta, timezone
from ..services.maxtownhall import refresh

recruiter_bp = Blueprint("recruiter", __name__)

@recruiter_bp.route("/recruiter", methods= ['GET', 'POST'])
def recruit():
    existing = clan_collection.find_one({
        "clan_tag": session.get("clan_tag"),
        "source": {"$ne": "clash_api_import"},
    })
    
    user = Recruiter(session.get("player_tag"), session.get("clan_tag"), headers)
    user.pull_clan_requirements()
    if request.method == "GET":
        if existing:
            required_league = existing["requirements"][0]
            required_builder_league = existing["requirements"][1]
            required_townhall = existing["requirements"][2]
            clan_description = {
                "description": existing.get("clan_info", {}).get("description", "")
            }
            status = existing["expires"]
        else:
            required_league = user.requirements[0]
            required_builder_league = user.requirements[1]
            required_townhall = user.requirements[2]
            clan_description = user.lookup_clan("description")
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
            "source": "live_listing",
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
        query = {
            "source": "live_listing",
            "requirements": user.requirements,
            "clan_info.description": data.get("description"),
            "last_updated": datetime.now(timezone.utc)
        }

        if data.get("updateExpiry") is True:
            expiry = datetime.now(timezone.utc) + timedelta(days=7)
            query["expires"] = expiry
            status = expiry
        else:
            status = data.get("expiry")

        clan_collection.update_one({"clan_tag" : session.get("clan_tag"), "source": {"$ne": "clash_api_import"}}, 
                                   {"$set": query})
        render_data = {
            "status": status,
            "message": "Listing updated successfully."
        }

    elif data.get("status") == "removeListing":
        deleted = clan_collection.delete_one({
            "clan_tag": session.get("clan_tag"),
            "source": {"$ne": "clash_api_import"},
        })
        if deleted.deleted_count:
            message = "Successfully deleted entry."
            return jsonify({"message": message}), 200

        return jsonify({"message": "Failed to delete."}), 404
        
    return jsonify(render_data), 200
