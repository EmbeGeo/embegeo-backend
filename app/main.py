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
from app.models.base import Base
from app.routes import health
from app.routes import sensor_data, statistics
from app.websocket import handlers as websocket_handlers


async def http_exception_handler(request: Request, exc: FastAPIHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
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
    description="Vision 모듈 기반 설비 센서 데이터 수집, 저장, 조회 시스템.",
    version="1.0.0",
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(FastAPIHTTPException, http_exception_handler)


@app.on_event("startup")
async def startup_event():
    print("Application startup...")
    await redis_client.connect()
    print("Redis client initialized.")

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables checked/created.")


@app.on_event("shutdown")
async def shutdown_event():
    print("Application shutdown...")
    await redis_client.disconnect()
    print("Redis client disconnected.")


# API 라우트 등록 (prefix: /api/v1)
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(sensor_data.router, prefix="/api/v1", tags=["Sensor Data"])
app.include_router(statistics.router, prefix="/api/v1", tags=["Statistics"])

# WebSocket
app.include_router(websocket_handlers.router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
