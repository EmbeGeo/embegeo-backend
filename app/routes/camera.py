
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.camera import (CameraCalibrationCreate,
                                CameraCalibrationResponse,
                                CameraCalibrationUpdate)
from app.schemas.common import BaseResponse
from app.services.camera_service import CameraService

router = APIRouter()


@router.post(
    "/camera/{camera_id}/calibration",
    response_model=BaseResponse[CameraCalibrationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create camera calibration settings",
)
async def create_camera_calibration(
    camera_id: int,
    calibration_data: CameraCalibrationCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Creates new camera calibration settings for a given camera ID.
    """
    if calibration_data.camera_id != camera_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=BaseResponse(
                status="error", message="Camera ID in path and body must match"
            ).model_dump(),
        )

    camera_service = CameraService(db)
    existing_calibration = await camera_service.get_calibration_by_camera_id(camera_id)
    if existing_calibration:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=BaseResponse(
                status="error",
                message=f"Calibration for camera ID {camera_id} already exists",
            ).model_dump(),
        )

    try:
        new_calibration = await camera_service.create_calibration(calibration_data)
        return BaseResponse(
            status="success",
            message="Camera calibration created successfully",
            data=new_calibration,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=BaseResponse(
                status="error", message=f"Failed to create camera calibration: {e}"
            ).model_dump(),
        )


@router.get(
    "/camera/{camera_id}/calibration",
    response_model=BaseResponse[CameraCalibrationResponse],
    summary="Get camera calibration settings",
)
async def get_camera_calibration(camera_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieves camera calibration settings for a given camera ID.
    """
    camera_service = CameraService(db)
    calibration = await camera_service.get_calibration_by_camera_id(camera_id)
    if not calibration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=BaseResponse(
                status="error",
                message=f"Calibration for camera ID {camera_id} not found",
            ).model_dump(),
        )
    return BaseResponse(status="success", data=calibration)


@router.put(
    "/camera/{camera_id}/calibration",
    response_model=BaseResponse[CameraCalibrationResponse],
    summary="Update camera calibration settings",
)
async def update_camera_calibration(
    camera_id: int,
    calibration_data: CameraCalibrationUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Updates existing camera calibration settings for a given camera ID.
    """
    camera_service = CameraService(db)
    updated_calibration = await camera_service.update_calibration(
        camera_id, calibration_data
    )
    if not updated_calibration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=BaseResponse(
                status="error",
                message=f"Calibration for camera ID {camera_id} not found",
            ).model_dump(),
        )
    return BaseResponse(
        status="success",
        message="Camera calibration updated successfully",
        data=updated_calibration,
    )


@router.delete(
    "/camera/{camera_id}/calibration",
    response_model=BaseResponse[dict],
    summary="Delete camera calibration settings",
)
async def delete_camera_calibration(camera_id: int, db: AsyncSession = Depends(get_db)):
    """
    Deletes camera calibration settings for a given camera ID.
    """
    camera_service = CameraService(db)
    deleted = await camera_service.delete_calibration(camera_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=BaseResponse(
                status="error",
                message=f"Calibration for camera ID {camera_id} not found",
            ).model_dump(),
        )
    return BaseResponse(
        status="success", message="Camera calibration deleted successfully"
    )
