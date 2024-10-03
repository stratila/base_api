from typing import List

from fastapi import APIRouter, Depends, Query

from app.api.routers.literals import (
    CREATE_USER_URL,
    RETRIEVE_USER_URL,
    LIST_USERS_URL,
    DELETE_USER_URL,
)
from app.api.security.authorization import Permissions
from app.api.schemas.users import (
    UserCreateSchema,
    UserReadSchema,
)

from app.service.services.users import (
    create_user,
    get_user,
    get_users,
    delete_users,
)


router = APIRouter()


@router.post(
    CREATE_USER_URL,
    response_model=UserReadSchema,
    status_code=201,
    dependencies=[Depends(Permissions("write_all_users"))],
    # responses={400: {"error_code": 0, "model": Model()}},
)
def user_post(user: UserCreateSchema):
    user_data = user.model_dump()
    user_id = create_user(**user_data)
    result_data = {"id": user_id, **user_data}
    # passing data to UserReadSchema will ignore redundant fields
    return UserReadSchema(**result_data)


@router.get(
    RETRIEVE_USER_URL,
    response_model=UserReadSchema,
    status_code=200,
    dependencies=[Depends(Permissions("read_all_users", "read_self_user"))],
)
def user_get(user_id: int):
    return get_user(user_id)


@router.get(
    LIST_USERS_URL,
    response_model=List[UserReadSchema],
    dependencies=[Depends(Permissions("read_all_users"))],
)
def users_get(
    user_id: int | None = Query(default=None),
    user_ids: list[int] | None = Query(default=None),
    first_name: str | None = Query(default=None),
    last_name: str | None = Query(default=None),
    username: str | None = Query(default=None),
    email: str | None = Query(default=None),
    role_name: str | None = Query(default=None),
):
    return get_users(
        user_id,
        user_ids,
        first_name,
        last_name,
        email,
        username,
        role_name,
    )


@router.delete(
    DELETE_USER_URL,
    status_code=204,
    dependencies=[Depends(Permissions("write_all_users"))],
)
def user_delete(user_id: int):
    delete_users(user_id)
