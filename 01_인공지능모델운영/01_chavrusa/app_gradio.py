"""Gradio frontend that submits user inputs to the FastAPI backend."""

import os
from typing import Dict

import gradio as gr
import requests

FASTAPI_URL = os.environ.get("FASTAPI_URL", "http://127.0.0.1:8000/predict/")


def predict_species(sepal_length: float, sepal_width: float, petal_length: float, petal_width: float):
    """Send measurements via POST to the FastAPI backend and parse the response."""
    payload = {
        "sepal_length": sepal_length,
        "sepal_width": sepal_width,
        "petal_length": petal_length,
        "petal_width": petal_width,
    }
    response = requests.post(FASTAPI_URL, json=payload, timeout=7)
    response.raise_for_status()
    return _format_response(response.json())


def _format_response(data: Dict[str, Dict]) -> str:
    prediction = data.get("prediction", "unknown")
    probabilities = data.get("probabilities", {})
    prob_str = "\n".join(f"{label}: {prob:.2%}" for label, prob in probabilities.items())
    return f"Predicted species: {prediction}\n\nProbabilities:\n{prob_str}"


def build_interface() -> gr.Interface:
    """Construct the Gradio interface for the mini-project."""
    slider_kwargs = dict(minimum=0.0, maximum=10.0, step=0.1)
    return gr.Interface(
        fn=predict_species,
        inputs=[
            gr.Slider(label="Sepal Length", **slider_kwargs),
            gr.Slider(label="Sepal Width", **slider_kwargs),
            gr.Slider(label="Petal Length", **slider_kwargs),
            gr.Slider(label="Petal Width", **slider_kwargs),
        ],
        outputs=gr.Textbox(label="Prediction"),
        title="Iris Predictor",
        description="Enter measurements and let the FastAPI backend predict the Iris species.",
    )


def main():
    """Launch the standalone Gradio client; set share=True to expose a public link."""
    interface = build_interface()
    interface.launch(share=True, server_name="127.0.0.1", server_port=7860)


if __name__ == "__main__":
    main()
