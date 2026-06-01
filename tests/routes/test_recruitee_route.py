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


def expected_active_query(collection, query=None):
    expected = dict(query or {})
    expected["expires"] = collection.find_query["expires"]
    assert "$gt" in collection.find_query["expires"]
    return expected


def test_recruitee_get_filters_logged_in_player_with_total(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

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
        "get_clan_collection",
        lambda: collection,
    )

    response = client.get("/recruitee?includeTotal=1&limit=1&offset=1")

    expected_query = {
        "requirements.0": {"$lte": 5},
        "requirements.1": {"$lte": 2200},
        "requirements.2": {"$lte": 13},
        "expires": collection.find_query["expires"],
    }

    assert response.status_code == 200
    assert response.get_json() == {
        "items": [{"clan_tag": "TEST2", "name": "test_clan_2"}],
        "total": 3,
        "limit": 1,
        "offset": 1,
    }
    assert collection.find_query == expected_query
    assert collection.count_query == expected_query
    assert "$gt" in collection.find_query["expires"]
    assert collection.find_projection == {"_id": 0}
    assert collection.cursor.sort_fields == [
        ("last_updated", -1),
        ("clan_tag", 1),
    ]
    assert collection.cursor.skip_count == 1
    assert collection.cursor.limit_count == 1


def test_recruitee_get_falls_back_to_guest_query_for_incomplete_stats(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection(
        [{"clan_tag": "TEST1", "name": "test_clan_1"}]
    )

    set_session(
        player_name="test_player",
        player_league=5,
        player_townhall=13,
    )
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.get("/recruitee")

    assert response.status_code == 200
    assert response.get_json() == [
        {"clan_tag": "TEST1", "name": "test_clan_1"}
    ]
    assert collection.find_query == expected_active_query(collection)


def test_recruitee_get_normalizes_string_matchmaking_stats(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection()

    set_session(
        player_name="test_player",
        player_league="5",
        player_builderbase_trophies="2200",
        player_townhall="13",
    )
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.get("/recruitee")

    assert response.status_code == 200
    assert collection.find_query == expected_active_query(
        collection,
        {
            "requirements.0": {"$lte": 5},
            "requirements.1": {"$lte": 2200},
            "requirements.2": {"$lte": 13},
        },
    )


def test_recruitee_get_returns_400_for_malformed_matchmaking_stat(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection()

    set_session(
        player_name="test_player",
        player_league="not-a-league",
        player_builderbase_trophies=2200,
        player_townhall=13,
    )
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.get("/recruitee")

    assert response.status_code == 400
    assert response.get_json() == {"error": "player_league is invalid."}
    assert collection.find_query is None


def test_recruitee_get_returns_guest_default_raw_list(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection(
        [
            {"clan_tag": "TEST1", "name": "test_clan_1"},
            {"clan_tag": "TEST2", "name": "test_clan_2"},
        ]
    )

    set_session(player_name="Guest")
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
    assert collection.find_query == {
        "expires": collection.find_query["expires"],
    }
    assert "$gt" in collection.find_query["expires"]
    assert collection.count_query is None
    assert collection.cursor.skip_count == 0
    assert collection.cursor.limit_count == 10


def test_recruitee_get_accepts_true_include_total(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection(
        [{"clan_tag": "TEST1", "name": "test_clan_1"}]
    )

    set_session(player_name="Guest")
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.get("/recruitee?includeTotal=true")

    assert response.status_code == 200
    assert response.get_json() == {
        "items": [{"clan_tag": "TEST1", "name": "test_clan_1"}],
        "total": 1,
        "limit": 10,
        "offset": 0,
    }
    expected_query = expected_active_query(collection)
    assert collection.find_query == expected_query
    assert collection.count_query == expected_query


def test_recruitee_get_accepts_false_include_total(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection(
        [{"clan_tag": "TEST1", "name": "test_clan_1"}]
    )

    set_session(player_name="Guest")
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.get("/recruitee?includeTotal=false")

    assert response.status_code == 200
    assert response.get_json() == [
        {"clan_tag": "TEST1", "name": "test_clan_1"}
    ]
    assert collection.find_query == expected_active_query(collection)
    assert collection.count_query is None


def test_recruitee_get_returns_400_for_invalid_include_total(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection()

    set_session(player_name="Guest")
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.get("/recruitee?includeTotal=maybe")

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "includeTotal must be true or false."
    }
    assert collection.find_query is None
    assert collection.count_query is None


def test_recruitee_post_filters_and_paginates_with_total(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection(
        [
            {"clan_tag": "TEST1", "name": "test_clan_1"},
            {"clan_tag": "TEST2", "name": "test_clan_2"},
            {"clan_tag": "TEST3", "name": "test_clan_3"},
        ]
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
        "expires": collection.find_query["expires"],
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
    assert collection.find_query == expected_query
    assert collection.count_query == expected_query
    assert "$gt" in collection.find_query["expires"]
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
    assert collection.find_one_query == {
        "clan_tag": "TEST123",
        "expires": collection.find_one_query["expires"],
    }
    assert "$gt" in collection.find_one_query["expires"]
    assert collection.find_one_projection == {"_id": 0}
    assert collection.find_query is None


def test_recruitee_post_returns_400_for_empty_clan_tag(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection()
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.post("/recruitee", json={"clanTag": ""})

    assert response.status_code == 400
    assert response.get_json() == {"error": "clanTag is required."}
    assert collection.find_query is None
    assert collection.find_one_query is None


def test_recruitee_post_returns_400_for_bad_clan_tag_type(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection()
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.post("/recruitee", json={"clanTag": []})

    assert response.status_code == 400
    assert response.get_json() == {"error": "clanTag must be a string."}
    assert collection.find_query is None
    assert collection.find_one_query is None


def test_recruitee_post_filters_by_location_name_without_location_id(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection(
        [{"clan_tag": "TEST123", "name": "test_clan"}]
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
    assert collection.find_query == {
        "clan_info.location.name": "International",
        "expires": collection.find_query["expires"],
    }
    assert "$gt" in collection.find_query["expires"]
    assert collection.count_query is None


def test_recruitee_returns_400_for_invalid_limit_and_offset(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection(
        [{"clan_tag": "TEST123", "name": "test_clan"}]
    )
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.get("/recruitee?includeTotal=1&limit=bad&offset=bad")

    assert response.status_code == 400
    assert response.get_json() == {"error": "limit must be an integer."}
    assert collection.find_query is None


def test_recruitee_post_returns_400_for_invalid_location_id(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection()
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
    assert response.get_json() == {
        "error": "location_id must be an integer."
    }
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
    assert collection.find_one_query == {
        "clan_tag": "MISSING",
        "expires": collection.find_one_query["expires"],
    }
    assert "$gt" in collection.find_one_query["expires"]
    assert collection.find_one_projection == {"_id": 0}


def test_recruitee_post_returns_400_for_empty_payload(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection()
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.post("/recruitee", json={})

    assert response.status_code == 400
    assert response.get_json() == {
        "error": (
            "recruitee payload must include exactly one of "
            "clanTag or filters."
        )
    }
    assert collection.find_query is None
    assert collection.find_one_query is None


def test_recruitee_post_returns_400_for_ambiguous_payload(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection()
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.post(
        "/recruitee",
        json={"clanTag": "TEST123", "filters": {}},
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": (
            "recruitee payload must include exactly one of "
            "clanTag or filters."
        )
    }
    assert collection.find_query is None
    assert collection.find_one_query is None


def test_recruitee_post_returns_400_for_clan_tag_alias(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection()
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.post("/recruitee", json={"clan_tag": "TEST123"})

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Unsupported recruitee field: clan_tag."
    }
    assert collection.find_query is None
    assert collection.find_one_query is None


def test_recruitee_post_returns_400_for_list_payload(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection()
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.post("/recruitee", json=[])

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Request body must be a JSON object."
    }
    assert collection.find_query is None


def test_recruitee_post_returns_400_for_bad_nested_filter_shape(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection()
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.post(
        "/recruitee",
        json={"filters": {"requirements": []}},
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "filters.requirements must be an object."
    }
    assert collection.find_query is None


def test_recruitee_post_returns_400_for_unknown_filter_field(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection()
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.post(
        "/recruitee",
        json={"filters": {"unexpected": "value"}},
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Unsupported filter field: unexpected."
    }
    assert collection.find_query is None


def test_recruitee_post_returns_400_for_unknown_nested_filter_field(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection()
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.post(
        "/recruitee",
        json={"filters": {"requirements": {"members": {"minimum": 30}}}},
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Unsupported members field: minimum."
    }
    assert collection.find_query is None


def test_recruitee_post_returns_400_for_invalid_war_frequency(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection()
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.post(
        "/recruitee",
        json={"filters": {"warFrequency": "sometimes"}},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "warFrequency is invalid."}
    assert collection.find_query is None


def test_recruitee_post_allows_empty_filters_as_browse(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection(
        [{"clan_tag": "TEST123", "name": "test_clan"}]
    )
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.post("/recruitee", json={"filters": {}})

    assert response.status_code == 200
    assert response.get_json() == [
        {"clan_tag": "TEST123", "name": "test_clan"}
    ]
    assert collection.find_query == expected_active_query(collection)


def test_recruitee_post_normalizes_numeric_string_filters(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.recruitee_route as recruitee_route

    collection = DummyClanCollection()
    monkeypatch.setattr(
        recruitee_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.post(
        "/recruitee",
        json={
            "filters": {
                "requirements": {
                    "townhall": "12",
                    "league": "4",
                    "members": {"min": "30", "max": "45"},
                },
                "minClanLevel": "10",
                "clanPoints": "35000",
            }
        },
    )

    assert response.status_code == 200
    assert collection.find_query == {
        "requirements.2": {"$gte": 12},
        "requirements.0": {"$gte": 4},
        "clan_info.clan_level": {"$gte": 10},
        "clan_info.clanPoints": {"$gte": 35000},
        "clan_info.member_count": {"$gte": 30, "$lte": 45},
        "expires": collection.find_query["expires"],
    }
    assert "$gt" in collection.find_query["expires"]
