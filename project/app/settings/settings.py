from functools import lru_cache
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


load_dotenv()


class EnvSettings(BaseSettings):
    env: str


class Settings(BaseSettings):
    env_settings: EnvSettings = EnvSettings()

    class Config:
        extra = "forbid"


@lru_cache
def get_settings():
    return Settings()
