from flask import Blueprint, request, session, jsonify
from ..api.recruiter_api import Recruiter
from ..config import headers
from ..services.mongo_db_client import clan_collection
from datetime import datetime, timedelta, timezone
from ..services.maxtownhall import refresh

recruiter_bp = Blueprint("recruiter", __name__)

@recruiter_bp.route("/recruiter", methods= ['GET', 'POST'])
def recruit():
    existing = clan_collection.find_one({"clan_tag": session.get("clan_tag")})
    
    user = Recruiter(session.get("player_tag"), session.get("clan_tag"), headers)
    user.pull_clan_requirements()
    if request.method == "GET":
        if existing:
            existing = existing["expires"]
        MAXTOWNHALL = refresh(headers)
        return jsonify({
            "oldRequiredTownhall" : user.requirements[2],
            "MAXTOWNHALL" : MAXTOWNHALL,
            "status" : existing
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

    elif data.get("status") == "update":
        expiry = datetime.now(timezone.utc) + timedelta(days=7) 
        clan_collection.update_one({"clan_tag" : session.get("clan_tag")}, 
                                   {'$set' : 
                                    {
                                     "last_updated" : datetime.now(timezone.utc),
                                     "expires" : expiry
                                     }})
        render_data = {}
        render_data["status"] = expiry
        
    return jsonify(render_data), 200
