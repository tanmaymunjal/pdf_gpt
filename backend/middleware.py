from logger import logger
from fastapi import Request


async def custom_middleware(request: Request, call_next):
    try:
        logger.info(f"Request received: {request.method} {request.url}")
        logger.info(f"Headers: {request.headers}")
        logger.info(f"Query Parameters: {request.query_params}")
        body = await request.body()
        logger.info(f"Request Body: {body.decode()}")

        response = await call_next(request)

        logger.info(f"Response: {response.status_code}")

        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise
