def test_invalid_route_returns_404(client):
    r = client.get("/does-not-exist")
    assert r.status_code == 404
    assert "error" in r.json()

def test_invalid_json_returns_422(client):
    r = client.post(
        "/v1/conversations/conv-1/public-data",
        data="{'invalid': 'json'}",  # malformed JSON
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 422
