"""Register routes for handling imported clans."""

import re

from flask import Blueprint, jsonify, request

from ..services.import_clash_api_clans import (
    get_imported_clan,
)
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

imported_clans_bp = Blueprint("imported_clans", __name__)

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


def _build_imported_query(filters):
    """Build a MongoDB query for imported clans from request filter data."""
    query = {
        "source": "clash_api_import",
    }

    name = filters.get("name")
    if name:
        query["name"] = {"$regex": re.escape(name.strip()), "$options": "i"}

    min_clan_level = filters.get("minClanLevel")
    if min_clan_level is not None:
        query["clan_info.clan_level"] = {"$gte": min_clan_level}

    min_clan_points = filters.get("clanPoints")
    if min_clan_points is not None:
        query["clan_info.clanPoints"] = {"$gte": min_clan_points}

    requirements = filters.get("requirements", {})
    members = requirements.get("members", {})
    min_members = members.get("min")
    max_members = members.get("max")
    if min_members is not None or max_members is not None:
        member_range = {}
        if min_members is not None:
            member_range["$gte"] = min_members
        if max_members is not None:
            member_range["$lte"] = max_members
        query["clan_info.member_count"] = member_range

    war_frequency = filters.get("warFrequency")
    if war_frequency:
        query["clan_info.warFrequency"] = war_frequency

    location = filters.get("location")
    if location:
        query["clan_info.location.name"] = location

    return query


@imported_clans_bp.post("/imported_clans")
@rate_limit("imported_clans", limit=20, window_seconds=60)
def imported_clans_post():
    """Return clan details for a tag or a filtered imported clan list."""
    try:
        default_limit = 10
        requested_limit = _get_requested_limit(default_limit)
        requested_offset = _get_requested_offset()
        raw_form = _validate_imported_payload(get_json_object(request))
    except RequestValidationError as exc:
        return jsonify({"error": exc.message}), 400

    clan_collection = get_clan_collection()

    clan_tag = raw_form.get("clanTag") or raw_form.get("clan_tag")
    if clan_tag:
        clan = get_imported_clan(clan_tag)
        if clan is None:
            return jsonify({"error": "Imported clan not found"}), 404
        return jsonify(clan)


    filters = raw_form.get("filters", {})
    query = _build_imported_query(filters)
    total = clan_collection.count_documents(query)
    items = list(
        clan_collection.find(query, {"_id": 0})
        .sort(
            [
                ("last_discovered", -1),
                ("last_updated", -1),
                ("clan_info.clan_level", -1),
                ("clan_info.member_count", -1),
                ("clan_tag", 1),
            ]
        )
        .skip(requested_offset)
        .limit(requested_limit)
    )

    return jsonify(
        {
            "items": items,
            "total": total,
            "limit": requested_limit,
            "offset": requested_offset,
        }
    )


def _validate_imported_payload(payload):
    """Return normalized imported-clans POST payload."""
    normalized = {}
    raw_tag = payload.get("clanTag") or payload.get("clan_tag")
    if raw_tag is not None:
        normalized["clanTag"] = normalize_tag(raw_tag, "clanTag")
        return normalized

    filters = ensure_object(payload.get("filters"), "filters")
    normalized["filters"] = _validate_imported_filters(filters)
    return normalized


def _validate_imported_filters(filters):
    normalized = {}

    name = optional_string(filters, "name", max_length=120)
    if name:
        normalized["name"] = name

    min_clan_level = optional_int(filters, "minClanLevel", min_value=0)
    if min_clan_level is not None:
        normalized["minClanLevel"] = min_clan_level
    clan_points = optional_int(filters, "clanPoints", min_value=0)
    if clan_points is not None:
        normalized["clanPoints"] = clan_points

    requirements = ensure_object(
        filters.get("requirements"),
        "filters.requirements",
    )
    members = ensure_object(
        requirements.get("members"),
        "filters.requirements.members",
    )
    normalized_members = _validate_members_filter(members)
    if normalized_members:
        normalized["requirements"] = {"members": normalized_members}

    war_frequency = optional_string(filters, "warFrequency", max_length=40)
    if war_frequency:
        normalized["warFrequency"] = war_frequency

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
