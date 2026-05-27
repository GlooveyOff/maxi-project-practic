def _register(client, email, full_name="User"):
    return client.post(
        "/api/auth/register",
        json={"email": email, "full_name": full_name, "password": "qwerty123"},
    )


def test_list_users_requires_admin(client):
    _register(client, "u1@neftegaz.ru")
    resp = client.get("/api/users")
    assert resp.status_code == 401


def test_employee_cannot_list_users(client):
    reg = _register(client, "emp@neftegaz.ru")
    token = reg.json()["access_token"]
    resp = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


def test_admin_can_list_users(client, auth_headers, admin_user):
    _register(client, "u1@neftegaz.ru")
    _register(client, "u2@neftegaz.ru")

    resp = client.get("/api/users", headers=auth_headers)
    assert resp.status_code == 200
    emails = [u["email"] for u in resp.json()]
    assert "admin@neftegaz.ru" in emails
    assert "u1@neftegaz.ru" in emails
    assert "u2@neftegaz.ru" in emails


def test_admin_can_change_user_role(client, auth_headers):
    reg = _register(client, "promo@neftegaz.ru")
    uid = reg.json()["user"]["id"]

    upd = client.patch(
        f"/api/users/{uid}",
        json={"role": "admin"},
        headers=auth_headers,
    )
    assert upd.status_code == 200
    assert upd.json()["role"] == "admin"


def test_admin_cannot_deactivate_self(client, auth_headers, admin_user):
    resp = client.patch(
        f"/api/users/{admin_user.id}",
        json={"is_active": False},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_admin_cannot_delete_self(client, auth_headers, admin_user):
    resp = client.delete(f"/api/users/{admin_user.id}", headers=auth_headers)
    assert resp.status_code == 400


def test_admin_can_delete_other_user(client, auth_headers):
    reg = _register(client, "delme@neftegaz.ru")
    uid = reg.json()["user"]["id"]

    resp = client.delete(f"/api/users/{uid}", headers=auth_headers)
    assert resp.status_code == 204

    listed = client.get("/api/users", headers=auth_headers).json()
    assert all(u["id"] != uid for u in listed)
