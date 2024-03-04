import random
import string
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from backend.configuration import global_config
from backend.password_hasher import PasswordHasher


def get_file_extension(filename: str) -> str:
    """
    Get the file extension from a filename.

    Args:
        filename (str): The name of the file.

    Returns:
        str: The file extension.
    """
    return filename.rsplit(".", maxsplit=1)[1]


def verify_password(user_password: str, salt: str, user_hashed_password: str):
    """
    Verify a password against its hashed value using a salt.

    Args:
        user_password (str): The password to verify.
        salt (str): The salt used for hashing.
        user_hashed_password (str): The hashed password.

    Returns:
        bool: True if the password is verified, False otherwise.
    """
    return PasswordHasher.hash_string(salt + user_password) == user_hashed_password


def generate_otp(length: int = 6) -> str:
    """
    Generate a random OTP (One-Time Password) of specified length.

    Args:
        length (int): The length of the OTP (default is 6).

    Returns:
        str: The generated OTP.
    """
    otp = "".join(random.choices(string.digits, k=length))
    return otp


def send_email(email: str, otp: str) -> None:
    """
    Send a given OTP (One-Time Password) to the provided email address.
    Uses the sendgrid service to do so

    Args:
        email (str): The recipient's email address.
        otp (str): The OTP to send.

    Returns:
        bool: True if the OTP is sent successfully, False otherwise.
    """
    # SendGrid API key
    SENDGRID_API_KEY = global_config["SendGrid"]["API_KEY"]

    # Email content
    sender_email = global_config["SendGrid"]["SENDER_EMAIL"]
    subject = "Your OTP"
    body = f"Your OTP is: {otp}"

    message = Mail(
        from_email=sender_email,
        to_emails=email,
        subject=subject,
        plain_text_content=body,
    )

    # Initialize SendGrid client
    sg = SendGridAPIClient(SENDGRID_API_KEY)

    # Send email
    response = sg.send(message)
    if response.status_code == 202:
        return otp
    else:
        raise Exception("Error in sending email")


def send_otp(email: str) -> bool:
    """
    Generate and send an OTP (One-Time Password) to the provided email address.

    Args:
        email (str): The recipient's email address.

    Returns:
        bool: True if the OTP is sent successfully, False otherwise.
    """
    try:
        otp = generate_otp(int(global_config["Application"]["OTP_LENGTH"].strip()))
        send_email(email, otp)
        return int(otp)
    except Exception as err:
        return 0
