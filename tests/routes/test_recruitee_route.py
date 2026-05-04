class DummyCursor:
    def __init__(self, docs):
        self.docs = docs
        self.sort_fields = None
        self.skip_count = None
        self.limit_count = None

    def sort(self, fields):
        self.sort_fields = fields
        return self

    def skip(self, count):
        self.skip_count = count
        return self

    def limit(self, count):
        self.limit_count = count
        return self

    def __iter__(self):
        start = self.skip_count or 0
        stop = start + self.limit_count
        return iter(self.docs[start:stop])


class DummyClanCollection:
    def __init__(self, docs=None, tag_result=None):
        self.cursor = DummyCursor(docs or [])
        self.tag_result = tag_result
        self.count_query = None
        self.find_query = None
        self.find_projection = None
        self.find_one_query = None
        self.find_one_projection = None

    def count_documents(self, query):
        self.count_query = query
        return len(self.cursor.docs)

    def find(self, query, projection):
        self.find_query = query
        self.find_projection = projection
        return self.cursor

    def find_one(self, query, projection):
        self.find_one_query = query
        self.find_one_projection = projection
        return self.tag_result


def test_recruitee_get_filters_logged_in_player_with_total(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    refresh_calls = []
    collection = DummyClanCollection(
        [
            {"clan_tag": "TEST1", "name": "test_clan_1"},
            {"clan_tag": "TEST2", "name": "test_clan_2"},
            {"clan_tag": "TEST3", "name": "test_clan_3"},
        ]
    )

    set_session(
        player_name="test_player",
        player_league=5,
        player_builderbase_trophies=2200,
        player_townhall=13,
    )
    monkeypatch.setattr(
        recruitee_route,
        "ensure_imported_clan_inventory",
        lambda: refresh_calls.append(True),
    )
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.get("/recruitee?includeTotal=1&limit=1&offset=1")

    expected_query = {
        "requirements.0": {"$lte": 5},
        "requirements.1": {"$lte": 2200},
        "requirements.2": {"$lte": 13},
    }

    assert response.status_code == 200
    assert response.get_json() == {
        "items": [{"clan_tag": "TEST2", "name": "test_clan_2"}],
        "total": 3,
        "limit": 1,
        "offset": 1,
    }
    assert refresh_calls == []
    assert collection.find_query == expected_query
    assert collection.count_query == expected_query
    assert collection.find_projection == {"_id": 0}
    assert collection.cursor.sort_fields == [
        ("last_updated", -1),
        ("clan_tag", 1),
    ]
    assert collection.cursor.skip_count == 1
    assert collection.cursor.limit_count == 1


def test_recruitee_get_returns_guest_default_raw_list(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    refresh_calls = []
    collection = DummyClanCollection(
        [
            {"clan_tag": "TEST1", "name": "test_clan_1"},
            {"clan_tag": "TEST2", "name": "test_clan_2"},
        ]
    )

    set_session(player_name="Guest")
    monkeypatch.setattr(
        recruitee_route,
        "ensure_imported_clan_inventory",
        lambda: refresh_calls.append(True),
    )
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.get("/recruitee")

    assert response.status_code == 200
    assert response.get_json() == [
        {"clan_tag": "TEST1", "name": "test_clan_1"},
        {"clan_tag": "TEST2", "name": "test_clan_2"},
    ]
    assert refresh_calls == [True]
    assert collection.find_query == {}
    assert collection.count_query is None
    assert collection.cursor.skip_count == 0
    assert collection.cursor.limit_count == 10


def test_recruitee_post_filters_and_paginates_with_total(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    refresh_calls = []
    collection = DummyClanCollection(
        [
            {"clan_tag": "TEST1", "name": "test_clan_1"},
            {"clan_tag": "TEST2", "name": "test_clan_2"},
            {"clan_tag": "TEST3", "name": "test_clan_3"},
        ]
    )

    monkeypatch.setattr(
        recruitee_route,
        "ensure_imported_clan_inventory",
        lambda: refresh_calls.append(True),
    )
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.post(
        "/recruitee?includeTotal=1&limit=2&offset=0",
        json={
            "filters": {
                "name": "  Test.*  ",
                "requirements": {
                    "townhall": 12,
                    "league": 4,
                    "members": {"min": 30, "max": 45},
                },
                "minClanLevel": 10,
                "clanPoints": 35000,
                "warFrequency": "always",
                "location_id": "32000007",
            }
        },
    )

    expected_query = {
        "name": {"$regex": "Test\\.\\*", "$options": "i"},
        "requirements.2": {"$gte": 12},
        "requirements.0": {"$gte": 4},
        "clan_info.clan_level": {"$gte": 10},
        "clan_info.clanPoints": {"$gte": 35000},
        "clan_info.member_count": {"$gte": 30, "$lte": 45},
        "clan_info.warFrequency": "always",
        "clan_info.location.id": 32000007,
    }

    assert response.status_code == 200
    assert response.get_json() == {
        "items": [
            {"clan_tag": "TEST1", "name": "test_clan_1"},
            {"clan_tag": "TEST2", "name": "test_clan_2"},
        ],
        "total": 3,
        "limit": 2,
        "offset": 0,
    }
    assert refresh_calls == [True]
    assert collection.find_query == expected_query
    assert collection.count_query == expected_query
    assert collection.find_projection == {"_id": 0}
    assert collection.cursor.sort_fields == [
        ("last_updated", -1),
        ("clan_tag", 1),
    ]
    assert collection.cursor.skip_count == 0
    assert collection.cursor.limit_count == 2


def test_recruitee_post_returns_clan_by_tag(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection(
        tag_result={"clan_tag": "TEST123", "name": "test_clan"}
    )
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.post("/recruitee", json={"clanTag": "TEST123"})

    assert response.status_code == 200
    assert response.get_json() == {"clan_tag": "TEST123", "name": "test_clan"}
    assert collection.find_one_query == {"clan_tag": "TEST123"}
    assert collection.find_one_projection == {"_id": 0}
    assert collection.find_query is None


def test_recruitee_post_filters_by_location_name_without_location_id(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    refresh_calls = []
    collection = DummyClanCollection(
        [{"clan_tag": "TEST123", "name": "test_clan"}]
    )
    monkeypatch.setattr(
        recruitee_route,
        "ensure_imported_clan_inventory",
        lambda: refresh_calls.append(True),
    )
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.post(
        "/recruitee",
        json={"filters": {"location": "International"}},
    )

    assert response.status_code == 200
    assert response.get_json() == [
        {"clan_tag": "TEST123", "name": "test_clan"}
    ]
    assert refresh_calls == [True]
    assert collection.find_query == {
        "clan_info.location.name": "International",
    }
    assert collection.count_query is None


def test_recruitee_uses_defaults_for_invalid_limit_and_offset(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection(
        [{"clan_tag": "TEST123", "name": "test_clan"}]
    )
    monkeypatch.setattr(
        recruitee_route,
        "ensure_imported_clan_inventory",
        lambda: None,
    )
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.get("/recruitee?includeTotal=1&limit=bad&offset=bad")

    assert response.status_code == 200
    assert response.get_json() == {
        "items": [{"clan_tag": "TEST123", "name": "test_clan"}],
        "total": 1,
        "limit": 10,
        "offset": 0,
    }
    assert collection.find_query == {}
    assert collection.count_query == {}
    assert collection.cursor.skip_count == 0
    assert collection.cursor.limit_count == 10


def test_recruitee_post_returns_400_for_invalid_location_id(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection()
    monkeypatch.setattr(
        recruitee_route,
        "ensure_imported_clan_inventory",
        lambda: None,
    )
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.post(
        "/recruitee",
        json={"filters": {"location_id": "not-a-number"}},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid location_id"}
    assert collection.find_query is None


def test_recruitee_post_returns_404_for_missing_clan_tag(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection(tag_result=None)
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.post("/recruitee", json={"clanTag": "MISSING"})

    assert response.status_code == 404
    assert response.get_json() == {"error": "Clan not found"}
    assert collection.find_one_query == {"clan_tag": "MISSING"}
    assert collection.find_one_projection == {"_id": 0}
