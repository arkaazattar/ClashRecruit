"""Convert stored Builder Base trophy requirements to league ids."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PACKAGE_PARENT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACKAGE_PARENT))

from ClashRecruit.services.builder_base_leagues import (  # noqa: E402
    BUILDER_BASE_LEAGUE_MAX_ID,
    builder_base_league_id_from_trophies,
)
from ClashRecruit.services.mongo_db_client import get_clan_collection  # noqa: E402


def migrate_builder_base_requirements(*, apply: bool) -> int:
    """Convert legacy trophy values in ``requirements.1`` to league ids."""
    clan_collection = get_clan_collection()
    query = {"requirements.1": {"$gt": BUILDER_BASE_LEAGUE_MAX_ID}}
    documents = clan_collection.find(query, {"_id": 1, "requirements": 1})

    migrated_count = 0
    for document in documents:
        requirements = list(document.get("requirements") or [])
        if len(requirements) < 2:
            continue

        old_value = requirements[1]
        new_value = builder_base_league_id_from_trophies(
            old_value,
            zero_as_no_requirement=True,
        )
        requirements[1] = new_value
        migrated_count += 1

        print(f"{document['_id']}: {old_value} -> {new_value}")
        if apply:
            clan_collection.update_one(
                {"_id": document["_id"]},
                {"$set": {"requirements": requirements}},
            )

    mode = "updated" if apply else "would update"
    print(f"{mode} {migrated_count} clan listing(s).")
    return migrated_count


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Convert legacy requirements.1 Builder Base trophy values "
            "to Builder Base league ids."
        ),
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write converted values to MongoDB. Omit for a dry run.",
    )
    args = parser.parse_args()
    migrate_builder_base_requirements(apply=args.apply)


if __name__ == "__main__":
    main()
