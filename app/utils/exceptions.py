from fastapi import HTTPException, status

from app.schemas.common import BaseResponse


class APIException(HTTPException):
    def __init__(self, status_code: int, message: str, data: any = None):
        super().__init__(
            status_code=status_code,
            detail=BaseResponse(
                status="error", message=message, data=data
            ).model_dump(),
        )


class NotFoundException(APIException):
    def __init__(self, resource_name: str = "Resource", identifier: str = ""):
        message = f"{resource_name} not found"
        if identifier:
            message += f" with identifier: {identifier}"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, message=message)


class BadRequestException(APIException):
    def __init__(self, message: str = "Bad Request", data: any = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, message=message, data=data
        )


class ConflictException(APIException):
    def __init__(self, message: str = "Conflict", data: any = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT, message=message, data=data
        )


class ServiceUnavailableException(APIException):
    def __init__(self, message: str = "Service Unavailable", data: any = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, message=message, data=data
        )
