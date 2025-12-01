from __future__ import annotations

import os
from pathlib import Path
from typing import Callable

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from data.database import initialize_db
from gemini_client import GeminiClient
from routers import creature, explorer

BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from a local .env file.
def _load_env() -> None:
    dotenv_path = BASE_DIR / ".env"
    if not dotenv_path.exists():
        return
    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv(dotenv_path=dotenv_path)
        return
    except Exception:
        # Fallback: minimal parser to avoid an extra dependency.
        for line in dotenv_path.read_text().splitlines():
            if not line or line.strip().startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


_load_env()

app = FastAPI(title="Gemini Chat + FastAPI CRUD", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


def get_gemini_client() -> GeminiClient:
    return GeminiClient()


@app.on_event("startup")
def on_startup() -> None:
    initialize_db()


@app.get("/")
def serve_index() -> FileResponse:
    index_path = BASE_DIR / "index.html"
    return FileResponse(index_path)


@app.post("/chat")
def chat(
    payload: ChatRequest, gemini: GeminiClient = Depends(get_gemini_client)
) -> JSONResponse:
    try:
        reply = gemini.generate(payload.message)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return JSONResponse({"reply": reply})


app.include_router(creature.router)
app.include_router(explorer.router)
