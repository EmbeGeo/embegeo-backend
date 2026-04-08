import asyncio

from app.database.connection import async_engine
from app.models.base import \
    Base  # Make sure to import Base from your models module


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
