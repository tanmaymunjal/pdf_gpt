# import pytest
# from fastapi import FastAPI, Request
# from starlette.responses import Response
# from starlette.testclient import TestClient
# from unittest.mock import AsyncMock, MagicMock
# from backend.middleware import custom_middleware
# from backend.mainapi import app
# import time


# @pytest.mark.asyncio
# async def test_custom_middleware():
#     client = TestClient(app)

#     # Make a request using the TestClient
#     response = client.get("/")

#     # Assert the response is correct
#     assert response.status_code == 200

#     # Mock the logger to verify logging calls
#     logger_mock = MagicMock()

#     # Replace your actual logger with the mock
#     global logger
#     logger = logger_mock

#     # Verify logging calls
#     logger_mock.info.assert_any_call(
#         "root:middleware.py:30 Request received: GET http://testserver/test-path?query=param"
#     )
#     logger_mock.info.assert_any_call(
#         "Headers: Headers({'host': 'testserver', 'user-agent': 'testclient', 'accept': '*/*'})"
#     )
#     logger_mock.info.assert_any_call("Query Parameters: query=param")
#     logger_mock.info.assert_any_call("Request Body: ")
#     logger_mock.error.assert_not_called()  # Ensure no errors were logged
