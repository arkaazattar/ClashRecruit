from datetime import datetime, timedelta, timezone

import ClashRecruit.services.recruiter_listing as recruiter_listing

FROZEN_NOW = datetime(2026, 5, 12, 12, 30, tzinfo=timezone.utc)


class DummyDeleteResult:
    def __init__(self, deleted_count):
        self.deleted_count = deleted_count


class DummyClanCollection:
    def __init__(self, existing=None, deleted_count=1):
        self.existing = existing
        self.deleted_count = deleted_count
        self.find_one_query = None
        self.inserted_doc = None
        self.update_call = None
        self.delete_query = None

    def find_one(self, query):
        self.find_one_query = query
        return self.existing

    def insert_one(self, doc):
        self.inserted_doc = doc

    def update_one(self, query, update):
        self.update_call = (query, update)

    def delete_one(self, query):
        self.delete_query = query
        return DummyDeleteResult(self.deleted_count)


class DummyRecruiter:
    instances = []

    def __init__(self, clan_tag, headers):
        self.clan_tag = clan_tag
        self.headers = headers
        self.requirements = [1, 2, 3]
        self.pull_called = False
        self.lookup_modes = []
        DummyRecruiter.instances.append(self)

    def pull_clan_requirements(self):
        self.pull_called = True
        return self.requirements

    def lookup_clan(self, mode=None):
        self.lookup_modes.append(mode)
        if mode == "description":
            return {"description": "test_clan_description"}

        return {
            "name": "test_clan",
            "description": "original_description",
            "member_count": 40,
        }


class FakeDatetime:
    @staticmethod
    def now(tz=None):
        return FROZEN_NOW


def setup_recruiter_listing(monkeypatch, collection):
    DummyRecruiter.instances = []
    monkeypatch.setattr(recruiter_listing, "Recruiter", DummyRecruiter)
    monkeypatch.setattr(
        recruiter_listing,
        "get_clan_collection",
        lambda: collection,
    )
    monkeypatch.setattr(recruiter_listing, "refresh", lambda headers: 17)
    monkeypatch.setattr(recruiter_listing, "datetime", FakeDatetime)


def test_get_recruiter_listing_page_returns_existing_listing(monkeypatch):
    existing = {
        "requirements": [4, 1800, 12],
        "clan_info": {"description": "existing_description"},
        "expires": "existing_expiry",
    }
    collection = DummyClanCollection(existing=existing)
    setup_recruiter_listing(monkeypatch, collection)

    payload, status_code = recruiter_listing.get_recruiter_listing_page(
        "TEST123"
    )

    assert status_code == 200
    assert payload == {
        "oldRequiredLeague": 4,
        "oldRequiredBuilderLeague": 1800,
        "oldRequiredTownhall": 12,
        "MAXTOWNHALL": 17,
        "clanDescription": "existing_description",
        "status": "existing_expiry",
    }
    assert collection.find_one_query == {
        "clan_tag": "TEST123",
        "source": {"$ne": "clash_api_import"},
    }
    assert DummyRecruiter.instances[0].pull_called is True
    assert DummyRecruiter.instances[0].lookup_modes == []


def test_get_recruiter_listing_page_uses_clash_defaults(monkeypatch):
    collection = DummyClanCollection(existing=None)
    setup_recruiter_listing(monkeypatch, collection)

    payload, status_code = recruiter_listing.get_recruiter_listing_page(
        "TEST123"
    )

    assert status_code == 200
    assert payload == {
        "oldRequiredLeague": 1,
        "oldRequiredBuilderLeague": 2,
        "oldRequiredTownhall": 3,
        "MAXTOWNHALL": 17,
        "clanDescription": "test_clan_description",
        "status": None,
    }
    assert DummyRecruiter.instances[0].lookup_modes == ["description"]


def test_create_recruiter_listing_inserts_live_listing(monkeypatch):
    collection = DummyClanCollection()
    setup_recruiter_listing(monkeypatch, collection)

    payload, status_code = recruiter_listing.create_recruiter_listing(
        "TEST123",
        "PLAYER123",
        {
            "requiredLeague": 5,
            "requiredBuilderLeague": 2400,
            "requiredTownhall": 13,
            "description": "new_description",
        },
    )

    expiry = FROZEN_NOW + timedelta(days=7)
    assert status_code == 200
    assert payload["message"] == "Listing created successfully."
    assert payload["source"] == "live_listing"
    assert payload["requirements"] == [5, 2400, 13]
    assert payload["name"] == "test_clan"
    assert payload["clan_tag"] == "TEST123"
    assert payload["player_tag"] == "PLAYER123"
    assert payload["clan_info"]["description"] == "new_description"
    assert payload["last_updated"] == FROZEN_NOW
    assert payload["expires"] == expiry
    assert payload["status"] == expiry
    assert collection.inserted_doc["last_updated"] == FROZEN_NOW
    assert collection.inserted_doc["expires"] == expiry


def test_update_recruiter_listing_refreshes_expiry(monkeypatch):
    collection = DummyClanCollection(existing={"requirements": [1, 2, 3]})
    setup_recruiter_listing(monkeypatch, collection)

    payload, status_code = recruiter_listing.update_recruiter_listing(
        "TEST123",
        {
            "requiredLeague": 6,
            "requiredBuilderLeague": 2600,
            "requiredTownhall": 14,
            "description": "updated_description",
            "updateExpiry": True,
        },
    )
    update_query, update_doc = collection.update_call
    set_doc = update_doc["$set"]
    expiry = FROZEN_NOW + timedelta(days=7)

    assert status_code == 200
    assert payload == {
        "status": expiry,
        "message": "Listing updated successfully.",
    }
    assert update_query == {
        "clan_tag": "TEST123",
        "source": {"$ne": "clash_api_import"},
    }
    assert set_doc == {
        "source": "live_listing",
        "requirements": [6, 2600, 14],
        "clan_info.description": "updated_description",
        "last_updated": FROZEN_NOW,
        "expires": expiry,
    }


def test_update_recruiter_listing_preserves_provided_expiry(monkeypatch):
    collection = DummyClanCollection(existing={"requirements": [1, 2, 3]})
    setup_recruiter_listing(monkeypatch, collection)

    payload, status_code = recruiter_listing.update_recruiter_listing(
        "TEST123",
        {
            "requiredLeague": 6,
            "requiredBuilderLeague": 2600,
            "requiredTownhall": 14,
            "description": "updated_description",
            "updateExpiry": False,
            "expiry": "provided_expiry",
        },
    )
    _, update_doc = collection.update_call
    set_doc = update_doc["$set"]

    assert status_code == 200
    assert payload == {
        "status": "provided_expiry",
        "message": "Listing updated successfully.",
    }
    assert "expires" not in set_doc


def test_remove_recruiter_listing_returns_delete_result(monkeypatch):
    collection = DummyClanCollection(deleted_count=1)
    setup_recruiter_listing(monkeypatch, collection)

    payload, status_code = recruiter_listing.remove_recruiter_listing(
        "TEST123"
    )

    assert status_code == 200
    assert payload == {"message": "Successfully deleted entry."}
    assert collection.delete_query == {
        "clan_tag": "TEST123",
        "source": {"$ne": "clash_api_import"},
    }


def test_remove_recruiter_listing_returns_404_when_not_deleted(monkeypatch):
    collection = DummyClanCollection(deleted_count=0)
    setup_recruiter_listing(monkeypatch, collection)

    payload, status_code = recruiter_listing.remove_recruiter_listing(
        "TEST123"
    )

    assert status_code == 404
    assert payload == {"message": "Failed to delete."}


def test_handle_recruiter_listing_action_rejects_unknown_status(monkeypatch):
    collection = DummyClanCollection()
    setup_recruiter_listing(monkeypatch, collection)

    payload, status_code = recruiter_listing.handle_recruiter_listing_action(
        "TEST123",
        "PLAYER123",
        {"status": "unexpected"},
    )

    assert status_code == 400
    assert payload == {"message": "Invalid listing status."}
    assert DummyRecruiter.instances == []
    assert collection.inserted_doc is None
    assert collection.update_call is None
    assert collection.delete_query is None
