from typing import Optional
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.camera_calibration import CameraCalibration
from app.schemas.camera import CameraCalibrationCreate, CameraCalibrationUpdate


class CameraService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_calibration(
        self, calibration_data: CameraCalibrationCreate
    ) -> CameraCalibration:
        new_calibration = CameraCalibration(**calibration_data.model_dump())
        self.db.add(new_calibration)
        await self.db.commit()
        await self.db.refresh(new_calibration)
        return new_calibration

    async def get_calibration_by_camera_id(
        self, camera_id: int
    ) -> Optional[CameraCalibration]:
        result = await self.db.execute(
            select(CameraCalibration).filter(CameraCalibration.camera_id == camera_id)
        )
        return result.scalars().first()

    async def update_calibration(
        self, camera_id: int, calibration_data: CameraCalibrationUpdate
    ) -> Optional[CameraCalibration]:
        calibration = await self.get_calibration_by_camera_id(camera_id)
        if not calibration:
            return None

        for key, value in calibration_data.model_dump(exclude_unset=True).items():
            setattr(calibration, key, value)

        await self.db.commit()
        await self.db.refresh(calibration)
        return calibration

    async def delete_calibration(self, camera_id: int) -> bool:
        result = await self.db.execute(
            delete(CameraCalibration).filter(CameraCalibration.camera_id == camera_id)
        )
        await self.db.commit()
        return result.rowcount > 0
