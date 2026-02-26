from flask import Blueprint, session, jsonify, request
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


@recruitee_bp.get("/recruitee")
def recruitee_get():

    if request.method == 'GET':
        player_name = session.get("player_name")
        default_limit = 10
        requested_limit = _get_requested_limit(default_limit)
        requested_offset = _get_requested_offset()

        if player_name == "Guest":
            data = list(
                clan_collection.find({}, {"_id": 0})
                .sort([("last_updated", -1), ("clan_tag", 1)])
                .skip(requested_offset)
                .limit(requested_limit)
            )
        else:
            data = list(
                clan_collection.find(
                    {
                        "requirements.0": {"$lte": session.get("player_league")},
                        "requirements.1": {"$lte": session.get("player_builderbase_trophies")},
                        "requirements.2": {"$lte": session.get("player_townhall")},
                    },
                    {"_id": 0}
                ).sort([("last_updated", -1), ("clan_tag", 1)]).skip(requested_offset).limit(requested_limit)
            )

        return jsonify(data)


@recruitee_bp.post("/recruitee")
def recruitee_post():
    # this can change based on whatever we would want
    DEFAULT_LIMIT = 10

    raw_form = request.get_json() or {}

    clan_tag = raw_form.get("clanTag", None) or raw_form.get("clan_tag", None)
    if clan_tag:
        data = clan_collection.find_one({"clan_tag": clan_tag}, {"_id": 0})
        if data is None:
            return jsonify({"error": "Clan not found"}), 404
        return jsonify(data)

    filters = raw_form.get("filters", {})
    query = {}

    name = filters.get("name", None)
    if name: query["name"] = name

    requirements = filters.get("requirements", {})
    min_townhall = requirements.get("townhall", None)
    min_league = requirements.get("league", None)
    if min_townhall is not None: query["requirements.townhall"] = {"$gte": min_townhall}
    if min_league is not None: query["requirements.league"] = {"$gte": min_league}

    min_clan_level = filters.get("minClanLevel", None)
    if min_clan_level is not None: query["clan_info.clan_level"] = {"$gte": min_clan_level}

    min_clan_points = filters.get("clanPoints", None)
    if min_clan_points is not None: query["clan_info.clanPoints"] = {"$gte": min_clan_points}

    members = filters.get("members", {})
    min_members = members.get("min", None)
    max_members = members.get("max", None)
    if min_members is not None or max_members is not None:
        member_range = {}
        if min_members is not None: member_range["$gte"] = min_members
        if max_members is not None: member_range["$lte"] = max_members
        query["clan_info.member_count"] = member_range

    war_frequency = filters.get("warFrequency", None)
    if war_frequency: query["clan_info.warFrequency"] = war_frequency

    location_id = filters.get("locationId", None)
    if location_id is not None: query["clan_info.location.id"] = location_id

    requested_limit = _get_requested_limit(DEFAULT_LIMIT)

    data = list(
        clan_collection.find(query, {"_id": 0})
        .sort([("last_updated", -1), ("clan_tag", 1)]).limit(requested_limit)
    )
    return jsonify(data)