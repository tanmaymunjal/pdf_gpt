import unittest
from fastapi import Request, Response
from backend.middleware import custom_middleware 
from backend.logger import logger
from unittest.mock import Mock

class TestCustomMiddleware(unittest.IsolatedAsyncioTestCase):
    async def test_custom_middleware(self):
        # Create a mock request
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = "/"
        request.headers = {"Content-Type": "application/json"}
        request.query_params = {"param1": "value1", "param2": "value2"}
        request.body = Mock(return_value=b'{"key": "value"}')

        # Create a mock call_next function
        async def mock_call_next(request):
            return Response("Mock Response", status_code=200)

        # Create a mock logger
        mock_logger = Mock()

        # Patch the logger in the module with the mock logger
        logger = mock_logger

        # Call the custom middleware
        response = await custom_middleware(request, mock_call_next)

        # Assert that the response status code is correct
        self.assertEqual(response.status_code, 200)

        # Assert that the logger was called with the expected messages
        mock_logger.info.assert_called_with("Request received: GET /")
        mock_logger.info.assert_called_with("Headers: {'Content-Type': 'application/json'}")
        mock_logger.info.assert_called_with("Query Parameters: {'param1': 'value1', 'param2': 'value2'}")
        mock_logger.info.assert_called_with("Request Body: {'key': 'value'}")
        mock_logger.info.assert_called_with("Response: 200")
