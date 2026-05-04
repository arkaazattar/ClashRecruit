def test_logout_clears_session_and_returns_success(client, set_session):
    set_session(
        player_tag="P123", 
        player_name="SomeUser", 
        recruiter_status=True
        )

    response = client.post("/logout")

    assert response.status_code == 200
    assert response.get_json() == {"message": True}
    with client.session_transaction() as sess:
        assert dict(sess) == {}
