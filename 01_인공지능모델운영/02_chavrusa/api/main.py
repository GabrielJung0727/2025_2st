"""FastAPI application exposing AdventureWorks analytics services."""

from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR / "src"))

from chavrusa.paths import PATHS  # noqa: E402

app = FastAPI(
    title="AdventureWorks Sales Insights",
    version="1.0.0",
    description="Value-added analytics, segmentation, and forecasting on top of the AdventureWorks sales data.",
)


class PredictionRequest(BaseModel):
    days_since_prev: float = Query(..., ge=0)
    order_sequence: int = Query(..., ge=1)
    total_due: float = Query(..., ge=0)
    avg_order_value_to_date: float = Query(..., ge=0)
    tenure_days: float = Query(..., ge=0)
    territory_id: int = Query(..., ge=-1)
    online_order_flag: int = Query(..., ge=0, le=1)


class CustomerQuery(BaseModel):
    customer_id: int


class DataCache:
    """In-memory cache for processed artifacts."""

    def __init__(self) -> None:
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        processed = PATHS.processed_dir
        self.summary: Dict[str, object] = json.loads((processed / "summary.json").read_text())
        self.monthly = pd.read_csv(processed / "monthly_sales.csv", parse_dates=["month"])
        self.category = pd.read_csv(processed / "category_sales.csv")
        self.territory = pd.read_csv(processed / "territory_sales.csv")
        self.rfm = pd.read_parquet(processed / "rfm_segments.parquet")
        self.rfm_summary = json.loads((processed / "rfm_summary.json").read_text())
        self.enriched = pd.read_parquet(processed / "enriched_sales.parquet")
        self.enriched["order_date"] = pd.to_datetime(self.enriched["order_date"])
        self.order_history = (
            self.enriched.groupby(
                ["sales_order_id", "customer_id", "territory_id", "territory_name", "order_date", "online_order_flag"]
            )["line_total"]
            .sum()
            .reset_index()
            .rename(columns={"line_total": "order_value"})
            .sort_values("order_date")
        )
        model_report_path = processed / "model_report.json"
        self.model_report = json.loads(model_report_path.read_text())
        self.model = joblib.load(PATHS.models_dir / "next_purchase_model.pkl")

    def get_customer_rfm(self, customer_id: int) -> Dict[str, object]:
        row = self.rfm.loc[self.rfm["customer_id"] == customer_id]
        if row.empty:
            raise KeyError(f"Customer {customer_id} not found")
        result = row.iloc[0].to_dict()
        result["last_order"] = pd.to_datetime(result["last_order"]).date().isoformat()
        return result

    def get_customer_orders(self, customer_id: int, limit: int) -> List[Dict[str, object]]:
        subset = self.order_history[self.order_history["customer_id"] == customer_id]
        if subset.empty:
            raise KeyError(f"Customer {customer_id} not found")
        subset = subset.tail(limit)
        subset["order_date"] = subset["order_date"].dt.date
        return subset.to_dict(orient="records")

    def predict(self, payload: PredictionRequest) -> float:
        features = [payload.model_dump()[col] for col in self.model_report["feature_columns"]]
        prediction = self.model.predict(np.array([features]))[0]
        return float(prediction)


@lru_cache(maxsize=1)
def get_cache() -> DataCache:
    return DataCache()


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics/summary")
def metrics_summary() -> Dict[str, object]:
    return get_cache().summary


@app.get("/metrics/monthly")
def metrics_monthly() -> List[Dict[str, object]]:
    monthly = get_cache().monthly.copy()
    monthly["month"] = monthly["month"].dt.to_pydatetime()
    return [
        {"month": row["month"].date().isoformat(), "revenue": round(float(row["line_total"]), 2)}
        for _, row in monthly.iterrows()
    ]


@app.get("/metrics/categories")
def metrics_categories(top_k: int = Query(10, ge=1)) -> List[Dict[str, object]]:
    df = get_cache().category.head(top_k)
    return [
        {"category": row["category_name"], "revenue": round(float(row["line_total"]), 2)}
        for _, row in df.iterrows()
    ]


@app.get("/metrics/territories")
def metrics_territories() -> List[Dict[str, object]]:
    df = get_cache().territory
    return [
        {"territory": row["territory_name"], "revenue": round(float(row["line_total"]), 2)}
        for _, row in df.iterrows()
    ]


@app.get("/rfm/segments")
def rfm_segments() -> Dict[str, object]:
    return get_cache().rfm_summary


@app.get("/rfm/customers/{customer_id}")
def rfm_customer(customer_id: int) -> Dict[str, object]:
    try:
        return get_cache().get_customer_rfm(customer_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/customers/{customer_id}/orders")
def customer_orders(customer_id: int, limit: int = Query(25, ge=1, le=200)) -> List[Dict[str, object]]:
    try:
        orders = get_cache().get_customer_orders(customer_id, limit)
        for order in orders:
            order["order_date"] = order["order_date"].isoformat()
            order["online_order_flag"] = bool(order["online_order_flag"])
        return orders
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/forecast/next-purchase")
def forecast_next_purchase(payload: PredictionRequest) -> Dict[str, object]:
    prediction = get_cache().predict(payload)
    return {
        "predicted_days_until_next_purchase": round(prediction, 2),
        "model_metrics": get_cache().model_report["metrics"],
        "inputs": payload.model_dump(),
    }

