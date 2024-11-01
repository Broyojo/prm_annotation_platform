import sys
from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings, cli_parse_args=True):
    project_name: str = "PRM Annotation Platform"
    db_url: str = "sqlite:///prmbench_database.db"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
