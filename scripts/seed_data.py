import asyncio
import random
from datetime import datetime, timedelta


from app.database.connection import AsyncSessionLocal
from app.models.camera_calibration import CameraCalibration
from app.models.data_log import DataLog


async def seed_data():
    async with AsyncSessionLocal() as session:
        # Clear existing data for a clean seed
        await session.execute(DataLog.__table__.delete())
        await session.execute(CameraCalibration.__table__.delete())
        await session.commit()

        # Seed Camera Calibration data
        print("Seeding Camera Calibration data...")
        for i in range(1, 4):  # 3 cameras
            calibration = CameraCalibration(
                camera_id=i,
                angle_x=round(random.uniform(-10, 10), 2),
                angle_y=round(random.uniform(-5, 5), 2),
                angle_z=round(random.uniform(-2, 2), 2),
                calibration_date=datetime.utcnow(),
            )
            session.add(calibration)
        await session.commit()
        print("Camera Calibration data seeded.")

        # Seed Data Logs
        print("Seeding Data Log data...")
        now = datetime.utcnow()
        for i in range(200):
            timestamp = now - timedelta(
                minutes=random.randint(0, 120), seconds=random.randint(0, 59)
            )
            frame_drop = random.choice(
                [True, False, False, False, False]
            )  # 20% chance of frame drop
            status = random.choice(["valid", "invalid", "pending"])
            error_message = "OCR mismatch" if status == "invalid" else None

            log = DataLog(
                timestamp=timestamp,
                ocr_text=f"OCR_TEXT_{random.randint(1000, 9999)}",
                confidence_score=round(random.uniform(0.7, 0.99), 2),
                image_path=f"/path/to/image_{random.randint(1, 100)}.jpg",
                camera_id=random.randint(1, 3),
                camera_angle_x=round(random.uniform(-10, 10), 2),
                camera_angle_y=round(random.uniform(-5, 5), 2),
                camera_angle_z=round(random.uniform(-2, 2), 2),
                frame_number=random.randint(1, 100000),
                frame_drop=frame_drop,
                status=status,
                error_message=error_message,
                created_at=timestamp,
                updated_at=timestamp,
            )
            session.add(log)
        await session.commit()
        print("Data Log data seeded.")
        print("Seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_data())
