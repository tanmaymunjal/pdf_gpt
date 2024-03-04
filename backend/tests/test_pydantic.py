"""The goal is this is that if I dont end up
   doing integration tests from frontend due to time constraints,9
   anytime, anyone changes the frontend api interface, they get
   a failing test to notify them
"""

import pytest
from pydantic import ValidationError
from backend.pydantic_models import (
    CreateUser,
    VerifyUser,
    LoginUser,
    PasswordResetRequestModel,
    TaskCompletionNotification,
)


def test_create_user_model():
    # Valid data
    user_data = {
        "user_name": "John Doe",
        "user_email": "john@example.com",
        "user_password": "password123",
    }
    assert CreateUser(**user_data)

    # Invalid data
    invalid_user_data = {"user_name": "John Doe", "user_password": "password123"}
    with pytest.raises(ValidationError):
        CreateUser(**invalid_user_data)


def test_verify_user_model():
    # Valid data
    verify_data = {"user_email": "john@example.com", "otp": 123456}
    assert VerifyUser(**verify_data)

    # Invalid data
    invalid_verify_data = {"user_email": "john@example.com"}
    with pytest.raises(ValidationError):
        VerifyUser(**invalid_verify_data)


def test_login_user_model():
    # Valid data
    login_data = {"user_email": "john@example.com", "user_password": "password123"}
    assert LoginUser(**login_data)

    # Invalid data
    invalid_login_data = {"user_email": "john@example.com"}
    with pytest.raises(ValidationError):
        LoginUser(**invalid_login_data)


def test_password_reset_request_model():
    # Valid data
    reset_data = {
        "user_email": "john@example.com",
        "user_otp": "123456",
        "user_new_password": "new_password123",
    }
    assert PasswordResetRequestModel(**reset_data)

    # Invalid data
    invalid_reset_data = {
        "user_email": "john@example.com",
        "user_new_password": "new_password123",
    }
    with pytest.raises(ValidationError):
        PasswordResetRequestModel(**invalid_reset_data)


def test_task_completion_notification_model():
    # Valid data
    notification_data = {
        "notification_auth": "auth_key",
        "task_id": "task123",
        "generated_summary": "This is a summary",
        "task_status": "completed",
    }
    assert TaskCompletionNotification(**notification_data)

    # Invalid data
    invalid_notification_data = {
        "notification_auth": "auth_key",
        "task_id": "task123",
        "task_status": "completed",
    }
    with pytest.raises(ValidationError):
        TaskCompletionNotification(**invalid_notification_data)
