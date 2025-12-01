"""Full pipeline orchestration for the AdventureWorks project."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict
from urllib.parse import quote

import pandas as pd
import requests

from . import data_access, db, eda, modeling, rfm
from .constants import BASE_DATA_URL, TABLE_SPECS
from .paths import PATHS
from .utils import save_dataframe, to_snake_case, write_json

logger = logging.getLogger(__name__)


def download_raw_tables(force: bool = False) -> None:
    """Download csv files from GitHub into the raw data directory."""
    for spec in TABLE_SPECS:
        destination = PATHS.raw_dir / f"{spec.table_name}.csv"
        if destination.exists() and not force:
            logger.info("Skipping download for %s", destination.name)
            continue
        url = f"{BASE_DATA_URL}/{quote(spec.source_file)}"
        logger.info("Downloading %s", url)
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        destination.write_bytes(response.content)


def load_into_sqlite() -> None:
    """Load downloaded csv files into sqlite tables."""
    for spec in TABLE_SPECS:
        csv_path = PATHS.raw_dir / f"{spec.table_name}.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Missing required csv: {csv_path}")
        df = pd.read_csv(csv_path)
        df.columns = [to_snake_case(col) for col in df.columns]
        logger.info("Writing %s (%d rows) to sqlite", spec.table_name, len(df))
        db.write_dataframe(df, spec.table_name, if_exists="replace")


def build_enriched_sales() -> pd.DataFrame:
    """Create a denormalized sales dataset for downstream analytics."""
    tables = data_access.load_sales_core()

    header = tables["sales_order_header"].copy()
    detail = tables["sales_order_detail"].copy()
    customer = tables["customer"]
    territory = tables["territory"][["territory_id", "name"]].rename(columns={"name": "territory_name"})
    address = tables["address"][["address_id", "city", "state_province_id", "postal_code"]].rename(
        columns={"address_id": "ship_to_address_id"}
    )
    state = tables["state"][["state_province_id", "name", "country_region_code"]].rename(
        columns={"name": "state_name"}
    )
    country = tables["country"][["country_region_code", "name"]].rename(columns={"name": "country_name"})
    product = tables["product"][
        ["product_id", "name", "product_number", "product_subcategory_id", "list_price", "color"]
    ].rename(columns={"name": "product_name"})
    subcategory = tables["subcategory"][["product_subcategory_id", "product_category_id", "name"]].rename(
        columns={"name": "subcategory_name"}
    )
    category = tables["category"][["product_category_id", "name"]].rename(columns={"name": "category_name"})

    header["order_date"] = pd.to_datetime(header["order_date"])
    header["ship_date"] = pd.to_datetime(header["ship_date"])
    header["due_date"] = pd.to_datetime(header["due_date"])
    detail["line_total"] = detail["line_total"].astype(float)
    header = header.merge(customer, on="customer_id", how="left", suffixes=("", "_customer"))
    header = header.merge(territory, on="territory_id", how="left")
    header = header.merge(address, on="ship_to_address_id", how="left")
    header = header.merge(state[["state_province_id", "state_name", "country_region_code"]], on="state_province_id", how="left")
    header = header.merge(country, on="country_region_code", how="left")

    product = product.merge(subcategory, on="product_subcategory_id", how="left")
    product = product.merge(category, on="product_category_id", how="left")
    detail = detail.merge(product, on="product_id", how="left")

    enriched = detail.merge(header, on="sales_order_id", how="left", suffixes=("", "_order"))
    selected_columns = [
        "sales_order_id",
        "sales_order_detail_id",
        "order_date",
        "ship_date",
        "customer_id",
        "person_id",
        "territory_id",
        "territory_name",
        "online_order_flag",
        "total_due",
        "sub_total",
        "tax_amt",
        "freight",
        "ship_to_address_id",
        "city",
        "state_name",
        "country_name",
        "postal_code",
        "product_id",
        "product_name",
        "product_number",
        "product_subcategory_id",
        "subcategory_name",
        "product_category_id",
        "category_name",
        "order_qty",
        "unit_price",
        "unit_price_discount",
        "line_total",
    ]
    enriched = enriched[selected_columns].copy()
    enriched["order_date"] = pd.to_datetime(enriched["order_date"])
    enriched["ship_date"] = pd.to_datetime(enriched["ship_date"])
    return enriched


def export_curated_datasets(enriched: pd.DataFrame) -> Dict[str, Path]:
    """Persist curated datasets for use by the API layer."""
    outputs = {}
    enriched_path = PATHS.processed_dir / "enriched_sales.parquet"
    save_dataframe(enriched, enriched_path)
    outputs["enriched_sales"] = enriched_path

    monthly = eda.monthly_sales(enriched)
    category = eda.category_performance(enriched)
    territory = eda.territory_performance(enriched)
    summary = eda.compute_summary(enriched)

    outputs["monthly_sales"] = PATHS.processed_dir / "monthly_sales.csv"
    outputs["category_sales"] = PATHS.processed_dir / "category_sales.csv"
    outputs["territory_sales"] = PATHS.processed_dir / "territory_sales.csv"
    save_dataframe(monthly, outputs["monthly_sales"])
    save_dataframe(category, outputs["category_sales"])
    save_dataframe(territory, outputs["territory_sales"])

    figures = eda.create_visualizations(monthly, category, territory)
    summary["figures"] = figures
    summary_path = PATHS.processed_dir / "summary.json"
    write_json(summary, summary_path)
    outputs["summary"] = summary_path

    rfm_df = rfm.compute_rfm(enriched)
    rfm_path = PATHS.processed_dir / "rfm_segments.parquet"
    save_dataframe(rfm_df, rfm_path)
    outputs["rfm"] = rfm_path
    rfm_summary = (
        rfm_df.groupby("segment")["customer_id"]
        .count()
        .reset_index()
        .rename(columns={"customer_id": "customer_count"})
        .sort_values("customer_count", ascending=False)
    )
    write_json(
        {
            "segments": rfm_summary.to_dict(orient="records"),
            "generated_rows": len(rfm_df),
        },
        PATHS.processed_dir / "rfm_summary.json",
    )

    orders = (
        enriched.groupby(
            ["sales_order_id", "customer_id", "territory_id", "order_date", "online_order_flag"]
        )
        .agg(total_due=("line_total", "sum"))
        .reset_index()
    )
    artifacts = modeling.train_next_purchase_model(
        modeling.build_next_purchase_dataset(orders)
    )
    write_json(
        {"metrics": artifacts.metrics, "feature_columns": artifacts.feature_columns},
        PATHS.processed_dir / "model_report.json",
    )
    outputs["model"] = artifacts.model_path
    return outputs
