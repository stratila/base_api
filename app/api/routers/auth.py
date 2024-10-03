from fastapi import APIRouter

from app.api.schemas.auth import (
    UserLoginSchema,
    UserSignUpSchema,
)
from app.api.routers.literals import (
    SIGN_UP_URL,
    LOG_IN_URL,
)

from app.service.services.auth import (
    signup as signup_service,
    login as login_service,
)


router = APIRouter()


@router.post(SIGN_UP_URL)
def signup(user: UserSignUpSchema):
    return signup_service(user.model_dump())


@router.post(LOG_IN_URL)
def login(user: UserLoginSchema):
    return login_service(user.model_dump())
