# Incheon Departure Congestion Analysis

Pipeline to pull Incheon Airport departure congestion snapshots, run quick EDA, and train a forecasting model for short-term congestion prediction.

## Setup
- Python 3.10+ recommended.
- Install deps: `pip install -r requirements.txt`
- Export API key (URL-encoded service key from data.go.kr): `export INCHEON_API_KEY="..."`.

## Fetch data
```
python scripts/fetch_departure_congestion.py --pages 3 --rows 200 --out data/departure_congestion.csv --verbose
```
- Optional filters: `--terminal P01` (T1), `--gate DG2_E` (gate position), `--type xml|json` (API often returns XML regardless).
- The API exposes recent 1-minute snapshots; increase `--pages` to pull more history.

## Run analysis
```
python notebooks/departure_congestion_analysis.py --data data/departure_congestion.csv --plot --train --epochs 30
```
- `--plot` shows EDA charts and residuals for the baseline regression.
- `--train` fits an LSTM with lookback window (default 30 minutes) and saves `models/lstm_forecaster.pt`.
- Adjust `--lookback` to experiment with different history lengths.

## What the models do
- Baseline: linear regression with time-of-day/weekday cyclic encodings + terminal/exit/gate one-hot features; prints RMSE/MAE and residual distribution.
- Deep model: LSTM sequence-to-one forecaster on congestion with temporal encodings to reduce loss across epochs; training curves show progress and overfitting risk.

## Next steps
- Schedule the fetch script (cron or Airflow) to build a rolling dataset.
- Add holiday/flight schedule features to improve forecasts.
- Export trained model to ONNX or TorchScript for lightweight deployment. 
