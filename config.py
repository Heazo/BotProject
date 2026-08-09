import logging
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Required environment variable is not set: {name}")
    return value


def _port() -> int:
    value = os.getenv("DB_PORT", "5432")
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError("DB_PORT must be an integer") from exc


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    vk_token: str
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    log_level: int


def load_settings() -> Settings:
    log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, None)
    if not isinstance(log_level, int):
        raise RuntimeError("LOG_LEVEL must be a valid logging level")

    return Settings(
        telegram_token=_required("TELEGRAM_TOKEN"),
        vk_token=_required("VK_TOKEN"),
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=_port(),
        db_name=os.getenv("DB_NAME", "studies_db"),
        db_user=os.getenv("DB_USER", "postgres"),
        db_password=_required("DB_PASSWORD"),
        log_level=log_level,
    )
