import string
import hashlib
from configuration import global_config


class PasswordHasher:
    def __init__(self, user_password):
        self.user_password = self.user_password

    @staticmethod
    def generate_random_string(length: int = 6) -> str:
        characters = string.ascii_letters + string.digits
        random_string = "".join(random.choices(characters, k=length))
        return random_string

    @staticmethod
    def hash_string(input_string, algorithm="sha256"):
        """
        Hashes a string using the specified algorithm.

        Args:
            input_string (str): The string to be hashed.
            algorithm (str): The hashing algorithm to use (default is "sha256").

        Returns:
            str: The hashed string.
        """
        # Encode the string to bytes
        string_bytes = input_string.encode("utf-8")

        # Create a new hash object
        hash_object = hashlib.new(algorithm)

        # Update the hash object with the bytes of the input string
        hash_object.update(string_bytes)

        # Get the hexadecimal representation of the hash
        hashed_string = hash_object.hexdigest()

        return hashed_string

    def hash_password(self) -> str:
        salt = PasswordHasher.generate_random_string(
            k=global_config["Application"]["SALT_LENGTH"]
        )
        new_user_password = salt + self.user_password
        user_hashed_password = PasswordHasher.hash_string(new_user_password)
        return salt, user_hashed_password
