"""Builder Base league helpers."""

from bisect import bisect_right
from typing import Final

BUILDER_BASE_LEAGUES: Final[list[tuple[int, str, int]]] = [
    (1, "Wood V", 0),
    (2, "Wood IV", 100),
    (3, "Wood III", 200),
    (4, "Wood II", 300),
    (5, "Wood I", 400),
    (6, "Clay V", 500),
    (7, "Clay IV", 600),
    (8, "Clay III", 700),
    (9, "Clay II", 800),
    (10, "Clay I", 900),
    (11, "Stone V", 1000),
    (12, "Stone IV", 1100),
    (13, "Stone III", 1200),
    (14, "Stone II", 1300),
    (15, "Stone I", 1400),
    (16, "Copper V", 1500),
    (17, "Copper IV", 1600),
    (18, "Copper III", 1700),
    (19, "Copper II", 1800),
    (20, "Copper I", 1900),
    (21, "Brass III", 2000),
    (22, "Brass II", 2200),
    (23, "Brass I", 2400),
    (24, "Iron III", 2600),
    (25, "Iron II", 2800),
    (26, "Iron I", 3000),
    (27, "Steel III", 3200),
    (28, "Steel II", 3400),
    (29, "Steel I", 3600),
    (30, "Titanium III", 3800),
    (31, "Titanium II", 4000),
    (32, "Titanium I", 4200),
    (33, "Platinum III", 4400),
    (34, "Platinum II", 4600),
    (35, "Platinum I", 4800),
    (36, "Emerald III", 5000),
    (37, "Emerald II", 5200),
    (38, "Emerald I", 5400),
    (39, "Ruby III", 5600),
    (40, "Ruby II", 5800),
    (41, "Ruby I", 6000),
    (42, "Diamond", 6200),
]

BUILDER_BASE_LEAGUE_MAX_ID: Final[int] = BUILDER_BASE_LEAGUES[-1][0]
_BUILDER_BASE_THRESHOLDS: Final[list[int]] = [
    threshold for _, _, threshold in BUILDER_BASE_LEAGUES
]
_BUILDER_BASE_NAMES_BY_ID: Final[dict[int, str]] = {
    league_id: name for league_id, name, _ in BUILDER_BASE_LEAGUES
}


def builder_base_league_id_from_trophies(
    trophies: object,
    *,
    zero_as_no_requirement: bool = False,
) -> int:
    """Return the Builder Base league id for a trophy value."""
    try:
        trophy_count = int(trophies)
    except (TypeError, ValueError):
        return 0 if zero_as_no_requirement else 1

    if trophy_count <= 0 and zero_as_no_requirement:
        return 0
    if trophy_count < 0:
        trophy_count = 0

    return bisect_right(_BUILDER_BASE_THRESHOLDS, trophy_count)


def builder_base_league_name(league_id: object) -> str:
    """Return a display label for a Builder Base league id."""
    try:
        normalized_id = int(league_id)
    except (TypeError, ValueError):
        return "No Builder Base Requirement"

    if normalized_id == 0:
        return "No Builder Base Requirement"
    return _BUILDER_BASE_NAMES_BY_ID.get(normalized_id, "Unknown")
