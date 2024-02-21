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
