"""Register home routes for login, logout, and database count requests."""

from datetime import datetime, timezone

from flask import Blueprint, jsonify, request, session

from ..api.clash_api import API
from ..config import headers
from ..services.mongo_db_client import get_clan_collection
from ..services.rate_limiter import is_rate_limited
from .rate_limit import rate_limit
from .validation import (
    RequestValidationError,
    ensure_allowed_fields,
    get_json_object,
    normalize_tag,
    required_string,
)

home_bp = Blueprint("home", __name__)
LOGIN_RATE_LIMIT = 5
LOGIN_RATE_WINDOW_SECONDS = 5
LOGIN_FIELDS = {"playerTag", "apiToken"}


@home_bp.post("/")
def home():
    """Validate a player, store session data, and return login details."""
    limiter_key = f"login:{request.remote_addr or 'unknown'}"
    limited, retry_after = is_rate_limited(
        limiter_key,
        limit=LOGIN_RATE_LIMIT,
        window_seconds=LOGIN_RATE_WINDOW_SECONDS,
    )
    if limited:
        response = jsonify(
            {
                "message": False,
                "receivedPlayerTag": (
                    "Too many login attempts. Please try again shortly."
                ),
            }
        )
        response.headers["Retry-After"] = str(retry_after)
        return response, 429

    try:
        data = get_json_object(request)
        ensure_allowed_fields(data, LOGIN_FIELDS, "login")
        received_tag = normalize_tag(data.get("playerTag"), "playerTag")
        received_token = required_string(data, "apiToken", max_length=128)
    except RequestValidationError as exc:
        return jsonify({"error": exc.message}), 400

    session.pop("player_league", None)
    session.pop("player_townhall", None)
    session.pop("player_townhall_weapon_level", None)
    session.pop("player_builderbase_trophies", None)
    session["player_tag"] = received_tag
    user = API(received_tag, received_token, headers)
    check_player_team = user.check_player()
    session["recruiter_status"] = user.recruiter_status

    if check_player_team:
        status = True
        reason = "Valid User"
        name = user.user_name
        session["player_name"] = name
        clan_tag = user.clantag
        session["clan_tag"] = clan_tag
        session["player_league"] = user.league
        session["player_townhall"] = user.townhall
        session["player_townhall_weapon_level"] = user.townhallWeaponLevel
        session["player_builderbase_trophies"] = user.builder_trophies
    else:
        status = False
        reason = f"{user.reason}"
        name = user.user_name
        session["player_name"] = name
        clan_tag = user.clantag
        session["clan_tag"] = clan_tag

    return jsonify(
        {
            "message": status,
            "receivedPlayerTag": reason,
            "recruit_status": session.get("recruiter_status"),
            "player_name": name,
            "clan_tag": clan_tag,
        }
    )


@home_bp.get("/database_count")
@rate_limit("database_count", limit=30, window_seconds=60)
def database_count():
    """Return the current number of stored clans in the database."""
    clan_collection = get_clan_collection()
    return jsonify(
        {
            "clan_count": clan_collection.count_documents(
                {"expires": {"$gt": datetime.now(timezone.utc)}}
            )
        }
    )


@home_bp.post("/logout")
@rate_limit("logout", limit=10, window_seconds=60)
def logout():
    """Clear the current session and confirm logout."""
    session.clear()
    return jsonify({"message": True})
