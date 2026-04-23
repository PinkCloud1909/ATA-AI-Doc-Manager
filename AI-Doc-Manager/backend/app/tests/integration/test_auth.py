import pytest


def test_successful_register(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "alice", "password": "alicepass123"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["username"] == "alice"
    assert payload["roles"] == ["user"]
    assert "GET:/api/v1/auth/me" in payload["permissions"]


def test_register_duplicate_username(client):
    first_response = client.post(
        "/api/v1/auth/register",
        json={"username": "alice", "password": "alicepass123"},
    )
    assert first_response.status_code == 201

    duplicate_response = client.post(
        "/api/v1/auth/register",
        json={"username": "alice", "password": "anotherpass123"},
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["code"] == "conflict"


def test_successful_login(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["expires_in"] > 0
    assert payload["access_token"]


def test_failed_login(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["code"] == "unauthorized"


def test_me_with_valid_token(client):
    register_response = client.post(
        "/api/v1/auth/register",
        json={"username": "bob", "password": "bobpass123"},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "bob", "password": "bobpass123"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["username"] == "bob"
    assert payload["roles"] == ["user"]
    assert "GET:/api/v1/auth/me" in payload["permissions"]


@pytest.mark.parametrize(
    ("headers", "expected_detail"),
    [
        ({}, "Authentication credentials were not provided"),
        ({"Authorization": "Bearer invalid-token"}, "Invalid authentication credentials"),
    ],
)
def test_me_without_or_with_invalid_token(client, headers, expected_detail):
    response = client.get("/api/v1/auth/me", headers=headers)

    assert response.status_code == 401
    assert response.json()["detail"] == expected_detail
