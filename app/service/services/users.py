from http import HTTPStatus

from app.api.security.password import get_password_hash  # move to service utils ?

from app.service.unit_of_work import SqlAlchemyUnitOfWork
from app.service.errors import ServiceError, cm_error_handler
from app.service.errors.messages import (
    ROLE_DOES_NOT_EXIST,
    USER_DOES_NOT_EXIST,
)
from app.service.services.helpers import check_unique_email_and_username


def create_user(
    email,
    username,
    first_name,
    last_name,
    role_name,
    password,
):
    uow = SqlAlchemyUnitOfWork()
    with uow, cm_error_handler():
        role_data = uow.tables.roles.get_role(role_name=role_name)

        if role_data is None:

            raise ServiceError(
                HTTPStatus.BAD_REQUEST,
                ROLE_DOES_NOT_EXIST.error_code,
                ROLE_DOES_NOT_EXIST.message.format(role_name=role_name),
            )

        check_unique_email_and_username(uow, email, username)

        user_id = uow.tables.users.add_user(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            password_hash=get_password_hash(password),
            role_id=role_data["id"],
        )
        uow.commit()

        return user_id


def get_user(user_id):
    uow = SqlAlchemyUnitOfWork()
    with uow, cm_error_handler():
        user = uow.tables.users.get_user(user_id)
        if user is None:
            raise ServiceError(
                HTTPStatus.NOT_FOUND,
                USER_DOES_NOT_EXIST.error_code,
                USER_DOES_NOT_EXIST.message.format(user_id=user_id),
            )

        return user


def get_users(
    user_id,
    user_ids,
    first_name,
    last_name,
    email,
    username,
    role_name,
):
    uow = SqlAlchemyUnitOfWork()
    with uow, cm_error_handler():
        users = uow.tables.users.get_users(
            user_id,
            user_ids,
            first_name,
            last_name,
            email,
            username,
            role_name,
        )
        return users


def delete_users(user_id):
    uow = SqlAlchemyUnitOfWork()
    with uow, cm_error_handler():
        row_count = uow.tables.users.delete_user(user_id)
        uow.commit()
        if row_count == 0:
            raise ServiceError(
                HTTPStatus.NOT_FOUND,
                USER_DOES_NOT_EXIST.error_code,
                USER_DOES_NOT_EXIST.message,
            )
