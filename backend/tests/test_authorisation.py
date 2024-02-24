import pytest
from datetime import datetime, timedelta
import jwt
from backend.authentication import encode_user, decode_jwt_token, get_current_user
from backend.configuration import global_config
from unittest.mock import MagicMock
from fastapi import HTTPException
from freezegun import freeze_time
from backend.models import User


@pytest.mark.parametrize(
    "user_email, jwt_secret, jwt_expiry",
    [
        ("user1@example.com", "secret_key_1", 3600),
        (
            "user2@example.com",
            "secret_key_2",
            1800,
        ),
        (
            "user3@example.com",
            "secret_key_3",
            7200,
        ),
        ("", "secret_key_4", 3600),
        ("user4@example.com", "", 3600),
    ],
)
@freeze_time("2024-01-01")
def test_encode_user(user_email, jwt_secret, jwt_expiry):
    current_time = datetime.utcnow()
    token = encode_user(user_email, jwt_secret, jwt_expiry)
    decoded_token = jwt.decode(token, jwt_secret, algorithms=["HS256"])
    assert decoded_token["user_email"] == user_email
    assert decoded_token["exp"] == int(
        datetime.timestamp(current_time + timedelta(seconds=jwt_expiry))
    )


@pytest.mark.parametrize(
    "user_email, jwt_secret, jwt_expiry",
    [
        ("user1@example.com", "secret_key_1", 3600),
        (
            "user2@example.com",
            "secret_key_2",
            1800,
        ),
        (
            "user3@example.com",
            "secret_key_3",
            7200,
        ),
        ("", "secret_key_4", 3600),
        ("user4@example.com", "", 3600),
    ],
)
@freeze_time("2024-01-01")
def test_decode_jwt_token(user_email, jwt_secret, jwt_expiry):
    # Test data
    token = jwt.encode({"user_email": user_email}, jwt_secret, algorithm="HS256")

    # Test method
    decoded_user_email = decode_jwt_token(token, jwt_secret)

    # Assertion
    assert user_email == decoded_user_email

    # Test expired token
    expired_token = jwt.encode(
        {
            "user_email": user_email,
            "exp": datetime.utcnow() - timedelta(seconds=jwt_expiry),
        },
        jwt_secret,
        algorithm="HS256",
    )
    with pytest.raises(HTTPException) as excinfo:
        decode_jwt_token(expired_token, jwt_secret)
    assert excinfo.value.status_code == 410

    # Test malformed token
    malformed_token = "malformed_token"
    with pytest.raises(HTTPException) as excinfo:
        decode_jwt_token(malformed_token)
    assert excinfo.value.status_code == 400


@pytest.mark.parametrize(
    "user_email, jwt_secret, jwt_expiry",
    [
        ("user1@example.com", "secret_key_1", 3600),
        (
            "user2@example.com",
            "secret_key_2",
            1800,
        ),
        (
            "user3@example.com",
            "secret_key_3",
            7200,
        ),
        ("", "secret_key_4", 3600),
        ("user4@example.com", "", 3600),
    ],
)
@freeze_time("2024-01-01")
def test_get_current_user(user_email, jwt_secret, jwt_expiry):
    # Mock User.objects
    user_mock = MagicMock()
    user_mock.first.return_value = User(user_email=user_email)
    User.objects = MagicMock(return_value=user_mock)

    # Test data
    token = encode_user(user_email, jwt_secret, jwt_expiry)

    # Test method
    user = get_current_user(token, jwt_secret)

    # Assertions
    assert user.user_email == user_email

    # Test user not found
    user_mock.first.return_value = None
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(token, jwt_secret)
    assert excinfo.value.status_code == 404
