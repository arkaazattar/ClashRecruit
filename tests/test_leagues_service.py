from ClashRecruit.clash_http_client import ClashApiJSONError, ClashApiResponse
from ClashRecruit.services import leagues


class DummyCursor:
    def __init__(self, docs):
        self.docs = docs

    def sort(self, field, direction):
        reverse = direction < 0
        return sorted(
            self.docs,
            key=lambda doc: doc.get(field, 0),
            reverse=reverse,
        )


class DummyLeagueMetadataCollection:
    def __init__(self, docs=None):
        self.docs = docs or []
        self.find_calls = []
        self.deleted_queries = []
        self.inserted = []

    def find(self, query, projection):
        self.find_calls.append((query, projection))
        kind = query["kind"]
        docs = [
            {
                key: value
                for key, value in doc.items()
                if key not in {"_id", "kind"}
            }
            for doc in self.docs
            if doc.get("kind") == kind
        ]
        return DummyCursor(docs)

    def delete_many(self, query):
        self.deleted_queries.append(query)
        self.docs = [
            doc for doc in self.docs if doc.get("kind") != query.get("kind")
        ]

    def insert_one(self, doc):
        self.inserted.append(doc)
        self.docs.append(doc)


def test_get_ranked_league_options_reads_database(monkeypatch):
    collection = DummyLeagueMetadataCollection(
        [
            {"kind": "ranked_league_tier", "value": 2, "label": "Skeleton 2"},
            {"kind": "ranked_league_tier", "value": 1, "label": "Skeleton 1"},
        ]
    )
    monkeypatch.setattr(
        leagues,
        "get_league_metadata_collection",
        lambda: collection,
    )

    assert leagues.get_ranked_league_options() == [
        {"value": 1, "label": "Skeleton 1"},
        {"value": 2, "label": "Skeleton 2"},
    ]
    assert collection.find_calls == [
        (
            {"kind": "ranked_league_tier"},
            {"_id": 0, "kind": 0},
        )
    ]


def test_get_builder_base_league_options_reads_database(monkeypatch):
    collection = DummyLeagueMetadataCollection(
        [
            {"kind": "builder_base_league", "value": 42, "label": "Diamond"},
            {
                "kind": "builder_base_league",
                "value": 0,
                "label": "No Builder Base Requirement",
            },
        ]
    )
    monkeypatch.setattr(
        leagues,
        "get_league_metadata_collection",
        lambda: collection,
    )

    assert leagues.get_builder_base_league_options() == [
        {"value": 0, "label": "No Builder Base Requirement"},
        {"value": 42, "label": "Diamond"},
    ]


def test_get_options_falls_back_when_database_is_empty(monkeypatch):
    collection = DummyLeagueMetadataCollection()
    monkeypatch.setattr(
        leagues,
        "get_league_metadata_collection",
        lambda: collection,
    )

    assert leagues.get_ranked_league_options() == (
        leagues.FALLBACK_RANKED_LEAGUE_OPTIONS
    )
    assert leagues.get_builder_base_league_options() == (
        leagues.FALLBACK_BUILDER_BASE_LEAGUE_OPTIONS
    )


def test_get_max_values_use_database_options(monkeypatch):
    collection = DummyLeagueMetadataCollection(
        [
            {
                "kind": "ranked_league_tier",
                "value": 36,
                "label": "Legend League 3",
            },
            {"kind": "builder_base_league", "value": 42, "label": "Diamond"},
        ]
    )
    monkeypatch.setattr(
        leagues,
        "get_league_metadata_collection",
        lambda: collection,
    )

    assert leagues.get_max_ranked_league() == 36
    assert leagues.get_max_builder_base_league() == 42


def test_update_ranked_league_tier_collection_fetches_and_replaces(
    monkeypatch,
):
    collection = DummyLeagueMetadataCollection(
        [{"kind": "ranked_league_tier", "value": 999, "label": "Old"}]
    )
    calls = []

    def fake_clash_get(path, headers):
        calls.append((path, headers))
        return ClashApiResponse(
            200,
            {
                "items": [
                    {"id": 105000000, "name": "Unranked"},
                    {"id": 105000001, "name": "Skeleton League 1"},
                    {"id": 105000034, "name": "Legend League"},
                    {"id": 105000035, "name": "Legend League"},
                    {"id": 105000036, "name": "Legend League"},
                ]
            },
        )

    monkeypatch.setattr(
        leagues,
        "get_league_metadata_collection",
        lambda: collection,
    )
    monkeypatch.setattr(leagues, "headers", {"Authorization": "Bearer test"})
    monkeypatch.setattr(leagues, "clash_get", fake_clash_get)

    leagues.update_ranked_league_tier_collection()

    assert calls == [
        ("leaguetiers", {"Authorization": "Bearer test"}),
    ]
    assert collection.deleted_queries == [{"kind": "ranked_league_tier"}]
    assert collection.inserted == [
        {"kind": "ranked_league_tier", "value": 0, "label": "Unranked"},
        {
            "kind": "ranked_league_tier",
            "value": 1,
            "label": "Skeleton League 1",
        },
        {"kind": "ranked_league_tier", "value": 34, "label": "Legend League"},
        {"kind": "ranked_league_tier", "value": 35, "label": "Legend League"},
        {"kind": "ranked_league_tier", "value": 36, "label": "Legend League"},
    ]


def test_update_builder_base_league_collection_fetches_and_replaces(
    monkeypatch,
):
    collection = DummyLeagueMetadataCollection(
        [{"kind": "builder_base_league", "value": 999, "label": "Old"}]
    )
    calls = []

    def fake_clash_get(path, headers):
        calls.append((path, headers))
        return ClashApiResponse(
            200,
            {
                "items": [
                    {"id": 44000000, "name": "Wood League V"},
                    {"id": 44000041, "name": "Diamond League"},
                ]
            },
        )

    monkeypatch.setattr(
        leagues,
        "get_league_metadata_collection",
        lambda: collection,
    )
    monkeypatch.setattr(leagues, "headers", {"Authorization": "Bearer test"})
    monkeypatch.setattr(leagues, "clash_get", fake_clash_get)

    leagues.update_builder_base_league_collection()

    assert calls == [
        ("builderbaseleagues", {"Authorization": "Bearer test"}),
    ]
    assert collection.deleted_queries == [{"kind": "builder_base_league"}]
    assert collection.inserted == [
        {
            "kind": "builder_base_league",
            "value": 0,
            "label": "No Builder Base Requirement",
        },
        {"kind": "builder_base_league", "value": 1, "label": "Wood League V"},
        {
            "kind": "builder_base_league",
            "value": 42,
            "label": "Diamond League",
        },
    ]


def test_update_ranked_league_tier_collection_stores_fallback_on_api_error(
    monkeypatch,
):
    collection = DummyLeagueMetadataCollection(
        [{"kind": "ranked_league_tier", "value": 999, "label": "Old"}]
    )
    monkeypatch.setattr(
        leagues,
        "get_league_metadata_collection",
        lambda: collection,
    )
    monkeypatch.setattr(
        leagues,
        "clash_get",
        lambda path, headers: (_ for _ in ()).throw(
            ClashApiJSONError("bad response")
        ),
    )

    leagues.update_ranked_league_tier_collection()

    assert collection.deleted_queries == [{"kind": "ranked_league_tier"}]
    assert collection.inserted == [
        {"kind": "ranked_league_tier", **option}
        for option in leagues.FALLBACK_RANKED_LEAGUE_OPTIONS
    ]
