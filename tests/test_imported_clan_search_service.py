from ClashRecruit.services.imported_clan_search import (
    IMPORTED_CLAN_SORT,
    build_imported_query,
    get_imported_clans_response,
)


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
    def __init__(self, docs):
        self.cursor = DummyCursor(docs)
        self.count_query = None
        self.find_query = None
        self.find_projection = None

    def count_documents(self, query):
        self.count_query = query
        return len(self.cursor.docs)

    def find(self, query, projection):
        self.find_query = query
        self.find_projection = projection
        return self.cursor


class AggregateClanCollection(DummyClanCollection):
    def __init__(self, docs):
        super().__init__(docs)
        self.aggregate_pipeline = None

    def aggregate(self, pipeline):
        self.aggregate_pipeline = pipeline
        return iter(self.cursor.docs)


def test_build_imported_query_uses_filters():
    query = build_imported_query(
        {
            "name": "  Test.*  ",
            "minClanLevel": 12,
            "clanPoints": 40000,
            "requirements": {"members": {"min": 30, "max": 45}},
            "warFrequency": "always",
            "location": "Canada",
        }
    )

    assert query["source"] == "clash_api_import"
    assert "$gt" in query["expires"]
    assert query["name"] == {"$regex": "Test\\.\\*", "$options": "i"}
    assert query["clan_info.clan_level"] == {"$gte": 12}
    assert query["clan_info.clanPoints"] == {"$gte": 40000}
    assert query["clan_info.member_count"] == {"$gte": 30, "$lte": 45}
    assert query["clan_info.warFrequency"] == "always"
    assert query["clan_info.location.name"] == "Canada"


def test_imported_clans_response_returns_paginated_search():
    collection = DummyClanCollection(
        [
            {"clan_tag": "ONE", "name": "First"},
            {"clan_tag": "TWO", "name": "Second"},
            {"clan_tag": "THREE", "name": "Third"},
        ]
    )

    payload, status_code = get_imported_clans_response(
        {"filters": {"location": "Canada"}},
        limit=1,
        offset=1,
        clan_collection=collection,
        imported_clan_lookup=lambda clan_tag: None,
    )

    assert status_code == 200
    assert payload == {
        "items": [{"clan_tag": "TWO", "name": "Second"}],
        "total": 3,
        "limit": 1,
        "offset": 1,
    }
    assert collection.count_query == collection.find_query
    assert collection.find_query["clan_info.location.name"] == "Canada"
    assert collection.find_projection == {"_id": 0}
    assert collection.cursor.sort_fields == IMPORTED_CLAN_SORT


def test_imported_clans_response_prioritizes_english_clans():
    collection = AggregateClanCollection(
        [{"clan_tag": "ONE", "name": "First"}]
    )

    payload, status_code = get_imported_clans_response(
        {"filters": {}},
        limit=10,
        offset=0,
        clan_collection=collection,
        imported_clan_lookup=lambda clan_tag: None,
    )

    assert status_code == 200
    assert payload["items"] == [{"clan_tag": "ONE", "name": "First"}]
    assert collection.aggregate_pipeline[0] == {"$match": collection.count_query}
    assert collection.aggregate_pipeline[2]["$sort"] == {
        "_listing_source_priority": 1,
        "_english_priority": 1,
        "last_discovered": -1,
        "last_updated": -1,
        "clan_info.clan_level": -1,
        "clan_info.member_count": -1,
        "clan_tag": 1,
    }


def test_imported_clans_response_returns_tag_lookup():
    lookup_calls = []

    def lookup(clan_tag):
        lookup_calls.append(clan_tag)
        return {"clan_tag": clan_tag, "name": "test_clan"}

    payload, status_code = get_imported_clans_response(
        {"clanTag": "TEST123"},
        limit=10,
        offset=0,
        clan_collection=object(),
        imported_clan_lookup=lookup,
    )

    assert status_code == 200
    assert payload == {"clan_tag": "TEST123", "name": "test_clan"}
    assert lookup_calls == ["TEST123"]


def test_imported_clans_response_returns_404_for_missing_tag():
    payload, status_code = get_imported_clans_response(
        {"clanTag": "MISSING"},
        limit=10,
        offset=0,
        clan_collection=object(),
        imported_clan_lookup=lambda clan_tag: None,
    )

    assert status_code == 404
    assert payload == {"error": "Imported clan not found"}
