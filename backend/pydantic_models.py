from pydantic import BaseModel


class CreateUser(BaseModel):
    user_name: str
    user_email: str
    user_password: str


class VerifyUser(BaseModel):
    user_email: str
    otp: int


class LoginUser(BaseModel):
    user_email: str
    user_password: str


class PasswordResetRequestModel(BaseModel):
    user_email: str
    user_otp: str
    user_new_password: str


class TaskCompletionNotification(BaseModel):
    notification_auth: str
    task_id: str
    generated_summary: None | str = None 
    task_status: str
