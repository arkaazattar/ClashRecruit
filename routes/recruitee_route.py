"""Register routes for handling recruitee requests."""

from flask import Blueprint, jsonify, request, session

from ..config import headers
from ..services.leagues import (
    get_builder_base_league_options,
    get_max_ranked_league,
    get_ranked_league_options,
)
from ..services.maxtownhall import refresh
from ..services.mongo_db_client import get_clan_collection
from ..services.recruitee_search import (
    get_recruitee_list_response,
    get_recruitee_post_response,
)
from .rate_limit import rate_limit
from .validation import (
    CLASH_WAR_FREQUENCIES,
    RequestValidationError,
    ensure_allowed_fields,
    ensure_exactly_one_field,
    ensure_object,
    get_json_object,
    normalize_tag,
    optional_enum,
    optional_int,
    optional_string,
    query_bool,
    query_int,
)

recruitee_bp = Blueprint("recruitee", __name__)

MAX_LIMIT = 200
MAX_CLAN_LEVEL = 99
MAX_CLAN_POINTS = 400000
RECRUITEE_PAYLOAD_FIELDS = {"clanTag", "filters"}
RECRUITEE_FILTER_FIELDS = {
    "name",
    "requirements",
    "minClanLevel",
    "clanPoints",
    "warFrequency",
    "location_id",
    "location",
}
RECRUITEE_REQUIREMENT_FIELDS = {"townhall", "league", "members"}
MEMBER_FILTER_FIELDS = {"min", "max"}
SOURCE_SORT_VALUES = {"community", "discovered"}


def _get_requested_limit(default_limit):
    """Return the validated `limit` query param capped to allowed bounds."""
    return query_int(
        request,
        "limit",
        default=default_limit,
        min_value=1,
        max_value=MAX_LIMIT,
    )


def _get_requested_offset():
    """Return the validated `offset` query param with a minimum of zero."""
    return query_int(request, "offset", default=0, min_value=0)


def _should_include_total():
    """Return whether the response should include paginated total metadata."""
    return query_bool(request, "includeTotal", default=False)


def _get_requested_source_sort():
    """Return source ordering preference for mixed live/imported results."""
    source_sort = request.args.get("sourceSort", "community").strip()
    if source_sort not in SOURCE_SORT_VALUES:
        raise RequestValidationError("sourceSort is invalid.")
    return source_sort


@recruitee_bp.get("/recruitee")
@rate_limit("recruitee_get", limit=60, window_seconds=60)
def recruitee_get():
    """Return clans for the current session with optional total metadata."""
    try:
        default_limit = 10
        requested_limit = _get_requested_limit(default_limit)
        requested_offset = _get_requested_offset()
        include_total = _should_include_total()
        source_sort = _get_requested_source_sort()
    except RequestValidationError as exc:
        return jsonify({"error": exc.message}), 400

    try:
        payload, status_code = get_recruitee_list_response(
            dict(session),
            limit=requested_limit,
            offset=requested_offset,
            include_total=include_total,
            source_sort=source_sort,
            clan_collection=get_clan_collection(),
        )
    except RequestValidationError as exc:
        return jsonify({"error": exc.message}), 400
    return jsonify(payload), status_code


@recruitee_bp.get("/recruitee/metadata")
@rate_limit("recruitee_metadata_get", limit=60, window_seconds=60)
def recruitee_metadata_get():
    """Return metadata needed to render recruitee filters."""
    return jsonify(
        {
            "builderBaseLeagueOptions": get_builder_base_league_options(),
            "leagueOptions": get_ranked_league_options(),
        }
    ), 200


@recruitee_bp.post("/recruitee")
@rate_limit("recruitee_post", limit=30, window_seconds=60)
def recruitee_post():
    """Return clan details by tag or a filtered clan list for recruitees."""
    try:
        default_limit = 10
        requested_limit = _get_requested_limit(default_limit)
        requested_offset = _get_requested_offset()
        include_total = _should_include_total()
        source_sort = _get_requested_source_sort()
        raw_form = _validate_recruitee_payload(get_json_object(request))
    except RequestValidationError as exc:
        return jsonify({"error": exc.message}), 400

    payload, status_code = get_recruitee_post_response(
        raw_form,
        limit=requested_limit,
        offset=requested_offset,
        include_total=include_total,
        source_sort=source_sort,
        clan_collection=get_clan_collection(),
    )
    return jsonify(payload), status_code


def _validate_recruitee_payload(payload):
    """Return normalized recruitee POST payload."""
    ensure_allowed_fields(payload, RECRUITEE_PAYLOAD_FIELDS, "recruitee")
    payload_mode = ensure_exactly_one_field(
        payload,
        RECRUITEE_PAYLOAD_FIELDS,
        "recruitee payload",
    )
    normalized = {}
    if payload_mode == "clanTag":
        normalized["clanTag"] = normalize_tag(payload["clanTag"], "clanTag")
        return normalized

    filters = ensure_object(payload["filters"], "filters")
    normalized["filters"] = _validate_filter_payload(filters)
    return normalized


def _validate_filter_payload(filters):
    ensure_allowed_fields(filters, RECRUITEE_FILTER_FIELDS, "filter")
    normalized = {}

    name = optional_string(filters, "name", max_length=120)
    if name:
        normalized["name"] = name

    requirements = ensure_object(
        filters.get("requirements"),
        "filters.requirements",
    )
    ensure_allowed_fields(
        requirements,
        RECRUITEE_REQUIREMENT_FIELDS,
        "requirements",
    )
    normalized_requirements = {}
    townhall = optional_int(
        requirements,
        "townhall",
        min_value=0,
    )
    if townhall is not None:
        max_townhall = refresh(headers)
        if townhall > max_townhall:
            raise RequestValidationError(
                f"townhall must be at most {max_townhall}."
            )
        normalized_requirements["townhall"] = townhall
    league = optional_int(requirements, "league", min_value=0)
    if league is not None:
        max_ranked_league = get_max_ranked_league()
        if league > max_ranked_league:
            raise RequestValidationError(
                f"league must be at most {max_ranked_league}."
            )
        normalized_requirements["league"] = league

    members = ensure_object(
        requirements.get("members"),
        "filters.requirements.members",
    )
    normalized_members = _validate_members_filter(members)
    if normalized_members:
        normalized_requirements["members"] = normalized_members
    if normalized_requirements:
        normalized["requirements"] = normalized_requirements

    min_clan_level = optional_int(
        filters,
        "minClanLevel",
        min_value=0,
        max_value=MAX_CLAN_LEVEL,
    )
    if min_clan_level is not None:
        normalized["minClanLevel"] = min_clan_level
    clan_points = optional_int(
        filters,
        "clanPoints",
        min_value=0,
        max_value=MAX_CLAN_POINTS,
    )
    if clan_points is not None:
        normalized["clanPoints"] = clan_points

    war_frequency = optional_enum(
        filters,
        "warFrequency",
        CLASH_WAR_FREQUENCIES,
    )
    if war_frequency:
        normalized["warFrequency"] = war_frequency

    location_id = optional_int(filters, "location_id", min_value=1)
    if location_id is not None:
        normalized["location_id"] = location_id
    else:
        location = optional_string(filters, "location", max_length=120)
        if location:
            normalized["location"] = location

    return normalized


def _validate_members_filter(members):
    ensure_allowed_fields(members, MEMBER_FILTER_FIELDS, "members")
    normalized = {}
    min_members = optional_int(members, "min", min_value=0, max_value=50)
    max_members = optional_int(members, "max", min_value=0, max_value=50)
    if (
        min_members is not None
        and max_members is not None
        and min_members > max_members
    ):
        raise RequestValidationError(
            "filters.requirements.members.min must be less than or equal "
            "to max."
        )
    if min_members is not None:
        normalized["min"] = min_members
    if max_members is not None:
        normalized["max"] = max_members
    return normalized
