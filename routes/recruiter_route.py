"""Register routes for handling recruiter requests."""

from flask import Blueprint, jsonify, request, session

from ..config import headers
from ..services.builder_base_leagues import BUILDER_BASE_LEAGUE_MAX_ID
from ..services.maxtownhall import refresh
from ..services.rate_limiter import is_rate_limited
from ..services.recruiter_listing import (
    get_recruiter_listing_page,
    handle_recruiter_listing_action,
)
from .validation import (
    RequestValidationError,
    ensure_allowed_fields,
    get_json_object,
    normalize_tag,
    optional_bool,
    optional_string,
    required_int,
)

recruiter_bp = Blueprint("recruiter", __name__)
RECRUITER_GET_RATE_LIMIT = 10
RECRUITER_GET_RATE_WINDOW_SECONDS = 60
RECRUITER_ACTION_RATE_WINDOW_SECONDS = 60
RECRUITER_ACTION_RATE_LIMITS = {
    "new": 1,
    "update": 2,
}
NEW_LISTING_FIELDS = {
    "status",
    "requiredLeague",
    "requiredBuilderLeague",
    "requiredTownhall",
    "description",
}
UPDATE_LISTING_FIELDS = NEW_LISTING_FIELDS | {"updateExpiry", "expiry"}
REMOVE_LISTING_FIELDS = {"status"}


@recruiter_bp.route("/recruiter", methods=["GET", "POST"])
def recruit():
    """Return recruiter listing data or create, update, and remove listings."""
    try:
        session_data = _validate_recruiter_session()
    except RequestValidationError as exc:
        return jsonify({"message": exc.message}), 403

    if request.method == "GET":
        limited_response = _rate_limit_recruiter_get()
        if limited_response:
            return limited_response

        payload, status_code = get_recruiter_listing_page(
            session_data["clan_tag"]
        )
        return jsonify(payload), status_code

    try:
        data = _validate_recruiter_payload(get_json_object(request))
        if data.get("status") == "new":
            session_data["player_tag"] = _validated_session_tag(
                "player_tag",
            )
    except RequestValidationError as exc:
        return jsonify({"error": exc.message}), 400

    limited_response = _rate_limit_recruiter_action(data, session_data)
    if limited_response:
        return limited_response

    payload, status_code = handle_recruiter_listing_action(
        session_data["clan_tag"],
        session_data.get("player_tag"),
        data,
    )
    return jsonify(payload), status_code


def _validate_recruiter_session():
    """Return normalized recruiter session identity data."""
    if session.get("recruiter_status") is not True:
        raise RequestValidationError("Forbidden")

    return {"clan_tag": _validated_session_tag("clan_tag")}


def _validated_session_tag(field_name):
    return normalize_tag(session.get(field_name), field_name)


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


def _rate_limit_recruiter_action(data, session_data):
    """Return a 429 response when a listing mutation is being spammed."""
    action = data.get("status")
    limit = RECRUITER_ACTION_RATE_LIMITS.get(action)
    if limit is None:
        return None

    clan_tag = session_data["clan_tag"]
    limited, retry_after = is_rate_limited(
        f"recruiter_action:{action}:{clan_tag}",
        limit=limit,
        window_seconds=RECRUITER_ACTION_RATE_WINDOW_SECONDS,
    )
    if not limited:
        return None

    response = jsonify(
        {"message": ("Please wait before changing your listing again.")}
    )
    response.headers["Retry-After"] = str(retry_after)
    return response, 429


def _validate_recruiter_payload(data):
    """Return normalized recruiter action data."""
    status = optional_string(data, "status")
    if status not in {"new", "update", "removeListing"}:
        raise RequestValidationError("Invalid listing status.")

    normalized = {"status": status}
    if status == "removeListing":
        ensure_allowed_fields(data, REMOVE_LISTING_FIELDS, "recruiter")
        return normalized

    allowed_fields = (
        UPDATE_LISTING_FIELDS if status == "update" else NEW_LISTING_FIELDS
    )
    ensure_allowed_fields(data, allowed_fields, "recruiter")

    normalized["requiredLeague"] = required_int(
        data,
        "requiredLeague",
        min_value=0,
        max_value=34,
    )
    normalized["requiredBuilderLeague"] = required_int(
        data,
        "requiredBuilderLeague",
        min_value=0,
        max_value=BUILDER_BASE_LEAGUE_MAX_ID,
    )
    normalized["requiredTownhall"] = required_int(
        data,
        "requiredTownhall",
        min_value=0,
    )
    max_townhall = refresh(headers)
    if normalized["requiredTownhall"] > max_townhall:
        raise RequestValidationError(
            f"requiredTownhall must be at most {max_townhall}."
        )
    normalized["description"] = optional_string(
        data,
        "description",
        max_length=5000,
    )

    if status == "update":
        update_expiry = optional_bool(data, "updateExpiry")
        if update_expiry is None:
            raise RequestValidationError("updateExpiry is required.")
        normalized["updateExpiry"] = update_expiry

    return normalized
