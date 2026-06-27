import pytest
from ClashRecruit.routes.validation import RequestValidationError
from ClashRecruit.services.recruitee_search import (
    RECRUITEE_SORT,
    build_recruitee_filter_query,
    get_matchmaking_base_query,
    get_recruitee_list_response,
    get_recruitee_post_response,
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


class AggregateClanCollection(DummyClanCollection):
    def __init__(self, docs=None, tag_result=None):
        super().__init__(docs, tag_result)
        self.aggregate_pipeline = None

    def aggregate(self, pipeline):
        self.aggregate_pipeline = pipeline
        return iter(self.cursor.docs)


def test_matchmaking_base_query_uses_logged_in_player_stats():
    query = get_matchmaking_base_query(
        {
            "player_name": "test_player",
            "player_league": "5",
            "player_builderbase_trophies": "2200",
            "player_townhall": "13",
        }
    )

    assert query == {
        "requirements.0": {"$lte": 5},
        "requirements.1": {"$lte": 22},
        "requirements.2": {"$lte": 13},
    }


def test_matchmaking_base_query_falls_back_for_guest_or_incomplete_stats():
    assert get_matchmaking_base_query({"player_name": "Guest"}) == {}
    assert get_matchmaking_base_query({
        "player_name": "test_player",
        "player_league": 5,
    }) == {}


def test_matchmaking_base_query_rejects_bad_session_stat():
    with pytest.raises(RequestValidationError) as exc:
        get_matchmaking_base_query(
            {
                "player_name": "test_player",
                "player_league": "not-a-league",
                "player_builderbase_trophies": 2200,
                "player_townhall": 13,
            }
        )

    assert exc.value.message == "player_league is invalid."


def test_build_recruitee_filter_query_uses_filters():
    query = build_recruitee_filter_query(
        {
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
    )

    assert query == {
        "name": {"$regex": "Test\\.\\*", "$options": "i"},
        "requirements.2": {"$gte": 12},
        "requirements.0": {"$gte": 4},
        "clan_info.clan_level": {"$gte": 10},
        "clan_info.clanPoints": {"$gte": 35000},
        "clan_info.member_count": {"$gte": 30, "$lte": 45},
        "clan_info.warFrequency": "always",
        "clan_info.location.id": 32000007,
    }


def test_recruitee_list_response_filters_and_includes_total():
    collection = DummyClanCollection(
        [
            {"clan_tag": "TEST1", "name": "test_clan_1"},
            {"clan_tag": "TEST2", "name": "test_clan_2"},
            {"clan_tag": "TEST3", "name": "test_clan_3"},
        ]
    )

    payload, status_code = get_recruitee_list_response(
        {
            "player_name": "test_player",
            "player_league": 5,
            "player_builderbase_trophies": 2200,
            "player_townhall": 13,
        },
        limit=1,
        offset=1,
        include_total=True,
        clan_collection=collection,
    )

    assert status_code == 200
    assert payload == {
        "items": [{"clan_tag": "TEST2", "name": "test_clan_2"}],
        "total": 3,
        "limit": 1,
        "offset": 1,
    }
    assert collection.find_query["requirements.0"] == {"$lte": 5}
    assert "$gt" in collection.find_query["expires"]
    assert collection.count_query == collection.find_query
    assert collection.find_projection == {"_id": 0}
    assert collection.cursor.sort_fields == RECRUITEE_SORT


def test_recruitee_list_response_prioritizes_community_and_english_clans():
    collection = AggregateClanCollection(
        [{"clan_tag": "TEST1", "name": "test_clan_1"}]
    )

    payload, status_code = get_recruitee_list_response(
        {},
        limit=10,
        offset=0,
        include_total=True,
        clan_collection=collection,
    )

    assert status_code == 200
    assert payload["items"] == [{"clan_tag": "TEST1", "name": "test_clan_1"}]
    assert collection.aggregate_pipeline[0] == {"$match": collection.count_query}
    assert collection.aggregate_pipeline[1]["$addFields"][
        "_listing_source_priority"
    ] == {
        "$cond": [{"$eq": ["$source", "clash_api_import"]}, 1, 0],
    }
    assert collection.aggregate_pipeline[2]["$sort"] == {
        "_listing_source_priority": 1,
        "_english_priority": 1,
        "last_updated": -1,
        "clan_tag": 1,
    }
    assert collection.aggregate_pipeline[3] == {"$skip": 0}
    assert collection.aggregate_pipeline[4] == {"$limit": 10}


def test_recruitee_list_response_can_prioritize_discovered_clans():
    collection = AggregateClanCollection(
        [{"clan_tag": "TEST1", "name": "test_clan_1"}]
    )

    payload, status_code = get_recruitee_list_response(
        {},
        limit=10,
        offset=0,
        include_total=True,
        source_sort="discovered",
        clan_collection=collection,
    )

    assert status_code == 200
    assert payload["items"] == [{"clan_tag": "TEST1", "name": "test_clan_1"}]
    assert collection.aggregate_pipeline[1]["$addFields"][
        "_listing_source_priority"
    ] == {
        "$cond": [{"$eq": ["$source", "clash_api_import"]}, 0, 1],
    }


def test_recruitee_post_response_returns_tag_lookup():
    collection = DummyClanCollection(
        tag_result={"clan_tag": "TEST123", "name": "test_clan"}
    )

    payload, status_code = get_recruitee_post_response(
        {"clanTag": "TEST123"},
        limit=10,
        offset=0,
        include_total=False,
        clan_collection=collection,
    )

    assert status_code == 200
    assert payload == {"clan_tag": "TEST123", "name": "test_clan"}
    assert collection.find_one_query["clan_tag"] == "TEST123"
    assert "$gt" in collection.find_one_query["expires"]
    assert collection.find_one_projection == {"_id": 0}


def test_recruitee_post_response_returns_404_for_missing_tag():
    collection = DummyClanCollection(tag_result=None)

    payload, status_code = get_recruitee_post_response(
        {"clanTag": "MISSING"},
        limit=10,
        offset=0,
        include_total=False,
        clan_collection=collection,
    )

    assert status_code == 404
    assert payload == {"error": "Clan not found"}


def test_recruitee_post_response_returns_raw_list_without_total():
    collection = DummyClanCollection(
        [{"clan_tag": "TEST123", "name": "test_clan"}]
    )

    payload, status_code = get_recruitee_post_response(
        {"filters": {"location": "International"}},
        limit=10,
        offset=0,
        include_total=False,
        clan_collection=collection,
    )

    assert status_code == 200
    assert payload == [{"clan_tag": "TEST123", "name": "test_clan"}]
    assert collection.find_query["clan_info.location.name"] == (
        "International"
    )
    assert "$gt" in collection.find_query["expires"]
    assert collection.count_query is None
