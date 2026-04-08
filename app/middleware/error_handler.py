from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.schemas.common import BaseResponse
from app.utils.exceptions import APIException


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except APIException as e:
            return JSONResponse(status_code=e.status_code, content=e.detail)
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content=BaseResponse(status="error", message=e.detail).model_dump(),
            )
        except Exception as e:
            # Catch all other unhandled exceptions
            return JSONResponse(
                status_code=500,
                content=BaseResponse(
                    status="error", message=f"An unexpected error occurred: {e}"
                ).model_dump(),
            )
