import uuid

def test_public_data_empty_then_set_and_get(client):
    conv = f"conv-{uuid.uuid4()}"
    
    r = client.get(f"/v1/conversations/{conv}/public-data")
    assert r.status_code == 200
    assert r.json() is None

    seed = {"foo": "bar", "k2": {"sk3": 15, "sk4": None}, "k3": [1, 2, 3, "foo"]}
    r = client.post(f"/v1/conversations/{conv}/public-data", json=seed)
    assert r.status_code == 200
    assert r.json() == seed

    patch = {"k2": {"sk4": "val4", "sk5": 42}, "k3": None, "k10": "val10"}
    r = client.post(f"/v1/conversations/{conv}/public-data", json=patch)
    assert r.status_code == 200
    assert r.json() == {
        "foo": "bar",
        "k2": {"sk3": 15, "sk4": "val4", "sk5": 42},
        "k3": None,
        "k10": "val10",
    }

    r = client.post(f"/v1/conversations/{conv}/public-data", json={"k3": ["replaced", 999]})
    assert r.status_code == 200
    assert r.json()["k3"] == ["replaced", 999]

    r = client.delete(f"/v1/conversations/{conv}/public-data")
    assert r.status_code == 204
    r = client.get(f"/v1/conversations/{conv}/public-data")
    assert r.status_code == 200
    assert r.json() is None


def test_private_data_is_independent_from_public(client):
    conv = f"conv-{uuid.uuid4()}"

    r = client.post(f"/v1/conversations/{conv}/public-data", json={"public_only": True})
    assert r.status_code == 200

    r = client.get(f"/v1/conversations/{conv}/private-data")
    assert r.status_code == 200
    assert r.json() is None

    secret = {"access_token": "xyz", "ext": {"telegram": "@alice"}}
    r = client.post(f"/v1/conversations/{conv}/private-data", json=secret)
    assert r.status_code == 200
    assert r.json() == secret

    r = client.get(f"/v1/conversations/{conv}/public-data")
    assert r.status_code == 200
    assert r.json() == {"public_only": True}

    r = client.delete(f"/v1/conversations/{conv}/private-data")
    assert r.status_code == 204

    r = client.get(f"/v1/conversations/{conv}/private-data")
    assert r.status_code == 200
    assert r.json() is None
    r = client.get(f"/v1/conversations/{conv}/public-data")
    assert r.status_code == 200
    assert r.json() == {"public_only": True}
