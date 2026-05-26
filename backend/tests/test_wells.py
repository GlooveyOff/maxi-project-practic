def _field(client, auth_headers, name="Тестовое"):
    resp = client.post(
        "/api/fields",
        json={
            "name": name,
            "location": "Тюменская область",
            "reserves_tons": 100000,
            "discovered_year": 1980,
            "status": "active",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def test_create_well_links_to_field(client, auth_headers):
    field_id = _field(client, auth_headers)
    resp = client.post(
        "/api/wells",
        json={
            "field_id": field_id,
            "name": "СКВ-001",
            "depth_m": 2500.5,
            "daily_output_tons": 120.0,
            "status": "operating",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    well = resp.json()
    assert well["field_id"] == field_id
    assert well["status"] == "operating"


def test_filter_wells_by_field(client, auth_headers):
    a = _field(client, auth_headers, name="ПолеA")
    b = _field(client, auth_headers, name="ПолеB")
    for name, fid in [("A-1", a), ("A-2", a), ("B-1", b)]:
        client.post(
            "/api/wells",
            json={"field_id": fid, "name": name, "depth_m": 1500},
            headers=auth_headers,
        )

    resp = client.get(f"/api/wells?field_id={a}")
    assert resp.status_code == 200
    names = sorted(w["name"] for w in resp.json())
    assert names == ["A-1", "A-2"]
