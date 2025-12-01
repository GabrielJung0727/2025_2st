"""Single FastAPI server that mounts a Gradio UI alongside the REST API."""

import os

os.environ.setdefault("FASTAPI_URL", "http://127.0.0.1:8000/api/predict/")

import gradio as gr
import uvicorn
from fastapi import FastAPI

from api import router as prediction_router
from app_gradio import build_interface


def create_app() -> FastAPI:
    """Create FastAPI app, include router, and mount the Gradio interface."""
    app = FastAPI(title="FastAPI + mounted Gradio")
    # Browsing /api/predict with GET will return 405; use POST from Swagger or /gradio.
    app.include_router(prediction_router, prefix="/api")
    gradio_ui = build_interface()
    gr.mount_gradio_app(app, gradio_ui, path="/gradio")
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("main_gradio_mount:app", host="127.0.0.1", port=8000, log_level="info")
