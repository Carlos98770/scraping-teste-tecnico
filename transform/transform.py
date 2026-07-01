import json
import logging
import pandas as pd
from scraper.config import BASE_URL

log = logging.getLogger(__name__)

def transform(raw: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(raw)

    df = df.rename(columns={"manufacturer_name": "brand_name"})

    text_cols = ["name", "part_number", "brand_name", "category",
                 "warranty", "material", "type"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.upper().replace("NONE", pd.NA)

    df["product_url"] = BASE_URL + "/peca/" + df["part_number"].str.upper()

    df["price"] = pd.to_numeric(df["price"], errors="coerce").round(2)

    for col in ["gross_weight", "width", "length"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].where(df[col] > 0, other=pd.NA)

    df["stock_quantity"] = pd.to_numeric(
        df["stock_quantity"], errors="coerce"
    ).astype("Int64")

    def serialize_applications(apps):
        if not isinstance(apps, list):
            return "[]"
        return json.dumps(
            [f"{a['make']} {a['model']} {a.get('years', '')}" for a in apps],
            ensure_ascii=False,
        )

    df["applications"] = df["applications"].apply(serialize_applications)

    df = df.drop_duplicates(subset="part_number")

    df.columns = df.columns.str.upper()

    final_cols = [
        "ID",
        "NAME",
        "PRODUCT_URL",
        "PART_NUMBER",
        "BRAND_NAME",
        "CATEGORY",
        "TYPE",
        "PRICE",
        "GROSS_WEIGHT",
        "WIDTH",
        "LENGTH",
        "WARRANTY",
        "MATERIAL",
        "PHOTO_URL",
        "STOCK_QUANTITY",
        "APPLICATIONS",
    ] 

    df = df[final_cols].reset_index(drop=True)

    log.info(f"Tratamento concluído: {len(df)} peças únicas")
    return df