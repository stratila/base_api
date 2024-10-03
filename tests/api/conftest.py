import pytest
from typing import TypedDict

from fastapi.testclient import TestClient

from app.api.security.password import get_password_hash
from app.database.dao import DbModels
from app.scripts.python.update_roles_and_permissions import (
    update_roles_and_permissions,
)


from app.api.app import app


# TODO: refactor responses types on db level
class RoleObj(TypedDict):
    role_name: str
    role_id: int


#######################################################################################
#                                DB FIXTURES                                          #
#######################################################################################


@pytest.fixture(scope="module")
def db_models(db_connection):
    return DbModels(db_connection)


@pytest.fixture(scope="module", autouse=True)
def load_permissions(db_connection):
    # set up
    update_roles_and_permissions(db_connection)

    try:
        yield
    finally:
        pass
        # tear down
        # deletes permission by cascade
        # db_connection.execute(text("DELETE FROM roles;"))


#######################################################################################
#                                ADMIN FIXTURES                                       #
#######################################################################################


@pytest.fixture(scope="module")
def admin_password():
    return "password123"


@pytest.fixture(scope="module")
def admin_role_object(db_models) -> RoleObj:
    return db_models.roles.get_role(role_name="administrator")


@pytest.fixture(scope="module")
def admin_data(admin_password, admin_role_object):
    return {
        "first_name": "Admin",
        "last_name": "Admin",
        "email": "AdminTest@test.com",
        "username": "AdminTest",
        "password_hash": get_password_hash(admin_password),
        "role_id": admin_role_object["id"],
    }


@pytest.fixture(scope="module")
def admin_bearer(db_models: DbModels, admin_data, admin_password):
    admin_id = db_models.users.add_user(
        **admin_data,
    )
    db_models.conn.commit()

    client = TestClient(app)
    # pcs = client.get("/").json()["postgres_connection_string"]
    # assert 'abc' == pcs
    response = client.post(
        "/login",
        json={
            "email": admin_data["email"],
            "password": admin_password,
        },
    )

    assert response.status_code == 200
    assert response.json()["access_token"]

    yield response.json()["access_token"]

    db_models.users.delete_user(admin_id)


#######################################################################################
#                                USER FIXTURES                                        #
#######################################################################################


@pytest.fixture(scope="module")
def user_password():
    return "password123"


@pytest.fixture(scope="module")
def user_role_object(db_models) -> RoleObj:
    return db_models.roles.get_role(role_name="user")


@pytest.fixture(scope="module")
def user_data(user_password, user_role_object):
    return {
        "first_name": "User",
        "last_name": "User",
        "email": "UserTest@test.com",
        "username": "UserTest",
        "password_hash": get_password_hash(user_password),
        "role_id": user_role_object["id"],
    }


@pytest.fixture(scope="module")
def user_bearer(db_models: DbModels, user_data, user_password):
    user_id = db_models.users.add_user(
        **user_data,
    )
    db_models.conn.commit()

    client = TestClient(app)

    response = client.post(
        "/login",
        json={
            "email": user_data["email"],
            "password": user_password,
        },
    )

    assert response.status_code == 200
    assert response.json()["access_token"]

    yield response.json()["access_token"]

    db_models.users.delete_user(user_id)


@pytest.fixture(scope="module")
def client_admin(admin_bearer):
    return TestClient(app, headers={"Authorization": f"Bearer {admin_bearer}"})


@pytest.fixture(scope="module")
def client_user(user_bearer):
    return TestClient(app, headers={"Authorization": f"Bearer {user_bearer}"})


@pytest.fixture(scope="function")
def users_data(db_models, user_password, user_role_object):
    data = {}
    users = {}
    for i in range(2):
        user_data = {
            "first_name": f"User_{i}",
            "last_name": f"User_{i}",
            "email": f"UserTest_{i}@test.com",
            "username": f"UserTest{i}",
            "password_hash": get_password_hash(user_password),
            "role_id": user_role_object["id"],
        }
        user_id = db_models.users.add_user(**user_data)
        users[f"user_{i}"] = {
            **user_data,
            "id": user_id,
            "role_name": user_role_object["role_name"],
        }
        db_models.conn.commit()

    data["users"] = users

    yield data

    for user in data["users"].values():
        db_models.users.delete_user(user["id"])


#######################################################################################
#                                DATA FIXTURES                                        #
#######################################################################################


@pytest.fixture
def user_create_data():
    return {
        "email": "john_doe@email.com",
        "username": "john_doe",
        "first_name": "john",
        "last_name": "doe",
        "role_name": "user",
        "password": "password123",
    }
