"""Service functions for saved clan operations."""

from datetime import datetime, timezone
from typing import Any

MAX_SAVED_CLANS = 10


def get_saved_clans_payload(
    player_tag: str,
    user_collection: Any,
    clan_collection: Any,
) -> dict[str, Any]:
    """Return the saved-clans response payload for a player."""
    user_doc = (
        user_collection.find_one(
            {"player_tag": player_tag},
            {"_id": 0, "saved_clans": 1},
        )
        or {}
    )
    saved_clan_tags = user_doc.get("saved_clans", [])
    hydrated = hydrate_saved_clans(saved_clan_tags, clan_collection)

    return {
        "saved_clans": hydrated,
        "count": len(saved_clan_tags),
        "max_saved_clans": MAX_SAVED_CLANS,
    }


def add_saved_clan(
    player_tag: str,
    clan_tag: str,
    user_collection: Any,
) -> tuple[dict[str, Any], int]:
    """Save a clan tag for a player and return the response payload."""
    current_doc = (
        user_collection.find_one(
            {"player_tag": player_tag},
            {"_id": 0, "saved_clans": 1},
        )
        or {}
    )
    current_saved = current_doc.get("saved_clans", [])
    if clan_tag in current_saved:
        return (
            {
                "message": "Clan already saved.",
                "clan_tag": clan_tag,
                "count": len(current_saved),
                "max_saved_clans": MAX_SAVED_CLANS,
            },
            200,
        )

    if len(current_saved) >= MAX_SAVED_CLANS:
        return (
            {
                "message": (
                    "You can save up to 10 clans. Remove one before saving "
                    "another."
                ),
                "count": len(current_saved),
                "max_saved_clans": MAX_SAVED_CLANS,
            },
            409,
        )

    user_collection.update_one(
        {"player_tag": player_tag},
        {
            "$addToSet": {"saved_clans": clan_tag},
            "$setOnInsert": {"player_tag": player_tag},
        },
        upsert=True,
    )

    return (
        {
            "message": "Clan saved.",
            "clan_tag": clan_tag,
            "count": len(current_saved) + 1,
            "max_saved_clans": MAX_SAVED_CLANS,
        },
        200,
    )


def delete_saved_clan(
    player_tag: str,
    clan_tag: str,
    user_collection: Any,
) -> tuple[dict[str, Any], int]:
    """Remove a saved clan tag for a player."""
    user_collection.update_one(
        {"player_tag": player_tag},
        {"$pull": {"saved_clans": clan_tag}},
    )
    return {"message": "Saved clan removed.", "clan_tag": clan_tag}, 200


def hydrate_saved_clans(
    saved_clan_tags: list[str],
    clan_collection: Any,
) -> list[dict[str, Any]]:
    """Build saved clan response objects from stored clan tags."""
    now = datetime.now(timezone.utc)
    listings = list(
        clan_collection.find(
            {"clan_tag": {"$in": saved_clan_tags}, "expires": {"$gt": now}},
            {
                "_id": 0,
                "clan_tag": 1,
                "name": 1,
                "requirements": 1,
                "clan_info": 1,
            },
        )
    )
    listing_by_saved_tag = {
        listing["clan_tag"]: listing for listing in listings
    }

    hydrated = []
    for saved_tag in saved_clan_tags:
        listing = listing_by_saved_tag.get(saved_tag)
        clan_info = listing.get("clan_info", {}) if listing else {}

        hydrated.append(
            {
                "clan_tag": saved_tag,
                "name": (
                    (listing.get("name") if listing else None)
                    or clan_info.get("name")
                    or saved_tag
                ),
                "requirements": (
                    listing.get("requirements") if listing else None
                ),
                "clan_info": clan_info,
                "listing_available": bool(listing),
            }
        )

    return hydrated
