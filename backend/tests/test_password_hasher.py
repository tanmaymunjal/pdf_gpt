import pytest
from unittest.mock import patch, MagicMock
from backend.password_hasher import PasswordHasher
import string
import hashlib

# Mocking global_config
global_config = {"Application": {"SALT_LENGTH": "6"}}


@pytest.mark.parametrize(
    "length",
    [
        (2),
        (6),
        (10),
        (0),
    ],
)
def test_generate_random_string(length):
    random_string = PasswordHasher.generate_random_string(length)
    assert len(random_string) == length
    assert all(char in string.ascii_letters + string.digits for char in random_string)


@pytest.mark.parametrize(
    "input_string", ["test_string", "", "234567890-p[poiuygfdxcvghjko;l,kmjgv]"]
)
def test_hash_string(input_string):
    algorithms = ["sha256", "md5", "sha1"]
    for algorithm in algorithms:
        expected_hashed_string = hashlib.new(
            algorithm, input_string.encode()
        ).hexdigest()
        # testing for default behaviour
        if algorithm == "sha256":
            hashed_string = PasswordHasher.hash_string(input_string)
        else:
            hashed_string = PasswordHasher.hash_string(input_string, algorithm)
        assert hashed_string == expected_hashed_string


@pytest.mark.parametrize(
    "user_password, expected_salt, expected_hashed_password",
    [
        ("password123", "abcd1234", "hashed_password"),
        ("securepassword", "efgh5678", "another_hashed_password"),
        ("123456", "ijkl9012", "yet_another_hashed_password"),
    ],
)
def test_hash_password(user_password, expected_salt, expected_hashed_password):
    expected_hashed_password = "hashed_password"

    # Mocking generate_random_string method to return a fixed salt
    with patch.object(
        PasswordHasher, "generate_random_string", return_value=expected_salt
    ):
        # Mocking hash_string method
        with patch.object(
            PasswordHasher, "hash_string", return_value=expected_hashed_password
        ):
            password_hasher = PasswordHasher(user_password)
            salt, hashed_password = password_hasher.hash_password()
            assert salt == expected_salt
            assert hashed_password == expected_hashed_password
