def test_register_creates_user_and_returns_token(client):
    resp = client.post(
        "/api/auth/register",
        json={
            "email": "ivanov@neftegaz.ru",
            "full_name": "Иванов Иван",
            "password": "qwerty123",
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["user"]["email"] == "ivanov@neftegaz.ru"
    assert data["user"]["role"] == "employee"


def test_register_duplicate_email_fails(client):
    body = {
        "email": "dup@neftegaz.ru",
        "full_name": "Дубль",
        "password": "qwerty123",
    }
    assert client.post("/api/auth/register", json=body).status_code == 201
    resp = client.post("/api/auth/register", json=body)
    assert resp.status_code == 400


def test_login_with_wrong_password_returns_401(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "petrov@neftegaz.ru",
            "full_name": "Петров",
            "password": "correct1",
        },
    )
    resp = client.post(
        "/api/auth/login",
        json={"email": "petrov@neftegaz.ru", "password": "wrong"},
    )
    assert resp.status_code == 401


def test_me_returns_current_user(client):
    reg = client.post(
        "/api/auth/register",
        json={
            "email": "sidorov@neftegaz.ru",
            "full_name": "Сидоров",
            "password": "qwerty123",
        },
    )
    token = reg.json()["access_token"]
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "sidorov@neftegaz.ru"
