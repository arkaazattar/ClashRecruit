"""Service for importing clans from the Clash of Clans API."""

from datetime import datetime, timedelta, timezone
from typing import Any

import requests
from celery.signals import worker_ready

from ..config import headers
from .celery_app import app
from .mongo_db_client import (
    clan_collection,
    import_state_collection,
    location_collection,
)

DISCOVERY_STALE_AFTER = timedelta(hours=6)
IMPORTED_CLAN_RETENTION = timedelta(days=3)


def _now() -> datetime:
    """Return the current UTC time."""
    return datetime.now(timezone.utc)


def _clean_tag(tag: str | None) -> str | None:
    """Return a cleaned clan tag, or ``None`` when the input is invalid."""
    if not tag:
        return None
    cleaned = str(tag).strip().upper().lstrip("#")
    if not cleaned:
        return None
    return cleaned


def _build_seed_key(seed: dict[str, Any]) -> str:
    """Return a stable key used to persist seed pagination state."""
    return "|".join(
        f"{key}:{value}"
        for key, value in sorted(seed.items())
        if value not in (None, "")
    )


def _seed_locations(limit: int = 4) -> list[int]:
    """Return a list of stored location IDs used to build discovery seeds."""
    locations = list(
        location_collection.find({}, {"_id": 0, "id": 1}).limit(limit)
    )
    return [location.get("id") for location in locations if location.get("id")]


def _build_discovery_seeds() -> list[dict[str, Any]]:
    """Build the search seed combinations used for importing clans."""
    seeds: list[dict[str, Any]] = []
    prefixes = ["a", "b", "c", "d", "e", "f", "m", "s", "t"]
    war_frequencies = ["always", "twicePerWeek", "oncePerWeek", "rarely"]
    member_ranges = [(10, 50), (15, 50), (20, 50), (25, 50)]
    min_levels = [3, 5, 8]
    location_ids = _seed_locations(limit=6)

    for prefix in prefixes:
        seeds.append({
            "name": prefix,
            "minMembers": 10,
            "limit": 10,
        })

    for war_frequency in war_frequencies:
        for min_members, max_members in member_ranges:
            seeds.append({
                "warFrequency": war_frequency,
                "minMembers": min_members,
                "maxMembers": max_members,
                "limit": 10,
            })

    for location_id in location_ids:
        for min_level in min_levels:
            seeds.append({
                "locationId": location_id,
                "minClanLevel": min_level,
                "minMembers": 10,
                "limit": 10,
            })

    return seeds


def _search_clans(filters: dict[str, Any]) -> dict[str, Any]:
    """Search clans from Clash API and return items with cursor metadata."""
    response = requests.get(
        "https://api.clashofclans.com/v1/clans",
        params=filters,
        headers=headers,
        timeout=15,
    )
    response.raise_for_status()
    payload = response.json()
    return {
        "items": payload.get("items", []),
        "after": payload.get("paging", {}).get("cursors", {}).get("after"),
    }


def _get_seed_state(seed_key: str) -> dict[str, Any] | None:
    """Return persisted pagination state for a discovery seed key."""
    return import_state_collection.find_one({"seed_key": seed_key}, {"_id": 0})


def _set_seed_after(seed_key: str, after: str | None) -> None:
    """Persist the next-page cursor and run timestamp for a discovery seed."""
    import_state_collection.update_one(
        {"seed_key": seed_key},
        {
            "$set": {
                "seed_key": seed_key,
                "after": after,
                "last_run": _now(),
            }
        },
        upsert=True,
    )


def _reset_seed_after(seed_key: str) -> None:
    """Clear persisted pagination state for a discovery seed key."""
    _set_seed_after(seed_key, None)


def _fetch_clan_detail(clan_tag: str | None) -> dict[str, Any] | None:
    """Fetch detailed clan data from the Clash API for a clan tag."""
    clean_tag = _clean_tag(clan_tag)
    if not clean_tag:
        return None

    encoded_tag = f"%23{clean_tag}"
    response = requests.get(
        f"https://api.clashofclans.com/v1/clans/{encoded_tag}",
        headers=headers,
        timeout=15,
    )

    if response.status_code == 404:
        return None

    response.raise_for_status()
    return response.json()


def _normalize_discovery_item(
    clan: dict[str, Any],
    seed_key: str,
) -> dict[str, Any]:
    """Normalize a search result clan into the imported clan document shape."""
    return {
        "clan_tag": _clean_tag(clan.get("tag")),
        "name": clan.get("name"),
        "source": "clash_api_import",
        "seed_key": seed_key,
        "requirements": [0, 0, 0],
        "requirements_source": "unsupported_by_api",
        "last_discovered": _now(),
        "clan_info": {
            "description": None,
            "location": clan.get("location") or {},
            "badge": clan.get("badgeUrls", {}).get("medium"),
            "clan_level": clan.get("clanLevel"),
            "member_count": clan.get("members"),
            "type": clan.get("type"),
            "warFrequency": clan.get("warFrequency"),
            "clanPoints": clan.get("clanPoints"),
        },
    }


def _extract_requirements(
    search_clan: dict[str, Any] | None = None,
    detail_clan: dict[str, Any] | None = None,
) -> list[int]:
    """Extract listing requirements from API search and detail payloads."""
    search_clan = search_clan or {}
    detail_clan = detail_clan or {}
    required_league = 0
    required_builder_trophies = (
        detail_clan.get("requiredBuilderBaseTrophies")
        if detail_clan.get("requiredBuilderBaseTrophies") is not None
        else search_clan.get("requiredBuilderBaseTrophies", 0)
    )
    required_townhall = (
        detail_clan.get("requiredTownhallLevel")
        if detail_clan.get("requiredTownhallLevel") is not None
        else search_clan.get("requiredTownhallLevel", 0)
    )
    return [
        required_league or 0,
        required_builder_trophies or 0,
        required_townhall or 0,
    ]


def _build_enriched_import_document(
    search_clan: dict[str, Any],
    detail_clan: dict[str, Any],
    seed_key: str,
) -> dict[str, Any]:
    """Build an imported clan document enriched with detail endpoint data."""
    description = (detail_clan.get("description") or "").strip()
    return {
        "clan_tag": _clean_tag(
            search_clan.get("tag") or detail_clan.get("tag")
        ),
        "name": detail_clan.get("name") or search_clan.get("name"),
        "source": "clash_api_import",
        "seed_key": seed_key,
        "requirements": _extract_requirements(
            search_clan=search_clan,
            detail_clan=detail_clan,
        ),
        "requirements_source": "clash_api",
        "last_discovered": _now(),
        "last_updated": _now(),
        "clan_info": {
            "description": description or None,
            "location": (
                detail_clan.get("location")
                or search_clan.get("location")
                or {}
            ),
            "badge": (
                detail_clan.get("badgeUrls", {}).get("medium")
                or search_clan.get("badgeUrls", {}).get("medium")
            ),
            "clan_level": (
                detail_clan.get("clanLevel")
                if detail_clan.get("clanLevel") is not None
                else search_clan.get("clanLevel")
            ),
            "member_count": (
                detail_clan.get("members")
                if detail_clan.get("members") is not None
                else search_clan.get("members")
            ),
            "type": detail_clan.get("type") or search_clan.get("type"),
            "warFrequency": (
                detail_clan.get("warFrequency")
                or search_clan.get("warFrequency")
            ),
            "clanPoints": (
                detail_clan.get("clanPoints")
                if detail_clan.get("clanPoints") is not None
                else search_clan.get("clanPoints")
            ),
        },
    }


def _passes_quality_gate(clan: dict[str, Any]) -> bool:
    """Return whether a clan satisfies minimum import quality thresholds."""
    members = clan.get("members") or 0
    clan_level = clan.get("clanLevel") or 0
    return members >= 20 and clan_level >= 5


@app.task(name="discover_imported_clans_task")
def discover_imported_clans_task() -> int:
    """Run one discovery cycle as a Celery task and return import count."""
    return discover_imported_clans()


def cleanup_old_imported_clans() -> int:
    """Delete stale imported clans past retention and return delete count."""
    cutoff = _now() - IMPORTED_CLAN_RETENTION
    result = clan_collection.delete_many({
        "source": "clash_api_import",
        "last_discovered": {"$lt": cutoff},
    })
    return result.deleted_count


def discover_imported_clans(max_seeds: int = 12) -> int:
    """Discover and upsert imported clans using seed-based API searches."""
    max_imports_per_cycle = 30
    max_pages_per_seed = 3
    cleanup_old_imported_clans()
    discovered = 0

    for seed in _build_discovery_seeds()[:max_seeds]:
        if discovered >= max_imports_per_cycle:
            break

        seed_key = _build_seed_key(seed)
        seed_state = _get_seed_state(seed_key) or {}
        after = seed_state.get("after")
        pages_processed = 0

        while (
            pages_processed < max_pages_per_seed
            and discovered < max_imports_per_cycle
        ):
            request_seed = seed.copy()
            if after:
                request_seed["after"] = after

            try:
                search_result = _search_clans(request_seed)
            except requests.RequestException:
                break

            clans = search_result.get("items", [])
            next_after = search_result.get("after")

            if not clans:
                _reset_seed_after(seed_key)
                break

            for clan in clans:
                if discovered >= max_imports_per_cycle:
                    break

                if not _passes_quality_gate(clan):
                    continue

                normalized = _normalize_discovery_item(clan, seed_key)
                clan_tag = normalized.get("clan_tag")
                if not clan_tag:
                    continue

                try:
                    detail = _fetch_clan_detail(clan_tag)
                except requests.RequestException:
                    continue

                if detail is None or not _passes_quality_gate(detail):
                    continue

                enriched_document = _build_enriched_import_document(
                    clan,
                    detail,
                    seed_key,
                )
                clan_collection.update_one(
                    {"clan_tag": clan_tag, "source": "clash_api_import"},
                    {
                        "$set": {
                            "name": enriched_document["name"],
                            "source": enriched_document["source"],
                            "seed_key": enriched_document["seed_key"],
                            "requirements": enriched_document["requirements"],
                            "requirements_source": enriched_document[
                                "requirements_source"
                            ],
                            "last_discovered": enriched_document[
                                "last_discovered"
                            ],
                            "last_updated": enriched_document["last_updated"],
                            "clan_info": enriched_document["clan_info"],
                        },
                    },
                    upsert=True,
                )
                discovered += 1

            pages_processed += 1
            if next_after:
                _set_seed_after(seed_key, next_after)
                after = next_after
            else:
                _reset_seed_after(seed_key)
                break

    return discovered


def ensure_imported_clan_inventory(min_complete: int = 30) -> None:
    """Ensure a recent minimum inventory of imported clans is available."""
    recent_threshold = _now() - DISCOVERY_STALE_AFTER
    complete_count = clan_collection.count_documents(
        {
            "source": "clash_api_import",
            "last_discovered": {"$gte": recent_threshold},
        }
    )
    if complete_count >= min_complete:
        return

    discover_imported_clans()


@worker_ready.connect
def run_import_refresh_on_worker_start(
    sender: Any = None,
    **kwargs: Any,
) -> None:
    """Queue an import discovery task when a Celery worker starts."""
    if sender is not None:
        sender.app.send_task("discover_imported_clans_task")


def get_imported_clan(clan_tag: str | None) -> dict[str, Any] | None:
    """Return imported clan data, fetching and caching when absent."""
    clean_tag = _clean_tag(clan_tag)
    if not clean_tag:
        return None

    clan = clan_collection.find_one(
        {"clan_tag": clean_tag, "source": "clash_api_import"},
        {"_id": 0},
    )
    if clan is not None:
        return clan

    detail = _fetch_clan_detail(clean_tag)
    if detail is None:
        return None

    clan_collection.update_one(
        {"clan_tag": clean_tag, "source": "clash_api_import"},
        {
            "$set": {
                "clan_tag": clean_tag,
                "name": detail.get("name"),
                "source": "clash_api_import",
                "requirements": _extract_requirements(detail_clan=detail),
                "requirements_source": "clash_api",
                "last_discovered": _now(),
                "last_updated": _now(),
                "clan_info": {
                    "description": (
                        (detail.get("description") or "").strip() or None
                    ),
                    "location": detail.get("location") or {},
                    "badge": detail.get("badgeUrls", {}).get("medium"),
                    "clan_level": detail.get("clanLevel"),
                    "member_count": detail.get("members"),
                    "type": detail.get("type"),
                    "warFrequency": detail.get("warFrequency"),
                    "clanPoints": detail.get("clanPoints"),
                },
            }
        },
        upsert=True,
    )
    return clan_collection.find_one(
        {"clan_tag": clean_tag, "source": "clash_api_import"},
        {"_id": 0},
    )
