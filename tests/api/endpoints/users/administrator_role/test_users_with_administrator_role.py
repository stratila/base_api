"""
Successful users requests with administrator role
"""

from typing import List
from pydantic import TypeAdapter
from app.api.schemas.users import UserReadSchema
from app.api.routers.literals import (
    RETRIEVE_USER_URL,
    LIST_USERS_URL,
    DELETE_USER_URL,
    CREATE_USER_URL,
)


def test_get_users(client_admin, users_data):
    response = client_admin.get(
        LIST_USERS_URL,
        params={"role_name": "user"},  # TODO test all params
    )
    assert response.status_code == 200

    users = TypeAdapter(List[UserReadSchema]).validate_python(response.json())

    for user in users:
        for user_data in users_data["users"].values():
            if user.id == user_data["id"]:
                assert user.first_name == user_data["first_name"]
                assert user.username == user_data["username"]
                assert user.last_name == user_data["last_name"]
                assert user.email == user_data["email"]
                assert user.role_name == user_data["role_name"]


def test_get_user(client_admin, users_data):
    user = users_data["users"]["user_0"]

    # TODO ugly: if repeatable multiple times write utils functionality
    # to pop certain values when getting the users test data
    user.pop("role_id")
    user.pop("password_hash")

    response = client_admin.get(RETRIEVE_USER_URL.format(user_id=user["id"]))
    assert response.status_code == 200

    response_user = (
        TypeAdapter(UserReadSchema).validate_python(response.json()).model_dump()
    )

    assert response_user == user


def test_post_user(client_admin, user_create_data):

    response = client_admin.post(
        CREATE_USER_URL,
        json=user_create_data,
    )

    assert response.status_code == 201

    response_user = TypeAdapter(UserReadSchema).validate_python(response.json())
    assert response_user.id
    assert response_user.first_name == user_create_data["first_name"]
    assert response_user.last_name == user_create_data["last_name"]
    assert response_user.username == user_create_data["username"]
    assert response_user.email == user_create_data["email"]
    assert response_user.role_name == user_create_data["role_name"]

    # clean up
    response = client_admin.delete(
        DELETE_USER_URL.format(user_id=response.json()["id"])
    )
    assert response.status_code == 204


# @pytest.mark.skip()
# def test_put_user(client, users_data):
#     user = users_data["users"]["user_0"]
#     response = client.put(
#         f"/users/{user['id']}",
#         json={
#             "first_name": "John2",
#             "middle_name": "Doe2",
#             "last_name": "Smith2",
#         },
#     )
#     assert response.status_code == 200

#     response_user = parse_obj_as(UserRead, response.json())

#     # unchanged fields
#     assert response_user.id == user["id"]
#     assert response_user.email == user["email"]
#     assert response_user.role == user["role"]
#     # changed fields
#     assert response_user.first_name == "John2"
#     assert response_user.middle_name == "Doe2"
#     assert response_user.last_name == "Smith2"

# @pytest.mark.skip()
# def test_user_change_itself(client_admin, users_data):
#     response = client_admin.get("/users/me")
#     user_id = response.json()["id"]
#     assert response.status_code == 200
#     response = client_admin.put(f"/users/{user_id}",
#  json={"first_name": "John_edited"})
#     print(response.text)
#     assert response.status_code == 200
#     assert response.json()["first_name"] == "John_edited"

#     other_user = users_data["users"]["user_0"]
#     response = client_admin.put(
#         f"/users/{other_user['id']}", json={"first_name": "John_edited"}
#     )
#     assert response.status_code == 403


def test_delete_user(client_admin, user_create_data):
    # create user
    response = client_admin.post(
        CREATE_USER_URL,
        json=user_create_data,
    )
    assert response.status_code == 201
    assert response.json()["id"]
    deleted_user_id = response.json()["id"]

    # delete user
    response = client_admin.delete(
        DELETE_USER_URL.format(user_id=response.json()["id"])
    )
    assert response.status_code == 204

    # check if user is deleted
    response = client_admin.get(RETRIEVE_USER_URL.format(user_id=deleted_user_id))
    assert response.status_code == 404
