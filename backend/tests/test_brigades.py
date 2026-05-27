def _create_field(client, headers, name="ПолеQA"):
    return client.post(
        "/api/fields",
        json={
            "name": name,
            "location": "тест",
            "reserves_tons": 100,
            "discovered_year": 1990,
            "status": "active",
        },
        headers=headers,
    ).json()["id"]


def _create_well(client, headers, field_id, name="QA-1"):
    return client.post(
        "/api/wells",
        json={"field_id": field_id, "name": name, "depth_m": 1000},
        headers=headers,
    ).json()["id"]


def _payload(**overrides):
    base = {
        "name": "Бригада №1",
        "foreman": "Сидоров Сидор",
        "members_count": 5,
        "phone": "+79991112233",
        "status": "available",
    }
    base.update(overrides)
    return base


def test_create_brigade_requires_admin(client):
    resp = client.post("/api/brigades", json=_payload())
    assert resp.status_code == 401


def test_admin_can_create_and_list_brigade(client, auth_headers):
    create = client.post("/api/brigades", json=_payload(), headers=auth_headers)
    assert create.status_code == 201, create.text
    body = create.json()
    assert body["name"] == "Бригада №1"
    assert body["active_requests"] == 0

    listed = client.get("/api/brigades", headers=auth_headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_brigade_status_filter(client, auth_headers):
    a = client.post("/api/brigades", json=_payload(name="Альфа", status="available"), headers=auth_headers)
    b = client.post("/api/brigades", json=_payload(name="Браво", status="resting"), headers=auth_headers)
    assert a.status_code == 201
    assert b.status_code == 201

    resp = client.get("/api/brigades?status=resting", headers=auth_headers)
    assert resp.status_code == 200
    assert [br["name"] for br in resp.json()] == ["Браво"]


def test_active_requests_counted(client, auth_headers):
    field_id = _create_field(client, auth_headers)
    well_id = _create_well(client, auth_headers, field_id)
    brigade_id = client.post(
        "/api/brigades",
        json=_payload(name="С активными"),
        headers=auth_headers,
    ).json()["id"]

    for title in ["A", "B", "C"]:
        client.post(
            "/api/requests",
            json={
                "well_id": well_id,
                "title": f"Заявка {title}",
                "description": "тестовая",
                "brigade_id": brigade_id,
                "priority": "high",
            },
            headers=auth_headers,
        )

    resp = client.get(f"/api/brigades/{brigade_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["active_requests"] == 3


def test_patch_brigade_status(client, auth_headers):
    brigade_id = client.post("/api/brigades", json=_payload(), headers=auth_headers).json()["id"]
    upd = client.patch(
        f"/api/brigades/{brigade_id}",
        json={"status": "on_site"},
        headers=auth_headers,
    )
    assert upd.status_code == 200
    assert upd.json()["status"] == "on_site"


def test_duplicate_brigade_name_rejected(client, auth_headers):
    client.post("/api/brigades", json=_payload(name="Уник"), headers=auth_headers)
    resp = client.post("/api/brigades", json=_payload(name="Уник"), headers=auth_headers)
    assert resp.status_code == 400
