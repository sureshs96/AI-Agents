import os
import json
import yaml
from pathlib import Path
from research_and_analyst.logger import GLOBAL_LOGGER as log
from research_and_analyst.exception.custom_exception import CustomException
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

def _project_root() -> Path:
    """Returns the absolute path of the project root directory."""
    return Path(__file__).resolve().parent.parent

def load_config(config_path: str | None = None) -> dict:
    """ 
    Load YAML configuration from a consistent project level location.


    """
    try:
        env_path = os.getenv("CONFIG_PATH")

        if config_path is None:
            config_path = env_path if env_path else _project_root() / "config" / "configuration.yaml"

        path = Path(config_path)
        if not path.is_absolute():
            path = _project_root() / path

        if not path.exists():
            log.error(f"Configuration file not found", path=str(path))
            raise FileNotFoundError(f"Configuration file not found at: {path}")
        
        with open(path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file) or {}

        top_keys = list(config.keys()) if isinstance(config, dict) else []
        log.info(f"Configuration loaded successfully", path=str(path), top_level_keys=top_keys)

    except Exception as e:
        log.error(f"Error loading configuration: {e}")
        raise CustomException(f"Error loading configuration: {e}")

    return config

if __name__ == "__main__":
    try:
        config = load_config()
        print(json.dumps(config, indent=2))
        log.info("Configuration loaded and printed successfully.")
    except CustomException as ce:
        print(f"CustomException occurred: {ce}")
        log.error(f"CustomException occurred: ", error=str(ce))