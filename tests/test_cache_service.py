from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from app.schemas.data import DataLogResponse
from app.services.cache_service import CacheService


@pytest.mark.asyncio
async def test_cache_latest_data():
    mock_redis = AsyncMock()
    with patch("app.cache.redis_client.redis_client", mock_redis):
        cache_service = CacheService()
        test_data = DataLogResponse(
            id=1,
            timestamp=datetime.utcnow(),
            ocr_text="Test Text",
            confidence_score=0.99,
            image_path="/path/to/test.jpg",
            camera_id=1,
            camera_angle_x=0.1,
            camera_angle_y=0.2,
            camera_angle_z=0.3,
            frame_number=1,
            frame_drop=False,
            status="valid",
            error_message=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        await cache_service.cache_latest_data(test_data)
        mock_redis.set.assert_called_once_with(
            cache_service.LATEST_DATA_KEY, test_data.model_dump_json(), ex=3600
        )


@pytest.mark.asyncio
async def test_get_latest_data_hit():
    test_data = DataLogResponse(
        id=1,
        timestamp=datetime.utcnow(),
        ocr_text="Test Text",
        confidence_score=0.99,
        image_path="/path/to/test.jpg",
        camera_id=1,
        camera_angle_x=0.1,
        camera_angle_y=0.2,
        camera_angle_z=0.3,
        frame_number=1,
        frame_drop=False,
        status="valid",
        error_message=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    mock_redis = AsyncMock()
    mock_redis.get.return_value = test_data.model_dump_json()

    with patch("app.cache.redis_client.redis_client", mock_redis):
        cache_service = CacheService()
        result = await cache_service.get_latest_data()
        mock_redis.get.assert_called_once_with(cache_service.LATEST_DATA_KEY)
        assert result is not None
        assert result.id == test_data.id
        assert result.ocr_text == test_data.ocr_text


@pytest.mark.asyncio
async def test_get_latest_data_miss():
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    with patch("app.cache.redis_client.redis_client", mock_redis):
        cache_service = CacheService()
        result = await cache_service.get_latest_data()
        mock_redis.get.assert_called_once_with(cache_service.LATEST_DATA_KEY)
        assert result is None


@pytest.mark.asyncio
async def test_invalidate_latest():
    mock_redis = AsyncMock()
    with patch("app.cache.redis_client.redis_client", mock_redis):
        cache_service = CacheService()
        await cache_service.invalidate_latest()
        mock_redis.delete.assert_called_once_with(cache_service.LATEST_DATA_KEY)
