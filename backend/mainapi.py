from fastapi import FastAPI, HTTPException, UploadFile, Depends
from typing import Annotated
import uvicorn
from io import StringIO
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
    TaskCompletionNotification,
)
from configuration import global_config
from models import User, PotentialUser, PasswordRecoveryRequest, UserTasks
from datetime import datetime, timedelta
from password_hasher import PasswordHasher
from middleware import custom_middleware
from celery_app import generate_summary
from parser import ParserFactory
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
    """
    Health check endpoint to ensure the service is up and running.
    """
    return {"message": "Service is up!"}


@app.post("/user/register/password")
async def register_user(user: CreateUser):
    """
    Endpoint to register a new user with email and password.

    Args:
        user (CreateUser): User data including email and password.

    Returns:
        dict: Message indicating OTP sent and expiry time.
    """
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
    """
    Endpoint to verify user's OTP for registration.

    Args:
        user_verification (VerifyUser): User data including email and OTP.

    Returns:
        dict: Message indicating successful user creation and JWT token.
    """
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
    """
    Endpoint to resend OTP for user registration.

    Args:
        user_email (str): Email of the user requesting OTP resend.

    Returns:
        dict: Message indicating OTP sent and expiry time.
    """
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
    """
    Endpoint for user login using email and password.

    Args:
        login_user (LoginUser): User data including email and password.

    Returns:
        dict: Message indicating successful login and JWT token.
    """
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
    """
    Endpoint to generate a refresh token for the current user.

    Args:
        current_user (User): Current user obtained from JWT token.

    Returns:
        dict: Message indicating successful refresh token creation.
    """
    return {
        "message": "Refresh token created",
        "refresh_token": encode_user(current_user.user_email),
    }


@app.post("/user/auth/forgot_password")
async def reset_password_request(user_email: str):
    """
    Endpoint to request password reset OTP.

    Args:
        user_email (str): Email of the user requesting password reset.

    Returns:
        dict: Message indicating OTP sent and expiry time.
    """
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
    """
    Endpoint to reset user password using OTP verification.

    Args:
        password_reset_request (PasswordResetRequest): Data including email, OTP, and new password.

    Returns:
        dict: Message indicating successful password reset.
    """
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
    """
    This endpoint allows authenticated users to upload a file, which will be parsed and summarized using GPT.
    The summary generation task is enqueued in background using Celery, and the task ID is
    returned to the user for tracking.

    Args:
        current_user (User): The current authenticated user obtained from JWT token.
        file (UploadFile): The file to be summarized.

    Returns:
        dict: A message indicating successful task enqueuing and the task ID.

    Raises:
        HTTPException(402): If the user has exhausted the free summary generations limit.
        HTTPException(400): If the uploaded file type is not supported.

    Note:
        - Supported file types for summary generation include .txt.
        - The user's available free summary generations are tracked, and they may need to upgrade their
          plan if the limit is exceeded.
    """
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
            status_code=400, detail="Please enter a valid supported file type"
        )
    read_docs = parser.read()
    task_id = generate_summary.delay(read_docs).task_id
    user_task = Task(
        user_email=current_user.user_email,
        user_task_id=task_id,
        user_read_docs=read_docs,
        user_task_completed=False,
        user_generated_summary=None,
    )
    user_task.save()
    return {
        "message": "Your task for summary generation has been enqued",
        "task_id": task_id,
    }


@app.post("/notify/task")
async def notify_task(notify_task: TaskCompletionNotification):
    """
    Endpoint to notify task completion by celery worker. Needs internal API key to authorise

    Args:
        notify_task (TaskCompletionNotification): Notification data including task ID and completion status.

    Returns:
        dict: Message indicating successful task completion notification.
    """
    if notify_task.notification_auth != global_config["Notification"]["API_KEY"]:
        raise HTTPException(status_code=401, detail="Notification request unauthorised")
    task = Task.objects(task_id=notify_task.task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task.update(
        set__user_generated_summary=notify_task.generated_summary,
        set__user_task_status=notify_task.task_status,
        set__user_task_completed=datetime.now(),
    )
    return {"message": "Task completed"}


@app.get("/user/get_summary")
async def get_summary(
    current_user: Annotated[User, Depends(get_current_user)], task_id: str
):
    """
    Endpoint to get summary for a specific task if task is completed.

    Args:
        current_user (User): Current user obtained from JWT token.
        task_id (str): ID of the task to get summary for.

    Returns:
        dict: Summary of the specified task.
    """
    task = Task.objects(user_email=current_user.user_email, task_id=task_id).first()
    if task is None:
        raise HTTPException(
            status_code=401,
            detail="The task can only be checked by the user to which the task belongs",
        )
    if task.user_task_status == "PENDING":
        return {"message": "Task is still running, please wait", "status": "PENDING"}
    if task.user_task_status == "FAILED":
        return {
            "message": "Task has failed, kindly resend the task or contact the team for further support",
            "status": "FAILED",
        }
    return {"message": "Task completed succesfully", "result": task.user_task_generated}


@app.get("/user/pending_tasks")
async def pending_tasks(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Endpoint to get all pending tasks for the current user.

    Args:
        current_user (User): Current user obtained from JWT token.

    Returns:
        list: List of pending tasks for the current user.
    """
    tasks = Task.objects(user_email=current_user.user_email, user_task_status="PENDING")
    tasks_list = [task.to_mongo().to_dict() for task in tasks]
    return {"pending_tasks": tasks_list}


@app.get("/user/completed_tasks")
async def get_all_completed_tasks(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Endpoint to get all completed tasks for the current user.

    Args:
        current_user (User): Current user obtained from JWT token.

    Returns:
        list: List of completed tasks for the current user.
    """

    tasks = Task.objects(
        user_email=current_user.user_email, user_task_status__in=["SUCCESS", "FAILED"]
    )
    tasks_list = [task.to_mongo().to_dict() for task in tasks]
    return {"completed_tasks": tasks_list}


@app.post("/user/update_key")
async def update_openai_key(update_api_key: UpdateAPIKey):
    """
    Endpoint to update OpenAI API key for the current user.

    Args:
        update_api_key (UpdateAPIKey): Data including user email and new OpenAI API key.

    Returns:
        dict: Message indicating successful update of OpenAI API key.
    """
    user = User.objects(user_email=update_api_key.user_email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.update(set__user_openai_key=update_api_key.openai_api_key)
    return {"message": "User openai key updated successfully"}


if __name__ == "__main__":
    uvicorn.run("mainapi:app", reload=True)
