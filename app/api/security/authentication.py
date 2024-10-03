import logging
import jwt
import time

from fastapi import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


from app.api.errors import AuthInvalidScheme, AuthInvalidToken, AuthInvalidCode
from app.config import settings


log = logging.getLogger(__name__)


class JWTToken:
    """JWT token generator and decoder."""

    @staticmethod
    def encode(payload: dict):  # TODO consider to user Pydantic model instead of dict
        access_token_expire_minutes = settings.access_token_expire_minutes
        jwt_algorithm = settings.jwt_algorithm
        jwt_secret_key = settings.jwt_secret_key

        payload = {
            "user_id": payload["user_id"],
            # "role_name": user["role_name"],  # unused since we're checking permissions
            "permissions": payload["role_with_permissions"]["permissions"],
            "expires": time.time() + access_token_expire_minutes * 60,
        }
        token = jwt.encode(payload, jwt_secret_key, algorithm=jwt_algorithm)
        return JWTToken()._token_response(token)

    @staticmethod
    def decode(token: str):

        jwt_algorithm = settings.jwt_algorithm
        jwt_secret_key = settings.jwt_secret_key
        try:
            decoded_token = jwt.decode(
                token, jwt_secret_key, algorithms=[jwt_algorithm]
            )
            return (
                JWTToken()._token_response(decoded_token)
                if decoded_token["expires"] > time.time()
                else None
            )
        except jwt.PyJWTError as e:
            log.error(f"pyjwt error: {e}")
            return {}

    @staticmethod
    def _token_response(token: str):
        return {"access_token": token}


class JWTBearer(HTTPBearer):
    """A JWT bearer dependency class that validates the JWT token."""

    def __init__(self, auto_error: bool = True):
        self.jwt_token = JWTToken()
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme.lower() == "bearer":
                raise AuthInvalidScheme()
            if not self.validate_jwt(credentials.credentials):
                raise AuthInvalidToken()
            return credentials.credentials
        else:
            raise AuthInvalidCode()

    def validate_jwt(self, token: str) -> bool:
        is_token_valid: bool = False
        payload = self.jwt_token.decode(token=token)
        log.info(f"validating {payload}")
        if payload:
            is_token_valid = True
        return is_token_valid
