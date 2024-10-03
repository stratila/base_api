"""
Bad users requests
"""

import pytest
from app.api.routers.literals import (
    CREATE_USER_URL,
    RETRIEVE_USER_URL,
    DELETE_USER_URL,
)
from app.service.errors.messages import ROLE_DOES_NOT_EXIST
from app.database.errors.messages import (
    USER_SHOULD_HAVE_UNIQUE_EMAIL as DB_USER_SHOULD_HAVE_UNIQUE_EMAIL,
    USER_SHOULD_HAVE_UNIQUE_USERNAME as DB_USER_SHOULD_HAVE_UNIQUE_USERNAME,
)  # for demonstration purposes

from app.service.errors.messages import (
    USER_SHOULD_HAVE_UNIQUE_EMAIL,
    USER_SHOULD_HAVE_UNIQUE_USERNAME,
)

from copy import deepcopy


def test_get_user_not_found(client_admin):
    response = client_admin.get(RETRIEVE_USER_URL.format(user_id=999))
    assert response.status_code == 404


def test_post_user_role_does_not_exist(client_admin, user_create_data):
    ROLE_NAME = "role_that_does_not_exist"
    user_create_data["role_name"] = ROLE_NAME
    response = client_admin.post(
        CREATE_USER_URL,
        json=user_create_data,
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == ROLE_DOES_NOT_EXIST.error_code
    assert response.json()["message"] == ROLE_DOES_NOT_EXIST.message.format(
        role_name=ROLE_NAME
    )


@pytest.mark.skip("an example of database user error")
def test_post_user_username_or_email_exists_raise_an_db_error(
    client_admin, user_create_data
):
    user_data = deepcopy(user_create_data)

    response = client_admin.post(
        CREATE_USER_URL,
        json=user_data,
    )
    assert response.status_code == 201

    # username

    user_data["email"] = "different_email@email.com"
    response = client_admin.post(
        CREATE_USER_URL,
        json=user_data,
    )

    assert response.status_code == 400
    assert DB_USER_SHOULD_HAVE_UNIQUE_USERNAME.message in response.json()["message"]
    assert (
        response.json()["error_code"] == DB_USER_SHOULD_HAVE_UNIQUE_USERNAME.error_code
    )

    # email

    user_data["email"] = user_create_data["email"]
    user_data["username"] = "different_username"
    response = client_admin.post(
        CREATE_USER_URL,
        json=user_data,
    )

    assert response.status_code == 400
    assert DB_USER_SHOULD_HAVE_UNIQUE_EMAIL.message in response.json()["message"]
    assert response.json()["error_code"] == DB_USER_SHOULD_HAVE_UNIQUE_EMAIL.error_code


def test_post_user_username_or_email_exists_raise_an_error(
    client_admin, user_create_data
):
    user_data = deepcopy(user_create_data)

    response = client_admin.post(
        CREATE_USER_URL,
        json=user_data,
    )
    assert response.status_code == 201

    # username

    user_data["email"] = "different_email@email.com"
    response = client_admin.post(
        CREATE_USER_URL,
        json=user_data,
    )

    assert response.status_code == 400
    assert USER_SHOULD_HAVE_UNIQUE_USERNAME.message in response.json()["message"]
    assert response.json()["error_code"] == USER_SHOULD_HAVE_UNIQUE_USERNAME.error_code

    # email

    user_data["email"] = user_create_data["email"]
    user_data["username"] = "different_username"
    response = client_admin.post(
        CREATE_USER_URL,
        json=user_data,
    )

    assert response.status_code == 400
    assert USER_SHOULD_HAVE_UNIQUE_EMAIL.message in response.json()["message"]
    assert response.json()["error_code"] == USER_SHOULD_HAVE_UNIQUE_EMAIL.error_code


def test_delete_nonexistent_user(client_admin):
    # delete user
    response = client_admin.delete(DELETE_USER_URL.format(user_id=999))
    assert response.status_code == 404


# def test_put_user_not_found(client, users_data):
#     user_0 = users_data["users"]["user_0"]
#     response = client.put("/users/999", json=user_0)
#     assert response.status_code == 404
