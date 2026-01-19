from flask import Blueprint, session, render_template
from ..services.mongo_db_client import clan_collection

recruitee_bp = Blueprint("recruitee", __name__)

@recruitee_bp.route("/recruitee")
def recruitee():

    clan_list = list(clan_collection.find({
        "requirements.1": {"$lte" : session.get("player_builderbase_trophies")},
        "requirements.2": {"$lte" : session.get("player_townhall")},
        "requirements.0": {"$lte" : session.get("player_league")                              
        }},
        {"_id" : 0}        
        ).limit(20))
    # print(clan_list)
    return render_template("recruitee.html", clan_list = clan_list)