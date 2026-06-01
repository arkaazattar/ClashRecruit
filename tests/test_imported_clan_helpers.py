import pytest
from ClashRecruit.routes.imported_clans_route import (
    _build_imported_query,
    _get_requested_limit,
    _get_requested_offset,
)
from ClashRecruit.routes.validation import RequestValidationError
from flask import Flask


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/imported_clans", 10),
        ("/imported_clans?limit=1", 1),
        ("/imported_clans?limit=200", 200),
    ],
)
def test_get_requested_limit(app: Flask, path: str, expected: int) -> None:
    with app.test_request_context(path):
        assert _get_requested_limit(10) == expected


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/imported_clans", 0),
        ("/imported_clans?offset=5", 5),
    ],
)
def test_get_requested_offset(app: Flask, path: str, expected: int) -> None:
    with app.test_request_context(path):
        assert _get_requested_offset() == expected


@pytest.mark.parametrize(
    ("path", "message"),
    [
        ("/imported_clans?limit=abc", "limit must be an integer."),
        ("/imported_clans?limit=0", "limit must be at least 1."),
        ("/imported_clans?limit=500", "limit must be at most 200."),
        ("/imported_clans?offset=abc", "offset must be an integer."),
        ("/imported_clans?offset=-10", "offset must be an integer."),
    ],
)
def test_invalid_pagination_raises_validation_error(
    app: Flask,
    path: str,
    message: str,
) -> None:
    with app.test_request_context(path):
        with pytest.raises(RequestValidationError, match=message):
            if "limit" in path:
                _get_requested_limit(10)
            else:
                _get_requested_offset()


def test_build_imported_query_empty_filters_returns_active_imports() -> None:
    query = _build_imported_query({})

    assert query == {
        "source": "clash_api_import",
        "expires": query["expires"],
    }
    assert "$gt" in query["expires"]


def test_build_imported_query_escapes_name_and_ignores_empty() -> None:
    query = _build_imported_query(
        {
            "name": "  test.*(name)  ",
            "warFrequency": "",
            "location": "",
        }
    )

    assert query == {
        "source": "clash_api_import",
        "expires": query["expires"],
        "name": {"$regex": "test\\.\\*\\(name\\)", "$options": "i"},
    }
    assert "$gt" in query["expires"]


@pytest.mark.parametrize(
    ("members", "expected"),
    [
        ({"min": 20}, {"$gte": 20}),
        ({"max": 45}, {"$lte": 45}),
        ({"min": 20, "max": 45}, {"$gte": 20, "$lte": 45}),
    ],
)
def test_build_imported_query_member_ranges(
    members: dict[str, int],
    expected: dict[str, int],
) -> None:
    query = _build_imported_query(
        {
            "requirements": {"members": members},
        }
    )

    assert query["source"] == "clash_api_import"
    assert "$gt" in query["expires"]
    assert query["clan_info.member_count"] == expected


def test_build_imported_query_all_scalar_filters() -> None:
    query = _build_imported_query(
        {
            "minClanLevel": 10,
            "clanPoints": 35000,
            "warFrequency": "always",
            "location": "International",
        }
    )

    assert query == {
        "source": "clash_api_import",
        "expires": query["expires"],
        "clan_info.clan_level": {"$gte": 10},
        "clan_info.clanPoints": {"$gte": 35000},
        "clan_info.warFrequency": "always",
        "clan_info.location.name": "International",
    }
    assert "$gt" in query["expires"]
