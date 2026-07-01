# database/ingest.py

import logging

import pandas as pd
from sqlalchemy.exc import IntegrityError

from database.database import SessionLocal, engine
from database.models import Base, Part

log = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)


def ingest(df: pd.DataFrame) -> None:
  
    session = SessionLocal()

    try:
        inseridos = 0
        ignorados = 0

        existentes = {
            part_number
            for (part_number,) in session.query(Part.part_number).all()
        }

        for _, row in df.iterrows():

            part_number = row["PART_NUMBER"]

            if part_number in existentes:
                ignorados += 1
                continue

            produto = Part(
                id=int(row["ID"]),
                name=row["NAME"],
                product_url=row["PRODUCT_URL"],
                part_number=part_number,
                brand_name=row["BRAND_NAME"],
                category=row["CATEGORY"],
                type=row.get("TYPE"),
                price=float(row["PRICE"]) if pd.notna(row["PRICE"]) else None,
                gross_weight=float(row["GROSS_WEIGHT"]) if pd.notna(row["GROSS_WEIGHT"]) else None,
                width=float(row["WIDTH"]) if pd.notna(row["WIDTH"]) else None,
                length=float(row["LENGTH"]) if pd.notna(row["LENGTH"]) else None,
                warranty=row.get("WARRANTY"),
                material=row.get("MATERIAL"),
                photo_url=row.get("PHOTO_URL"),
                stock_quantity=(
                    int(row["STOCK_QUANTITY"])
                    if pd.notna(row["STOCK_QUANTITY"])
                    else None
                ),
                applications=row.get("APPLICATIONS"),
            )

            session.add(produto)

            existentes.add(part_number)

            inseridos += 1

        session.commit()

        log.info(
            "Ingestão concluída | Inseridos: %d | Ignorados: %d",
            inseridos,
            ignorados,
        )

    except IntegrityError as e:
        session.rollback()
        log.exception("Erro de integridade durante a ingestão.")
        raise e

    except Exception as e:
        session.rollback()
        log.exception("Erro inesperado durante a ingestão.")
        raise e

    finally:
        session.close()