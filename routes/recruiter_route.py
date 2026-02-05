from flask import Blueprint, request, session, render_template, jsonify
from ..api.recruiter_api import Recruiter
from ..config import headers
from ..services.mongo_db_client import clan_collection
from datetime import datetime, timedelta, timezone
from ..services.maxtownhall import refresh

recruiter_bp = Blueprint("recruiter", __name__)

@recruiter_bp.route("/recruiter", methods= ['GET', 'POST'])
def recruit():
    
    user = Recruiter(session.get("player_tag"), session.get("clan_tag"), headers)
    user.pull_clan_requirements()
    if request.method == "GET":
        MAXTOWNHALL = refresh(headers)
        return jsonify({
            "oldRequiredTownhall" : user.requirements[2],
            "MAXTOWNHALL" : MAXTOWNHALL
        })
    
    # return jsonify(
    #     {
    #         "testing_return" : 123
    #     }
    # )

    data = request.get_json()    
    
    new_required_league = data.get("requiredLeague", None)
    new_required_builder_league = data.get("requiredBuilderLeague", None)
    new_required_townhall = data.get("requiredTownhall", None)
    user.requirements[0] = new_required_league
    user.requirements[1] = new_required_builder_league
    user.requirements[2] = new_required_townhall
    clan_info = user.lookup_clan()

    data = {
        "requirements": user.requirements,
        "clan_tag": session.get("clan_tag"),
        "player_tag": session.get("player_tag"),
        "clan_info": clan_info,
        "last_updated" : datetime.now(timezone.utc),
        "expires": datetime.now(timezone.utc) + timedelta(days = 7)
    }
    render_data = data.copy()
    
    existing = clan_collection.find_one({"clan_tag": data["clan_tag"]})
    if not existing:
        clan_collection.insert_one(data)
        clan_collection.create_index("expires", expireAfterSeconds=0)

    else: 
        clan_collection.update_one({"clan_tag" : session.get("clan_tag")}, 
                                   {'$set' : 
                                    {"requirements" : user.requirements, 
                                     "clan_info" : clan_info,
                                     "last_updated" : datetime.now(timezone.utc)
                                     }})

    return jsonify(render_data), 200