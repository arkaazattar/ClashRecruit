from datetime import datetime, timezone
from unittest.mock import Mock

import ClashRecruit.services.import_clash_api_clans as import_service
import pytest
import requests


@pytest.mark.parametrize(
    ("raw_tag", "expected"),
    [
        (" #test123 ", "TEST123"),
        ("test123", "TEST123"),
        ("", None),
        (None, None),
        ("  #  ", None),
    ],
)
def test_clean_tag_normalizes_and_rejects_empty(raw_tag, expected):
    assert import_service._clean_tag(raw_tag) == expected


def test_extract_requirements_prefers_detail_values_over_search_values():
    requirements = import_service._extract_requirements(
        search_clan={
            "requiredBuilderBaseTrophies": 1200,
            "requiredTownhallLevel": 10,
        },
        detail_clan={
            "requiredBuilderBaseTrophies": 2400,
            "requiredTownhallLevel": 13,
        },
    )

    assert requirements == [0, 2400, 13]


def test_extract_requirements_uses_search_fallbacks_and_zero_defaults():
    assert import_service._extract_requirements(
        search_clan={
            "requiredBuilderBaseTrophies": 1200,
            "requiredTownhallLevel": 10,
        }
    ) == [0, 1200, 10]
    assert import_service._extract_requirements() == [0, 0, 0]


def test_build_seed_key_sorts_and_ignores_empty_values():
    assert import_service._build_seed_key(
        {"name": "test", "after": "", "limit": 10, "locationId": None}
    ) == "limit:10|name:test"


def test_seed_locations_returns_non_empty_ids(monkeypatch):
    class DummyCursor:
        def __init__(self):
            self.limit_count = None

        def limit(self, count):
            self.limit_count = count
            return [
                {"id": 32000007},
                {"name": "missing_id"},
                {"id": 0},
                {"id": 32000008},
            ]

    class DummyLocationCollection:
        def __init__(self):
            self.cursor = DummyCursor()
            self.find_call = None

        def find(self, query, projection):
            self.find_call = (query, projection)
            return self.cursor

    collection = DummyLocationCollection()
    monkeypatch.setattr(
        import_service,
        "_location_collection",
        lambda: collection,
    )

    assert import_service._seed_locations(limit=3) == [32000007, 32000008]
    assert collection.find_call == ({}, {"_id": 0, "id": 1})
    assert collection.cursor.limit_count == 3


def test_build_discovery_seeds_includes_prefix_war_and_location_seeds(
    monkeypatch,
):
    monkeypatch.setattr(
        import_service,
        "_seed_locations",
        lambda limit: [1, 2],
    )

    seeds = import_service._build_discovery_seeds()

    assert seeds[0] == {"name": "a", "minMembers": 10, "limit": 10}
    assert {
        "warFrequency": "always",
        "minMembers": 10,
        "maxMembers": 50,
        "limit": 10,
    } in seeds
    assert {
        "locationId": 1,
        "minClanLevel": 3,
        "minMembers": 10,
        "limit": 10,
    } in seeds
    assert len(seeds) == 31


def test_normalize_discovery_item_builds_import_shell(monkeypatch):
    frozen_now = datetime(2026, 5, 4, tzinfo=timezone.utc)
    monkeypatch.setattr(import_service, "_now", lambda: frozen_now)

    document = import_service._normalize_discovery_item(
        {
            "tag": "#test123",
            "name": "test_clan",
            "location": {"id": 32000007, "name": "International"},
            "badgeUrls": {"medium": "badge_url"},
            "clanLevel": 10,
            "members": 42,
            "type": "open",
            "warFrequency": "always",
            "clanPoints": 36000,
        },
        "seed-key",
    )

    assert document == {
        "clan_tag": "TEST123",
        "name": "test_clan",
        "source": "clash_api_import",
        "seed_key": "seed-key",
        "requirements": [0, 0, 0],
        "requirements_source": "unsupported_by_api",
        "last_discovered": frozen_now,
        "clan_info": {
            "description": None,
            "location": {"id": 32000007, "name": "International"},
            "badge": "badge_url",
            "clan_level": 10,
            "member_count": 42,
            "type": "open",
            "warFrequency": "always",
            "clanPoints": 36000,
        },
    }


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ({"members": 20, "clanLevel": 5}, True),
        ({"members": 19, "clanLevel": 5}, False),
        ({"members": 20, "clanLevel": 4}, False),
        ({}, False),
    ],
)
def test_passes_quality_gate(payload, expected):
    assert import_service._passes_quality_gate(payload) is expected


def test_build_enriched_import_document_uses_detail_with_search_fallbacks(
    monkeypatch,
):
    frozen_now = datetime(2026, 5, 4, tzinfo=timezone.utc)
    monkeypatch.setattr(import_service, "_now", lambda: frozen_now)

    document = import_service._build_enriched_import_document(
        search_clan={
            "tag": "#TEST123",
            "name": "search_clan",
            "location": {"id": 32000007, "name": "International"},
            "badgeUrls": {"medium": "search_badge"},
            "clanLevel": 9,
            "members": 35,
            "type": "open",
            "warFrequency": "always",
            "clanPoints": 35000,
            "requiredBuilderBaseTrophies": 1600,
            "requiredTownhallLevel": 11,
        },
        detail_clan={
            "tag": "#TEST123",
            "name": "test_clan",
            "description": "  test description  ",
            "badgeUrls": {},
            "members": 40,
            "requiredBuilderBaseTrophies": 2200,
            "requiredTownhallLevel": 13,
        },
        seed_key="name:a|limit:10",
    )

    assert document == {
        "clan_tag": "TEST123",
        "name": "test_clan",
        "source": "clash_api_import",
        "seed_key": "name:a|limit:10",
        "requirements": [0, 2200, 13],
        "requirements_source": "clash_api",
        "last_discovered": frozen_now,
        "last_updated": frozen_now,
        "clan_info": {
            "description": "test description",
            "location": {"id": 32000007, "name": "International"},
            "badge": "search_badge",
            "clan_level": 9,
            "member_count": 40,
            "type": "open",
            "warFrequency": "always",
            "clanPoints": 35000,
        },
    }


def test_search_clans_calls_api_with_timeout_and_returns_cursor(monkeypatch):
    fake_response = Mock()
    fake_response.json.return_value = {
        "items": [{"tag": "#TEST123"}],
        "paging": {"cursors": {"after": "cursor-1"}},
    }
    fake_get = Mock(return_value=fake_response)
    monkeypatch.setattr(import_service.requests, "get", fake_get)

    result = import_service._search_clans({"name": "test", "limit": 10})

    assert result == {"items": [{"tag": "#TEST123"}], "after": "cursor-1"}
    fake_response.raise_for_status.assert_called_once_with()
    fake_get.assert_called_once_with(
        "https://api.clashofclans.com/v1/clans",
        params={"name": "test", "limit": 10},
        headers=import_service.headers,
        timeout=15,
    )


def test_fetch_clan_detail_returns_none_for_invalid_tag_without_network(
    monkeypatch,
):
    monkeypatch.setattr(
        import_service.requests,
        "get",
        lambda *args, **kwargs: pytest.fail("network should not be called"),
    )

    assert import_service._fetch_clan_detail("  #  ") is None


def test_fetch_clan_detail_returns_none_for_404(monkeypatch):
    fake_response = Mock(status_code=404)
    fake_get = Mock(return_value=fake_response)
    monkeypatch.setattr(import_service.requests, "get", fake_get)

    assert import_service._fetch_clan_detail("#missing") is None
    fake_response.raise_for_status.assert_not_called()
    fake_get.assert_called_once_with(
        "https://api.clashofclans.com/v1/clans/%23MISSING",
        headers=import_service.headers,
        timeout=15,
    )


def test_fetch_clan_detail_raises_and_returns_json_for_success(monkeypatch):
    fake_response = Mock(status_code=200)
    fake_response.json.return_value = {"tag": "#TEST123", "name": "test_clan"}
    fake_get = Mock(return_value=fake_response)
    monkeypatch.setattr(import_service.requests, "get", fake_get)

    assert import_service._fetch_clan_detail("test123") == {
        "tag": "#TEST123",
        "name": "test_clan",
    }
    fake_response.raise_for_status.assert_called_once_with()


def test_seed_state_helpers_read_update_and_reset(monkeypatch):
    frozen_now = datetime(2026, 5, 4, tzinfo=timezone.utc)

    class DummyImportStateCollection:
        def __init__(self):
            self.find_one_call = None
            self.update_calls = []

        def find_one(self, query, projection):
            self.find_one_call = (query, projection)
            return {"after": "cursor-1"}

        def update_one(self, query, update, upsert=False):
            self.update_calls.append((query, update, upsert))

    collection = DummyImportStateCollection()
    monkeypatch.setattr(import_service, "_now", lambda: frozen_now)
    monkeypatch.setattr(
        import_service,
        "_import_state_collection",
        lambda: collection,
    )

    assert import_service._get_seed_state("seed-key") == {"after": "cursor-1"}
    import_service._set_seed_after("seed-key", "cursor-2")
    import_service._reset_seed_after("seed-key")

    assert collection.find_one_call == (
        {"seed_key": "seed-key"},
        {"_id": 0},
    )
    assert collection.update_calls == [
        (
            {"seed_key": "seed-key"},
            {
                "$set": {
                    "seed_key": "seed-key",
                    "after": "cursor-2",
                    "last_run": frozen_now,
                }
            },
            True,
        ),
        (
            {"seed_key": "seed-key"},
            {
                "$set": {
                    "seed_key": "seed-key",
                    "after": None,
                    "last_run": frozen_now,
                }
            },
            True,
        ),
    ]


def test_cleanup_old_imported_clans_deletes_past_retention(monkeypatch):
    frozen_now = datetime(2026, 5, 4, tzinfo=timezone.utc)

    class DummyDeleteResult:
        deleted_count = 4

    class DummyClanCollection:
        def __init__(self):
            self.delete_query = None

        def delete_many(self, query):
            self.delete_query = query
            return DummyDeleteResult()

    clan_collection = DummyClanCollection()
    monkeypatch.setattr(import_service, "_now", lambda: frozen_now)
    monkeypatch.setattr(
        import_service,
        "_clan_collection",
        lambda: clan_collection,
    )

    assert import_service.cleanup_old_imported_clans() == 4
    assert clan_collection.delete_query == {
        "source": "clash_api_import",
        "last_discovered": {
            "$lt": frozen_now - import_service.IMPORTED_CLAN_RETENTION
        },
    }


def test_discover_imported_clans_resumes_upserts_and_updates_cursor(
    monkeypatch,
):
    frozen_now = datetime(2026, 5, 4, tzinfo=timezone.utc)
    cleanup_calls = []
    state_updates = []

    class DummyClanCollection:
        def __init__(self):
            self.update_calls = []

        def update_one(self, query, update, upsert=False):
            self.update_calls.append((query, update, upsert))

    clan_collection = DummyClanCollection()
    search_calls = []

    def fake_search(seed):
        search_calls.append(seed)
        if len(search_calls) == 1:
            return {
                "items": [
                    {
                        "tag": "#TEST123",
                        "name": "search_clan",
                        "clanLevel": 10,
                        "members": 40,
                    }
                ],
                "after": "cursor-2",
            }
        return {"items": [], "after": None}

    monkeypatch.setattr(import_service, "_now", lambda: frozen_now)
    monkeypatch.setattr(
        import_service,
        "cleanup_old_imported_clans",
        lambda: cleanup_calls.append(True),
    )
    monkeypatch.setattr(
        import_service,
        "_build_discovery_seeds",
        lambda: [{"name": "test", "limit": 10}],
    )
    monkeypatch.setattr(
        import_service,
        "_get_seed_state",
        lambda seed_key: {"after": "cursor-1"},
    )
    monkeypatch.setattr(import_service, "_search_clans", fake_search)
    monkeypatch.setattr(
        import_service,
        "_fetch_clan_detail",
        lambda clan_tag: {
            "tag": "#TEST123",
            "name": "test_clan",
            "clanLevel": 10,
            "members": 40,
            "requiredTownhallLevel": 13,
        },
    )
    monkeypatch.setattr(
        import_service,
        "_set_seed_after",
        lambda seed_key, after: state_updates.append((seed_key, after)),
    )
    monkeypatch.setattr(
        import_service,
        "_clan_collection",
        lambda: clan_collection,
    )

    assert import_service.discover_imported_clans(max_seeds=1) == 1

    seed_key = "limit:10|name:test"
    assert cleanup_calls == [True]
    assert search_calls == [
        {"name": "test", "limit": 10, "after": "cursor-1"},
        {"name": "test", "limit": 10, "after": "cursor-2"},
    ]
    assert state_updates == [(seed_key, "cursor-2"), (seed_key, None)]
    update_query, update_doc, upsert = clan_collection.update_calls[0]
    assert update_query == {
        "clan_tag": "TEST123",
        "source": "clash_api_import",
    }
    assert upsert is True
    assert update_doc["$set"]["name"] == "test_clan"
    assert update_doc["$set"]["requirements"] == [0, 0, 13]
    assert update_doc["$set"]["last_discovered"] == frozen_now


def test_discover_imported_clans_skips_low_quality_bad_tags_and_bad_detail(
    monkeypatch,
):
    class DummyClanCollection:
        def __init__(self):
            self.update_calls = []

        def update_one(self, query, update, upsert=False):
            self.update_calls.append((query, update, upsert))

    clan_collection = DummyClanCollection()

    def fake_fetch(clan_tag):
        if clan_tag == "RAISES":
            raise requests.RequestException("detail failed")
        if clan_tag == "MISSING":
            return None
        if clan_tag == "LOWDETAIL":
            return {"tag": "#LOWDETAIL", "clanLevel": 4, "members": 40}
        return {"tag": f"#{clan_tag}", "clanLevel": 10, "members": 40}

    monkeypatch.setattr(
        import_service,
        "cleanup_old_imported_clans",
        lambda: 0,
    )
    monkeypatch.setattr(
        import_service,
        "_build_discovery_seeds",
        lambda: [{"name": "test", "limit": 10}],
    )
    monkeypatch.setattr(import_service, "_get_seed_state", lambda seed_key: {})
    monkeypatch.setattr(
        import_service,
        "_search_clans",
        lambda seed: {
            "items": [
                {"tag": "#LOWSEARCH", "clanLevel": 4, "members": 40},
                {"tag": "  #  ", "clanLevel": 10, "members": 40},
                {"tag": "#RAISES", "clanLevel": 10, "members": 40},
                {"tag": "#MISSING", "clanLevel": 10, "members": 40},
                {"tag": "#LOWDETAIL", "clanLevel": 10, "members": 40},
            ],
            "after": None,
        },
    )
    monkeypatch.setattr(import_service, "_fetch_clan_detail", fake_fetch)
    monkeypatch.setattr(
        import_service,
        "_reset_seed_after",
        lambda seed_key: None,
    )
    monkeypatch.setattr(
        import_service,
        "_clan_collection",
        lambda: clan_collection,
    )

    assert import_service.discover_imported_clans(max_seeds=1) == 0
    assert clan_collection.update_calls == []


def test_discover_imported_clans_breaks_seed_on_search_error(monkeypatch):
    search_calls = []
    reset_calls = []

    def fake_search(seed):
        search_calls.append(seed)
        raise requests.RequestException("search failed")

    monkeypatch.setattr(
        import_service,
        "cleanup_old_imported_clans",
        lambda: 0,
    )
    monkeypatch.setattr(
        import_service,
        "_build_discovery_seeds",
        lambda: [{"name": "test", "limit": 10}],
    )
    monkeypatch.setattr(import_service, "_get_seed_state", lambda seed_key: {})
    monkeypatch.setattr(import_service, "_search_clans", fake_search)
    monkeypatch.setattr(
        import_service,
        "_reset_seed_after",
        lambda seed_key: reset_calls.append(seed_key),
    )

    assert import_service.discover_imported_clans(max_seeds=1) == 0
    assert search_calls == [{"name": "test", "limit": 10}]
    assert reset_calls == []


def test_discover_imported_clans_task_delegates(monkeypatch):
    monkeypatch.setattr(import_service, "discover_imported_clans", lambda: 7)

    assert import_service.discover_imported_clans_task() == 7


def test_ensure_imported_clan_inventory_task_delegates(monkeypatch):
    ensure_calls = []

    monkeypatch.setattr(
        import_service,
        "ensure_imported_clan_inventory",
        lambda min_complete=30: ensure_calls.append(min_complete),
    )

    import_service.ensure_imported_clan_inventory_task()
    import_service.ensure_imported_clan_inventory_task(min_complete=42)

    assert ensure_calls == [30, 42]


def test_run_import_refresh_on_worker_start_queues_task():
    sender = Mock()

    import_service.run_import_refresh_on_worker_start(sender=sender)
    import_service.run_import_refresh_on_worker_start(sender=None)

    sender.app.send_task.assert_called_once_with(
        "ensure_imported_clan_inventory_task"
    )


def test_ensure_imported_clan_inventory_skips_when_recent_count_is_enough(
    monkeypatch,
):
    frozen_now = datetime(2026, 5, 4, tzinfo=timezone.utc)
    discover_calls = []

    class DummyClanCollection:
        def __init__(self):
            self.count_query = None

        def count_documents(self, query):
            self.count_query = query
            return 30

    clan_collection = DummyClanCollection()
    monkeypatch.setattr(import_service, "_now", lambda: frozen_now)
    monkeypatch.setattr(
        import_service,
        "_clan_collection",
        lambda: clan_collection,
    )
    monkeypatch.setattr(
        import_service,
        "discover_imported_clans",
        lambda: discover_calls.append(True),
    )

    import_service.ensure_imported_clan_inventory(min_complete=30)

    assert discover_calls == []
    assert clan_collection.count_query == {
        "source": "clash_api_import",
        "last_discovered": {
            "$gte": frozen_now - import_service.DISCOVERY_STALE_AFTER
        },
    }


def test_ensure_imported_clan_inventory_discovers_when_count_is_low(
    monkeypatch,
):
    discover_calls = []

    class DummyClanCollection:
        def count_documents(self, query):
            return 2

    monkeypatch.setattr(
        import_service,
        "_clan_collection",
        lambda: DummyClanCollection(),
    )
    monkeypatch.setattr(
        import_service,
        "discover_imported_clans",
        lambda: discover_calls.append(True),
    )

    import_service.ensure_imported_clan_inventory(min_complete=30)

    assert discover_calls == [True]


def test_get_imported_clan_returns_cached_document_without_fetch(
    monkeypatch,
):
    cached = {"clan_tag": "TEST123", "name": "test_clan"}

    class DummyClanCollection:
        def __init__(self):
            self.find_one_calls = []

        def find_one(self, query, projection):
            self.find_one_calls.append((query, projection))
            return cached

    clan_collection = DummyClanCollection()
    monkeypatch.setattr(
        import_service,
        "_clan_collection",
        lambda: clan_collection,
    )
    monkeypatch.setattr(
        import_service,
        "_fetch_clan_detail",
        lambda clan_tag: pytest.fail("detail fetch should not be called"),
    )

    result = import_service.get_imported_clan(" #test123 ")

    assert result == cached
    assert clan_collection.find_one_calls == [
        (
            {"clan_tag": "TEST123", "source": "clash_api_import"},
            {"_id": 0},
        )
    ]


def test_get_imported_clan_fetches_caches_and_returns_imported_document(
    monkeypatch,
):
    frozen_now = datetime(2026, 5, 4, tzinfo=timezone.utc)
    imported = {"clan_tag": "TEST123", "name": "test_clan"}

    class DummyClanCollection:
        def __init__(self):
            self.find_one_calls = []
            self.update_call = None

        def find_one(self, query, projection):
            self.find_one_calls.append((query, projection))
            if len(self.find_one_calls) == 1:
                return None
            return imported

        def update_one(self, query, update, upsert=False):
            self.update_call = (query, update, upsert)

    clan_collection = DummyClanCollection()
    monkeypatch.setattr(import_service, "_now", lambda: frozen_now)
    monkeypatch.setattr(
        import_service,
        "_clan_collection",
        lambda: clan_collection,
    )
    monkeypatch.setattr(
        import_service,
        "_fetch_clan_detail",
        lambda clan_tag: {
            "tag": "#TEST123",
            "name": "test_clan",
            "description": "  cached description  ",
            "location": {"id": 32000007, "name": "International"},
            "badgeUrls": {"medium": "badge_url"},
            "clanLevel": 10,
            "members": 42,
            "type": "inviteOnly",
            "warFrequency": "always",
            "clanPoints": 36000,
            "requiredBuilderBaseTrophies": 2200,
            "requiredTownhallLevel": 13,
        },
    )

    result = import_service.get_imported_clan("TEST123")
    update_query, update_doc, upsert = clan_collection.update_call
    set_doc = update_doc["$set"]

    assert result == imported
    assert update_query == {
        "clan_tag": "TEST123",
        "source": "clash_api_import",
    }
    assert upsert is True
    assert set_doc["clan_tag"] == "TEST123"
    assert set_doc["name"] == "test_clan"
    assert set_doc["requirements"] == [0, 2200, 13]
    assert set_doc["last_discovered"] == frozen_now
    assert set_doc["last_updated"] == frozen_now
    assert set_doc["clan_info"] == {
        "description": "cached description",
        "location": {"id": 32000007, "name": "International"},
        "badge": "badge_url",
        "clan_level": 10,
        "member_count": 42,
        "type": "inviteOnly",
        "warFrequency": "always",
        "clanPoints": 36000,
    }
