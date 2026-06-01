def test_saved_clans_get_hydrates_available_and_missing_listings(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.saved_clans_route as saved_clans_route

    class DummyUserCollection:
        def find_one(self, query, projection):
            assert query == {"player_tag": "PLAYER123"}
            assert projection == {"_id": 0, "saved_clans": 1}
            return {"saved_clans": ["ABC123", "MISSING"]}

    class DummyClanCollection:
        def find(self, query, projection):
            assert query["clan_tag"] == {"$in": ["ABC123", "MISSING"]}
            assert "$gt" in query["expires"]
            assert projection == {
                "_id": 0,
                "clan_tag": 1,
                "name": 1,
                "requirements": 1,
                "clan_info": 1,
            }
            return [
                {
                    "clan_tag": "ABC123",
                    "name": "test_clan",
                    "requirements": [1, 2, 3],
                    "clan_info": {"name": "test_clan_info"},
                }
            ]

    set_session(player_tag="PLAYER123")
    monkeypatch.setattr(
        saved_clans_route,
        "get_user_collection",
        lambda: DummyUserCollection(),
    )
    monkeypatch.setattr(
        saved_clans_route,
        "get_clan_collection",
        lambda: DummyClanCollection(),
    )

    response = client.get("/saved-clans")

    assert response.status_code == 200
    assert response.get_json() == {
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


def test_saved_clans_get_returns_empty_saved_list(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.saved_clans_route as saved_clans_route

    class DummyUserCollection:
        def find_one(self, query, projection):
            assert query == {"player_tag": "PLAYER123"}
            assert projection == {"_id": 0, "saved_clans": 1}
            return {"saved_clans": []}

    class DummyClanCollection:
        def find(self, query, projection):
            assert query["clan_tag"] == {"$in": []}
            assert "$gt" in query["expires"]
            assert projection == {
                "_id": 0,
                "clan_tag": 1,
                "name": 1,
                "requirements": 1,
                "clan_info": 1,
            }
            return []

    set_session(player_tag="PLAYER123")
    monkeypatch.setattr(
        saved_clans_route,
        "get_user_collection",
        lambda: DummyUserCollection(),
    )
    monkeypatch.setattr(
        saved_clans_route,
        "get_clan_collection",
        lambda: DummyClanCollection(),
    )

    response = client.get("/saved-clans")

    assert response.status_code == 200
    assert response.get_json() == {
        "saved_clans": [],
        "count": 0,
        "max_saved_clans": 10,
    }


def test_saved_clans_get_uses_clan_info_name_when_top_level_name_missing(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.saved_clans_route as saved_clans_route

    class DummyUserCollection:
        def find_one(self, query, projection):
            return {"saved_clans": ["ABC123"]}

    class DummyClanCollection:
        def find(self, query, projection):
            return [
                {
                    "clan_tag": "ABC123",
                    "requirements": [1, 2, 3],
                    "clan_info": {"name": "test_clan_info"},
                }
            ]

    set_session(player_tag="PLAYER123")
    monkeypatch.setattr(
        saved_clans_route,
        "get_user_collection",
        lambda: DummyUserCollection(),
    )
    monkeypatch.setattr(
        saved_clans_route,
        "get_clan_collection",
        lambda: DummyClanCollection(),
    )

    response = client.get("/saved-clans")

    assert response.status_code == 200
    assert response.get_json() == {
        "saved_clans": [
            {
                "clan_tag": "ABC123",
                "name": "test_clan_info",
                "requirements": [1, 2, 3],
                "clan_info": {"name": "test_clan_info"},
                "listing_available": True,
            }
        ],
        "count": 1,
        "max_saved_clans": 10,
    }


def test_saved_clans_post_adds_normalized_tag(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.saved_clans_route as saved_clans_route

    class DummyUserCollection:
        def __init__(self):
            self.update_call = None

        def find_one(self, query, projection):
            assert query == {"player_tag": "PLAYER123"}
            assert projection == {"_id": 0, "saved_clans": 1}
            return {"saved_clans": ["EXISTING"]}

        def update_one(self, query, update, upsert=False):
            self.update_call = (query, update, upsert)

    user_collection = DummyUserCollection()

    set_session(player_tag="PLAYER123")
    monkeypatch.setattr(
        saved_clans_route,
        "get_user_collection",
        lambda: user_collection,
    )

    response = client.post("/saved-clans/%23ABC123")

    assert response.status_code == 200
    assert response.get_json() == {
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


def test_saved_clans_post_returns_400_for_empty_tag(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.saved_clans_route as saved_clans_route

    monkeypatch.setattr(
        saved_clans_route,
        "get_user_collection",
        lambda: object(),
    )
    set_session(player_tag="PLAYER123")

    response = client.post("/saved-clans/%20%20")

    assert response.status_code == 400
    assert response.get_json() == {"error": "clan_tag is required."}


def test_saved_clans_post_returns_existing_without_update(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.saved_clans_route as saved_clans_route

    class DummyUserCollection:
        def __init__(self):
            self.update_called = False

        def find_one(self, query, projection):
            return {"saved_clans": ["ABC123"]}

        def update_one(self, query, update, upsert=False):
            self.update_called = True

    user_collection = DummyUserCollection()

    set_session(player_tag="PLAYER123")
    monkeypatch.setattr(
        saved_clans_route,
        "get_user_collection",
        lambda: user_collection,
    )

    response = client.post("/saved-clans/ABC123")

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "Clan already saved.",
        "clan_tag": "ABC123",
        "count": 1,
        "max_saved_clans": 10,
    }
    assert user_collection.update_called is False


def test_saved_clans_post_returns_conflict_at_limit(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.saved_clans_route as saved_clans_route

    class DummyUserCollection:
        def __init__(self):
            self.update_called = False

        def find_one(self, query, projection):
            return {"saved_clans": [f"TAG{i}" for i in range(10)]}

        def update_one(self, query, update, upsert=False):
            self.update_called = True

    user_collection = DummyUserCollection()

    set_session(player_tag="PLAYER123")
    monkeypatch.setattr(
        saved_clans_route,
        "get_user_collection",
        lambda: user_collection,
    )

    response = client.post("/saved-clans/ABC123")

    assert response.status_code == 409
    assert response.get_json() == {
        "message": (
            "You can save up to 10 clans. Remove one before saving another."
        ),
        "count": 10,
        "max_saved_clans": 10,
    }
    assert user_collection.update_called is False


def test_saved_clans_delete_removes_normalized_tag(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.saved_clans_route as saved_clans_route

    class DummyUserCollection:
        def __init__(self):
            self.update_call = None

        def update_one(self, query, update):
            self.update_call = (query, update)

    user_collection = DummyUserCollection()

    set_session(player_tag="PLAYER123")
    monkeypatch.setattr(
        saved_clans_route,
        "get_user_collection",
        lambda: user_collection,
    )

    response = client.delete("/saved-clans/%23ABC123")

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "Saved clan removed.",
        "clan_tag": "ABC123",
    }
    assert user_collection.update_call == (
        {"player_tag": "PLAYER123"},
        {"$pull": {"saved_clans": "ABC123"}},
    )
