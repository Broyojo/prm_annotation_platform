from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME = "PRM Annotation Platform"

    # TODO:
    # configure to load from .env or CLI


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
