from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HOST: str
    PORT: int
    RELOAD: bool

    HOST_REDIS: str
    PORT_REDIS: str

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.HOST_REDIS}:{self.PORT_REDIS}"

    class Config:
        env_file = ".env"


settings = Settings()
