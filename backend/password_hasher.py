import string
import hashlib
from configuration import global_config
import random


class PasswordHasher:
    """
    Utility class to hash passwords and generate random strings for salting.

    This class provides methods to generate a random string, hash a string using a specified algorithm,
    and hash a user password with salt.

    Attributes:
        user_password (str): The user's password to be hashed.
    """

    def __init__(self, user_password):
        """
        Initialize the PasswordHasher instance with the user's password.

        Args:
            user_password (str): The user's password to be hashed.
        """
        self.user_password = user_password

    @staticmethod
    def generate_random_string(length: int = 6) -> str:
        """
        Generate a random alpha-numeric string of specified length.

        Args:
            length (int): The length of the random string (default is 6).

        Returns:
            str: The generated random string.
        """
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
        """
        Hash the user's password with salt.

        Returns:
            tuple: A tuple containing the generated salt and the hashed password.
        """
        salt = PasswordHasher.generate_random_string(
            length=int(global_config["Application"]["SALT_LENGTH"])
        )
        new_user_password = salt + self.user_password
        user_hashed_password = PasswordHasher.hash_string(new_user_password)
        return salt, user_hashed_password
