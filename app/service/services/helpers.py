from http import HTTPStatus
from app.service.unit_of_work import AbstractUnitOfWork
from app.service.errors import ServiceError
from app.service.errors.messages import (
    USER_SHOULD_HAVE_UNIQUE_EMAIL,
    USER_SHOULD_HAVE_UNIQUE_USERNAME,
)


def check_unique_email_and_username(uow: AbstractUnitOfWork, email: str, username: str):
    exst_usr_email = uow.tables.users.get_users(email=email)
    exst_usr_username = uow.tables.users.get_users(username=username)

    if exst_usr_username and exst_usr_username[0]["username"] == username:
        raise ServiceError(
            HTTPStatus.BAD_REQUEST,
            USER_SHOULD_HAVE_UNIQUE_USERNAME.error_code,
            USER_SHOULD_HAVE_UNIQUE_USERNAME.message,
        )
    if exst_usr_email and exst_usr_email[0]["email"] == email:
        raise ServiceError(
            HTTPStatus.BAD_REQUEST,
            USER_SHOULD_HAVE_UNIQUE_EMAIL.error_code,
            USER_SHOULD_HAVE_UNIQUE_EMAIL.message,
        )
