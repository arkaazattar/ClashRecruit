"""Service functions for session and user state responses."""

from datetime import datetime, timezone
from typing import Any

USER_INFO_FIELDS = [
    "expLevel",
    "leagueTier",
    "builderBaseLeague",
    "builderHallLevel",
    "clan",
]


def get_session_state_payload(
    *,
    username: str,
    recruit_status: bool,
    clan_tag: str | None,
    townhall: Any,
    townhall_weapon_level: Any,
    clan_collection: Any,
) -> dict[str, Any]:
    """Return current session status and active listing state."""
    has_active_listing = False
    response_townhall = None
    response_townhall_weapon_level = None

    if username != "Guest":
        response_townhall = townhall
        response_townhall_weapon_level = townhall_weapon_level

    if clan_tag and clan_collection is not None:
        listing = clan_collection.find_one(
            {
                "clan_tag": clan_tag,
                "expires": {"$gt": datetime.now(timezone.utc)},
            },
            {"_id": 1},
        )
        has_active_listing = listing is not None

    return {
        "username": username,
        "recruit_status": recruit_status,
        "has_active_listing": has_active_listing,
        "townhall": response_townhall,
        "townhallWeaponLevel": response_townhall_weapon_level,
    }


def get_user_info_payload(player_tag: str | None, api_factory: Any) -> dict:
    """Return extended player info for a player tag."""
    if player_tag is None:
        return {}

    user = api_factory(player_tag)
    return user.check_player(USER_INFO_FIELDS) or {}
