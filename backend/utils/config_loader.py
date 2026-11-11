from pathlib import Path
from backend.logger import GLOBAL_LOGGER as log
from dotenv import load_dotenv
import os
import yaml

load_dotenv()


def _project_root():
    return Path(__file__).resolve().parents[2]


def load_config(config_path: str = None):
    confpath = os.getenv("config_apth")

    if config_path is None:
        config_path = confpath

    path = Path(config_path)

    if not path.is_absolute():
        path = _project_root()/path

    log.info("current config path", path=path)

    if not path.exists():
        raise FileNotFoundError("config yaml file not found")

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
