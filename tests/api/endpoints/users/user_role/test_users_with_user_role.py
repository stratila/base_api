"""
Successful users requests with user role
"""

from fastapi.testclient import TestClient
from pydantic import TypeAdapter
from app.api.security.authentication import JWTToken
from app.api.routers.literals import RETRIEVE_USER_URL
from app.api.schemas.users import UserReadSchema


def test_get_uses_itself(client_user: TestClient):
    """User can call GET /users on itself"""
    jwt_token = client_user.headers["Authorization"].replace("Bearer", "").strip()
    decoded_token_payload = JWTToken().decode(jwt_token)
    user_id = decoded_token_payload["access_token"]["user_id"]

    response = client_user.get(RETRIEVE_USER_URL.format(user_id=user_id))
    assert response.status_code == 200

    response_user = TypeAdapter(UserReadSchema).validate_python(response.json())

    assert response_user.id == user_id
