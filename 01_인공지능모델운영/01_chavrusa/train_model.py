"""Train and persist a simple Iris classifier."""

from pathlib import Path

import joblib
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


MODEL_PATH = Path(__file__).resolve().parent / "iris_model.pkl"


def train_and_save_model(output_path: Path = MODEL_PATH) -> None:
    """Train a classifier on the Iris dataset and serialize the fitted model."""
    iris = load_iris()
    X_train, X_test, y_train, _ = train_test_split(
        iris.data, iris.target, test_size=0.2, random_state=42, stratify=iris.target
    )
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    joblib.dump(clf, output_path)
    print(f"Saved Iris model to {output_path}")


def main() -> None:
    """Entry point for standalone training runs."""
    train_and_save_model()


if __name__ == "__main__":
    main()
