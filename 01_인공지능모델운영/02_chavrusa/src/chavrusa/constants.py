"""Static metadata for dataset ingestion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

BASE_DATA_URL = "https://raw.githubusercontent.com/olafusimichael/AdventureWorksCSV/main"


@dataclass(frozen=True)
class TableSpec:
    """Represents a csv file that is ingested into sqlite."""

    table_name: str
    source_file: str


TABLE_SPECS: List[TableSpec] = [
    TableSpec("sales_salesorderheader", "Sales SalesOrderHeader.csv"),
    TableSpec("sales_salesorderdetail", "Sales SalesOrderDetail.csv"),
    TableSpec("sales_customer", "Sales Customer.csv"),
    TableSpec("sales_salesterritory", "Sales SalesTerritory.csv"),
    TableSpec("person_person", "Person Person.csv"),
    TableSpec("person_address", "Person Address.csv"),
    TableSpec("person_stateprovince", "Person StateProvince.csv"),
    TableSpec("person_countryregion", "Person CountryRegion.csv"),
    TableSpec("production_product", "Production Product.csv"),
    TableSpec("production_productsubcategory", "Production ProductSubcategory.csv"),
    TableSpec("production_productcategory", "Production ProductCategory.csv"),
    TableSpec("sales_specialofferproduct", "Sales SpecialOfferProduct.csv"),
    TableSpec("sales_store", "Sales Store.csv"),
]

