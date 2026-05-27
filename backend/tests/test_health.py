def test_health_endpoint_returns_ok(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_unknown_endpoint_returns_404(client):
    resp = client.get("/api/no-such-route")
    assert resp.status_code == 404


def test_me_without_token_returns_401(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_create_field_without_token_returns_401(client):
    resp = client.post(
        "/api/fields",
        json={
            "name": "Без прав",
            "location": "Тест",
            "reserves_tons": 1,
            "discovered_year": 2000,
        },
    )
    assert resp.status_code == 401
