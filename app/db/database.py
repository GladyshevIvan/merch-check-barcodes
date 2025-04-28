from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession, AsyncAttrs
from app.config import settings


engine = create_async_engine(settings.ASYNC_DATABASE_URL)  #Создание асинхронного движка Базы Данных
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)  #Создание фабрики сессий для взаимодействия с базой данных


async def get_async_session():
    async with async_session_maker() as session:
        yield session


#Базовый класс для всех моделей
class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True  #Класс абстрактный, чтобы не создавать отдельную таблицу для него