"""Create lazy MongoDB accessors and explicit startup initialization hooks."""

from functools import lru_cache
from typing import Any

from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from .. import config


class MongoDependencyError(RuntimeError):
    """Raised when MongoDB is required but unavailable."""


@lru_cache(maxsize=1)
def get_mongo_client() -> MongoClient:
    """Return the shared MongoDB client for this process."""
    db_uri = (config.DBURI or "").strip()
    if not db_uri:
        raise MongoDependencyError(
            "DBURI is missing. Set DBURI before using MongoDB."
        )
    return MongoClient(db_uri, server_api=ServerApi("1"))


def _get_database() -> Database[Any]:
    """Return the application database handle."""
    return get_mongo_client()["clan_info_db"]


def get_location_collection() -> Collection[Any]:
    """Return the locations collection."""
    return _get_database()["locations"]


def get_clan_collection() -> Collection[Any]:
    """Return the clans collection."""
    return _get_database()["clans"]


def get_user_collection() -> Collection[Any]:
    """Return the users collection."""
    return _get_database()["users"]


def get_import_state_collection() -> Collection[Any]:
    """Return the import state collection."""
    return _get_database()["import_state"]


def _ping_mongo() -> None:
    """Check MongoDB availability by issuing a ping command."""
    try:
        get_mongo_client().admin.command("ping")
    except PyMongoError as exc:
        raise MongoDependencyError("Could not connect to MongoDB.") from exc


def _ensure_indexes() -> None:
    """Create indexes required by the application."""
    clan_collection = get_clan_collection()
    user_collection = get_user_collection()
    import_state_collection = get_import_state_collection()

    clan_collection.create_index("expires", expireAfterSeconds=0)
    user_collection.create_index("player_tag", unique=True)
    clan_collection.create_index([("clan_tag", 1), ("source", 1)], unique=True)

    clan_collection.create_index("source")
    clan_collection.create_index("last_updated")
    clan_collection.create_index([("last_updated", -1), ("clan_tag", 1)])
    clan_collection.create_index("requirements.0")
    clan_collection.create_index("requirements.1")
    clan_collection.create_index("requirements.2")
    clan_collection.create_index("last_discovered")
    clan_collection.create_index("last_enriched")
    clan_collection.create_index("detail_status")
    clan_collection.create_index("clan_info.location.id")
    clan_collection.create_index("clan_info.location.name")
    clan_collection.create_index("clan_info.member_count")
    clan_collection.create_index("clan_info.clan_level")
    clan_collection.create_index("clan_info.clanPoints")
    clan_collection.create_index("clan_info.warFrequency")

    import_state_collection.create_index("seed_key", unique=True)


def initialize_mongo() -> None:
    """Run explicit startup checks and index initialization for MongoDB."""
    _ping_mongo()
    _ensure_indexes()


def reset_mongo_client_cache() -> None:
    """Reset cached Mongo client state for tests."""
    get_mongo_client.cache_clear()
