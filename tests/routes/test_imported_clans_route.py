def test_imported_clans_post_filters_and_paginates(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.imported_clans_route as imported_clans_route

    refresh_calls = []

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
        def __init__(self):
            self.cursor = DummyCursor(
                [
                    {"clan_tag": "ONE", "name": "First"},
                    {"clan_tag": "TWO", "name": "Second"},
                    {"clan_tag": "THREE", "name": "Third"},
                ]
            )
            self.count_query = None
            self.find_query = None
            self.find_projection = None

        def count_documents(self, query):
            self.count_query = query
            return 3

        def find(self, query, projection):
            self.find_query = query
            self.find_projection = projection
            return self.cursor

    collection = DummyClanCollection()

    def fake_refresh():
        refresh_calls.append(True)

    monkeypatch.setattr(
        imported_clans_route,
        "ensure_imported_clan_inventory",
        fake_refresh,
    )
    monkeypatch.setattr(
        imported_clans_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.post(
        "/imported_clans?limit=1&offset=1",
        json={
            "filters": {
                "name": "  Test.*  ",
                "minClanLevel": 12,
                "clanPoints": 40000,
                "requirements": {"members": {"min": 30, "max": 45}},
                "warFrequency": "always",
                "location": "Canada",
            }
        },
    )

    expected_query = {
        "source": "clash_api_import",
        "name": {"$regex": "Test\\.\\*", "$options": "i"},
        "clan_info.clan_level": {"$gte": 12},
        "clan_info.clanPoints": {"$gte": 40000},
        "clan_info.member_count": {"$gte": 30, "$lte": 45},
        "clan_info.warFrequency": "always",
        "clan_info.location.name": "Canada",
    }

    assert response.status_code == 200
    assert response.get_json() == {
        "items": [{"clan_tag": "TWO", "name": "Second"}],
        "total": 3,
        "limit": 1,
        "offset": 1,
    }
    assert refresh_calls == [True]
    assert collection.count_query == expected_query
    assert collection.find_query == expected_query
    assert collection.find_projection == {"_id": 0}
    assert collection.cursor.sort_fields == [
        ("last_discovered", -1),
        ("last_updated", -1),
        ("clan_info.clan_level", -1),
        ("clan_info.member_count", -1),
        ("clan_tag", 1),
    ]
    assert collection.cursor.skip_count == 1
    assert collection.cursor.limit_count == 1


def test_imported_clans_post_returns_clan_by_tag(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.imported_clans_route as imported_clans_route

    lookup_calls = []

    def fake_get_imported_clan(clan_tag):
        lookup_calls.append(clan_tag)
        return {"clan_tag": clan_tag, "name": "test_clan"}

    monkeypatch.setattr(
        imported_clans_route,
        "get_clan_collection",
        lambda: object(),
    )
    monkeypatch.setattr(
        imported_clans_route,
        "get_imported_clan",
        fake_get_imported_clan,
    )

    response = client.post("/imported_clans", json={"clanTag": "TEST123"})

    assert response.status_code == 200
    assert response.get_json() == {"clan_tag": "TEST123", "name": "test_clan"}
    assert lookup_calls == ["TEST123"]


def test_imported_clans_post_returns_404_for_missing_tag(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.imported_clans_route as imported_clans_route

    monkeypatch.setattr(
        imported_clans_route,
        "get_clan_collection",
        lambda: object(),
    )
    monkeypatch.setattr(
        imported_clans_route,
        "get_imported_clan",
        lambda clan_tag: None,
    )

    response = client.post("/imported_clans", json={"clan_tag": "MISSING"})

    assert response.status_code == 404
    assert response.get_json() == {"error": "Imported clan not found"}
