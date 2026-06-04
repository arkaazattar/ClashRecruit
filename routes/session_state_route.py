"""Register routes for handling session state requests."""

from flask import Blueprint, jsonify, session

from ..api.clash_api import API
from ..config import headers
from ..services.mongo_db_client import get_clan_collection
from ..services.session_state import (
    get_session_state_payload,
    get_user_info_payload,
)
from .rate_limit import rate_limit
from .validation import RequestValidationError, normalize_tag

session_state_bp = Blueprint("session_state", __name__)


@session_state_bp.route("/session-state")
@rate_limit("session_state", limit=20, window_seconds=60)
def session_state():
    """Return current session status, player state, and active listing info."""
    username = session.get("player_name", "Guest")
    clan_tag = _normalized_session_tag("clan_tag")

    return jsonify(
        get_session_state_payload(
            username=username,
            recruit_status=bool(session.get("recruiter_status")),
            clan_tag=clan_tag,
            townhall=session.get("player_townhall"),
            townhall_weapon_level=session.get(
                "player_townhall_weapon_level"
            ),
            clan_collection=get_clan_collection() if clan_tag else None,
        )
    )


@session_state_bp.route("/session-state/user-info")
@rate_limit("session_state_user_info", limit=10, window_seconds=60)
def session_state_user_info():
    """Return extended player info for the current session when available."""
    player_tag = _normalized_session_tag("player_tag")

    return jsonify(
        get_user_info_payload(
            player_tag,
            lambda tag: API(tag, None, headers),
        )
    )


def _normalized_session_tag(field_name):
    value = session.get(field_name)
    if value is None or value == "Guest":
        return None

    try:
        return normalize_tag(value, field_name)
    except RequestValidationError:
        session.pop(field_name, None)
        return None
