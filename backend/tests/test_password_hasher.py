import pytest
from unittest.mock import patch, MagicMock
from backend.configuration import global_config
from backend.password_hasher import PasswordHasher
import string

# Mocking global_config
global_config = {
    "Application": {
        "SALT_LENGTH": "6"
    }
}

def test_generate_random_string():
    length = 8
    random_string = PasswordHasher.generate_random_string(length)
    assert len(random_string) == length
    assert all(char in string.ascii_letters + string.digits for char in random_string)

def test_hash_string():
    input_string = "test_string"
    hashed_string = PasswordHasher.hash_string(input_string)
    assert isinstance(hashed_string, str)

def test_hash_password():
    user_password = "password123"
    salt_length = int(global_config["Application"]["SALT_LENGTH"])
    expected_salt = "abcd1234"
    expected_hashed_password = "hashed_password"
    
    # Mocking generate_random_string method to return a fixed salt
    with patch.object(PasswordHasher, "generate_random_string", return_value=expected_salt):
        # Mocking hash_string method
        with patch.object(PasswordHasher, "hash_string", return_value=expected_hashed_password):
            password_hasher = PasswordHasher(user_password)
            salt, hashed_password = password_hasher.hash_password()
            assert salt == expected_salt
            assert hashed_password == expected_hashed_password
