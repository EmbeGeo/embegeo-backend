from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.data_log import DataLog
from app.schemas.data import DataLogCreate

@pytest.mark.asyncio
async def test_receive_ocr_data(client: AsyncClient, db_session: AsyncSession):
    test_data = {
        "ocr_text": "Sample OCR Text",
        "confidence_score": 0.99,
        "image_path": "/images/test.jpg",
        "camera_id": 1,
        "camera_angle_x": 0.1,
        "camera_angle_y": 0.2,
        "camera_angle_z": 0.3,
        "frame_number": 100,
        "frame_drop": False,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    response = await client.post("/api/data/ocr", json=test_data)

    assert response.status_code == 201
    assert response.json()["status"] == "saved"
    assert response.json()["message"] == "데이터 저장 완료"
    assert "id" in response.json()["data"]

    # Verify data in database
    saved_log = await db_session.get(DataLog, response.json()["data"]["id"])
    assert saved_log is not None
    assert saved_log.ocr_text == test_data["ocr_text"]
    assert saved_log.camera_id == test_data["camera_id"]


@pytest.mark.asyncio
async def test_receive_ocr_data_invalid_confidence_score(client: AsyncClient):
    test_data = {
        "ocr_text": "Sample OCR Text",
        "confidence_score": 1.5,  # Invalid score
        "image_path": "/images/test.jpg",
        "camera_id": 1,
        "camera_angle_x": 0.1,
        "camera_angle_y": 0.2,
        "camera_angle_z": 0.3,
        "frame_number": 100,
        "frame_drop": False,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    response = await client.post("/api/data/ocr", json=test_data)

    assert response.status_code == 400
    assert response.json()["detail"]["status"] == "error"
    assert "Invalid confidence score" in response.json()["detail"]["message"]


@pytest.mark.asyncio
async def test_get_data_in_range(client: AsyncClient, db_session: AsyncSession):
    # Add some test data
    now = datetime.utcnow()
    for i in range(5):
        log = DataLog(
            ocr_text=f"Text {i}",
            confidence_score=0.9,
            image_path=f"/path/{i}.jpg",
            camera_id=1,
            camera_angle_x=0.1,
            camera_angle_y=0.2,
            camera_angle_z=0.3,
            frame_number=i,
            frame_drop=(i % 2 == 0),
            timestamp=now - timedelta(minutes=5 - i),
        )
        db_session.add(log)
    await db_session.commit()

    start_time = (now - timedelta(minutes=6)).isoformat() + "Z"
    end_time = (now + timedelta(minutes=1)).isoformat() + "Z"

    response = await client.get(
        "/api/data/range",
        params={"start_time": start_time, "end_time": end_time, "camera_id": 1},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["data"]["total_records"] == 5
    assert len(response.json()["data"]["data"]) > 0


@pytest.mark.asyncio
async def test_search_data_logs(client: AsyncClient, db_session: AsyncSession):
    # Add some test data
    now = datetime.utcnow()
    for i in range(10):
        log = DataLog(
            ocr_text=f"Search Text {i}",
            confidence_score=0.8,
            image_path=f"/search/{i}.jpg",
            camera_id=2 if i % 2 == 0 else 3,
            camera_angle_x=0.1,
            camera_angle_y=0.2,
            camera_angle_z=0.3,
            frame_number=i,
            frame_drop=(i % 3 == 0),
            status="valid" if i < 5 else "invalid",
            timestamp=now - timedelta(minutes=10 - i),
        )
        db_session.add(log)
    await db_session.commit()

    start_time = (now - timedelta(minutes=11)).isoformat() + "Z"
    end_time = (now + timedelta(minutes=1)).isoformat() + "Z"

    response = await client.get(
        "/api/data/search",
        params={
            "start_time": start_time,
            "end_time": end_time,
            "camera_id": 2,
            "status": "valid",
            "limit": 5,
            "offset": 0,
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "data" in response.json()["data"]
    assert "total" in response.json()["data"]

    # Based on test data, camera_id 2 and status 'valid'
    # Should get 'Search Text 0', 'Search Text 2', 'Search Text 4'
    assert response.json()["data"]["total"] == 3
    assert len(response.json()["data"]["data"]) == 3
    assert (
        response.json()["data"]["data"][0]["ocr_text"] == "Search Text 4"
    )  # Ordered descending by timestamp


@pytest.mark.asyncio
async def test_get_frame_drop_statistics(client: AsyncClient, db_session: AsyncSession):
    # Add some test data
    now = datetime.utcnow()
    for i in range(20):
        log = DataLog(
            ocr_text=f"Stat Text {i}",
            confidence_score=0.7,
            image_path=f"/stat/{i}.jpg",
            camera_id=4,
            camera_angle_x=0.1,
            camera_angle_y=0.2,
            camera_angle_z=0.3,
            frame_number=i,
            frame_drop=(i % 5 == 0),  # Every 5th frame is dropped
            timestamp=now - timedelta(seconds=20 - i),
        )
        db_session.add(log)
    await db_session.commit()

    start_time = (now - timedelta(seconds=25)).isoformat() + "Z"
    end_time = (now + timedelta(seconds=5)).isoformat() + "Z"

    response = await client.get(
        "/api/stats/frame-drop",
        params={"start_time": start_time, "end_time": end_time, "camera_id": 4},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["data"]["total_frames"] == 20
    assert response.json()["data"]["dropped_frames"] == 4  # 0, 5, 10, 15
    assert response.json()["data"]["drop_rate"] == 20.0
    assert "stats_by_minute" in response.json()["data"]
