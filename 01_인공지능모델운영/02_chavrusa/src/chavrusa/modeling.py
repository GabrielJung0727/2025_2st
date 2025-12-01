"""Feature engineering and modeling for predictive services."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from .paths import PATHS


@dataclass
class ModelArtifacts:
    model_path: Path
    feature_columns: list[str]
    metrics: Dict[str, float]


def build_next_purchase_dataset(orders: pd.DataFrame) -> pd.DataFrame:
    """Constructs features for predicting days until the next purchase."""
    orders = orders.sort_values(["customer_id", "order_date"]).copy()
    orders["next_order_date"] = orders.groupby("customer_id")["order_date"].shift(-1)
    orders["prev_order_date"] = orders.groupby("customer_id")["order_date"].shift(1)
    orders["days_until_next"] = (orders["next_order_date"] - orders["order_date"]).dt.days
    orders["days_since_prev"] = (orders["order_date"] - orders["prev_order_date"]).dt.days.fillna(999)
    orders["order_sequence"] = orders.groupby("customer_id").cumcount() + 1
    orders["total_spend_to_date"] = orders.groupby("customer_id")["total_due"].cumsum()
    orders["avg_order_value_to_date"] = orders["total_spend_to_date"] / orders["order_sequence"]
    orders["tenure_days"] = (
        orders["order_date"] - orders.groupby("customer_id")["order_date"].transform("min")
    ).dt.days
    orders = orders.dropna(subset=["days_until_next"])
    feature_df = orders[
        [
            "customer_id",
            "order_date",
            "days_until_next",
            "days_since_prev",
            "order_sequence",
            "total_due",
            "avg_order_value_to_date",
            "tenure_days",
            "territory_id",
            "online_order_flag",
        ]
    ].copy()
    feature_df["online_order_flag"] = feature_df["online_order_flag"].astype(int)
    feature_df["territory_id"] = feature_df["territory_id"].fillna(-1)
    return feature_df


def train_next_purchase_model(feature_df: pd.DataFrame, *, random_state: int = 42) -> ModelArtifacts:
    X = feature_df[
        [
            "days_since_prev",
            "order_sequence",
            "total_due",
            "avg_order_value_to_date",
            "tenure_days",
            "territory_id",
            "online_order_flag",
        ]
    ]
    y = feature_df["days_until_next"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state
    )
    model = RandomForestRegressor(
        n_estimators=300,
        min_samples_leaf=2,
        random_state=random_state,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    metrics = {
        "mae": float(mean_absolute_error(y_test, preds)),
        "rmse": float(mean_squared_error(y_test, preds, squared=False)),
        "r2": float(r2_score(y_test, preds)),
    }
    model_path = PATHS.models_dir / "next_purchase_model.pkl"
    joblib.dump(model, model_path)
    return ModelArtifacts(model_path=model_path, feature_columns=list(X.columns), metrics=metrics)

