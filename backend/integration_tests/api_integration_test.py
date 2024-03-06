from backend.models import PotentialUser, User
from backend.configuration import global_config
from datetime import datetime, timedelta
import jwt
import pytest
from unittest.mock import patch
import time
from mongoengine import connect, disconnect
import requests

global_data = {}


@pytest.fixture(scope="module")
def setup_app():
    db = connect(global_config["Application"]["DB"])
    db.drop_database(global_config["Application"]["DB"])
    yield
    disconnect()


def test_example(setup_app):
    response = requests.get(f"{global_config['Application']['API_GATEWAY']}/")
    assert response.status_code == 200
    assert response.json() == {"message": "Service is up!"}


def test_register_user(setup_app):
    response = requests.post(
        f"{global_config['Application']['API_GATEWAY']}/user/register/password",
        json={
            "user_email": "testuser@example.com",
            "user_name": "Test User",
            "user_password": "securepassword",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "OTP verification sent successfully!"
    assert "expiry_in" in data


def test_verify_user_otp(setup_app):
    mock_otp = str(
        PotentialUser.objects(user_email="testuser@example.com").first().user_otp_sent
    )
    response = requests.post(
        f"{global_config['Application']['API_GATEWAY']}/user/register/verify",
        json={"user_email": "testuser@example.com", "otp": mock_otp},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User created successfully"
    assert "jwt_token" in data


def test_login_user(setup_app):
    login_data = {
        "user_email": "testuser@example.com",
        "user_password": "securepassword",
    }
    response = requests.post(
        f"{global_config['Application']['API_GATEWAY']}/user/login/password",
        json=login_data,
    )
    assert response.status_code == 200
    assert "jwt_token" in response.json()
    jwt_token = response.json()["jwt_token"]
    decoded_jwt_token = jwt.decode(
        jwt_token, global_config["Application"]["JWT_SECRET"], algorithms=["HS256"]
    )
    assert decoded_jwt_token["user_email"] == "testuser@example.com"
    global_data["jwt_token"] = jwt_token
    global_data["decoded_jwt_token"] = decoded_jwt_token


def test_generate_refresh_token(setup_app):
    response = requests.post(
        f"{global_config['Application']['API_GATEWAY']}/user/auth/refresh_token",
        params={"token": global_data["jwt_token"]},
    )
    assert response.status_code == 200
    assert "refresh_token" in response.json()
    refresh_token = response.json()["refresh_token"]
    decoded_refresh_token = jwt.decode(
        refresh_token, global_config["Application"]["JWT_SECRET"], algorithms=["HS256"]
    )
    assert decoded_refresh_token["user_email"] == "testuser@example.com"
    assert decoded_refresh_token["exp"] >= global_data["decoded_jwt_token"]["exp"]


def test_reset_password_request(setup_app):
    response = requests.post(
        f"{global_config['Application']['API_GATEWAY']}/user/auth/forgot_password",
        params={"user_email": "testuser@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "OTP verification sent successfully!"
    assert "expiry_in" in data


def test_generate_summary_unsupported_file_type(setup_app):
    test_file_name = "unsupported_file.kpgfy'"

    response = requests.post(
        f"{global_config['Application']['API_GATEWAY']}/generate_summary",
        params={"token": global_data["jwt_token"]},
        files={"file": (test_file_name, b"PDF content, which is unsupported.")},
    )

    assert response.status_code == 400
    assert "valid supported file type" in response.json().get("detail")


def test_generate_summary(setup_app):

    with open("unit_tests/test.txt", "rb") as f:
        response = requests.post(
            f"{global_config['Application']['API_GATEWAY']}/generate_summary",
            params={"token": global_data["jwt_token"]},
            files={"file": ("test.txt", f)},
        )

    assert response.status_code == 200
    assert (
        response.json()["message"] == "Your task for summary generation has been enqued"
    )
    assert "task_id" in response.json()


def test_pending_tasks(setup_app):
    # The setup_tasks should ensure there are pending tasks for the user
    response = requests.get(
        f"{global_config['Application']['API_GATEWAY']}/user/pending_tasks",
        params={"token": global_data["jwt_token"]},
    )
    assert response.status_code == 200
    tasks = response.json()["pending_tasks"]
    assert isinstance(tasks, list)
    assert len(tasks) > 0
    assert all(task["user_task_status"] == "PENDING" for task in tasks)


@pytest.mark.slow
def test_completed_task_and_summary(setup_app):
    # sleep for 10 seconds for task to complete
    time.sleep(10)
    response = requests.get(
        f"{global_config['Application']['API_GATEWAY']}/user/completed_tasks",
        params={"token": global_data["jwt_token"]},
    )
    assert response.status_code == 200
    completed_tasks = response.json()["completed_tasks"]
    assert len(completed_tasks) > 0  # Ensure there is at least one completed task

    # Step 2: Select a completed task and use its task_id to fetch the summary
    task_id = completed_tasks[0][
        "user_task_id"
    ]  # Assuming there's at least one completed task and it has a task_id
    response = requests.get(
        f"{global_config['Application']['API_GATEWAY']}/user/get_summary",
        params={"token": global_data["jwt_token"], "task_id": task_id},
    )
    assert response.status_code == 200
    summary_data = response.json()
    assert summary_data["message"] == "Task completed succesfully"
    assert "result" in summary_data  # Ensure the summary data includes a 'result' key

    # Verify that the task_id used is indeed from a completed task
    assert (
        summary_data.get("status", None) != "PENDING"
    )  # The task status should not be PENDING


def test_update_openai_key(setup_app):

    user_email = "testuser@example.com"
    new_openai_api_key = "newkey123456"
    response = requests.post(
        f"{global_config['Application']['API_GATEWAY']}/user/update_key",
        params={
            "token": global_data["jwt_token"],
            "openai_api_key": new_openai_api_key,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User openai key updated successfully"

    # Optionally, verify the key was actually updated in the database
    updated_user = User.objects(user_email=user_email).first()
    assert updated_user is not None
    assert updated_user.user_openai_key == new_openai_api_key


def test_reset_password(setup_app):

    user_email = "testuser@example.com"
    new_password = "newsecurepassword"
    user_otp = (
        User.objects(user_email=user_email).first().user_password_recovery_request.otp
    )

    response = requests.post(
        f"{global_config['Application']['API_GATEWAY']}/user/auth/reset_password",
        json={
            "user_email": user_email,
            "user_otp": user_otp,
            "user_new_password": new_password,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Password updated successfully"
    assert "jwt" in data

    # try to login using new password
    login_data = {
        "user_email": "testuser@example.com",
        "user_password": "newsecurepassword",
    }
    response = requests.post(
        f"{global_config['Application']['API_GATEWAY']}/user/login/password",
        json=login_data,
    )
    assert response.status_code == 200

    response = requests.post(
        f"{global_config['Application']['API_GATEWAY']}/user/auth/refresh_token",
        params={"token": global_data["jwt_token"]},
    )
    assert response.status_code == 401


def test_resend_otp(setup_app):
    user_email = "newtestuser@example.com"
    response = requests.post(
        f"{global_config['Application']['API_GATEWAY']}/user/register/password",
        json={
            "user_email": user_email,
            "user_name": "Test User",
            "user_password": "securepassword",
        },
    )
    curr_otp = PotentialUser.objects(user_email=user_email).first().user_otp_sent
    assert response.status_code == 200
    response = requests.post(
        f"{global_config['Application']['API_GATEWAY']}/user/register/resend_otp",
        params={"user_email": user_email},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "OTP verification sent successfully!"
    assert "expiry_in" in data

    # verify the OTP and send time were updated in the database
    updated_potential_user = PotentialUser.objects(user_email=user_email).first()
    assert updated_potential_user is not None
    # assert updated_potential_user.user_otp_sent !=curr_otp
    # Ensure the OTP send time is updated to now, allow some leeway for test execution time
    assert datetime.now() - updated_potential_user.user_otp_sent_at < timedelta(
        minutes=1
    )
