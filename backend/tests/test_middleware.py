import pytest
from fastapi import FastAPI, Request
from starlette.responses import Response
from starlette.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from backend.middleware import CustomMiddleware
from backend.mainapi import Application
from backend.celery_app import celery_application
import time


@pytest.mark.asyncio
async def test_custom_middleware():
    logger_mock = MagicMock()

    custom_middleware = CustomMiddleware(logger_mock).generate_middleware()
    app = (
        Application(FastAPI(), custom_middleware, "test_db", ["*"], celery_application)
        .build_application()
        .add_routes()
        .get_app()
    )

    client = TestClient(app)

    # Make a request using the TestClient
    response = client.get("/", params={"query": "param"})

    # Assert the response is correct
    assert response.status_code == 200
    # Verify logging calls
    logger_mock.info.assert_any_call(
        "Request received: GET http://testserver/?query=param"
    )
    logger_mock.info.assert_any_call("Request Body: ")
    logger_mock.error.assert_not_called()
