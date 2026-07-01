import logging
from pathlib import Path

from scraper.config import (
    COOKIE,
    RAW_DATA_PATH,
    PROCESSED_DATA_PATH,
)
from scraper.scraper import fetch_all_parts
from scraper.storage import save_raw, load_raw
from transform.transform import transform
from database.ingest import ingest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

log = logging.getLogger(__name__)


def main():
    log.info("=== INICIANDO PIPELINE ETL ===")

    if Path(RAW_DATA_PATH).exists():
        log.info("Arquivo RAW encontrado. Pulando scraping...")
        raw = load_raw()
    else:
        log.info("Arquivo RAW não encontrado. Iniciando scraping...")
        raw = fetch_all_parts(COOKIE)

        log.info("Salvando dados brutos...")
        save_raw(raw)

    log.info("Transformando dados...")
    df = transform(raw)

    log.info("Salvando CSV tratado...")
    df.to_csv(
        PROCESSED_DATA_PATH,
        index=False,
        float_format="%.2f",
    )

    log.info("Realizando ingestão no SQLite...")
    ingest(df)

    log.info("=== PIPELINE FINALIZADO ===")


if __name__ == "__main__":
    main()