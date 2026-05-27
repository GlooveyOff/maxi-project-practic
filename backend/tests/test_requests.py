def _setup_well(client, headers):
    field_id = client.post(
        "/api/fields",
        json={
            "name": "ReqField",
            "location": "loc",
            "reserves_tons": 100,
            "discovered_year": 1990,
            "status": "active",
        },
        headers=headers,
    ).json()["id"]
    well_id = client.post(
        "/api/wells",
        json={"field_id": field_id, "name": "ReqWell", "depth_m": 1000},
        headers=headers,
    ).json()["id"]
    return well_id


def test_create_request_requires_auth(client):
    resp = client.post(
        "/api/requests",
        json={
            "well_id": 1,
            "title": "Без авторизации",
            "description": "не должно создаться",
            "priority": "medium",
        },
    )
    assert resp.status_code == 401


def test_create_request_unknown_well_returns_400(client, auth_headers):
    resp = client.post(
        "/api/requests",
        json={
            "well_id": 9999,
            "title": "Несуществующая скважина",
            "description": "проверяем ошибку",
            "priority": "low",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_create_and_close_request_sets_closed_at(client, auth_headers):
    well_id = _setup_well(client, auth_headers)
    create = client.post(
        "/api/requests",
        json={
            "well_id": well_id,
            "title": "Заявка на ТО",
            "description": "плановое обслуживание",
            "priority": "medium",
        },
        headers=auth_headers,
    )
    assert create.status_code == 201
    req_id = create.json()["id"]
    assert create.json()["closed_at"] is None

    upd = client.patch(
        f"/api/requests/{req_id}",
        json={"status": "done"},
        headers=auth_headers,
    )
    assert upd.status_code == 200
    assert upd.json()["status"] == "done"
    assert upd.json()["closed_at"] is not None


def test_reopen_request_clears_closed_at(client, auth_headers):
    well_id = _setup_well(client, auth_headers)
    req = client.post(
        "/api/requests",
        json={
            "well_id": well_id,
            "title": "Возврат в работу",
            "description": "будем переоткрывать",
            "priority": "low",
        },
        headers=auth_headers,
    ).json()

    client.patch(f"/api/requests/{req['id']}", json={"status": "done"}, headers=auth_headers)
    reopened = client.patch(
        f"/api/requests/{req['id']}",
        json={"status": "in_progress"},
        headers=auth_headers,
    )
    assert reopened.json()["closed_at"] is None


def test_priority_filter(client, auth_headers):
    well_id = _setup_well(client, auth_headers)
    for p in ["low", "high", "high", "critical"]:
        client.post(
            "/api/requests",
            json={
                "well_id": well_id,
                "title": f"Заявка {p}",
                "description": "тестовая",
                "priority": p,
            },
            headers=auth_headers,
        )

    high = client.get("/api/requests?priority=high", headers=auth_headers)
    assert high.status_code == 200
    assert {r["priority"] for r in high.json()} == {"high"}
    assert len(high.json()) == 2


def test_assign_brigade_to_request(client, auth_headers):
    well_id = _setup_well(client, auth_headers)
    brigade_id = client.post(
        "/api/brigades",
        json={"name": "Бр-1", "foreman": "Иванов", "members_count": 3},
        headers=auth_headers,
    ).json()["id"]

    req = client.post(
        "/api/requests",
        json={
            "well_id": well_id,
            "title": "С бригадой",
            "description": "назначена бригада",
            "priority": "high",
            "brigade_id": brigade_id,
        },
        headers=auth_headers,
    )
    assert req.status_code == 201
    assert req.json()["brigade_id"] == brigade_id


def test_assign_unknown_brigade_returns_400(client, auth_headers):
    well_id = _setup_well(client, auth_headers)
    resp = client.post(
        "/api/requests",
        json={
            "well_id": well_id,
            "title": "Неизвестная бригада",
            "description": "бригады с таким id нет",
            "priority": "low",
            "brigade_id": 9999,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_stats_overview_returns_aggregates(client, auth_headers):
    well_id = _setup_well(client, auth_headers)
    client.post(
        "/api/requests",
        json={
            "well_id": well_id,
            "title": "Для статистики",
            "description": "одна открытая заявка",
            "priority": "low",
        },
        headers=auth_headers,
    )
    resp = client.get("/api/stats/overview", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    for key in [
        "fields_total", "fields_active", "wells_total", "wells_operating",
        "requests_open", "requests_done", "daily_output_tons", "brigades_available",
    ]:
        assert key in data
    assert data["requests_open"] >= 1
