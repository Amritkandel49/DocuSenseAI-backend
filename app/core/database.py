from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from app.core.config import settings


engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo = True
)

AsyncSessionLocal = async_sessionmaker(
    bind = engine,
    autocommit = False,
    autoflush = False,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

from app.models.user import User

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
            




