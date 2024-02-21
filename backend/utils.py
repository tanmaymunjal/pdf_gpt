import random
import string


def get_file_extension(filename: str) -> str:
    return filename.rsplit(".", maxsplit=1)[1]


def verify_password(user_password: str, salt: str, user_hashed_password: str):
    return hash_string(salt + user_password) == user_hashed_password


def generate_otp(length: int = 6) -> str:
    otp = "".join(random.choices(string.digits, k=length))
    return otp


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
