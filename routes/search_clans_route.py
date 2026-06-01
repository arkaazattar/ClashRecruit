"""Register routes for handling clan search requests."""

from flask import Blueprint, jsonify, request, session

from ..api.recruitee_api import Recruitee
from ..config import headers
from .rate_limit import rate_limit
from .validation import (
    CLASH_WAR_FREQUENCIES,
    RequestValidationError,
    ensure_allowed_fields,
    get_json_object,
    optional_enum,
    optional_int,
    optional_string,
)

search_clans_bp = Blueprint("search_clans", __name__)

MAX_CLAN_LEVEL = 99
MAX_CLAN_POINTS = 400000
SEARCH_FILTER_FIELDS = {
    "name",
    "warFrequency",
    "locationId",
    "minMembers",
    "maxMembers",
    "minClanPoints",
    "minClanLevel",
    "labelIds",
    "limit",
}
PAGINATION_FIELDS = {"after"}
ALLOWED_SEARCH_FIELDS = SEARCH_FILTER_FIELDS | PAGINATION_FIELDS


@search_clans_bp.post("/search_clans")
@rate_limit("search_clans", limit=10, window_seconds=60)
def search_clans():
    """Search clans using provided filters and return matching results."""
    try:
        filters, after = _validate_search_filters(get_json_object(request))
    except RequestValidationError as exc:
        return jsonify({"error": exc.message}), 400

    user = Recruitee(
        session.get("player_tag"),
        headers,
    )
    clans = user.searchClan(filters, after)

    error = clans.get("error")
    if error:
        if (
            error.get("reason") == "badRequest"
            and error.get("message")
            == "At least one filtering parameter must exist"
        ):
            return jsonify(
                {
                    "error": (
                        "Add at least one random clan filter before searching."
                    ),
                    "reason": error.get("reason"),
                    "message": error.get("message"),
                }
            ), 400

        return jsonify(
            {
                "error": error.get("message") or "Failed to search clans.",
                "reason": error.get("reason"),
            }
        ), error.get("status") or 400

    return jsonify(clans)


def _validate_search_filters(filters):
    """Return normalized Clash clan search filters and pagination cursor."""
    ensure_allowed_fields(filters, ALLOWED_SEARCH_FIELDS, "search")

    normalized = {}
    name = optional_string(filters, "name", max_length=120)
    if name:
        normalized["name"] = name

    war_frequency = optional_enum(
        filters,
        "warFrequency",
        CLASH_WAR_FREQUENCIES,
    )
    if war_frequency:
        normalized["warFrequency"] = war_frequency

    _copy_optional_int(
        filters,
        normalized,
        "locationId",
        min_value=1,
    )
    min_members = _copy_optional_int(
        filters,
        normalized,
        "minMembers",
        min_value=1,
        max_value=50,
    )
    max_members = _copy_optional_int(
        filters,
        normalized,
        "maxMembers",
        min_value=1,
        max_value=50,
    )
    if (
        min_members is not None
        and max_members is not None
        and min_members > max_members
    ):
        raise RequestValidationError(
            "minMembers must be less than or equal to maxMembers."
        )

    _copy_optional_int(
        filters,
        normalized,
        "minClanPoints",
        min_value=0,
        max_value=MAX_CLAN_POINTS,
    )
    _copy_optional_int(
        filters,
        normalized,
        "minClanLevel",
        min_value=1,
        max_value=MAX_CLAN_LEVEL,
    )
    _copy_optional_int(
        filters,
        normalized,
        "limit",
        min_value=1,
        max_value=100,
    )

    label_ids = optional_string(filters, "labelIds", max_length=240)
    if label_ids:
        normalized["labelIds"] = _validate_label_ids(label_ids)

    after = optional_string(filters, "after", max_length=512)

    if not any(key in normalized for key in SEARCH_FILTER_FIELDS - {"limit"}):
        raise RequestValidationError(
            "Add at least one random clan filter before searching."
        )

    return normalized, after


def _copy_optional_int(filters, normalized, field_name, **bounds):
    value = optional_int(filters, field_name, **bounds)
    if value is not None:
        normalized[field_name] = value
    return value


def _validate_label_ids(label_ids):
    ids = [label_id.strip() for label_id in label_ids.split(",")]
    if not all(label_id.isdecimal() for label_id in ids):
        raise RequestValidationError(
            "labelIds must be a comma-separated list of integers."
        )
    return ",".join(ids)
