from typing import Annotated, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.db_config import db_settings

# Создаем асинхронный движок базы данных
DB_URL: str = db_settings.db_url(driver="asyncpg")
engine = create_async_engine(DB_URL, echo=False)

SessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)
