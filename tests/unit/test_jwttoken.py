import time
import pytest
from unittest import mock
from app.api.security.authentication import (
    JWTToken,
)
import jwt


@pytest.fixture
def mock_settings():
    with mock.patch("app.api.security.authentication.settings") as settings_mock:
        settings_mock.access_token_expire_minutes = 15
        settings_mock.jwt_algorithm = "HS256"
        settings_mock.jwt_secret_key = "supersecretkey"
        yield settings_mock


def test_encode_token(mock_settings):
    payload = {
        "user_id": 1,
        "role_with_permissions": {"permissions": ["read", "write"]},
    }

    expected_token = "fake_encoded_token"
    with mock.patch(
        "app.api.security.authentication.jwt.encode", return_value=expected_token
    ):
        token_response = JWTToken.encode(payload)

        # Check the structure of the returned response
        assert "access_token" in token_response
        assert token_response["access_token"] == expected_token

        # Ensure the payload includes the correct permissions and expiry
        jwt.encode.assert_called_once_with(
            {
                "user_id": payload["user_id"],
                "permissions": payload["role_with_permissions"]["permissions"],
                "expires": mock.ANY,  # We don't need to check the exact timestamp
            },
            mock_settings.jwt_secret_key,
            algorithm=mock_settings.jwt_algorithm,
        )


def test_decode_valid_token(mock_settings):
    valid_token = "valid_token"
    payload = {
        "user_id": 1,
        "permissions": ["read", "write"],
        "expires": time.time() + 600,  # Token is still valid
    }

    with mock.patch("app.api.security.authentication.jwt.decode", return_value=payload):
        token_response = JWTToken.decode(valid_token)

        assert "access_token" in token_response
        assert token_response["access_token"] == payload

        jwt.decode.assert_called_once_with(
            valid_token,
            mock_settings.jwt_secret_key,
            algorithms=[mock_settings.jwt_algorithm],
        )


def test_decode_expired_token(mock_settings):
    expired_token = "expired_token"
    expired_payload = {
        "user_id": 1,
        "permissions": ["read", "write"],
        "expires": time.time() - 600,  # Token has expired
    }

    with mock.patch(
        "app.api.security.authentication.jwt.decode", return_value=expired_payload
    ):
        token_response = JWTToken.decode(expired_token)

        assert token_response is None


def test_decode_invalid_token(mock_settings):
    invalid_token = "invalid_token"

    with mock.patch(
        "app.api.security.authentication.jwt.decode",
        side_effect=jwt.PyJWTError("Invalid token"),
    ):
        token_response = JWTToken.decode(invalid_token)

        assert token_response == {}
