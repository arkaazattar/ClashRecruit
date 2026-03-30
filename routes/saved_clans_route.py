from flask import Blueprint, jsonify, session

from ..services.mongo_db_client import clan_collection, user_collection


saved_clans_bp = Blueprint("saved_clans", __name__)

MAX_SAVED_CLANS = 10


def _hydrate_saved_clans(saved_clan_tags):
    listings = list(
        clan_collection.find(
            {"clan_tag": {"$in": saved_clan_tags}},
            {"_id": 0, "clan_tag": 1, "name": 1, "requirements": 1, "clan_info": 1},
        )
    )
    listing_by_saved_tag = {listing["clan_tag"]: listing for listing in listings}

    hydrated = []
    for saved_tag in saved_clan_tags:
        listing = listing_by_saved_tag.get(saved_tag)
        clan_info = listing.get("clan_info", {}) if listing else {}

        hydrated.append(
            {
                "clan_tag": saved_tag,
                "name": (listing.get("name") if listing else None) or clan_info.get("name") or saved_tag,
                "requirements": listing.get("requirements") if listing else None,
                "clan_info": clan_info,
                "listing_available": bool(listing),
            }
        )

    return hydrated


@saved_clans_bp.get("/saved-clans")
def get_saved_clans():
    player_tag = session.get("player_tag")
    if not player_tag:
        return jsonify({"message": "Unauthorized"}), 401

    user_doc = user_collection.find_one(
        {"player_tag": player_tag},
        {"_id": 0, "saved_clans": 1},
    ) or {}
    saved_clan_tags = user_doc.get("saved_clans", [])
    hydrated = _hydrate_saved_clans(saved_clan_tags)

    return jsonify(
        {
            "saved_clans": hydrated,
            "count": len(saved_clan_tags),
            "max_saved_clans": MAX_SAVED_CLANS,
        }
    ), 200


@saved_clans_bp.post("/saved-clans/<clan_tag>")
def add_saved_clan(clan_tag):
    player_tag = session.get("player_tag")
    if not player_tag:
        return jsonify({"message": "Unauthorized"}), 401

    normalized_tag = clan_tag.lstrip("#")

    current_doc = user_collection.find_one(
        {"player_tag": player_tag},
        {"_id": 0, "saved_clans": 1},
    ) or {}
    current_saved = current_doc.get("saved_clans", [])
    if normalized_tag in current_saved:
        return jsonify(
            {
                "message": "Clan already saved.",
                "clan_tag": normalized_tag,
                "count": len(current_saved),
                "max_saved_clans": MAX_SAVED_CLANS,
            }
        ), 200

    if len(current_saved) >= MAX_SAVED_CLANS:
        return jsonify(
            {
                "message": "You can save up to 10 clans. Remove one before saving another.",
                "count": len(current_saved),
                "max_saved_clans": MAX_SAVED_CLANS,
            }
        ), 409

    user_collection.update_one(
        {"player_tag": player_tag},
        {
            "$addToSet": {"saved_clans": normalized_tag},
            "$setOnInsert": {"player_tag": player_tag},
        },
        upsert=True,
    )

    return jsonify(
        {
            "message": "Clan saved.",
            "clan_tag": normalized_tag,
            "count": len(current_saved) + 1,
            "max_saved_clans": MAX_SAVED_CLANS,
        }
    ), 200


@saved_clans_bp.delete("/saved-clans/<clan_tag>")
def delete_saved_clan(clan_tag):
    player_tag = session.get("player_tag")
    if not player_tag:
        return jsonify({"message": "Unauthorized"}), 401

    normalized_tag = clan_tag.lstrip("#")

    user_collection.update_one(
        {"player_tag": player_tag},
        {"$pull": {"saved_clans": normalized_tag}},
    )

    return jsonify({"message": "Saved clan removed.", "clan_tag": normalized_tag}), 200
