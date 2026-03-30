from datetime import datetime, timezone

from flask import Blueprint, jsonify, session

from ..api.clash_api import API
from ..config import headers
from ..services.mongo_db_client import clan_collection

session_state_bp = Blueprint("session_state", __name__)

@session_state_bp.route("/session-state")
def session_state():
        username = session.get("player_name", "Guest")
        recruit_status = bool(session.get("recruiter_status"))
        has_active_listing = False
        townhall = None
        townhallWeaponLevel = None
        clan_tag = session.get("clan_tag")

        if username != "Guest":  
            player_tag = session.get("player_tag")
            user = API(player_tag, None, headers)
            user.check_player()
            townhall = user.townhall
            townhallWeaponLevel = user.townhallWeaponLevel
            clan_tag = user.clantag or clan_tag
        
        if clan_tag:
            now = datetime.now(timezone.utc)
            listing = clan_collection.find_one(
                {
                    "clan_tag": clan_tag,
                    "expires": {"$gt": now}
                },
                {"_id": 1}
            )
            has_active_listing = listing is not None

        return jsonify(
            username=username,
            recruit_status=recruit_status,
            has_active_listing=has_active_listing,
            townhall=townhall,
            townhallWeaponLevel=townhallWeaponLevel
        )

@session_state_bp.route("/session-state/user-info")
def session_state_user_info():
        player_tag = session.get("player_tag", "Guest")

        if player_tag == "Guest":
            return jsonify({})

        user = API(player_tag, None, headers)
        stats = user.check_player([
            "expLevel",
            "leagueTier",
            "builderBaseLeague",
            "builderHallLevel",
            "clan"
        ])

        return jsonify(stats or {})
