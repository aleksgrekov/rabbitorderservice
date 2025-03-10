from typing import Annotated, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.db_config import db_settings

# Формируем URL для подключения к базе данных
DB_URL: str = db_settings.db_url(driver="asyncpg")

# Создание асинхронного движка базы данных с использованием SQLAlchemy
engine = create_async_engine(DB_URL, echo=False)

# Создание фабрики сессий для работы с асинхронной базой данных
SessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)
