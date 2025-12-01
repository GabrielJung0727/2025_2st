"""FastAPI backend that loads the stored Iris model and serves predictions."""

from pathlib import Path
from typing import Dict

import joblib
import numpy as np
from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sklearn.datasets import load_iris

MODEL_PATH = Path(__file__).resolve().parent / "iris_model.pkl"


class IrisFeatures(BaseModel):
    """Input schema for Iris species prediction."""

    sepal_length: float = Field(..., gt=0, description="Sepal length in centimeters")
    sepal_width: float = Field(..., gt=0, description="Sepal width in centimeters")
    petal_length: float = Field(..., gt=0, description="Petal length in centimeters")
    petal_width: float = Field(..., gt=0, description="Petal width in centimeters")


class PredictionResponse(BaseModel):
    """Response schema for prediction requests."""

    prediction: str
    probabilities: Dict[str, float]


router = APIRouter()


def load_model(path: Path = MODEL_PATH):
    """Lazy-load the persisted classifier."""
    if not path.exists():
        raise FileNotFoundError(f"Model file not found at {path}")
    return joblib.load(path)


@router.post(
    "/predict/",
    response_model=PredictionResponse,
    summary="Predict the Iris species",
    description="Expose a POST endpoint for UI clients that submit feature values.",
)
def predict_species(features: IrisFeatures):
    """Handle POST requests from UIs; raises HTTP 422 for invalid input."""
    try:
        clf = load_model()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    array = np.array(
        [[features.sepal_length, features.sepal_width, features.petal_length, features.petal_width]]
    )
    preds = clf.predict(array)
    probs = clf.predict_proba(array)[0]
    target_names = {idx: name for idx, name in enumerate(load_iris().target_names)}
    return {
        "prediction": target_names[preds[0]],
        "probabilities": {
            target_names[idx]: float(prob) for idx, prob in enumerate(probs)
        },
    }


app = FastAPI(
    title="Iris Prediction API",
    description="Expose /predict/ as a POST API for downstream UI clients.",
    version="0.1.0",
)


@app.get("/")
def root():
    """Explain how to use the API when navigating via browser."""
    return {"detail": "Send POST requests to /predict/ with sepal/petal measurements."}


app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="127.0.0.1", port=8000, log_level="info")
