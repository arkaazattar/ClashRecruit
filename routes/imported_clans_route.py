"""Register routes for handling imported clans."""

import re

from flask import Blueprint, jsonify, request

from ..services.import_clash_api_clans import (ensure_imported_clan_inventory,
                                               get_imported_clan)
from ..services.mongo_db_client import clan_collection

imported_clans_bp = Blueprint("imported_clans", __name__)

MAX_LIMIT = 200


def _get_requested_limit(default_limit):
    """Return the validated `limit` query param capped to allowed bounds."""
    raw_limit = request.args.get("limit")
    if raw_limit is None:
        return default_limit

    try:
        parsed_limit = int(raw_limit)
    except (TypeError, ValueError):
        return default_limit

    return max(1, min(parsed_limit, MAX_LIMIT))


def _get_requested_offset():
    """Return the validated `offset` query param with a minimum of zero."""
    raw_offset = request.args.get("offset")
    if raw_offset is None:
        return 0

    try:
        parsed_offset = int(raw_offset)
    except (TypeError, ValueError):
        return 0

    return max(0, parsed_offset)


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
def imported_clans_post():
    """Return clan details for a tag or a filtered imported clan list."""
    default_limit = 10
    requested_limit = _get_requested_limit(default_limit)
    requested_offset = _get_requested_offset()
    raw_form = request.get_json() or {}

    clan_tag = raw_form.get("clanTag") or raw_form.get("clan_tag")
    if clan_tag:
        clan = get_imported_clan(clan_tag)
        if clan is None:
            return jsonify({"error": "Imported clan not found"}), 404
        return jsonify(clan)

    ensure_imported_clan_inventory()

    filters = raw_form.get("filters", {})
    query = _build_imported_query(filters)
    total = clan_collection.count_documents(query)
    items = list(
        clan_collection.find(query, {"_id": 0})
        .sort([
            ("last_discovered", -1),
            ("last_updated", -1),
            ("clan_info.clan_level", -1),
            ("clan_info.member_count", -1),
            ("clan_tag", 1),
        ])
        .skip(requested_offset)
        .limit(requested_limit)
    )

    return jsonify({
        "items": items,
        "total": total,
        "limit": requested_limit,
        "offset": requested_offset,
    })
