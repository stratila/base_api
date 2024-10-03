from app.api.routers.literals import (
    SIGN_UP_URL,
    LOG_IN_URL,
)


def test_signup(client_user, client_admin):
    response = client_user.post(
        SIGN_UP_URL,
        json={
            "first_name": "John",
            "last_name": "Doe",
            "username": "john_doe",
            "email": "example@test.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    assert response.json()["access_token"]

    response = client_admin.get("/users/?email=example@test.com")
    assert response.status_code == 200
    assert response.json()[0]["id"]

    response = client_admin.delete(f"/users/{response.json()[0]['id']}")
    assert response.status_code == 204


def test_login(client_user, client_admin):
    response = client_user.post(
        SIGN_UP_URL,
        json={
            "first_name": "John",
            "last_name": "Doe",
            "username": "john_doe",
            "email": "login@test.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    assert response.json()["access_token"]

    response = client_user.post(
        LOG_IN_URL,
        json={
            "email": "login@test.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    assert response.json()["access_token"]

    response = client_admin.get("/users/?email=login@test.com")
    assert response.status_code == 200
    assert response.json()[0]["id"]

    response = client_admin.delete(f"/users/{response.json()[0]['id']}")
    assert response.status_code == 204
