from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
    )

    #Настройки Базы данных
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    #Переменные из .env, которые понадобятся при проверке
    HOURS_LIMIT: int
    DISTANCE_LIMIT: int
    TIME_ZONE: str

    @property
    def ASYNC_DATABASE_URL(self):
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'


settings = Settings()