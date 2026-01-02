import json
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings

# Load config.json from root
config_path = Path(__file__).parent.parent / "config.json"
with open(config_path, "r") as f:
    config_data = json.load(f)


class Settings(BaseSettings):
    # App settings
    app_name: str = config_data["app"]["name"]
    app_version: str = config_data["app"]["version"]

    # Backend settings
    host: str = config_data["backend"]["host"]
    port: int = config_data["backend"]["port"]
    cors_origins: List[str] = config_data["backend"]["cors_origins"]

    # Classifier settings
    default_mode: str = config_data["classifier"]["default_mode"]
    default_use_filter: bool = config_data["classifier"]["default_use_filter"]
    default_async_mode: bool = config_data["classifier"]["default_async_mode"]
    default_max_concurrency: int = config_data["classifier"]["default_max_concurrency"]
    max_concurrency_limit: int = config_data["classifier"]["max_concurrency_limit"]
    allowed_file_types: List[str] = config_data["classifier"]["allowed_file_types"]
    output_directory: str = config_data["classifier"]["output_directory"]

    # Storage settings
    test_history_file: str = config_data["storage"]["test_history_file"]
    max_history_items: int = config_data["storage"]["max_history_items"]


settings = Settings()
