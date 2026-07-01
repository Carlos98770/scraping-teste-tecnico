import json
from pathlib import Path

from scraper.config import RAW_DATA_PATH


def save_raw(raw: list[dict]) -> None:

    Path(RAW_DATA_PATH).parent.mkdir(parents=True, exist_ok=True)

    with open(RAW_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=4)


def load_raw() -> list[dict]:

    with open(RAW_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)