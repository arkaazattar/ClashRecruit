from unittest.mock import Mock

import ClashRecruit.services.maxtownhall as maxtownhall
import pytest
from ClashRecruit.clash_http_client import ClashApiResponse


class DummyCache:
    def __init__(self, value=None):
        self.value = value
        self.set_calls = []

    def get(self, key):
        assert key == "MAXTOWNHALL"
        return self.value

    def set(self, key, value, expire):
        self.set_calls.append((key, value, expire))
        self.value = value


def test_refresh_returns_cached_max_townhall(monkeypatch):
    monkeypatch.setattr(maxtownhall, "get_cache", lambda: DummyCache("17"))
    monkeypatch.setattr(
        maxtownhall,
        "get_max_townhall",
        lambda headers: pytest.fail("API refresh should not be called"),
    )

    assert maxtownhall.refresh({"Authorization": "Bearer token"}) == 17


def test_refresh_fetches_max_townhall_on_cache_miss(monkeypatch):
    monkeypatch.setattr(maxtownhall, "get_cache", lambda: DummyCache(None))
    monkeypatch.setattr(maxtownhall, "get_max_townhall", lambda headers: 18)

    assert maxtownhall.refresh({"Authorization": "Bearer token"}) == 18


def test_get_max_townhall_fetches_top_player_detail_and_caches(monkeypatch):
    cache = DummyCache()
    ranking_response = ClashApiResponse(
        200,
        {"items": [{"tag": "#PLAYER123"}]},
    )
    player_response = ClashApiResponse(200, {"townHallLevel": "17"})
    fake_get = Mock(side_effect=[ranking_response, player_response])

    monkeypatch.setattr(maxtownhall, "get_cache", lambda: cache)
    monkeypatch.setattr(maxtownhall, "clash_get", fake_get)

    result = maxtownhall.get_max_townhall(
        {"Authorization": "Bearer token"}
    )

    assert result == 17
    assert cache.set_calls == [("MAXTOWNHALL", 17, 86400)]
    assert fake_get.call_args_list == [
        (
            (
                "https://api.clashofclans.com/v1/locations/32000249/"
                "rankings/players?limit=1",
            ),
            {
                "headers": {"Authorization": "Bearer token"},
            },
        ),
        (
            ("https://api.clashofclans.com/v1/players/%23PLAYER123",),
            {
                "headers": {"Authorization": "Bearer token"},
            },
        ),
    ]


def test_get_max_townhall_raises_when_player_detail_has_no_townhall(
    monkeypatch,
):
    ranking_response = ClashApiResponse(
        200,
        {"items": [{"tag": "#PLAYER123"}]},
    )
    player_response = ClashApiResponse(200, {})
    monkeypatch.setattr(
        maxtownhall,
        "clash_get",
        Mock(side_effect=[ranking_response, player_response]),
    )

    with pytest.raises(
        ValueError,
        match="Missing 'townHallLevel' in Clash API response.",
    ):
        maxtownhall.get_max_townhall({"Authorization": "Bearer token"})
