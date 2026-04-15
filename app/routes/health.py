from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text

from app.cache.redis_client import redis_client
from app.database.connection import async_engine
from app.schemas.common import BaseResponse

router = APIRouter()


@router.get(
    "/health", response_model=BaseResponse[dict], summary="Health check endpoint"
)
async def health_check():
    """
    Performs a health check on the application and its dependencies (database, Redis).
    """
    db_status = "disconnected"
    redis_status = "disconnected"

    try:
        # Check DB connection
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception as e:
        print(f"Database connection error: {e}")
        db_status = f"error: {e}"

    try:
        # Check Redis connection
        if redis_client._redis is not None:
            await redis_client._redis.ping()
            redis_status = "connected"
        else:
            await redis_client.connect()  # Attempt to connect if not already
            if redis_client._redis:
                redis_status = "connected"
            else:
                redis_status = "error: Redis client not initialized or connected"
    except Exception as e:
        print(f"Redis connection error: {e}")
        redis_status = f"error: {e}"

    if db_status == "connected" and redis_status == "connected":
        return BaseResponse(
            status="ok",
            data={
                "database": db_status,
                "redis": redis_status,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
            message="Application is healthy",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=BaseResponse(
                status="error",
                data={
                    "database": db_status,
                    "redis": redis_status,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                },
                message="Application is unhealthy",
            ).model_dump(),
        )
