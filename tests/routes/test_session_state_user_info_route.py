def test_session_state_user_info_returns_empty_for_guest(client, monkeypatch):
    import ClashRecruit.routes.session_state_route as session_state_route

    class _FailIfCalledAPI:
        def __init__(self, *args, **kwargs):
            raise AssertionError(
                "API should not be called for Guest user-info"
                )

    monkeypatch.setattr(session_state_route, "API", _FailIfCalledAPI)

    response = client.get("/session-state/user-info")

    assert response.status_code == 200
    assert response.get_json() == {}
