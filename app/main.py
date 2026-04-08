from typing import Any, Callable

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.cache.redis_client import redis_client
from app.config import settings
from app.database.connection import async_engine
from app.models.base import Base  # Import Base for metadata
from app.routes import camera, data, health
from app.websocket import handlers as websocket_handlers


# Custom exception handler to return BaseResponse format
async def http_exception_handler(request: Request, exc: FastAPIHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,  # Assuming detail is already a BaseResponse.model_dump()
    )


async def custom_websocket_error_handler(
    websocket: WebSocket, exc: WebSocketDisconnect
):
    """
    Custom WebSocket error handler to ensure proper disconnection and logging.
    """
    print(f"WebSocket disconnected with code: {exc.code}, reason: {exc.reason}")
    # You might want to remove the websocket from manager here if not already handled by manager.disconnect
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "WebSocket disconnected due to an error."},
    )


class CustomFastAPI(FastAPI):
    def get(self, path: str, *args: Any, **kwargs: Any) -> Callable:
        kwargs["response_class"] = JSONResponse
        return super().get(path, *args, **kwargs)

    def post(self, path: str, *args: Any, **kwargs: Any) -> Callable:
        kwargs["response_class"] = JSONResponse
        return super().post(path, *args, **kwargs)

    def put(self, path: str, *args: Any, **kwargs: Any) -> Callable:
        kwargs["response_class"] = JSONResponse
        return super().put(path, *args, **kwargs)

    def delete(self, path: str, *args: Any, **kwargs: Any) -> Callable:
        kwargs["response_class"] = JSONResponse
        return super().delete(path, *args, **kwargs)


app = CustomFastAPI(
    title="EasyGeo Backend API",
    description="OCR based facility data collection, storage, and retrieval system.",
    version="1.0.0",
    debug=settings.DEBUG,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(FastAPIHTTPException, http_exception_handler)
# Not directly handling WebSocketDisconnect here, it's caught in the handler function


@app.on_event("startup")
async def startup_event():
    print("Application startup...")
    # Initialize Redis client
    await redis_client.connect()
    print("Redis client initialized.")

    # Create all tables if they don't exist
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables checked/created.")


@app.on_event("shutdown")
async def shutdown_event():
    print("Application shutdown...")
    # Close Redis connection
    await redis_client.disconnect()
    print("Redis client disconnected.")
    # Close DB connection pool (handled by SQLAlchemy async_engine's disposal)


# Include API routes
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(data.router, prefix="/api", tags=["Data"])
app.include_router(camera.router, prefix="/api", tags=["Camera"])

# Include WebSocket handlers
app.include_router(websocket_handlers.router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()(),
    )
