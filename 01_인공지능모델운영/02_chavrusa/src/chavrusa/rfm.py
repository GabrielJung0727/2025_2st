"""Customer RFM segmentation utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd

SEGMENT_RULES = {
    "Champions": ((4, 5), (4, 5), (4, 5)),
    "Loyal": ((2, 5), (3, 5), (3, 5)),
    "Potential Loyalist": ((3, 5), (2, 4), (2, 4)),
    "Need Attention": ((2, 3), (2, 3), (2, 3)),
    "At Risk": ((1, 2), (3, 5), (3, 5)),
    "Hibernating": ((1, 2), (1, 2), (1, 2)),
}


def compute_rfm(enriched: pd.DataFrame) -> pd.DataFrame:
    """Compute recency, frequency, and monetary scores for each customer."""
    snapshot_date = enriched["order_date"].max() + pd.Timedelta(days=1)
    grouped = (
        enriched.groupby("customer_id")
        .agg(
            last_order=("order_date", "max"),
            frequency=("sales_order_id", pd.Series.nunique),
            monetary=("line_total", "sum"),
        )
        .reset_index()
    )
    grouped["recency"] = (snapshot_date - grouped["last_order"]).dt.days
    grouped["recency_score"] = pd.qcut(grouped["recency"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
    grouped["frequency_score"] = pd.qcut(grouped["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    grouped["monetary_score"] = pd.qcut(grouped["monetary"], 5, labels=[1, 2, 3, 4, 5]).astype(int)
    grouped["segment"] = grouped.apply(_label_segment, axis=1)
    return grouped


def _label_segment(row: pd.Series) -> str:
    r, f, m = row["recency_score"], row["frequency_score"], row["monetary_score"]
    for segment, (r_range, f_range, m_range) in SEGMENT_RULES.items():
        if _in_range(r, r_range) and _in_range(f, f_range) and _in_range(m, m_range):
            return segment
    return "Others"


def _in_range(value: int, bounds: tuple[int, int]) -> bool:
    return bounds[0] <= value <= bounds[1]

