import jwt
from models import User
from fastapi import HTTPException


def encode_user(user_email: str):
    """
    Generates a JSON Web Token (JWT) containing user information.

    Args:
        user_email (str): Email of the user to be encoded in the JWT.

    Returns:
        str: JWT token containing user_email payload.
    """
    payload = {
        "user_email": user.user_email,
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(seconds=config["Application"]["JWT_EXPIRY_TIME"]),
    }

    # Secret key to sign the token (keep it secure!)
    secret_key = config["Application"]["JWT_SECRET"]

    # Generate JWT token
    token = jwt.encode(payload, secret_key, algorithm="HS256")

    return token


def decode_jwt_token(token) -> str:
    """
    Decodes a JSON Web Token (JWT) and extracts user_email from it.

    Args:
        token (str): JWT token to be decoded.

    Returns:
        str: User email extracted from the decoded token.

    Raises:
        HTTPException: If the token is expired or malformed.
    """
    secret_key = config["Application"]["JWT_SECRET"]
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
        return decoded_token["user_email"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=410, detail="The jwt token has expired")
    except:
        raise HTTPException(status_code=400, detail="Misformed jwt token")


async def get_current_user(token: str):
    """
    Retrieves the user corresponding to the given JWT token.

    Args:
        token (str): JWT token representing the user.

    Returns:
        User: User object corresponding to the provided token.

    Raises:
        HTTPException: If the user corresponding to the token is not found.
    """
    user_email = decode_jwt_token(token)
    user = User.objects(user_email=user_email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
