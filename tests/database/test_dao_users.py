import pytest
from sqlalchemy import Connection, select, insert, delete
from app.database.models import users, roles
from app.database.dao import DbModels
from app.database.errors import DatabaseError
from app.database.errors.messages import (
    USER_SHOULD_HAVE_UNIQUE_EMAIL,
    USER_SHOULD_HAVE_UNIQUE_USERNAME,
)


def test_add_user(
    db_connection: Connection,
    db_models: DbModels,
    test_user: dict,
):

    user_id = db_models.users.add_user(**test_user)
    db_connection.commit()

    result = (
        db_connection.execute(select(users).where(users.c.id == user_id))
        .mappings()
        .first()
    )
    result = dict(result)
    assert result.pop("id") == user_id
    assert result == test_user

    # clean up
    db_connection.execute(delete(users).where(users.c.id == user_id))
    db_connection.commit()


def test_get_user(
    db_connection: Connection,
    db_models: DbModels,
    test_user: dict,
):
    [user_id] = db_connection.execute(
        insert(users).values(**test_user).returning(users.c.id),
    ).first()
    db_connection.commit()

    [role_name] = db_connection.execute(
        select(roles.c.role_name).where(roles.c.id == test_user["role_id"])
    ).first()

    result = db_models.users.get_user(user_id)

    test_user.pop("role_id")
    test_user.pop("password_hash")

    assert result.pop("id") == user_id
    assert result.pop("role_name") == role_name
    assert result == test_user

    # clean up
    db_connection.execute(delete(users).where(users.c.id == user_id))
    db_connection.commit()


def test_get_users(
    db_models: DbModels,
    test_data: dict,
):
    test_users = test_data["users"]
    users_result = db_models.users.get_users(user_ids=[u["id"] for u in test_users])
    for user in users_result:
        for test_user in test_users:
            if test_user["id"] == user["id"]:
                test_user.pop("password_hash")
                assert user == test_user

    test_user = test_users[0]
    user_result = db_models.users.get_users(user_id=test_user["id"])
    assert user_result[0] == test_user
    user_result = db_models.users.get_users(first_name=test_user["first_name"])
    assert user_result[0] == test_user
    user_result = db_models.users.get_users(last_name=test_user["last_name"])
    assert user_result[0] == test_user
    user_result = db_models.users.get_users(email=test_user["email"])
    assert user_result[0] == test_user
    user_result = db_models.users.get_users(username=test_user["username"])
    assert user_result[0] == test_user
    user_result = db_models.users.get_users(role_name="role_name")
    assert len(user_result) == len(test_users)


def test_get_hashed_password_by_email(
    db_connection: Connection,
    db_models: DbModels,
    test_user: dict,
):
    user_id = db_models.users.add_user(**test_user)
    db_connection.commit()

    user_with_pwd_hash = db_models.users.get_hashed_password_by_email(
        test_user["email"]
    )
    assert test_user["password_hash"] == user_with_pwd_hash["password_hash"]

    # clean up
    db_connection.execute(delete(users).where(users.c.id == user_id))
    db_connection.commit()


def test_delete_user(
    db_connection: Connection,
    db_models: DbModels,
    test_user: dict,
):
    user_id = db_models.users.add_user(**test_user)
    db_connection.commit()

    row_count = db_models.users.delete_user(user_id)
    db_connection.commit()
    assert row_count == 1

    user = db_connection.execute(select(users).where(users.c.id == user_id)).first()
    assert user is None


def test_delete_non_existing_user(
    db_connection: Connection,
    db_models: DbModels,
):
    row_count = db_models.users.delete_user(1000)
    db_connection.commit()
    assert row_count == 0


# Bad tests


@pytest.mark.skip("an example of database user error")
def test_add_user_with_existing_username_or_email_raise_error(
    db_connection: Connection, db_models: DbModels, test_user
):
    user_id = db_models.users.add_user(**test_user)
    db_connection.commit()

    with pytest.raises(DatabaseError, match=USER_SHOULD_HAVE_UNIQUE_USERNAME.message):
        test_user["email"] == "differentmail@email.com"
        db_models.users.add_user(**test_user)

    with pytest.raises(DatabaseError, match=USER_SHOULD_HAVE_UNIQUE_EMAIL.message):
        test_user["username"] = "different_username"
        db_models.users.add_user(**test_user)

    # clean up
    db_connection.execute(delete(users).where(users.c.id == user_id))
    db_connection.commit()
