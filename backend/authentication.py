import jwt
from backend.models import User
from fastapi import HTTPException
from backend.configuration import global_config
from datetime import datetime, timedelta


def encode_user(
    user_email: str,
    secret_key: str = global_config["Application"]["JWT_SECRET"],
    exp=int(global_config["Application"]["JWT_EXPIRY_TIME"].strip()),
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
        "exp": datetime.utcnow() + timedelta(seconds=exp),
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
        return decoded_token["user_email"]
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
    user_email = decode_jwt_token(token, secret_key)
    user = User.objects(user_email=user_email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
