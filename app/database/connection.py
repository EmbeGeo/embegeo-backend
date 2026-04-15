from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from app.config import settings

# MySQL connection string from settings
DATABASE_URL = settings.DATABASE_URL

# Create the asynchronous engine
# Pool options are crucial for performance in an async environment
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True if settings.DEBUG else False,  # Echo SQL statements for debugging
    pool_size=10,  # Adjust based on expected concurrency
    max_overflow=20,  # Max connections that can be opened beyond pool_size
    pool_timeout=30,  # seconds to wait for a connection
    pool_recycle=3600,  # recycle connections after an hour
    connect_args={"connect_timeout": 10},  # Timeout for initial connection
)

# Create a configured "Session" class
# This will be used to create new AsyncSession objects
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Important for async usage
)


async def get_async_db():
    """Dependency for getting an async database session."""
    async with AsyncSessionLocal() as session:
        yield session
