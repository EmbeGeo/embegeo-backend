from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from app.config import settings

# MySQL connection string from settings
DATABASE_URL = settings.DATABASE_URL

# Create the asynchronous engine
# Pool options are crucial for performance in an async environment
async_engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    connect_args={"connect_timeout": 10},
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
