"""League metadata helpers backed by MongoDB and the Clash API."""

import re
from typing import Any

from ..clash_http_client import ClashApiError
from ..clash_http_client import get as clash_get
from ..config import headers
from .builder_base_leagues import BUILDER_BASE_LEAGUES
from .mongo_db_client import get_league_metadata_collection

BUILDER_BASE_LEAGUES_ENDPOINT = "builderbaseleagues"
RANKED_LEAGUE_TIERS_ENDPOINT = "leaguetiers"
BUILDER_BASE_LEAGUE_KIND = "builder_base_league"
RANKED_LEAGUE_TIER_KIND = "ranked_league_tier"
BUILDER_BASE_LEAGUE_ID_OFFSET = 43999999
RANKED_LEAGUE_TIER_ID_OFFSET = 105000000
TRAILING_NUMBER_PATTERN = re.compile(r"(\d+)$")

FALLBACK_RANKED_LEAGUE_OPTIONS = [
    {"value": 0, "label": "Unranked"},
    {"value": 1, "label": "Skeleton 1"},
    {"value": 2, "label": "Skeleton 2"},
    {"value": 3, "label": "Skeleton 3"},
    {"value": 4, "label": "Barbarian 4"},
    {"value": 5, "label": "Barbarian 5"},
    {"value": 6, "label": "Barbarian 6"},
    {"value": 7, "label": "Archer 7"},
    {"value": 8, "label": "Archer 8"},
    {"value": 9, "label": "Archer 9"},
    {"value": 10, "label": "Wizard 10"},
    {"value": 11, "label": "Wizard 11"},
    {"value": 12, "label": "Wizard 12"},
    {"value": 13, "label": "Valkyrie 13"},
    {"value": 14, "label": "Valkyrie 14"},
    {"value": 15, "label": "Valkyrie 15"},
    {"value": 16, "label": "Witch 16"},
    {"value": 17, "label": "Witch 17"},
    {"value": 18, "label": "Witch 18"},
    {"value": 19, "label": "Golem 19"},
    {"value": 20, "label": "Golem 20"},
    {"value": 21, "label": "Golem 21"},
    {"value": 22, "label": "P.E.K.K.A 22"},
    {"value": 23, "label": "P.E.K.K.A 23"},
    {"value": 24, "label": "P.E.K.K.A 24"},
    {"value": 25, "label": "Electro Titan 25"},
    {"value": 26, "label": "Electro Titan 26"},
    {"value": 27, "label": "Electro Titan 27"},
    {"value": 28, "label": "Dragon 28"},
    {"value": 29, "label": "Dragon 29"},
    {"value": 30, "label": "Dragon 30"},
    {"value": 31, "label": "Electro Dragon 31"},
    {"value": 32, "label": "Electro Dragon 32"},
    {"value": 33, "label": "Electro Dragon 33"},
    {"value": 34, "label": "Legend League 1"},
    {"value": 35, "label": "Legend League 2"},
    {"value": 36, "label": "Legend League 3"},
]
FALLBACK_BUILDER_BASE_LEAGUE_OPTIONS = [
    {"value": 0, "label": "No Builder Base Requirement"},
    *[
        {"value": league_id, "label": name}
        for league_id, name, _ in BUILDER_BASE_LEAGUES
    ],
]


def get_ranked_league_options() -> list[dict[str, object]]:
    """Return stored ranked league tier options."""
    return _get_options_from_db(
        RANKED_LEAGUE_TIER_KIND,
        FALLBACK_RANKED_LEAGUE_OPTIONS,
    )


def get_builder_base_league_options() -> list[dict[str, object]]:
    """Return stored Builder Base league options."""
    return _get_options_from_db(
        BUILDER_BASE_LEAGUE_KIND,
        FALLBACK_BUILDER_BASE_LEAGUE_OPTIONS,
    )


def get_max_ranked_league() -> int:
    """Return the highest stored ranked league tier value."""
    return _max_option_value(get_ranked_league_options())


def get_max_builder_base_league() -> int:
    """Return the highest stored Builder Base league value."""
    return _max_option_value(get_builder_base_league_options())


def ranked_league_name(value: object) -> str:
    """Return the display label for a ranked league tier value."""
    return _option_label(
        value,
        get_ranked_league_options(),
        "Unranked",
        "Unknown",
    )


def builder_base_league_name(value: object) -> str:
    """Return the display label for a Builder Base league value."""
    return _option_label(
        value,
        get_builder_base_league_options(),
        "No Builder Base Requirement",
        "Unknown",
    )


def update_league_metadata_collection() -> None:
    """Refresh ranked and Builder Base league metadata in MongoDB."""
    update_ranked_league_tier_collection()
    update_builder_base_league_collection()


def update_ranked_league_tier_collection() -> None:
    """Fetch ranked league tiers from Clash and store them in MongoDB."""
    try:
        response = clash_get(RANKED_LEAGUE_TIERS_ENDPOINT, headers=headers)
        options = _build_options(
            response.payload,
            fallback_prefix="League",
            id_offset=RANKED_LEAGUE_TIER_ID_OFFSET,
        )
    except (ClashApiError, KeyError, TypeError, ValueError):
        options = FALLBACK_RANKED_LEAGUE_OPTIONS

    _replace_options(RANKED_LEAGUE_TIER_KIND, options)


def update_builder_base_league_collection() -> None:
    """Fetch Builder Base leagues from Clash and store them in MongoDB."""
    try:
        response = clash_get(BUILDER_BASE_LEAGUES_ENDPOINT, headers=headers)
        options = _build_options(
            response.payload,
            fallback_prefix="Builder Base League",
            id_offset=BUILDER_BASE_LEAGUE_ID_OFFSET,
            initial_option={
                "value": 0,
                "label": "No Builder Base Requirement",
            },
        )
    except (ClashApiError, KeyError, TypeError, ValueError):
        options = FALLBACK_BUILDER_BASE_LEAGUE_OPTIONS

    _replace_options(BUILDER_BASE_LEAGUE_KIND, options)


def _get_options_from_db(
    kind: str,
    fallback_options: list[dict[str, object]],
) -> list[dict[str, object]]:
    collection = get_league_metadata_collection()
    options = list(
        collection.find(
            {"kind": kind},
            {"_id": 0, "kind": 0},
        ).sort("value", 1)
    )
    if _is_valid_options(options):
        return options

    return list(fallback_options)


def _replace_options(kind: str, options: list[dict[str, object]]) -> None:
    collection = get_league_metadata_collection()
    collection.delete_many({"kind": kind})
    for option in options:
        collection.insert_one({"kind": kind, **option})


def _build_options(
    payload: dict[str, Any],
    *,
    fallback_prefix: str,
    id_offset: int,
    initial_option: dict[str, object] | None = None,
) -> list[dict[str, object]]:
    items = payload.get("items")
    if not isinstance(items, list):
        raise ValueError("Missing league items in Clash API response.")

    options = [initial_option] if initial_option else []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            continue

        value = _league_value_from_item(item, index, id_offset)
        label = _league_label_from_item(item, fallback_prefix, value)
        options.append({"value": value, "label": label})

    options = _dedupe_options(options)
    if not options:
        raise ValueError("Clash API returned no usable league items.")

    return options


def _league_value_from_item(
    item: dict[str, Any],
    fallback_value: int,
    id_offset: int,
) -> int:
    try:
        value = int(item["id"]) - id_offset
    except (KeyError, TypeError, ValueError):
        value = None
    if value is not None and value >= 0:
        return value

    for key in ("rank", "tier"):
        try:
            value = int(item[key])
        except (KeyError, TypeError, ValueError):
            continue
        if value > 0:
            return value

    name = item.get("name")
    if isinstance(name, str):
        match = TRAILING_NUMBER_PATTERN.search(name.strip())
        if match:
            return int(match.group(1))

    return fallback_value


def _league_label_from_item(
    item: dict[str, Any],
    fallback_prefix: str,
    value: int,
) -> str:
    name = item.get("name")
    if isinstance(name, str) and name.strip():
        return name.strip()

    return f"{fallback_prefix} {value}"


def _dedupe_options(
    options: list[dict[str, object] | None],
) -> list[dict[str, object]]:
    deduped = []
    seen_values = set()
    for option in options:
        if not isinstance(option, dict):
            continue
        value = option.get("value")
        if value in seen_values:
            continue
        seen_values.add(value)
        deduped.append(option)

    return deduped


def _is_valid_options(value: object) -> bool:
    if not isinstance(value, list):
        return False
    if not value:
        return False

    return all(
        isinstance(option, dict)
        and isinstance(option.get("value"), int)
        and isinstance(option.get("label"), str)
        for option in value
    )


def _max_option_value(options: list[dict[str, object]]) -> int:
    return max(option["value"] for option in options)


def _option_label(
    value: object,
    options: list[dict[str, object]],
    zero_label: str,
    unknown_label: str,
) -> str:
    try:
        normalized_value = int(value)
    except (TypeError, ValueError):
        return zero_label

    if normalized_value == 0:
        return zero_label

    labels = {option["value"]: option["label"] for option in options}
    return labels.get(normalized_value, unknown_label)


if __name__ == "__main__":
    update_league_metadata_collection()
