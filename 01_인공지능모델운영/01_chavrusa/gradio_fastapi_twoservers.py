"""Example that launches FastAPI and Gradio as independent servers."""

from threading import Thread

import uvicorn

from app_gradio import build_interface
from api import app as fastapi_app


def _run_fastapi():
    """Start the FastAPI backend on 127.0.0.1:8000."""
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="info")


def _run_gradio():
    """Start the Gradio frontend on 127.0.0.1:7860."""
    interface = build_interface()
    interface.launch(share=False, server_name="127.0.0.1", server_port=7860)


def main():
    """Run both servers concurrently to simulate separate frontend/backend deployments."""
    api_thread = Thread(target=_run_fastapi, daemon=True)
    api_thread.start()
    _run_gradio()


if __name__ == "__main__":
    main()
