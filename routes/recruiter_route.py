from flask import Blueprint, request, session, render_template
from ..api.recruiter_api import Recruiter
from ..config import headers
from ..services.mongo_db_client import clan_collection
from datetime import datetime, timedelta, timezone

recruiter_bp = Blueprint("recruiter", __name__)

@recruiter_bp.route("/recruiter", methods= ['GET', 'POST'])
def recruit():
    user_required_league = 0
    if request.method == 'POST':
        
        user_required_league = int(request.form.get("required_league"))
    
    user = Recruiter(session.get("player_tag"), session.get("clan_tag"), headers)
    requirements = user.pull_clan_requirements()
    requirements[0] = user_required_league
    clan_info = user.lookup_clan()

    data = {
        "requirements": requirements,
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
                                    {"requirements" : requirements, 
                                     "clan_info" : clan_info,
                                     "last_updated" : datetime.now(timezone.utc)
                                     }})

    return render_template("recruiter.html", data = render_data)