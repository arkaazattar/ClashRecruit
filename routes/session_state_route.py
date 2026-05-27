"""Register routes for handling session state requests."""

from datetime import datetime, timezone

from flask import Blueprint, jsonify, session

from ..api.clash_api import API
from ..config import headers
from ..services.mongo_db_client import get_clan_collection
from .rate_limit import rate_limit

session_state_bp = Blueprint("session_state", __name__)


@session_state_bp.route("/session-state")
@rate_limit("session_state", limit=20, window_seconds=60)
def session_state():
    """Return current session status, player state, and active listing info."""
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
        clan_collection = get_clan_collection()
        now = datetime.now(timezone.utc)
        listing = clan_collection.find_one(
            {"clan_tag": clan_tag, "expires": {"$gt": now}}, {"_id": 1}
        )
        has_active_listing = listing is not None

    return jsonify(
        username=username,
        recruit_status=recruit_status,
        has_active_listing=has_active_listing,
        townhall=townhall,
        townhallWeaponLevel=townhallWeaponLevel,
    )


@session_state_bp.route("/session-state/user-info")
@rate_limit("session_state_user_info", limit=10, window_seconds=60)
def session_state_user_info():
    """Return extended player info for the current session when available."""
    player_tag = session.get("player_tag", "Guest")

    if player_tag == "Guest":
        return jsonify({})

    user = API(player_tag, None, headers)
    stats = user.check_player(
        [
            "expLevel",
            "leagueTier",
            "builderBaseLeague",
            "builderHallLevel",
            "clan",
        ]
    )

    return jsonify(stats or {})
