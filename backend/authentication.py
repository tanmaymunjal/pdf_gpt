import jwt
from backend.models import User
from fastapi import HTTPException
from backend.configuration import global_config
from datetime import datetime, timedelta, timezone


def encode_user(
    user_email: str,
    curr_date_time: int,
    secret_key: str = global_config["Application"]["JWT_SECRET"],
    exp: int = int(global_config["Application"]["JWT_EXPIRY_TIME"].strip()),
):
    """
    Generates a JSON Web Token (JWT) containing user information.

    Args:
        user_email (str): Email of the user to be encoded in the JWT.
        secret_key (str, optional): Secret key used for encoding the JWT. Defaults
            to the JWT_SECRET value from global configuration.
        exp (int, optional): Expiry time for the JWT in seconds. Defaults to the
            JWT_EXPIRY_TIME value from global configuration.

    Returns:
        str: JWT token to authenticate user.
    """
    payload = {
        "user_email": user_email,
        "exp": curr_date_time + timedelta(seconds=exp),
        "issued_at": int(curr_date_time.replace(tzinfo=timezone.utc).timestamp()),
    }

    # Generate JWT token
    token = jwt.encode(payload, secret_key, algorithm="HS256")

    return token


def decode_jwt_token(
    token, secret_key=global_config["Application"]["JWT_SECRET"]
) -> str:
    """
    Decodes a JSON Web Token (JWT) and extracts user_email from it.

    Args:
        token (str): JWT token to be decoded.
        secret_key (str, optional): Secret key used for decoding the JWT. Defaults
            to the JWT_SECRET value from global configuration.

    Returns:
        str: User email extracted from the decoded token.

    Raises:
        HTTPException: If the token is expired or malformed.
    """
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
        return decoded_token["user_email"], datetime.utcfromtimestamp(
            decoded_token["issued_at"]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=410, detail="The jwt token has expired")
    except Exception as err:
        raise HTTPException(status_code=400, detail="Malformed jwt token")


def get_current_user(
    token: str, secret_key=global_config["Application"]["JWT_SECRET"]
) -> User:
    """
    Retrieves the user corresponding to the given JWT token.

    Args:
        token (str): JWT token representing the user.
        secret_key (str, optional): Secret key used for decoding the JWT. Defaults
            to the JWT_SECRET value from global configuration.

    Returns:
        User: User object corresponding to the provided token.

    Raises:
        HTTPException: If the user corresponding to the token is not found.
    """
    user_email, issued_at = decode_jwt_token(token, secret_key)
    user = User.objects(user_email=user_email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.jwt_invalidated_at is not None and issued_at < user.jwt_invalidated_at:
        raise HTTPException(
            status_code=401, detail="This jwt token has already been invalidated"
        )
    return user


def get_current_user_secure_external(token: str):
    """
    Retrieves the user corresponding to the given JWT token.

    Args:
        token (str): JWT token representing the user.

    Returns:
        User: User object corresponding to the provided token.

    Raises:
        HTTPException: If the user corresponding to the token is not found.
    """
    return get_current_user(token)
