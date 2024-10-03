from http import HTTPStatus

from app.api.security.password import get_password_hash, verify_password_hash
from app.api.security.authentication import JWTToken


from app.service.unit_of_work import SqlAlchemyUnitOfWork
from app.service.errors import ServiceError, cm_error_handler
from app.service.services.helpers import check_unique_email_and_username
from app.service.errors.messages import (
    AUTH_WRONG_CREDENTIALS,
)


def signup(user_data):
    uow = SqlAlchemyUnitOfWork()
    with uow, cm_error_handler():
        user_data["password_hash"] = get_password_hash(user_data.pop("password"))
        user_data["role_id"] = uow.tables.roles.get_role(role_name="user").get(
            "id"
        )  # user role

        check_unique_email_and_username(uow, user_data["email"], user_data["username"])

        user_id = uow.tables.users.add_user(**user_data)

        role_with_permissions = uow.tables.roles.get_role_with_permissions(
            user_data["role_id"]
        )
        uow.commit()

    return JWTToken().encode(
        {"user_id": user_id, "role_with_permissions": role_with_permissions}
    )


def login(user_data):
    uow = SqlAlchemyUnitOfWork()
    with uow, cm_error_handler():
        u = uow.tables.users.get_hashed_password_by_email(user_data["email"])
        if u and verify_password_hash(user_data["password"], u["password_hash"]):
            role_with_permissions = uow.tables.roles.get_role_with_permissions(
                u["role_id"]
            )
            return JWTToken().encode(
                {"user_id": u["id"], "role_with_permissions": role_with_permissions}
            )
    raise ServiceError(
        HTTPStatus.UNAUTHORIZED,
        AUTH_WRONG_CREDENTIALS.error_code,
        AUTH_WRONG_CREDENTIALS.message,
    )
