"""Register routes for handling recruitee requests."""

import re

from flask import Blueprint, jsonify, request, session

from ..services.mongo_db_client import get_clan_collection
from .rate_limit import rate_limit
from .validation import (
    RequestValidationError,
    ensure_object,
    get_json_object,
    normalize_tag,
    optional_int,
    optional_string,
    query_int,
)

recruitee_bp = Blueprint("recruitee", __name__)

MAX_LIMIT = 200


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
    return request.args.get("includeTotal", "0") == "1"


@recruitee_bp.get("/recruitee")
@rate_limit("recruitee_get", limit=60, window_seconds=60)
def recruitee_get():
    """Return clans for the current session with optional total metadata."""
    try:
        default_limit = 10
        requested_limit = _get_requested_limit(default_limit)
        requested_offset = _get_requested_offset()
    except RequestValidationError as exc:
        return jsonify({"error": exc.message}), 400

    clan_collection = get_clan_collection()
    player_name = session.get("player_name", None)

    if not player_name or player_name == "Guest":
        base_query = {}
    else:
        base_query = {
            "requirements.0": {"$lte": session.get("player_league")},
            "requirements.1": {
                "$lte": session.get("player_builderbase_trophies")
            },
            "requirements.2": {"$lte": session.get("player_townhall")},
        }

    data = list(
        clan_collection.find(base_query, {"_id": 0})
        .sort([("last_updated", -1), ("clan_tag", 1)])
        .skip(requested_offset)
        .limit(requested_limit)
    )

    if not _should_include_total():
        return jsonify(data)

    total = clan_collection.count_documents(base_query)
    return jsonify(
        {
            "items": data,
            "total": total,
            "limit": requested_limit,
            "offset": requested_offset,
        }
    )


@recruitee_bp.post("/recruitee")
@rate_limit("recruitee_post", limit=30, window_seconds=60)
def recruitee_post():
    """Return clan details by tag or a filtered clan list for recruitees."""
    try:
        default_limit = 10
        requested_limit = _get_requested_limit(default_limit)
        requested_offset = _get_requested_offset()
        raw_form = _validate_recruitee_payload(get_json_object(request))
    except RequestValidationError as exc:
        return jsonify({"error": exc.message}), 400

    clan_collection = get_clan_collection()

    clan_tag = raw_form.get("clanTag")
    if clan_tag is not None:
        data = clan_collection.find_one({"clan_tag": clan_tag}, {"_id": 0})
        if data is None:
            return jsonify({"error": "Clan not found"}), 404
        return jsonify(data)


    filters = raw_form.get("filters", {})
    query = {}

    name = filters.get("name", None)
    if name:
        query["name"] = {"$regex": re.escape(name.strip()), "$options": "i"}
    requirements = filters.get("requirements", {})
    min_townhall = requirements.get("townhall", None)
    min_league = requirements.get("league", None)
    if min_townhall is not None:
        query["requirements.2"] = {"$gte": min_townhall}
    if min_league is not None:
        query["requirements.0"] = {"$gte": min_league}

    min_clan_level = filters.get("minClanLevel", None)
    if min_clan_level is not None:
        query["clan_info.clan_level"] = {"$gte": min_clan_level}

    min_clan_points = filters.get("clanPoints", None)
    if min_clan_points is not None:
        query["clan_info.clanPoints"] = {"$gte": min_clan_points}

    members = requirements.get("members", {})
    min_members = members.get("min", None)
    max_members = members.get("max", None)
    if min_members is not None or max_members is not None:
        member_range = {}
        if min_members is not None:
            member_range["$gte"] = min_members
        if max_members is not None:
            member_range["$lte"] = max_members
        query["clan_info.member_count"] = member_range
    war_frequency = filters.get("warFrequency", None)
    if war_frequency:
        query["clan_info.warFrequency"] = war_frequency

    location_id = filters.get("location_id", None)
    if location_id:
        try:
            query["clan_info.location.id"] = int(location_id)
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid location_id"}), 400
    else:
        location_name = filters.get("location", None)
        if location_name:
            query["clan_info.location.name"] = location_name

    data = list(
        clan_collection.find(query, {"_id": 0})
        .sort([("last_updated", -1), ("clan_tag", 1)])
        .skip(requested_offset)
        .limit(requested_limit)
    )

    if not _should_include_total():
        return jsonify(data)

    total = clan_collection.count_documents(query)
    return jsonify(
        {
            "items": data,
            "total": total,
            "limit": requested_limit,
            "offset": requested_offset,
        }
    )


def _validate_recruitee_payload(payload):
    """Return normalized recruitee POST payload."""
    normalized = {}
    if "clanTag" in payload:
        normalized["clanTag"] = normalize_tag(payload["clanTag"], "clanTag")
        return normalized

    filters = ensure_object(payload.get("filters"), "filters")
    normalized["filters"] = _validate_filter_payload(filters)
    return normalized


def _validate_filter_payload(filters):
    normalized = {}

    name = optional_string(filters, "name", max_length=120)
    if name:
        normalized["name"] = name

    requirements = ensure_object(
        filters.get("requirements"),
        "filters.requirements",
    )
    normalized_requirements = {}
    townhall = optional_int(
        requirements,
        "townhall",
        min_value=0,
        max_value=25,
    )
    if townhall is not None:
        normalized_requirements["townhall"] = townhall
    league = optional_int(requirements, "league", min_value=0, max_value=34)
    if league is not None:
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

    min_clan_level = optional_int(filters, "minClanLevel", min_value=0)
    if min_clan_level is not None:
        normalized["minClanLevel"] = min_clan_level
    clan_points = optional_int(filters, "clanPoints", min_value=0)
    if clan_points is not None:
        normalized["clanPoints"] = clan_points

    war_frequency = optional_string(filters, "warFrequency", max_length=40)
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
