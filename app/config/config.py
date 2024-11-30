# Native imports
from typing import Text
from multiprocessing import cpu_count
# 3rd party imports
from pydantic import Field
from pydantic_settings import BaseSettings

# Project imports
from .constants import Env


class Settings(BaseSettings):
    # App configuration
    app_name: Text = "app-name"
    app_version: Text = "0.1.0"
    app_env: Text = Field(Env.Dev, env="APP_ENV")
    app_port: int = Field(5000, env="APP_PORT")

    # Deploy configuration
    workers: int = Field(cpu_count() * 2, env="WORKERS")

    # Papertrail configuration
    pt_host: str = "logs3.papertrailapp.com"
    pt_port: int = 33780

    class Config:
        env_file = ".env"
        case_sensitive = False

    # Database configuration
    db_host: str = Field("localhost", env="DB_HOST")
    db_port: int = Field(5432, env="DB_PORT")
    db_name: str = Field("postgres", env="DB_NAME")
    db_user: str = Field("postgres", env="DB_USER")
    db_password: str = Field("postgres", env="DB_PASSWORD")
    


settings = Settings()


class Config:
    DEBUG = not settings.app_env == Env.Prd
    ENV = "production" if settings.app_env == Env.Prd else "dev"
    VERSION = settings.app_version
