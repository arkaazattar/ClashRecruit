"""Service functions for recruitee clan listing search."""

import re
from datetime import datetime, timezone
from typing import Any

from ..routes.validation import RequestValidationError
from .builder_base_leagues import builder_base_league_id_from_trophies
from .clan_search_sorting import priority_sort_pipeline

MATCHMAKING_SESSION_FIELDS = {
    "player_league": "requirements.0",
    "player_builderbase_trophies": "requirements.1",
    "player_townhall": "requirements.2",
}
RECRUITEE_SORT = [("last_updated", -1), ("clan_tag", 1)]


def get_recruitee_list_response(
    session_data: dict[str, Any],
    *,
    limit: int,
    offset: int,
    include_total: bool,
    clan_collection: Any,
    source_sort: str = "community",
) -> tuple[Any, int]:
    """Return clans for a session with optional total metadata."""
    query = active_listing_query(get_matchmaking_base_query(session_data))
    return _paginated_response(
        query,
        limit=limit,
        offset=offset,
        include_total=include_total,
        source_sort=source_sort,
        clan_collection=clan_collection,
    ), 200


def get_recruitee_post_response(
    payload: dict[str, Any],
    *,
    limit: int,
    offset: int,
    include_total: bool,
    clan_collection: Any,
    source_sort: str = "community",
) -> tuple[Any, int]:
    """Return clan details by tag or a filtered clan list."""
    clan_tag = payload.get("clanTag")
    if clan_tag is not None:
        data = clan_collection.find_one(
            active_listing_query({"clan_tag": clan_tag}),
            {"_id": 0},
        )
        if data is None:
            return {"error": "Clan not found"}, 404
        return data, 200

    query = active_listing_query(build_recruitee_filter_query(
        payload.get("filters", {})
    ))
    return _paginated_response(
        query,
        limit=limit,
        offset=offset,
        include_total=include_total,
        source_sort=source_sort,
        clan_collection=clan_collection,
    ), 200


def get_matchmaking_base_query(
    session_data: dict[str, Any],
) -> dict[str, dict[str, int]]:
    """Return a clan match query for the current player session."""
    player_name = session_data.get("player_name")
    if not player_name or player_name == "Guest":
        return {}

    stats = {}
    for session_key, query_key in MATCHMAKING_SESSION_FIELDS.items():
        value = session_data.get(session_key)
        if value is None:
            return {}
        stats[query_key] = _session_int(value, session_key)

    if "requirements.1" in stats:
        stats["requirements.1"] = builder_base_league_id_from_trophies(
            stats["requirements.1"],
        )

    return {query_key: {"$lte": value} for query_key, value in stats.items()}


def build_recruitee_filter_query(filters: dict[str, Any]) -> dict[str, Any]:
    """Build a MongoDB query for recruitee search filters."""
    query = {}

    name = filters.get("name")
    if name:
        query["name"] = {"$regex": re.escape(name.strip()), "$options": "i"}

    requirements = filters.get("requirements", {})
    min_townhall = requirements.get("townhall")
    min_league = requirements.get("league")
    if min_townhall is not None:
        query["requirements.2"] = {"$gte": min_townhall}
    if min_league is not None:
        query["requirements.0"] = {"$gte": min_league}

    min_clan_level = filters.get("minClanLevel")
    if min_clan_level is not None:
        query["clan_info.clan_level"] = {"$gte": min_clan_level}

    min_clan_points = filters.get("clanPoints")
    if min_clan_points is not None:
        query["clan_info.clanPoints"] = {"$gte": min_clan_points}

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

    location_id = filters.get("location_id")
    if location_id:
        query["clan_info.location.id"] = int(location_id)
    else:
        location_name = filters.get("location")
        if location_name:
            query["clan_info.location.name"] = location_name

    return query


def active_listing_query(
    query: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a query scoped to active listings."""
    active_query = dict(query or {})
    active_query["expires"] = {"$gt": datetime.now(timezone.utc)}
    return active_query


def _paginated_response(
    query: dict[str, Any],
    *,
    limit: int,
    offset: int,
    include_total: bool,
    clan_collection: Any,
    source_sort: str = "community",
) -> Any:
    if hasattr(clan_collection, "aggregate"):
        data = list(
            clan_collection.aggregate(
                priority_sort_pipeline(
                    query,
                    RECRUITEE_SORT,
                    offset=offset,
                    limit=limit,
                    source_sort=source_sort,
                )
            )
        )
    else:
        data = list(
            clan_collection.find(query, {"_id": 0})
            .sort(RECRUITEE_SORT)
            .skip(offset)
            .limit(limit)
        )

    if not include_total:
        return data

    return {
        "items": data,
        "total": clan_collection.count_documents(query),
        "limit": limit,
        "offset": offset,
    }


def _session_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool):
        raise RequestValidationError(f"{field_name} is invalid.")
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        if stripped and stripped.isdecimal():
            return int(stripped)
    raise RequestValidationError(f"{field_name} is invalid.")
