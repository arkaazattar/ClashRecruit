from ClashRecruit.services.saved_clans import (
    add_saved_clan,
    delete_saved_clan,
    get_saved_clans_payload,
)


class DummyUserCollection:
    def __init__(self, saved_clans=None):
        self.saved_clans = saved_clans or []
        self.find_one_query = None
        self.find_one_projection = None
        self.update_call = None

    def find_one(self, query, projection):
        self.find_one_query = query
        self.find_one_projection = projection
        return {"saved_clans": self.saved_clans}

    def update_one(self, query, update, upsert=False):
        self.update_call = (query, update, upsert)


class DummyClanCollection:
    def __init__(self, listings):
        self.listings = listings
        self.find_query = None
        self.find_projection = None

    def find(self, query, projection):
        self.find_query = query
        self.find_projection = projection
        return self.listings


def test_get_saved_clans_payload_hydrates_available_and_missing_listings():
    user_collection = DummyUserCollection(["ABC123", "MISSING"])
    clan_collection = DummyClanCollection(
        [
            {
                "clan_tag": "ABC123",
                "name": "test_clan",
                "requirements": [1, 2, 3],
                "clan_info": {"name": "test_clan_info"},
            }
        ]
    )

    payload = get_saved_clans_payload(
        "PLAYER123",
        user_collection,
        clan_collection,
    )

    assert payload == {
        "saved_clans": [
            {
                "clan_tag": "ABC123",
                "name": "test_clan",
                "requirements": [1, 2, 3],
                "clan_info": {"name": "test_clan_info"},
                "listing_available": True,
            },
            {
                "clan_tag": "MISSING",
                "name": "MISSING",
                "requirements": None,
                "clan_info": {},
                "listing_available": False,
            },
        ],
        "count": 2,
        "max_saved_clans": 10,
    }
    assert user_collection.find_one_query == {"player_tag": "PLAYER123"}
    assert clan_collection.find_query["clan_tag"] == {
        "$in": ["ABC123", "MISSING"],
    }
    assert "$gt" in clan_collection.find_query["expires"]


def test_add_saved_clan_adds_tag_when_under_limit():
    user_collection = DummyUserCollection(["EXISTING"])

    payload, status_code = add_saved_clan(
        "PLAYER123",
        "ABC123",
        user_collection,
    )

    assert status_code == 200
    assert payload == {
        "message": "Clan saved.",
        "clan_tag": "ABC123",
        "count": 2,
        "max_saved_clans": 10,
    }
    assert user_collection.update_call == (
        {"player_tag": "PLAYER123"},
        {
            "$addToSet": {"saved_clans": "ABC123"},
            "$setOnInsert": {"player_tag": "PLAYER123"},
        },
        True,
    )


def test_add_saved_clan_returns_existing_without_update():
    user_collection = DummyUserCollection(["ABC123"])

    payload, status_code = add_saved_clan(
        "PLAYER123",
        "ABC123",
        user_collection,
    )

    assert status_code == 200
    assert payload["message"] == "Clan already saved."
    assert payload["count"] == 1
    assert user_collection.update_call is None


def test_add_saved_clan_returns_conflict_at_limit():
    user_collection = DummyUserCollection([f"TAG{i}" for i in range(10)])

    payload, status_code = add_saved_clan(
        "PLAYER123",
        "ABC123",
        user_collection,
    )

    assert status_code == 409
    assert payload == {
        "message": (
            "You can save up to 10 clans. Remove one before saving another."
        ),
        "count": 10,
        "max_saved_clans": 10,
    }
    assert user_collection.update_call is None


def test_delete_saved_clan_removes_tag():
    user_collection = DummyUserCollection()

    payload, status_code = delete_saved_clan(
        "PLAYER123",
        "ABC123",
        user_collection,
    )

    assert status_code == 200
    assert payload == {
        "message": "Saved clan removed.",
        "clan_tag": "ABC123",
    }
    assert user_collection.update_call == (
        {"player_tag": "PLAYER123"},
        {"$pull": {"saved_clans": "ABC123"}},
        False,
    )
