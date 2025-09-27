import uuid

def test_aplm_correlation_id_echoed_in_response_headers(client):
    conv = f"conv-{uuid.uuid4()}"
    corr = "trace-pytest-001"
    r = client.get(f"/v1/conversations/{conv}/public-data", headers={"aplm-correlation-id": corr})
    assert r.status_code == 200
    assert r.headers.get("aplm-correlation-id") == corr

def test_delete_returns_204_no_body(client):
    conv = f"conv-{uuid.uuid4()}"
    r = client.delete(f"/v1/conversations/{conv}/public-data")
    assert r.status_code == 204
    assert not r.content
