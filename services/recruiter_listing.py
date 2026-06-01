"""Service functions for recruiter listing lifecycle operations."""

from datetime import datetime, timedelta, timezone

from ..api.recruiter_api import Recruiter
from ..config import headers
from .maxtownhall import refresh
from .mongo_db_client import get_clan_collection

LISTING_DURATION = timedelta(days=7)
VALID_LISTING_STATUSES = {"new", "update", "removeListing"}


def get_recruiter_listing_page(
    clan_tag: str | None,
) -> tuple[dict[str, object], int]:
    """Return recruiter listing form data for a clan."""
    clan_collection = get_clan_collection()
    existing = clan_collection.find_one(_listing_query(clan_tag))

    recruiter = _recruiter_with_requirements(clan_tag)
    if existing:
        required_league = existing["requirements"][0]
        required_builder_league = existing["requirements"][1]
        required_townhall = existing["requirements"][2]
        clan_description = existing.get("clan_info", {}).get(
            "description",
            "",
        )
        status = existing["expires"]
    else:
        required_league = recruiter.requirements[0]
        required_builder_league = recruiter.requirements[1]
        required_townhall = recruiter.requirements[2]
        clan_description = recruiter.lookup_clan("description")[
            "description"
        ]
        status = None

    return (
        {
            "oldRequiredLeague": required_league,
            "oldRequiredBuilderLeague": required_builder_league,
            "oldRequiredTownhall": required_townhall,
            "MAXTOWNHALL": refresh(headers),
            "clanDescription": clan_description,
            "status": status,
        },
        200,
    )


def handle_recruiter_listing_action(
    clan_tag: str | None,
    player_tag: str | None,
    data: dict[str, object],
) -> tuple[dict[str, object], int]:
    """Create, update, or remove a recruiter listing from request data."""
    listing_status = data.get("status")
    if listing_status not in VALID_LISTING_STATUSES:
        return {"message": "Invalid listing status."}, 400

    if listing_status == "removeListing":
        return remove_recruiter_listing(clan_tag)

    if listing_status == "new":
        return create_recruiter_listing(clan_tag, player_tag, data)

    return update_recruiter_listing(clan_tag, data)


def create_recruiter_listing(
    clan_tag: str | None,
    player_tag: str | None,
    data: dict[str, object],
) -> tuple[dict[str, object], int]:
    """Create a live recruiter listing for a clan."""
    clan_collection = get_clan_collection()
    recruiter = _recruiter_with_requirements(clan_tag)
    _set_requirements_from_data(recruiter, data)

    clan_info = recruiter.lookup_clan()
    clan_info["description"] = data.get("description")

    now = datetime.now(timezone.utc)
    expiry = now + LISTING_DURATION
    document = {
        "source": "live_listing",
        "requirements": recruiter.requirements,
        "name": clan_info.get("name"),
        "clan_tag": clan_tag,
        "player_tag": player_tag,
        "clan_info": clan_info,
        "last_updated": now,
        "expires": expiry,
    }
    render_data = document.copy()
    clan_collection.insert_one(document)
    render_data["status"] = expiry
    render_data["message"] = "Listing created successfully."

    return render_data, 200


def update_recruiter_listing(
    clan_tag: str | None,
    data: dict[str, object],
) -> tuple[dict[str, object], int]:
    """Update a live recruiter listing for a clan."""
    clan_collection = get_clan_collection()
    recruiter = _recruiter_with_requirements(clan_tag)
    _set_requirements_from_data(recruiter, data)

    update_doc = {
        "source": "live_listing",
        "requirements": recruiter.requirements,
        "clan_info.description": data.get("description"),
        "last_updated": datetime.now(timezone.utc),
    }

    if data.get("updateExpiry") is True:
        expiry = datetime.now(timezone.utc) + LISTING_DURATION
        update_doc["expires"] = expiry
        status = expiry
    else:
        existing = clan_collection.find_one(_listing_query(clan_tag)) or {}
        status = existing.get("expires")

    clan_collection.update_one(
        _listing_query(clan_tag),
        {"$set": update_doc},
    )

    return {"status": status, "message": "Listing updated successfully."}, 200


def remove_recruiter_listing(
    clan_tag: str | None,
) -> tuple[dict[str, object], int]:
    """Remove a live recruiter listing for a clan."""
    clan_collection = get_clan_collection()
    deleted = clan_collection.delete_one(_listing_query(clan_tag))
    if deleted.deleted_count:
        return {"message": "Successfully deleted entry."}, 200

    return {"message": "Failed to delete."}, 404


def _listing_query(clan_tag: str | None) -> dict[str, object]:
    return {
        "clan_tag": clan_tag,
        "source": {"$ne": "clash_api_import"},
    }


def _recruiter_with_requirements(clan_tag: str | None) -> Recruiter:
    recruiter = Recruiter(clan_tag, headers)
    recruiter.pull_clan_requirements()
    return recruiter


def _set_requirements_from_data(
    recruiter: Recruiter,
    data: dict[str, object],
) -> None:
    recruiter.requirements[0] = data.get("requiredLeague")
    recruiter.requirements[1] = data.get("requiredBuilderLeague")
    recruiter.requirements[2] = data.get("requiredTownhall")
