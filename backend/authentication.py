import jwt
from models import User
from fastapi import HTTPException


def encode_user(user_email: str):
    # Example payload data
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
    secret_key = config["Application"]["JWT_SECRET"]
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
        return decoded_token["user_email"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=410, detail="The jwt token has expired")
    except:
        raise HTTPException(status_code=400, detail="Misformed jwt token")


async def get_current_user(token: str):
    user_email = decode_jwt_token(token)
    user = User.objects(user_email=user_email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
