"""
End-to-end workflow for the Incheon departure congestion dataset:
  - Load CSVs fetched by scripts/fetch_departure_congestion.py
  - Clean and enrich timestamps
  - Quick EDA plots (time series, boxplots, residuals)
  - Baseline regression for congestion forecasting + residual analysis
  - LSTM forecasting model to minimize loss and enable short-term prediction

Run (after installing requirements in a virtualenv):
  python notebooks/departure_congestion_analysis.py --data data/*.csv --plot
  python notebooks/departure_congestion_analysis.py --data data/*.csv --train --epochs 30

The script keeps dependencies minimal; install via:
  pip install -r requirements.txt
"""
from __future__ import annotations

import argparse
import glob
import os
from dataclasses import dataclass
from typing import Iterable, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import torch
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from torch import nn

sns.set_theme(style="whitegrid")


def load_data(paths: Iterable[str]) -> pd.DataFrame:
    files: List[str] = []
    for p in paths:
        files.extend(glob.glob(p))
    if not files:
        raise FileNotFoundError("No CSV files matched --data")
    frames = []
    for f in files:
        df = pd.read_csv(f)
        frames.append(df)
    data = pd.concat(frames, ignore_index=True)
    # regdate format is yyyymmddHHMMSS from API
    data["regdate"] = pd.to_datetime(data["regdate"], format="%Y%m%d%H%M%S", errors="coerce")
    data = data.dropna(subset=["regdate"])
    data = data.sort_values("regdate")
    # normalize terminal/exit text
    for col in ["terminalid", "exitnumber", "gatenumber", "gateid"]:
        if col in data.columns:
            data[col] = data[col].astype(str).str.upper()
    # Some API responses use string numbers; coerce to numeric
    data["congestion"] = pd.to_numeric(data["congestion"], errors="coerce")
    if "waittime" in data.columns:
        data["waittime"] = pd.to_numeric(data["waittime"], errors="coerce")
    data = data.dropna(subset=["congestion"])
    # Time features
    data["minute"] = data["regdate"].dt.minute
    data["hour"] = data["regdate"].dt.hour
    data["dow"] = data["regdate"].dt.dayofweek
    data["day"] = data["regdate"].dt.day
    # Cyclic encodings to help models learn daily patterns
    data["hour_sin"] = np.sin(2 * np.pi * data["hour"] / 24)
    data["hour_cos"] = np.cos(2 * np.pi * data["hour"] / 24)
    data["dow_sin"] = np.sin(2 * np.pi * data["dow"] / 7)
    data["dow_cos"] = np.cos(2 * np.pi * data["dow"] / 7)
    return data.reset_index(drop=True)


def plot_quick_eda(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    sns.lineplot(ax=axes[0, 0], data=df, x="regdate", y="congestion", hue="terminalid", linewidth=1)
    axes[0, 0].set_title("Congestion over time by terminal")
    sns.boxplot(ax=axes[0, 1], data=df, x="terminalid", y="congestion")
    axes[0, 1].set_title("Distribution by terminal")
    sns.boxplot(ax=axes[1, 0], data=df, x="hour", y="congestion")
    axes[1, 0].set_title("By hour of day")
    sns.scatterplot(ax=axes[1, 1], data=df, x="regdate", y="congestion", hue="exitnumber", alpha=0.5, s=15)
    axes[1, 1].set_title("By exit number")
    plt.tight_layout()
    plt.show()


def build_regression(df: pd.DataFrame) -> Tuple[Pipeline, pd.DataFrame]:
    target = df["congestion"]
    feature_cols = [
        "terminalid",
        "gateid",
        "exitnumber",
        "gatenumber",
        "hour_sin",
        "hour_cos",
        "dow_sin",
        "dow_cos",
        "day",
    ]
    if "waittime" in df.columns:
        feature_cols.append("waittime")
    # Keep only columns that exist
    feature_cols = [c for c in feature_cols if c in df.columns]
    features = df[feature_cols]
    cat_cols = [c for c in ["terminalid", "gateid", "exitnumber", "gatenumber"] if c in features.columns]
    num_cols = [c for c in features.columns if c not in cat_cols]
    pre = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
            ("num", StandardScaler(), num_cols),
        ]
    )
    model = Pipeline([("prep", pre), ("lr", LinearRegression())])
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    residuals = y_test - preds
    metrics = pd.DataFrame(
        {
            "rmse": [np.sqrt(mean_squared_error(y_test, preds))],
            "mae": [mean_absolute_error(y_test, preds)],
        }
    )
    print("Baseline regression metrics:\n", metrics)
    res_df = pd.DataFrame({"actual": y_test, "pred": preds, "residual": residuals})
    sns.histplot(res_df["residual"], kde=True)
    plt.title("Residual distribution (baseline)")
    plt.show()
    return model, res_df


@dataclass
class LSTMConfig:
    lookback: int = 30  # minutes
    hidden_size: int = 64
    num_layers: int = 2
    lr: float = 1e-3
    epochs: int = 20
    train_split: float = 0.8
    device: str = "cpu"


class LSTMForecaster(nn.Module):
    def __init__(self, n_features: int, config: LSTMConfig):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=n_features,
            hidden_size=config.hidden_size,
            num_layers=config.num_layers,
            batch_first=True,
        )
        self.head = nn.Sequential(
            nn.Linear(config.hidden_size, config.hidden_size),
            nn.ReLU(),
            nn.Linear(config.hidden_size, 1),
        )

    def forward(self, x):
        out, _ = self.lstm(x)
        last = out[:, -1, :]
        return self.head(last)


def make_sequences(df: pd.DataFrame, config: LSTMConfig) -> Tuple[torch.Tensor, torch.Tensor]:
    feature_cols = ["congestion", "hour_sin", "hour_cos", "dow_sin", "dow_cos"]
    if "waittime" in df.columns:
        feature_cols.append("waittime")
    values = df[feature_cols].to_numpy()
    sequences = []
    targets = []
    for i in range(len(values) - config.lookback):
        seq = values[i : i + config.lookback]
        tgt = values[i + config.lookback, 0]
        sequences.append(seq)
        targets.append(tgt)
    X = torch.tensor(np.stack(sequences), dtype=torch.float32)
    y = torch.tensor(targets, dtype=torch.float32).unsqueeze(-1)
    return X, y


def train_lstm(df: pd.DataFrame, config: LSTMConfig) -> Tuple[LSTMForecaster, List[float], List[float]]:
    X, y = make_sequences(df, config)
    split_idx = int(len(X) * config.train_split)
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train, y_val = y[:split_idx], y[split_idx:]

    model = LSTMForecaster(n_features=X.shape[2], config=config).to(config.device)
    optim = torch.optim.Adam(model.parameters(), lr=config.lr)
    loss_fn = nn.MSELoss()
    train_loss_history: List[float] = []
    val_loss_history: List[float] = []
    for epoch in range(config.epochs):
        model.train()
        optim.zero_grad()
        preds = model(X_train)
        loss = loss_fn(preds, y_train)
        loss.backward()
        optim.step()

        model.eval()
        with torch.no_grad():
            val_pred = model(X_val)
            val_loss = loss_fn(val_pred, y_val)
        train_loss_history.append(loss.item())
        val_loss_history.append(val_loss.item())
        print(f"[Epoch {epoch+1}/{config.epochs}] train_loss={loss.item():.4f} val_loss={val_loss.item():.4f}")
    return model, train_loss_history, val_loss_history


def plot_training_curves(train_loss: List[float], val_loss: List[float]) -> None:
    plt.figure(figsize=(8, 4))
    plt.plot(train_loss, label="train")
    plt.plot(val_loss, label="val")
    plt.xlabel("Epoch")
    plt.ylabel("MSE loss")
    plt.title("LSTM training curves")
    plt.legend()
    plt.tight_layout()
    plt.show()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="EDA + forecasting for departure congestion")
    parser.add_argument("--data", nargs="+", required=True, help="CSV files or globs to load")
    parser.add_argument("--plot", action="store_true", help="Show EDA plots")
    parser.add_argument("--train", action="store_true", help="Train LSTM forecaster")
    parser.add_argument("--epochs", type=int, default=20, help="Epochs for LSTM")
    parser.add_argument("--lookback", type=int, default=30, help="History window (minutes)")
    parser.add_argument("--device", default="cpu", help="cpu or cuda")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = load_data(args.data)
    if args.plot:
        plot_quick_eda(df)

    _, res_df = build_regression(df)
    sns.scatterplot(data=res_df, x="pred", y="actual", alpha=0.5)
    plt.plot([res_df["pred"].min(), res_df["pred"].max()], [res_df["pred"].min(), res_df["pred"].max()], "r--")
    plt.title("Prediction vs actual (baseline)")
    plt.tight_layout()
    plt.show()

    if args.train:
        config = LSTMConfig(epochs=args.epochs, lookback=args.lookback, device=args.device)
        model, train_loss, val_loss = train_lstm(df, config)
        plot_training_curves(train_loss, val_loss)
        save_dir = "models"
        os.makedirs(save_dir, exist_ok=True)
        feature_order = ["congestion", "hour_sin", "hour_cos", "dow_sin", "dow_cos"]
        if "waittime" in df.columns:
            feature_order.append("waittime")
        torch.save(
            {"model_state": model.state_dict(), "config": config, "feature_order": feature_order},
            os.path.join(save_dir, "lstm_forecaster.pt"),
        )
        print(f"Saved model to {os.path.join(save_dir, 'lstm_forecaster.pt')}")


if __name__ == "__main__":
    main()
