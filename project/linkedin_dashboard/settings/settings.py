from functools import lru_cache

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()

class EnvSettings(BaseSettings):
    environment: str


class DatasetSettings(BaseSettings):
    job_postings_path: str
    job_skills_path: str
    skills_path: str


class Settings(BaseSettings):
    env_settings: EnvSettings = EnvSettings()
    dataset_settings: DatasetSettings = DatasetSettings()

    class Config:
        extra = "forbid"


@lru_cache
def get_settings():
    return Settings()
