from fastapi.testclient import TestClient
from fastapi import FastAPI
from backend.mainapi import Application
from backend.models import PotentialUser
from backend.middleware import custom_middleware
from mongoengine import disconnect, connect
import pytest


@pytest.fixture(scope="module")
def setup_app():
    db = connect("test_db")
    db.drop_database("test_db")
    app = (
        Application(FastAPI(), custom_middleware, "test_db", ["*"])
        .build_application()
        .add_routes()
        .get_app()
    )
    client = TestClient(app)
    yield client  # Provide the client to the tests
    disconnect()


def test_example(setup_app):
    response = setup_app.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Service is up!"}


def test_register_user(setup_app):
    response = setup_app.post(
        "/user/register/password",
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
    response = setup_app.post(
        "/user/register/verify",
        json={"user_email": "testuser@example.com", "otp": mock_otp},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User created successfully"
    assert "jwt_token" in data
