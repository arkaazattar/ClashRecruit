"""Register routes for handling recruiter requests."""

from flask import Blueprint, jsonify, request, session

from ..services.recruiter_listing import (
    get_recruiter_listing_page,
    handle_recruiter_listing_action,
)
from ..services.rate_limiter import is_rate_limited

recruiter_bp = Blueprint("recruiter", __name__)
RECRUITER_GET_RATE_LIMIT = 10
RECRUITER_GET_RATE_WINDOW_SECONDS = 60
RECRUITER_ACTION_RATE_WINDOW_SECONDS = 60
RECRUITER_ACTION_RATE_LIMITS = {
    "new": 1,
    "update": 2,
}


@recruiter_bp.route("/recruiter", methods=["GET", "POST"])
def recruit():
    """Return recruiter listing data or create, update, and remove listings."""
    if not session.get("recruiter_status"):
        return jsonify({"message": "Forbidden"}), 403

    if request.method == "GET":
        limited_response = _rate_limit_recruiter_get()
        if limited_response:
            return limited_response

        payload, status_code = get_recruiter_listing_page(
            session.get("clan_tag")
        )
        return jsonify(payload), status_code

    data = request.get_json(silent=True) or {}
    limited_response = _rate_limit_recruiter_action(data)
    if limited_response:
        return limited_response

    payload, status_code = handle_recruiter_listing_action(
        session.get("clan_tag"),
        session.get("player_tag"),
        data,
    )
    return jsonify(payload), status_code


def _rate_limit_recruiter_get():
    """Return a 429 response when recruiter page loads are being spammed."""
    limited, retry_after = is_rate_limited(
        f"recruiter_get:{request.remote_addr or 'unknown'}",
        limit=RECRUITER_GET_RATE_LIMIT,
        window_seconds=RECRUITER_GET_RATE_WINDOW_SECONDS,
    )
    if not limited:
        return None

    response = jsonify(
        {"message": "Too many requests. Please try again shortly."}
    )
    response.headers["Retry-After"] = str(retry_after)
    return response, 429


def _rate_limit_recruiter_action(data):
    """Return a 429 response when a listing mutation is being spammed."""
    action = data.get("status")
    limit = RECRUITER_ACTION_RATE_LIMITS.get(action)
    if limit is None:
        return None

    clan_tag = session.get("clan_tag") or "unknown"
    limited, retry_after = is_rate_limited(
        f"recruiter_action:{action}:{clan_tag}",
        limit=limit,
        window_seconds=RECRUITER_ACTION_RATE_WINDOW_SECONDS,
    )
    if not limited:
        return None

    response = jsonify(
        {
            "message": (
                "Please wait before changing your listing again."
            )
        }
    )
    response.headers["Retry-After"] = str(retry_after)
    return response, 429
