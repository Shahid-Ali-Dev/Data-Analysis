from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path
import yaml
from dotenv import load_dotenv

from pathlib import Path

load_dotenv()

ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = ROOT / "config.yaml"

@dataclass
class Settings:
    duckdb_path: Path = Path(os.getenv("BMI_DUCKDB_PATH", ROOT / "data" / "bmi.duckdb"))
    data_dir: Path = Path(os.getenv("BMI_DATA_DIR", ROOT / "data"))
    mlflow_uri: str = os.getenv("BMI_MLFLOW_TRACKING_URI", str(ROOT / "mlruns"))
    default_state: str = os.getenv("BMI_DEFAULT_STATE", "Maharashtra")
    default_mandi: str = os.getenv("BMI_DEFAULT_MANDI", "Nashik")
    default_commodity: str = os.getenv("BMI_DEFAULT_COMMODITY", "Onion")
    config: dict | None = None

    @classmethod
    def load(cls) -> "Settings":
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        s = cls()
        s.config = config
        return s

SETTINGS = Settings.load()
