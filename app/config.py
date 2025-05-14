import redis
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    '''Класс конфигурации'''

    #Настройки PostgreSQL
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    #Настройки Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    #Переменные, которые понадобятся при проверке
    HOURS_LIMIT: int
    DISTANCE_LIMIT: int
    TIME_ZONE: str

    @property
    def ASYNC_DATABASE_URL(self):
        '''Строка подключения к Базе Данных'''

        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'


settings = Settings()


#Асинхронная функция для создания Redis-клиента
async def create_redis_client():
    '''Создание асинхронного Redis-клиента'''

    return redis.asyncio.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=False
    )