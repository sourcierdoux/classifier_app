import json
from pathlib import Path
from typing import List

# Load config.json
config_path = Path(__file__).parent.parent / "config.json"
with open(config_path, "r") as f:
    config_data = json.load(f)


class Config:
    # App settings
    APP_NAME = config_data["app"]["name"]
    APP_VERSION = config_data["app"]["version"]

    # Classifier settings
    DEFAULT_MODE = config_data["classifier"]["default_mode"]
    DEFAULT_USE_FILTER = config_data["classifier"]["default_use_filter"]
    DEFAULT_ASYNC_MODE = config_data["classifier"]["default_async_mode"]
    DEFAULT_MAX_CONCURRENCY = config_data["classifier"]["default_max_concurrency"]
    MAX_CONCURRENCY_LIMIT = config_data["classifier"]["max_concurrency_limit"]
    ALLOWED_FILE_TYPES = config_data["classifier"]["allowed_file_types"]
    OUTPUT_DIRECTORY = config_data["classifier"]["output_directory"]

    # Storage settings
    TEST_HISTORY_FILE = config_data["storage"]["test_history_file"]
    MAX_HISTORY_ITEMS = config_data["storage"]["max_history_items"]


config = Config()
