class DummyRecruitee:
    instances = []
    result = None

    def __init__(self, player_tag, headers):
        self.player_tag = player_tag
        self.headers = headers
        self.search_call = None
        DummyRecruitee.instances.append(self)

    def searchClan(self, filters, after=None):
        self.search_call = (filters, after)
        return DummyRecruitee.result


def setup_search_route(monkeypatch, result):
    import ClashRecruit.routes.search_clans_route as search_clans_route

    DummyRecruitee.instances = []
    DummyRecruitee.result = result
    monkeypatch.setattr(search_clans_route, "Recruitee", DummyRecruitee)


def test_search_clans_returns_success_payload(
    client,
    monkeypatch,
    set_session,
):
    setup_search_route(
        monkeypatch,
        {
            "items": [{"tag": "#TEST1", "name": "test_clan"}],
            "after": "cursor-1",
            "error": None,
        },
    )
    set_session(player_tag="PLAYER123")

    response = client.post(
        "/search_clans",
        json={"name": "test", "after": "cursor-0"},
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "items": [{"tag": "#TEST1", "name": "test_clan"}],
        "after": "cursor-1",
        "error": None,
    }
    assert DummyRecruitee.instances[0].player_tag == "PLAYER123"
    assert DummyRecruitee.instances[0].search_call == (
        {"name": "test", "after": "cursor-0"},
        "cursor-0",
    )


def test_search_clans_maps_empty_filter_error(client, monkeypatch):
    setup_search_route(
        monkeypatch,
        {
            "items": [],
            "after": None,
            "error": {
                "reason": "badRequest",
                "message": "At least one filtering parameter must exist",
                "status": 400,
            },
        },
    )

    response = client.post("/search_clans", json={})

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Add at least one random clan filter before searching.",
        "reason": "badRequest",
        "message": "At least one filtering parameter must exist",
    }


def test_search_clans_maps_generic_api_error(client, monkeypatch):
    setup_search_route(
        monkeypatch,
        {
            "items": [],
            "after": None,
            "error": {
                "reason": "accessDenied",
                "message": "Invalid authorization",
                "status": 403,
            },
        },
    )

    response = client.post("/search_clans", json={"name": "test"})

    assert response.status_code == 403
    assert response.get_json() == {
        "error": "Invalid authorization",
        "reason": "accessDenied",
    }


def test_search_clans_returns_400_for_list_payload(client, monkeypatch):
    setup_search_route(
        monkeypatch,
        {"items": [], "after": None, "error": None},
    )

    response = client.post("/search_clans", json=[])

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Request body must be a JSON object."
    }
    assert DummyRecruitee.instances == []


def test_search_clans_returns_400_for_nested_filter_value(client, monkeypatch):
    setup_search_route(
        monkeypatch,
        {"items": [], "after": None, "error": None},
    )

    response = client.post("/search_clans", json={"name": {"bad": "shape"}})

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "name must be a string or integer."
    }
    assert DummyRecruitee.instances == []
