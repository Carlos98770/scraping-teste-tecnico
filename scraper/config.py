import os
from dotenv import load_dotenv

load_dotenv()

COOKIE = os.getenv("COOKIE", "")

BASE_URL = "https://teste-tecnico-dados.hubbi.app"
INERTIA_VER = "307ff2505cf92e67ab9812b871be52b0"

TOTAL_PAGES = 834
WORKERS = 10
REQUEST_TIMEOUT = 30

RAW_DATA_PATH = "data/raw/raw_parts.json"
PROCESSED_DATA_PATH = "data/processed/parts.csv"

LOG_FILE = "scraper.log"

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36"
)