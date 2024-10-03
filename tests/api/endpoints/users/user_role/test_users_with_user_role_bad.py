"""
Successful users requests with user role
"""

from app.api.routers.literals import (
    RETRIEVE_USER_URL,
    LIST_USERS_URL,
    CREATE_USER_URL,
    DELETE_USER_URL,
)


def test_get_users_unauthorized(client_user):
    response = client_user.get(
        LIST_USERS_URL,
        params={"role_name": "user"},
    )
    assert response.status_code == 403
    # TODO add message check


def test_get_user_unauthorized(client_user):
    response = client_user.get(RETRIEVE_USER_URL.format(user_id=999))
    assert response.status_code == 403


def test_post_user_unauthorized(client_user):
    response = client_user.post(
        CREATE_USER_URL,
        json={},
    )
    assert response.status_code == 403


def test_delete_user_unauthorized(client_user):
    response = client_user.delete(DELETE_USER_URL.format(user_id=999))
    assert response.status_code == 403
