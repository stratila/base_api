import pytest

from sqlalchemy import insert, delete

from app.database.models import users, roles

from app.database.dao import DbModels

from tests.database.utils import random_string, create_role


@pytest.fixture(scope="module")
def db_models(db_connection):
    return DbModels(db_connection)


@pytest.fixture()
def test_user(db_connection):
    role_id = create_role(db_connection, "role_name")
    test_user = {
        "email": f"{random_string()}@example.com",
        "username": random_string(10),
        "first_name": random_string(5),
        "last_name": random_string(5),
        "password_hash": random_string(16),
        "role_id": role_id,
    }
    yield test_user

    # clean up
    db_connection.execute(delete(roles).where(roles.c.id == role_id))
    db_connection.commit()


@pytest.fixture()
def test_data(db_connection):

    # create a role
    role_name = "role_name"
    role_id = create_role(db_connection, role_name)

    result_data = {
        "users": [
            {
                "email": f"{random_string()}@example.com",
                "username": random_string(10),
                "first_name": random_string(5),
                "last_name": random_string(5),
                "password_hash": random_string(16),
                "role_id": role_id,
            }
            for _ in range(10)
        ],
    }

    user_ids = []
    for user_data in result_data["users"]:
        result = db_connection.execute(
            insert(users)
            .values(
                email=user_data["email"],
                username=user_data["username"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                password_hash=user_data["password_hash"],
                role_id=user_data["role_id"],
            )
            .returning(users.c.id)
        )
        user_data["id"] = result.first()[0]
        user_data["role_name"] = role_name
        user_data.pop("role_id")
        user_ids.append(user_data["id"])

    yield result_data

    # clean up
    db_connection.execute(delete(users).where(users.c.id.in_(user_ids)))
    db_connection.execute(delete(roles).where(roles.c.id == role_id))
    db_connection.commit()
