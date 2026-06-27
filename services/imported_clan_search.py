"""Service functions for imported clan lookup and search."""

import re
from datetime import datetime, timezone
from typing import Any

from .clan_search_sorting import priority_sort_pipeline

IMPORTED_CLAN_SORT = [
    ("last_discovered", -1),
    ("last_updated", -1),
    ("clan_info.clan_level", -1),
    ("clan_info.member_count", -1),
    ("clan_tag", 1),
]


def get_imported_clans_response(
    payload: dict[str, Any],
    *,
    limit: int,
    offset: int,
    clan_collection: Any,
    imported_clan_lookup: Any,
) -> tuple[dict[str, Any], int]:
    """Return an imported clan lookup or filtered search response."""
    clan_tag = payload.get("clanTag")
    if clan_tag is not None:
        clan = imported_clan_lookup(clan_tag)
        if clan is None:
            return {"error": "Imported clan not found"}, 404
        return clan, 200

    filters = payload.get("filters", {})
    query = build_imported_query(filters)
    total = clan_collection.count_documents(query)
    if hasattr(clan_collection, "aggregate"):
        items = list(
            clan_collection.aggregate(
                priority_sort_pipeline(
                    query,
                    IMPORTED_CLAN_SORT,
                    offset=offset,
                    limit=limit,
                )
            )
        )
    else:
        items = list(
            clan_collection.find(query, {"_id": 0})
            .sort(IMPORTED_CLAN_SORT)
            .skip(offset)
            .limit(limit)
        )

    return (
        {
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset,
        },
        200,
    )


def build_imported_query(filters: dict[str, Any]) -> dict[str, Any]:
    """Build a MongoDB query for imported clans from filter data."""
    query = {
        "source": "clash_api_import",
        "expires": {"$gt": datetime.now(timezone.utc)},
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
