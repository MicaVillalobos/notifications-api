def test_register_success(client):
    response = client.post(
        "/auth/register",
        json={"email": "mica@example.com", "password": "password123"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "mica@example.com"
    assert "id" in data
    assert "hashed_password" not in data
    assert "password" not in data


def test_register_duplicate_email(client):
    payload = {"email": "dup@example.com", "password": "password123"}
    client.post("/auth/register", json=payload)

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 400


def test_register_invalid_email(client):
    response = client.post(
        "/auth/register",
        json={"email": "no-es-un-email", "password": "password123"},
    )

    assert response.status_code == 422


def test_register_short_password(client):
    response = client.post(
        "/auth/register",
        json={"email": "short@example.com", "password": "123"},
    )

    assert response.status_code == 422


def test_login_success(client):
    client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": "password123"},
    )

    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={"email": "wrong@example.com", "password": "password123"},
    )

    response = client.post(
        "/auth/login",
        json={"email": "wrong@example.com", "password": "incorrecta"},
    )

    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/login",
        json={"email": "noexiste@example.com", "password": "password123"},
    )

    assert response.status_code == 401


def test_get_me(client):
    client.post("/auth/register", json={"email": "me@example.com", "password": "password123"})
    login = client.post("/auth/login", json={"email": "me@example.com", "password": "password123"})
    token = login.json()["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert "hashed_password" not in data


def test_me_requires_auth(client):
    response = client.get("/auth/me")
    assert response.status_code in (401, 403)


def test_me_invalid_token(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer token-invalido"})
    assert response.status_code == 401


def test_refresh_token(client):
    client.post(
        "/auth/register",
        json={"email": "refresh@example.com", "password": "password123"},
    )
    login = client.post(
        "/auth/login", json={"email": "refresh@example.com", "password": "password123"}
    )
    refresh_token = login.json()["refresh_token"]

    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_refresh_with_access_token_fails(client):
    client.post(
        "/auth/register",
        json={"email": "refresh2@example.com", "password": "password123"},
    )
    login = client.post(
        "/auth/login", json={"email": "refresh2@example.com", "password": "password123"}
    )
    access_token = login.json()["access_token"]

    response = client.post("/auth/refresh", json={"refresh_token": access_token})

    assert response.status_code == 401
