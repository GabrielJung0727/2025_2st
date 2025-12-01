"""Read frequently used AdventureWorks tables into pandas."""

from __future__ import annotations

from functools import lru_cache
from typing import Dict

import pandas as pd

from . import db


@lru_cache(maxsize=None)
def load_table(table_name: str) -> pd.DataFrame:
    return db.read_query(f"SELECT * FROM {table_name}")


def load_sales_core() -> Dict[str, pd.DataFrame]:
    """Loads the core fact/dimension tables needed for analytics."""
    tables = {
        "sales_order_header": load_table("sales_salesorderheader"),
        "sales_order_detail": load_table("sales_salesorderdetail"),
        "customer": load_table("sales_customer"),
        "territory": load_table("sales_salesterritory"),
        "person": load_table("person_person"),
        "address": load_table("person_address"),
        "state": load_table("person_stateprovince"),
        "country": load_table("person_countryregion"),
        "product": load_table("production_product"),
        "subcategory": load_table("production_productsubcategory"),
        "category": load_table("production_productcategory"),
    }
    return tables

