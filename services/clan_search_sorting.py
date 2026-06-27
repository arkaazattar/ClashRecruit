"""Shared sort helpers for clan listing search results."""

from typing import Any

ENGLISH_PRIORITY_LOCATIONS = (
    "australia",
    "canada",
    "india",
    "international",
    "ireland",
    "new zealand",
    "philippines",
    "singapore",
    "south africa",
    "united kingdom",
    "united states",
)

LISTING_SOURCE_PRIORITY_FIELD = "_listing_source_priority"
ENGLISH_PRIORITY_FIELD = "_english_priority"


def priority_sort_pipeline(
    query: dict[str, Any],
    sort_fields: list[tuple[str, int]],
    *,
    offset: int,
    limit: int,
    source_sort: str = "community",
) -> list[dict[str, Any]]:
    """Return an aggregation pipeline that sorts by listing quality first."""
    imported_priority = 0 if source_sort == "discovered" else 1
    live_priority = 1 if source_sort == "discovered" else 0
    return [
        {"$match": query},
        {
            "$addFields": {
                LISTING_SOURCE_PRIORITY_FIELD: {
                    "$cond": [
                        {"$eq": ["$source", "clash_api_import"]},
                        imported_priority,
                        live_priority,
                    ],
                },
                ENGLISH_PRIORITY_FIELD: {
                    "$cond": [
                        {
                            "$in": [
                                {
                                    "$toLower": {
                                        "$ifNull": [
                                            "$clan_info.location.name",
                                            "",
                                        ],
                                    },
                                },
                                list(ENGLISH_PRIORITY_LOCATIONS),
                            ],
                        },
                        0,
                        1,
                    ],
                },
            },
        },
        {
            "$sort": {
                LISTING_SOURCE_PRIORITY_FIELD: 1,
                ENGLISH_PRIORITY_FIELD: 1,
                **dict(sort_fields),
            },
        },
        {"$skip": offset},
        {"$limit": limit},
        {
            "$project": {
                "_id": 0,
                LISTING_SOURCE_PRIORITY_FIELD: 0,
                ENGLISH_PRIORITY_FIELD: 0,
            },
        },
    ]
