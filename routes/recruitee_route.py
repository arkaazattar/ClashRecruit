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


@recruitee_bp.route("/recruitee", methods=['GET', 'POST'])
def recruitee():

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

    data = request.get_json() or {}
    clan_tag = data.get("clanTag")
    if not clan_tag:
        return jsonify({"error": "Missing clanTag"}), 400

    clan_info = clan_collection.find_one({"clan_tag": clan_tag}, {"_id": 0})
    if clan_info is None:
        return jsonify({"error": "Clan not found"}), 404
    return jsonify(clan_info)
