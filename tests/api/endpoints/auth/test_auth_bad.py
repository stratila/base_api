from app.api.routers.literals import (
    SIGN_UP_URL,
    LOG_IN_URL,
)


def test_signup_twice_throws_error(client_user, client_admin):
    response = client_user.post(
        SIGN_UP_URL,
        json={
            "first_name": "John",
            "username": "john_smith",
            "last_name": "Smith",
            "email": "example@test.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    assert response.json()["access_token"]

    response = client_user.post(
        SIGN_UP_URL,
        json={
            "first_name": "John",
            "username": "john_smith",
            "last_name": "Smith",
            "email": "example@test.com",
            "password": "password123",
        },
    )

    assert response.status_code == 400
    assert "User should have unique username" in response.json()["message"]

    response = client_user.post(
        SIGN_UP_URL,
        json={
            "first_name": "John",
            "username": "john_smith_different",
            "last_name": "Smith",
            "email": "example@test.com",
            "password": "password123",
        },
    )

    assert response.status_code == 400
    assert "User should have unique email" in response.json()["message"]

    # Clean up

    response = client_admin.get("/users/?email=example@test.com")
    assert response.status_code == 200
    assert response.json()[0]["id"]

    response = client_admin.delete(f"/users/{response.json()[0]['id']}")
    assert response.status_code == 204


# TODO add test with username too


def test_login_with_wrong_credentials(client_user):
    response = client_user.post(
        LOG_IN_URL,
        json={
            "email": "login@test.com",
            "password": "password123",
        },
    )

    assert response.status_code == 401
    assert "Wrong credentials" in response.json()["message"]
