class DummyAPI:
    instances = []

    def __init__(self, player_tag, api_token, headers):
        self.player_tag = player_tag
        self.api_token = api_token
        self.headers = headers
        self.recruiter_status = True
        self.user_name = "test_player"
        self.clantag = "TESTCLAN"
        self.league = 5
        self.townhall = 13
        self.townhallWeaponLevel = 2
        self.builder_trophies = 2400
        self.reason = None
        DummyAPI.instances.append(self)

    def check_player(self):
        return True


class InvalidDummyAPI(DummyAPI):
    def __init__(self, player_tag, api_token, headers):
        super().__init__(player_tag, api_token, headers)
        self.recruiter_status = False
        self.user_name = "Guest"
        self.clantag = None
        self.reason = "Player tag is incorrect"

    def check_player(self):
        return False


def test_home_login_valid_player_sets_session(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.home_route as home_route

    DummyAPI.instances = []
    monkeypatch.setattr(home_route, "API", DummyAPI)

    response = client.post(
        "/",
        json={"playerTag": "PLAYER123", "apiToken": "token-123"},
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "message": True,
        "receivedPlayerTag": "Valid User",
        "recruit_status": True,
        "player_name": "test_player",
        "clan_tag": "TESTCLAN",
    }
    assert DummyAPI.instances[0].player_tag == "PLAYER123"
    assert DummyAPI.instances[0].api_token == "token-123"

    with client.session_transaction() as session:
        assert session["player_tag"] == "PLAYER123"
        assert session["recruiter_status"] is True
        assert session["player_name"] == "test_player"
        assert session["clan_tag"] == "TESTCLAN"
        assert session["player_league"] == 5
        assert session["player_townhall"] == 13
        assert session["player_townhall_weapon_level"] == 2
        assert session["player_builderbase_trophies"] == 2400


def test_home_login_invalid_player_sets_failure_session(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.home_route as home_route

    monkeypatch.setattr(home_route, "API", InvalidDummyAPI)
    set_session(
        player_league=5,
        player_townhall=13,
        player_townhall_weapon_level=2,
        player_builderbase_trophies=2400,
    )

    response = client.post(
        "/",
        json={"playerTag": "BADTAG", "apiToken": "token-123"},
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "message": False,
        "receivedPlayerTag": "Player tag is incorrect",
        "recruit_status": False,
        "player_name": "Guest",
        "clan_tag": None,
    }

    with client.session_transaction() as session:
        assert session["player_tag"] == "BADTAG"
        assert session["recruiter_status"] is False
        assert session["player_name"] == "Guest"
        assert session["clan_tag"] is None
        assert "player_league" not in session
        assert "player_townhall" not in session
        assert "player_townhall_weapon_level" not in session
        assert "player_builderbase_trophies" not in session


def test_home_login_normalizes_player_tag(client, monkeypatch):
    import ClashRecruit.routes.home_route as home_route

    DummyAPI.instances = []
    monkeypatch.setattr(home_route, "API", DummyAPI)

    response = client.post(
        "/",
        json={"playerTag": "  #player123  ", "apiToken": "token-123"},
    )

    assert response.status_code == 200
    assert DummyAPI.instances[0].player_tag == "PLAYER123"


def test_home_login_returns_400_for_missing_json_object(client, monkeypatch):
    import ClashRecruit.routes.home_route as home_route

    DummyAPI.instances = []
    monkeypatch.setattr(home_route, "API", DummyAPI)

    response = client.post("/")

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Request body must be a JSON object."
    }
    assert DummyAPI.instances == []


def test_home_login_returns_400_for_invalid_player_tag(client, monkeypatch):
    import ClashRecruit.routes.home_route as home_route

    DummyAPI.instances = []
    monkeypatch.setattr(home_route, "API", DummyAPI)

    response = client.post("/", json={"playerTag": "   "})

    assert response.status_code == 400
    assert response.get_json() == {"error": "playerTag is required."}
    assert DummyAPI.instances == []


def test_home_login_rate_limits_repeated_attempts(client, monkeypatch):
    import ClashRecruit.routes.home_route as home_route

    DummyAPI.instances = []
    monkeypatch.setattr(home_route, "API", DummyAPI)

    for _ in range(home_route.LOGIN_RATE_LIMIT):
        response = client.post(
            "/",
            json={"playerTag": "PLAYER123", "apiToken": "token-123"},
        )
        assert response.status_code == 200

    response = client.post(
        "/",
        json={"playerTag": "PLAYER123", "apiToken": "token-123"},
    )

    assert response.status_code == 429
    assert response.headers["Retry-After"]
    assert response.get_json() == {
        "message": False,
        "receivedPlayerTag": (
            "Too many login attempts. Please try again shortly."
        ),
    }
    assert len(DummyAPI.instances) == home_route.LOGIN_RATE_LIMIT
