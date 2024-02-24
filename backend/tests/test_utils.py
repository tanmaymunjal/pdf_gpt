import pytest
from unittest.mock import MagicMock, patch
from backend.utils import (
    get_file_extension,
    verify_password,
    generate_otp,
)
from backend.password_hasher import PasswordHasher

# Mocking global_config
global_config = {
    "SendGrid": {"API_KEY": "fake_api_key", "SENDER_EMAIL": "test@example.com"},
    "Application": {"OTP_LENGTH": "6"},
}


@pytest.mark.parametrize(
    "filename, expected_extension",
    [
        ("example.txt", "txt"),
        ("image.jpg", "jpg"),
        ("script.js", "js"),
    ],
)
def test_get_file_extension(filename, expected_extension):
    assert get_file_extension(filename) == expected_extension


@pytest.mark.parametrize(
    "user_password, salt",
    [
        ("password", "salt"),
        ("user123", "uqysg123"),
        ("", "hey"),
    ],
)
def test_verify_password(user_password, salt):
    hashed_password = PasswordHasher.hash_string(salt + user_password)
    assert verify_password(user_password, salt, hashed_password)


@pytest.mark.parametrize(
    "k",
    [
        (2),
        (4),
        (6),
    ],
)
def test_generate_otp(k):
    otp = generate_otp(k)
    assert len(otp) == k
    assert otp.isdigit()


def test_generate_otp_default():
    otp = generate_otp(6)
    assert len(otp) == 6
    assert otp.isdigit()
