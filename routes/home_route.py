from flask import request, session, Blueprint, jsonify
from ..api.clash_api import API
from ..config import headers

home_bp = Blueprint("home", __name__)

@home_bp.route("/", methods=["POST"])

def home():
    
    data = request.get_json()

    received_tag = data.get('playerTag')
    received_token = data.get('apiToken')
    session["player_tag"] = received_tag
    user = API(received_tag, received_token, headers)
    check_player_team = user.check_player()
    session["recruiter_status"] = user.recruiter_status

    if check_player_team == True:
        status = True
        reason = "Valid User"
        name = user.user_name
        session["player_name"] = name
        clan_tag = user.clantag
        session["clan_tag"] = clan_tag
        session["player_league"] = user.league
        session["player_townhall"] = user.townhall
        session["player_builderbase_trophies"] = user.builder_trophies
    else:
        status = False
        reason = f"{user.reason}"
        name = user.user_name
        session["player_name"] = name
        clan_tag = user.clantag
        session["clan_tag"] = clan_tag

    return jsonify({
        "message": status, 
        "receivedPlayerTag": reason,
        "recruit_status" : session.get("recruiter_status"),
        "player_name" : name,
        "clan_tag" : clan_tag
    })

@home_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": True})
