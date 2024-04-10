from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


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

    class Config:
        env_file = ".env"


settings = Settings()
