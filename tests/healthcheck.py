def test_healthcheck_ok(client):
    resp = client.get("/healthcheck")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
