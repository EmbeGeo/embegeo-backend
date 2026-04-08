from datetime import datetime, timedeltafrom typing import Any, Dict, List, Optional

from sqlalchemy import extract, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.data_log import DataLog
from app.schemas.common import PaginatedResponse
from app.schemas.data import (DataGroupedByMinute, DataLogCreate,
                              DataLogUpdate, FrameDropStats, GroupedRecord)


class DataService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_ocr_data(self, data: DataLogCreate) -> DataLog:
        new_data_log = DataLog(**data.model_dump())
        self.db.add(new_data_log)
        await self.db.commit()
        await self.db.refresh(new_data_log)
        return new_data_log

    async def get_data_by_minute(
        self, start_time: datetime, end_time: datetime, camera_id: Optional[int] = None
    ) -> GroupedDataResponse:
        query = select(DataLog).filter(
            DataLog.timestamp >= start_time, DataLog.timestamp < end_time
        )
        if camera_id is not None:
            query = query.filter(DataLog.camera_id == camera_id)

        query = query.order_by(DataLog.timestamp)
        result = await self.db.execute(query)
        data_logs = result.scalars().all()

        grouped_data: Dict[datetime, List[DataLog]] = {}
        for log in data_logs:
            minute_start = log.timestamp.replace(second=0, microsecond=0)
            if minute_start not in grouped_data:
                grouped_data[minute_start] = []
            grouped_data[minute_start].append(log)

        response_data = []
        for minute, logs in sorted(grouped_data.items()):
            frame_drop_count = sum(1 for log in logs if log.frame_drop)
            records = [
                GroupedRecord(
                    timestamp=log.timestamp,
                    ocr_text=log.ocr_text,
                    confidence_score=log.confidence_score,
                    frame_drop=log.frame_drop,
                )
                for log in logs
            ]
            response_data.append(
                DataGroupedByMinute(
                    minute=minute, records=records, frame_drop_count=frame_drop_count
                )
            )

        return DataGroupedByMinute(data=response_data, total_records=len(data_logs))

    async def search_data(
        self,
        start_time: datetime,
        end_time: datetime,
        camera_id: Optional[int] = None,
        status: Optional[str] = None,
        frame_drop: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedResponse[DataLog]:
        query = select(DataLog).filter(
            DataLog.timestamp >= start_time, DataLog.timestamp < end_time
        )

        if camera_id is not None:
            query = query.filter(DataLog.camera_id == camera_id)
        if status is not None:
            query = query.filter(DataLog.status == status)
        if frame_drop is not None:
            query = query.filter(DataLog.frame_drop == frame_drop)

        # Get total count for pagination
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(total_query)
        total = total_result.scalar_one()

        # Apply limit and offset for pagination
        query = query.order_by(DataLog.timestamp.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        data_logs = result.scalars().all()

        return PaginatedResponse(
            data=[
                DataLog.model_validate(log) for log in data_logs
            ],  # Assuming DataLog model has a model_validate or similar for Pydantic conversion
            total=total,
            page=offset // limit + 1,
            per_page=limit,
        )

    async def get_frame_drop_stats(
        self, start_time: datetime, end_time: datetime, camera_id: Optional[int] = None
    ) -> FrameDropStats:
        query_total_frames = select(func.count(DataLog.id)).filter(
            DataLog.timestamp >= start_time, DataLog.timestamp < end_time
        )
        if camera_id is not None:
            query_total_frames = query_total_frames.filter(
                DataLog.camera_id == camera_id
            )

        total_frames_result = await self.db.execute(query_total_frames)
        total_frames = total_frames_result.scalar_one()

        query_dropped_frames = select(func.count(DataLog.id)).filter(
            DataLog.timestamp >= start_time,
            DataLog.timestamp < end_time,
            DataLog.frame_drop == True,
        )
        if camera_id is not None:
            query_dropped_frames = query_dropped_frames.filter(
                DataLog.camera_id == camera_id
            )

        dropped_frames_result = await self.db.execute(query_dropped_frames)
        dropped_frames = dropped_frames_result.scalar_one()

        drop_rate = (dropped_frames / total_frames * 100) if total_frames > 0 else 0.0

        # Stats by minute
        stats_by_minute_query = select(
            func.strftime("%Y-%m-%dT%H:%M:00Z", DataLog.timestamp).label(
                "minute"
            ),  # This might need adjustment for MySQL's date_format
            func.count(DataLog.id).label("total"),
            func.sum(func.cast(DataLog.frame_drop, Integer)).label("dropped"),
        ).filter(DataLog.timestamp >= start_time, DataLog.timestamp < end_time)
        if camera_id is not None:
            stats_by_minute_query = stats_by_minute_query.filter(
                DataLog.camera_id == camera_id
            )

        stats_by_minute_query = stats_by_minute_query.group_by(text("minute")).order_by(
            text("minute")
        )

        # Adjust for MySQL's DATE_FORMAT
        # The prompt specifies MySQL, so using DATE_FORMAT for minute grouping
        # func.strftime is for SQLite. For MySQL, it should be something like:
        # func.date_format(DataLog.timestamp, '%Y-%m-%dT%H:%i:00Z').label("minute")

        # Re-evaluating the minute grouping for MySQL
        stats_by_minute_query = select(
            func.date_format(DataLog.timestamp, "%Y-%m-%dT%H:%i:00Z").label("minute"),
            func.count(DataLog.id).label("total"),
            func.sum(func.case((DataLog.frame_drop == True, 1), else_=0)).label(
                "dropped"
            ),
        ).filter(DataLog.timestamp >= start_time, DataLog.timestamp < end_time)
        if camera_id is not None:
            stats_by_minute_query = stats_by_minute_query.filter(
                DataLog.camera_id == camera_id
            )

        stats_by_minute_query = stats_by_minute_query.group_by(text("minute")).order_by(
            text("minute")
        )

        stats_by_minute_result = await self.db.execute(stats_by_minute_query)
        stats_by_minute_data = []
        for row in stats_by_minute_result:
            minute_total = row.total
            minute_dropped = row.dropped if row.dropped is not None else 0
            stats_by_minute_data.append(
                {
                    "minute": row.minute,
                    "total": minute_total,
                    "dropped": minute_dropped,
                    "rate": (minute_dropped / minute_total * 100)
                    if minute_total > 0
                    else 0.0,
                }
            )

        return FrameDropStats(
            total_frames=total_frames,
            dropped_frames=dropped_frames,
            drop_rate=drop_rate,
            stats_by_minute=stats_by_minute_data,
        )
