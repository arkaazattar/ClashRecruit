"""Register routes for saved a users saved clans."""

from flask import Blueprint, jsonify, session

from ..services.mongo_db_client import get_clan_collection, get_user_collection
from ..services.saved_clans import (
    add_saved_clan as add_saved_clan_service,
)
from ..services.saved_clans import (
    delete_saved_clan as delete_saved_clan_service,
)
from ..services.saved_clans import (
    get_saved_clans_payload,
)
from .rate_limit import rate_limit
from .validation import RequestValidationError, normalize_tag

saved_clans_bp = Blueprint("saved_clans", __name__)


@saved_clans_bp.get("/saved-clans")
@rate_limit("saved_clans_get", limit=30, window_seconds=60)
def get_saved_clans():
    """Return the current user's saved clans and limits as JSON."""
    player_tag = _validated_session_player_tag()
    if player_tag is None:
        return jsonify({"message": "Unauthorized"}), 401

    payload = get_saved_clans_payload(
        player_tag,
        get_user_collection(),
        get_clan_collection(),
    )
    return jsonify(payload), 200


@saved_clans_bp.post("/saved-clans/<clan_tag>")
@rate_limit("saved_clans_post", limit=20, window_seconds=60)
def add_saved_clan(clan_tag):
    """Return a JSON response after saving a clan tag for the current user.

    Args:
        clan_tag (str): The clan tag to save for the current user.
    """
    player_tag = _validated_session_player_tag()
    if player_tag is None:
        return jsonify({"message": "Unauthorized"}), 401

    try:
        normalized_tag = normalize_tag(clan_tag, "clan_tag")
    except RequestValidationError as exc:
        return jsonify({"error": exc.message}), 400

    payload, status_code = add_saved_clan_service(
        player_tag,
        normalized_tag,
        get_user_collection(),
    )
    return jsonify(payload), status_code


@saved_clans_bp.delete("/saved-clans/<clan_tag>")
@rate_limit("saved_clans_delete", limit=20, window_seconds=60)
def delete_saved_clan(clan_tag):
    """Return a JSON response after removing a saved clan tag for the user.

    Args:
        clan_tag (str): The clan tag to remove from the current user's saved
            clans.
    """
    player_tag = _validated_session_player_tag()
    if player_tag is None:
        return jsonify({"message": "Unauthorized"}), 401

    try:
        normalized_tag = normalize_tag(clan_tag, "clan_tag")
    except RequestValidationError as exc:
        return jsonify({"error": exc.message}), 400

    payload, status_code = delete_saved_clan_service(
        player_tag,
        normalized_tag,
        get_user_collection(),
    )
    return jsonify(payload), status_code


def _validated_session_player_tag():
    try:
        return normalize_tag(session.get("player_tag"), "player_tag")
    except RequestValidationError:
        return None
