import random
import string
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from configuration import global_config


def get_file_extension(filename: str) -> str:
    return filename.rsplit(".", maxsplit=1)[1]


def verify_password(user_password: str, salt: str, user_hashed_password: str):
    return hash_string(salt + user_password) == user_hashed_password


def generate_otp(length: int = 6) -> str:
    otp = "".join(random.choices(string.digits, k=length))
    return otp


def send_otp_email(email: str, otp: str) -> None:
    """Send OTP to the provided email address."""
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

    try:
        # Initialize SendGrid client
        sg = SendGridAPIClient(SENDGRID_API_KEY)

        # Send email
        response = sg.send(message)
        if response.status_code == 202:
            return otp
        else:
            return 0
    except Exception as e:
        return 0


def send_otp(email: str) -> bool:
    try:
        otp = generate_otp()
        send_otp_email(email, otp)
        return int(otp)
    except:
        return 0
