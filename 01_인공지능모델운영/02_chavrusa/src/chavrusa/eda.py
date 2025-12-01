"""EDA utilities and visualization helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .paths import PATHS

sns.set_theme(style="whitegrid")


def compute_summary(enriched: pd.DataFrame) -> Dict[str, float]:
    total_revenue = enriched["line_total"].sum()
    total_orders = enriched["sales_order_id"].nunique()
    total_customers = enriched["customer_id"].nunique()
    avg_order_value = total_revenue / max(total_orders, 1)
    return {
        "total_revenue": round(float(total_revenue), 2),
        "total_orders": int(total_orders),
        "total_customers": int(total_customers),
        "avg_order_value": round(float(avg_order_value), 2),
        "data_period_start": enriched["order_date"].min().date().isoformat(),
        "data_period_end": enriched["order_date"].max().date().isoformat(),
    }


def monthly_sales(enriched: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        enriched.assign(month=enriched["order_date"].dt.to_period("M").dt.to_timestamp())
        .groupby("month")["line_total"]
        .sum()
        .reset_index()
        .sort_values("month")
    )
    return monthly


def category_performance(enriched: pd.DataFrame) -> pd.DataFrame:
    return (
        enriched.groupby("category_name")["line_total"]
        .sum()
        .reset_index()
        .sort_values("line_total", ascending=False)
    )


def territory_performance(enriched: pd.DataFrame) -> pd.DataFrame:
    return (
        enriched.groupby("territory_name")["line_total"]
        .sum()
        .reset_index()
        .sort_values("line_total", ascending=False)
    )


def create_visualizations(monthly: pd.DataFrame, category: pd.DataFrame, territory: pd.DataFrame) -> Dict[str, str]:
    figures = {}
    figures["monthly_sales"] = _plot_line(
        monthly,
        x_col="month",
        y_col="line_total",
        title="Monthly Sales Trend",
        filename="monthly_sales.png",
    )
    figures["category_share"] = _plot_bar(
        category.head(10),
        x_col="line_total",
        y_col="category_name",
        title="Top Categories by Revenue",
        filename="category_share.png",
    )
    figures["territory_sales"] = _plot_bar(
        territory,
        x_col="line_total",
        y_col="territory_name",
        title="Revenue by Territory",
        filename="territory_sales.png",
    )
    return figures


def _plot_line(df: pd.DataFrame, x_col: str, y_col: str, title: str, filename: str) -> str:
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df[x_col], df[y_col], marker="o")
    ax.set_title(title)
    ax.set_xlabel("")
    ax.set_ylabel("Revenue")
    fig.autofmt_xdate()
    path = PATHS.figures_dir / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return str(path.relative_to(PATHS.root))


def _plot_bar(df: pd.DataFrame, x_col: str, y_col: str, title: str, filename: str) -> str:
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(data=df, x=x_col, y=y_col, ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Revenue")
    ax.set_ylabel("")
    fig.tight_layout()
    path = PATHS.figures_dir / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    return str(path.relative_to(PATHS.root))
