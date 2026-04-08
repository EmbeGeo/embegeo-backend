import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.utils.logger import logger


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request details
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "request_method": request.method,
                "request_path": request.url.path,
                "request_client_host": request.client.host,
                "request_headers": dict(request.headers),
            },
        )

        response = await call_next(request)
        process_time = time.time() - start_time

        # Log response details
        logger.info(
            f"Response: {request.method} {request.url.path} - Status {response.status_code}",
            extra={
                "response_status_code": response.status_code,
                "response_process_time": f"{process_time:.4f}s",
                "response_headers": dict(response.headers),
            },
        )
        return response
