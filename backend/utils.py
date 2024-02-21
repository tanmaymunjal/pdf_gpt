import random
import string
import hashlib
from configuration import global_config


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


def get_file_extension(filename: str) -> str:
    return filename.rsplit(".", maxsplit=1)[1]


def generate_otp(length: int = 6) -> str:
    otp = "".join(random.choices(string.digits, k=length))
    return otp


def generate_random_string(length: int = 6) -> str:
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choices(characters, k=length))
    return random_string


def send_otp_email(email: str, otp: str) -> None:
    """Send OTP to the provided email address."""
    # SMTP server configuration
    smtp_server = "smtp.example.com"
    smtp_port = 587  # Port for TLS encryption
    smtp_username = "your_smtp_username"
    smtp_password = "your_smtp_password"

    # Email content
    sender_email = "your_email@example.com"
    subject = "Your OTP"
    body = f"Your OTP is: {otp}"

    # Connect to SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)

    # Send email
    message = f"Subject: {subject}\n\n{body}"
    server.sendmail(sender_email, email, message)

    # Quit server
    server.quit()


def send_otp(email: str) -> bool:
    try:
        otp = generate_otp()
        send_otp_email(email, otp)
        return int(otp)
    except:
        return 0


def hash_password(user_password: str) -> str:
    salt = generate_random_string(k=global_config["Application"]["SALT_LENGTH"])
    new_user_password = salt + user_password
    user_hashed_password = hash_string(new_user_password)
    return salt, user_hashed_password


def verify_password(user_password: str,salt: str, user_hashed_password: str):
    return hash_string(salt + user_password) == user_hashed_password
