import re
from flask import Blueprint, jsonify, request, session
from ..services.import_clash_api_clans import ensure_imported_clan_inventory
from ..services.mongo_db_client import clan_collection

recruitee_bp = Blueprint("recruitee", __name__)


MAX_LIMIT = 200


def _get_requested_limit(default_limit):
    raw_limit = request.args.get("limit")
    if raw_limit is None:
        return default_limit

    try:
        parsed_limit = int(raw_limit)
    except (TypeError, ValueError):
        return default_limit

    return max(1, min(parsed_limit, MAX_LIMIT))


def _get_requested_offset():
    raw_offset = request.args.get("offset")
    if raw_offset is None:
        return 0

    try:
        parsed_offset = int(raw_offset)
    except (TypeError, ValueError):
        return 0

    return max(0, parsed_offset)


def _should_refresh_imported_inventory():
    return _get_requested_offset() == 0


def _should_include_total():
    return request.args.get("includeTotal", "0") == "1"


@recruitee_bp.get("/recruitee")
def recruitee_get():
    player_name = session.get("player_name", None)
    default_limit = 10
    requested_limit = _get_requested_limit(default_limit)
    requested_offset = _get_requested_offset()

    if _should_refresh_imported_inventory():
        ensure_imported_clan_inventory()

    if not player_name or player_name == "Guest":
        base_query = {}
    else:
        base_query = {
            "requirements.0": {"$lte": session.get("player_league")},
            "requirements.1": {"$lte": session.get("player_builderbase_trophies")},
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
    return jsonify({
        "items": data,
        "total": total,
        "limit": requested_limit,
        "offset": requested_offset,
    })


@recruitee_bp.post("/recruitee")
def recruitee_post():
    DEFAULT_LIMIT = 10
    requested_limit = _get_requested_limit(DEFAULT_LIMIT)
    requested_offset = _get_requested_offset()

    raw_form = request.get_json() or {}

    clan_tag = raw_form.get("clanTag", None) or raw_form.get("clan_tag", None)
    if clan_tag:
        data = clan_collection.find_one({"clan_tag": clan_tag}, {"_id": 0})
        if data is None:
            return jsonify({"error": "Clan not found"}), 404
        return jsonify(data)

    if _should_refresh_imported_inventory():
        ensure_imported_clan_inventory()

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
        query["clan_info.location.id"] = int(location_id)
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
    return jsonify({
        "items": data,
        "total": total,
        "limit": requested_limit,
        "offset": requested_offset,
    })
