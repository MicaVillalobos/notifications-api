def test_create_notification(client, auth_headers):
    response = client.post(
        "/notifications",
        headers=auth_headers,
        json={
            "title": "Recordatorio",
            "content": "Tu turno es mañana",
            "channel": "email",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Recordatorio"
    assert data["channel"] == "email"
    assert data["status"] == "enviado"
    assert "id" in data
    assert "user_id" in data


def test_create_notification_all_channels(client, auth_headers):
    for channel in ("email", "sms", "push"):
        response = client.post(
            "/notifications",
            headers=auth_headers,
            json={"title": "T", "content": "C", "channel": channel},
        )
        assert response.status_code == 201
        assert response.json()["channel"] == channel
        assert response.json()["status"] == "enviado"


def test_create_notification_invalid_channel(client, auth_headers):
    response = client.post(
        "/notifications",
        headers=auth_headers,
        json={"title": "T", "content": "C", "channel": "telegram"},
    )
    assert response.status_code == 422


def test_create_notification_requires_auth(client):
    response = client.post(
        "/notifications",
        json={"title": "T", "content": "C", "channel": "email"},
    )
    assert response.status_code in (401, 403)


def test_list_notifications(client, auth_headers):
    client.post(
        "/notifications",
        headers=auth_headers,
        json={"title": "A", "content": "C", "channel": "email"},
    )
    client.post(
        "/notifications",
        headers=auth_headers,
        json={"title": "B", "content": "C", "channel": "sms"},
    )

    response = client.get("/notifications", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_notification(client, auth_headers):
    created = client.post(
        "/notifications",
        headers=auth_headers,
        json={"title": "A", "content": "C", "channel": "email"},
    )
    notification_id = created.json()["id"]

    response = client.get(f"/notifications/{notification_id}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["id"] == notification_id


def test_get_notification_not_found(client, auth_headers):
    response = client.get("/notifications/9999", headers=auth_headers)
    assert response.status_code == 404


def test_update_notification_partial(client, auth_headers):
    created = client.post(
        "/notifications",
        headers=auth_headers,
        json={"title": "Original", "content": "Contenido", "channel": "email"},
    )
    notification_id = created.json()["id"]

    response = client.put(
        f"/notifications/{notification_id}",
        headers=auth_headers,
        json={"title": "Editado"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Editado"
    assert data["content"] == "Contenido"


def test_delete_notification(client, auth_headers):
    created = client.post(
        "/notifications",
        headers=auth_headers,
        json={"title": "A", "content": "C", "channel": "email"},
    )
    notification_id = created.json()["id"]

    delete_response = client.delete(f"/notifications/{notification_id}", headers=auth_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/notifications/{notification_id}", headers=auth_headers)
    assert get_response.status_code == 404


def _register_and_login(client, email):
    client.post("/auth/register", json={"email": email, "password": "password123"})
    login = client.post("/auth/login", json={"email": email, "password": "password123"})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_user_cannot_access_others_notification(client):
    alice = _register_and_login(client, "alice@example.com")
    bob = _register_and_login(client, "bob@example.com")

    created = client.post(
        "/notifications",
        headers=alice,
        json={"title": "Privada de Alice", "content": "Secreto", "channel": "email"},
    )
    alice_notification_id = created.json()["id"]

    response = client.get(f"/notifications/{alice_notification_id}", headers=bob)

    assert response.status_code == 404


def test_user_cannot_update_others_notification(client):
    alice = _register_and_login(client, "alice2@example.com")
    bob = _register_and_login(client, "bob2@example.com")

    created = client.post(
        "/notifications",
        headers=alice,
        json={"title": "De Alice", "content": "Secreto", "channel": "email"},
    )
    alice_notification_id = created.json()["id"]

    response = client.put(
        f"/notifications/{alice_notification_id}",
        headers=bob,
        json={"title": "Hackeada por Bob"},
    )

    assert response.status_code == 404


def test_user_cannot_delete_others_notification(client):
    alice = _register_and_login(client, "alice3@example.com")
    bob = _register_and_login(client, "bob3@example.com")

    created = client.post(
        "/notifications",
        headers=alice,
        json={"title": "De Alice", "content": "Secreto", "channel": "email"},
    )
    alice_notification_id = created.json()["id"]

    response = client.delete(f"/notifications/{alice_notification_id}", headers=bob)

    assert response.status_code == 404


def test_list_only_returns_own_notifications(client):
    alice = _register_and_login(client, "alice4@example.com")
    bob = _register_and_login(client, "bob4@example.com")

    client.post(
        "/notifications",
        headers=alice,
        json={"title": "De Alice", "content": "C", "channel": "email"},
    )
    client.post(
        "/notifications",
        headers=bob,
        json={"title": "De Bob", "content": "C", "channel": "sms"},
    )

    alice_list = client.get("/notifications", headers=alice)
    bob_list = client.get("/notifications", headers=bob)

    assert len(alice_list.json()) == 1
    assert len(bob_list.json()) == 1
    assert alice_list.json()[0]["title"] == "De Alice"
    assert bob_list.json()[0]["title"] == "De Bob"


def test_notification_persisted_when_send_fails(client, auth_headers, monkeypatch):
    def fail_send(self, notification):
        raise RuntimeError("Fallo simulado del canal")

    monkeypatch.setattr("app.channels.email.EmailChannel.enviar", fail_send)

    response = client.post(
        "/notifications",
        headers=auth_headers,
        json={"title": "Con fallo", "content": "C", "channel": "email"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "fallido"
    assert "id" in data
