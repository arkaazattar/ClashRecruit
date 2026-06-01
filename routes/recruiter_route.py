"""Register routes for handling recruiter requests."""

from flask import Blueprint, jsonify, request, session

from ..services.rate_limiter import is_rate_limited
from ..services.recruiter_listing import (
    get_recruiter_listing_page,
    handle_recruiter_listing_action,
)
from .validation import (
    RequestValidationError,
    ensure_allowed_fields,
    get_json_object,
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
MAX_BUILDER_BASE_TROPHIES = 10000
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

    try:
        data = _validate_recruiter_payload(get_json_object(request))
    except RequestValidationError as exc:
        return jsonify({"error": exc.message}), 400

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
        max_value=MAX_BUILDER_BASE_TROPHIES,
    )
    normalized["requiredTownhall"] = required_int(
        data,
        "requiredTownhall",
        min_value=0,
        max_value=25,
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
