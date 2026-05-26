def _payload(**overrides):
    base = {
        "name": "Самотлорское",
        "location": "ХМАО, Нижневартовск",
        "reserves_tons": 1_200_000.5,
        "discovered_year": 1965,
        "status": "active",
        "description": "Крупнейшее месторождение в России",
    }
    base.update(overrides)
    return base


def test_create_field_requires_admin(client):
    resp = client.post("/api/fields", json=_payload())
    assert resp.status_code == 401


def test_admin_can_create_and_get_field(client, auth_headers):
    create = client.post("/api/fields", json=_payload(), headers=auth_headers)
    assert create.status_code == 201, create.text
    field_id = create.json()["id"]

    get = client.get(f"/api/fields/{field_id}")
    assert get.status_code == 200
    body = get.json()
    assert body["name"] == "Самотлорское"
    assert body["wells_count"] == 0


def test_list_fields_supports_search(client, auth_headers):
    client.post("/api/fields", json=_payload(name="Приобское"), headers=auth_headers)
    client.post(
        "/api/fields",
        json=_payload(name="Ванкорское", location="Красноярский край"),
        headers=auth_headers,
    )
    resp = client.get("/api/fields?q=ван")
    assert resp.status_code == 200
    names = [f["name"] for f in resp.json()]
    assert "Ванкорское" in names
    assert "Приобское" not in names


def test_update_and_delete_field(client, auth_headers):
    created = client.post(
        "/api/fields", json=_payload(name="Уренгойское"), headers=auth_headers
    ).json()
    field_id = created["id"]

    upd = client.put(
        f"/api/fields/{field_id}",
        json={"status": "suspended"},
        headers=auth_headers,
    )
    assert upd.status_code == 200
    assert upd.json()["status"] == "suspended"

    delete = client.delete(f"/api/fields/{field_id}", headers=auth_headers)
    assert delete.status_code == 204
    assert client.get(f"/api/fields/{field_id}").status_code == 404
