from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.common import BaseResponse, PaginatedResponse
from app.schemas.data import (DataLogCreate, DataLogResponse, FrameDropStats,
                              GroupedDataResponse)
from app.services.cache_service import CacheService
from app.services.data_service import DataService
from app.services.validation_service import ValidationService

router = APIRouter()


@router.post(
    "/data/ocr",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="Receive OCR data from AI",
)
async def receive_ocr_data(
    data: DataLogCreate,
    db: AsyncSession = Depends(get_db),
    cache_service: CacheService = Depends(CacheService),
):
    """
    Receives OCR data, validates it, saves to MySQL, caches in Redis, and broadcasts via WebSocket.
    """
    if not ValidationService.is_valid_confidence_score(data.confidence_score):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=BaseResponse(
                status="error",
                message="Invalid confidence score. Must be between 0.0 and 1.0.",
            ).model_dump(),
        )
    if not ValidationService.is_valid_camera_id(data.camera_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=BaseResponse(
                status="error", message="Invalid camera ID. Must be a positive integer."
            ).model_dump(),
        )

    try:
        data_service = DataService(db)
        new_log = await data_service.save_ocr_data(data)

        # Cache the latest data
        await cache_service.cache_latest_data(DataLogResponse.model_validate(new_log))

        # TODO: Broadcast via WebSocket (requires WebSocketManager instance)

        return BaseResponse(
            status="saved",
            message="데이터 저장 완료",
            data={"id": new_log.id, "status": new_log.status},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=BaseResponse(
                status="error", message=f"Failed to save data: {e}"
            ).model_dump(),
        )


@router.get(
    "/data/range",
    response_model=BaseResponse[GroupedDataResponse],
    summary="Retrieve data by time range (minute-wise)",
)
async def get_data_in_range(
    start_time: datetime = Query(
        ..., description="Start time (ISO 8601 format, e.g., 2026-04-10T14:25:00Z)"
    ),
    end_time: datetime = Query(
        ..., description="End time (ISO 8601 format, e.g., 2026-04-10T14:35:00Z)"
    ),
    camera_id: Optional[int] = Query(
        None, description="Optional camera ID to filter data"
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves OCR data grouped by minute within a specified time range,
    optionally filtered by camera ID.
    """
    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=BaseResponse(
                status="error", message="start_time must be before end_time"
            ).model_dump(),
        )

    data_service = DataService(db)
    grouped_data = await data_service.get_data_by_minute(
        start_time, end_time, camera_id
    )
    return BaseResponse(status="success", data=grouped_data)


@router.get(
    "/data/search",
    response_model=BaseResponse[PaginatedResponse[DataLogResponse]],
    summary="Search data with filters",
)
async def search_data_logs(
    start_time: datetime = Query(..., description="Start time (ISO 8601 format)"),
    end_time: datetime = Query(..., description="End time (ISO 8601 format)"),
    camera_id: Optional[int] = Query(None, description="Optional camera ID to filter"),
    status: Optional[str] = Query(
        None,
        description="Optional data status to filter ('valid', 'invalid', 'pending')",
    ),
    frame_drop: Optional[bool] = Query(
        None, description="Optional frame drop status to filter"
    ),
    limit: int = Query(
        20, ge=1, le=100, description="Number of records to return per page"
    ),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_db),
):
    """
    Searches OCR data logs based on various filters and provides pagination.
    """
    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=BaseResponse(
                status="error", message="start_time must be before end_time"
            ).model_dump(),
        )

    data_service = DataService(db)
    paginated_response = await data_service.search_data(
        start_time=start_time,
        end_time=end_time,
        camera_id=camera_id,
        status=status,
        frame_drop=frame_drop,
        limit=limit,
        offset=offset,
    )
    return BaseResponse(status="success", data=paginated_response)


@router.get(
    "/stats/frame-drop",
    response_model=BaseResponse[FrameDropStats],
    summary="Get frame drop statistics",
)
async def get_frame_drop_statistics(
    start_time: datetime = Query(..., description="Start time (ISO 8601 format)"),
    end_time: datetime = Query(..., description="End time (ISO 8601 format)"),
    camera_id: Optional[int] = Query(
        None, description="Optional camera ID to filter stats"
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves statistics on frame drops within a specified time range,
    optionally filtered by camera ID.
    """
    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=BaseResponse(
                status="error", message="start_time must be before end_time"
            ).model_dump(),
        )

    data_service = DataService(db)
    stats = await data_service.get_frame_drop_stats(start_time, end_time, camera_id)
    return BaseResponse(status="success", data=stats)
