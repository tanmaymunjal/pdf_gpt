from fastapi import FastAPI, HTTPException, UploadFile
from typing import Annotated
import uvicorn
from io import StringIO
from parser import ParserFactory
from summarise_gpt import summarise_doc
from utils import get_file_extension, send_otp, hash_password, verify_password
from fastapi.middleware.cors import CORSMiddleware
from pydantic_models import CreateUser, VerifyUser, LoginUser
from configuration import global_config
from models import User, PotentialUser
from datetime import datetime, timedelta
import mongoengine

# Create an instance of the FastAPI class
app = FastAPI()

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
    user = User.objects(user_email=user.user_email).first()
    if user is not None:
        raise HTTPException(status_code=400, detail="User already exists!")
    otp = send_otp(user.user_email)
    if otp != 0:
        salt, user_hashed_password = (hash_password(user.user_password),)
        potential_user = PotentialUser(
            user_email=user.user_email,
            user_name=user.user_name,
            user_hashed_password=user_hashed_password,
            user_salt=user_salt,
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
    return {"message": "User created successfully", "user_email": user.user_email}


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
async def login_user(login_user:LoginUser):
    user = User.objects(user_email=login_user.user_email).first()
    if user is None:
        raise HTTPException(status_code=404,detail="User not found")
    if not verify_password(login_user.user_password,user.salt,user.user_hashed_password):
        raise HTTPException(status_code=401,detail="Incorrect Password")
    return {"message":"User logged in"}

    
@app.post("/generate_summary")
async def generate_summary(file: UploadFile):
    file_extension = get_file_extension(file.filename)
    source_stream = await file.read()
    try:
        parser = ParserFactory(source_stream, file_extension).build()
    except NotImplementedError:
        raise HTTPException(
            status_code=400, detail="Please send a file with valid supported extension"
        )
    read_docs = parser.read()
    return {"summary": summarise_doc(read_docs)}


if __name__ == "__main__":
    uvicorn.run("mainapi:app", reload=True)
