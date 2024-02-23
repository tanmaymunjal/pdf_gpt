from fastapi import FastAPI, HTTPException, UploadFile, Depends
from typing import Annotated
import uvicorn
from io import StringIO
from parser import ParserFactory
from summarise_gpt import GPTSummarisation
from utils import (
    get_file_extension,
    send_otp,
    verify_password,
)
from authentication import encode_user, decode_jwt_token, get_current_user
from fastapi.middleware.cors import CORSMiddleware
from pydantic_models import (
    CreateUser,
    VerifyUser,
    LoginUser,
    PasswordResetRequest,
    UpdateAPIKey,
)
from configuration import global_config
from models import User, PotentialUser, PasswordRecoveryRequest
from datetime import datetime, timedelta
from password_hasher import PasswordHasher
from middleware import custom_middleware
import mongoengine

# Create an instance of the FastAPI class
app = FastAPI()
# set middleware
app.middleware("http")(custom_middleware)
app.middleware("https")(custom_middleware)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

mongoengine.connect(global_config["Application"]["DB"])


@app.get("/")
async def sanity_check():
    return {"message": "Service is up!"}


@app.post("/user/register/password")
async def register_user(user: CreateUser):
    current_user = User.objects(user_email=user.user_email).first()
    if current_user is not None:
        raise HTTPException(status_code=400, detail="User already exists!")
    otp = send_otp(user.user_email)
    if otp != 0:
        password_hasher = PasswordHasher(user.user_password)
        salt, user_hashed_password = password_hasher.hash_password()
        potential_user = PotentialUser(
            user_email=user.user_email,
            user_name=user.user_name,
            user_hashed_password=user_hashed_password,
            user_salt=salt,
            user_otp_sent=otp,
        )
        potential_user.save()
        return {
            "message": "OTP verification sent successfully!",
            "expiry_in": global_config["Application"]["OTP_EXPIRY_TIME"],
        }
    raise HTTPException(status_code=500, detail="OTP sending service returned an error")


@app.post("/user/register/verify")
async def verify_user_otp(user_verification: VerifyUser):
    potential_user = PotentialUser.objects(
        user_email=user_verification.user_email
    ).first()
    if potential_user is None:
        raise HTTPException(
            status_code=404, detail="The user to be verified was not found"
        )
    is_otp_correct = potential_user.user_otp_sent == user_verification.otp
    if not is_otp_correct:
        raise HTTPException(status_code=401, detail="The provided otp is not correct")
    is_otp_valid = (
        potential_user.user_otp_sent_at
        + timedelta(seconds=global_config["Application"]["OTP_EXPIRY_TIME"])
        >= datetime.now()
    )
    if not is_otp_valid:
        raise HTTPException(
            status_code=410,
            detail="The provided otp has been expired, please use a new one",
        )
    user = User(
        user_email=potential_user.user_email,
        user_name=potential_user.user_name,
        user_hashed_password=potential_user.user_hashed_password,
        user_salt=potential_user.user_salt,
    )
    user.save()
    return {
        "message": "User created successfully",
        "jwt_token": encode_user(user.user_email),
    }


@app.post("/user/register/resend_otp")
async def resend_otp(user_email: str):
    potential_user = PotentialUser.objects(
        user_email=user_verification.user_email
    ).first()
    if potential_user is None:
        raise HTTPException(
            status_code=404, detail="The user to have otp resent was not found"
        )
    otp = send_otp(user.user_email)
    if otp != 0:
        potential_user.update(
            set__user_otp_sent=otp, set__user_otp_sent_at=datetime.now()
        )
        return {
            "message": "OTP verification sent successfully!",
            "expiry_in": global_config["Application"]["OTP_EXPIRY_TIME"],
        }
    raise HTTPException(status_code=500, detail="OTP sending service returned an error")


@app.post("/user/login/password")
async def login_user(login_user: LoginUser):
    user = User.objects(user_email=login_user.user_email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(
        login_user.user_password, user.salt, user.user_hashed_password
    ):
        raise HTTPException(status_code=401, detail="Incorrect Password")
    return {"message": "User logged in", "jwt_token": encode_user(user.user_email)}


@app.post("/user/auth/refresh_token")
async def get_refresh_token(current_user: Annotated[User, Depends(get_current_user)]):
    return {
        "message": "Refresh token created",
        "refresh_token": encode_user(current_user.user_email),
    }


@app.post("/user/auth/forgot_password")
async def reset_password_request(user_email: str):
    user = User.objects(user_email=login_user.user_email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    otp = send_otp(user.user_email)
    if otp != 0:
        password_recovery_request = PasswordRecoveryRequest(
            otp=otp,
            otp_expirty=datetime.now()
            + timedelta(seconds=global_config["Application"]["OTP_EXPIRY_TIME"]),
        )
        user.update(set__user_password_recovery_request=password_recovery_requestW)
        return {
            "message": "OTP verification sent successfully!",
            "expiry_in": global_config["Application"]["OTP_EXPIRY_TIME"],
        }
    raise HTTPException(status_code=500, detail="OTP sending service returned an error")


@app.post("/user/auth/reset_password")
async def reset_password(password_reset_request: PasswordResetRequest):
    user = User.objects(user_email=password_reset_request.user_email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    password_recovery_data = user.user_password_recovery_request
    if password_recovery_data is None:
        raise HTTPException(status_code=404, detail="No password reset request found")
    sent_otp = password_recovery_data.otp
    otp_expiry = password_recovery_data.otp_expirty
    if datetime.now() > otp_expirty:
        raise HTTPException(
            status_code=410,
            detail="The provided otp has been expired, please use a new one",
        )
    if sent_otp != password_reset_request.user_otp:
        raise HTTPException(status_code=401, detail="Incorrect otp sent")
    password_hasher = PasswordHasher(password_reset_request.user_new_password)
    salt, user_hashed_password = password_hasher.hash_password()
    user.update(
        set__user_hashed_password=user_hashed_password,
        set__user_salt=salt,
        password_reset_request=None,
    )
    return {
        "message": "Password updated successfully",
        "jwt": encode_user(user.user_email),
    }


@app.post("/generate_summary")
async def generate_summary(
    current_user: Annotated[User, Depends(get_current_user)], file: UploadFile
):
    file_extension = get_file_extension(file.filename)
    source_stream = await file.read()
    if current_user.user_openai_key is None:
        gpt_summariser = GPTSummarisation()
        current_user.update(set__user_docs_capacity=current_user.user_docs_capacity - 1)
        if current_user.user_docs_capacity < 0:
            raise HTTPException(
                status_code=402, detail="You have utilised all free summary generations"
            )
    else:
        gpt_summariser = GPTSummarisation(api_key=current_user.user_openai_key)
    try:
        parser = ParserFactory(source_stream, file_extension).build()
    except NotImplementedError:
        raise HTTPException(
            status_code=400, detail="Please send a file with valid supported extension"
        )
    read_docs = parser.read()
    return {"summary": gpt_summariser.summarise_doc(read_docs)}


@app.post("/user/update_key")
async def update_openai_key(update_api_key: UpdateAPIKey):
    user = User.objects(user_email=update_api_key.user_email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.update(set__user_openai_key=update_api_key.openai_api_key)
    return {"message": "User openai key updated successfully"}


if __name__ == "__main__":
    uvicorn.run("mainapi:app", reload=True)
