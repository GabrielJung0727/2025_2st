import os
import tempfile
from typing import Optional

import google.generativeai as genai
from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

# Load .env even when running from api/ folder
load_dotenv(find_dotenv())

# Configure Gemini client once at startup
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Create a .env file from .env.example or export the variable."
    )

genai.configure(api_key=API_KEY)
MODEL_NAME = os.getenv("GEMINI_MODEL", "models/gemini-1.5-flash")
model = genai.GenerativeModel(MODEL_NAME)

app = FastAPI(title="Gemini FastAPI Starter", version="0.1.0")


@app.get("/")
def root() -> dict:
    return {
        "message": "Gemini FastAPI Starter running. See /docs for interactive docs.",
        "endpoints": ["/health", "/chat", "/files", "/rag"],
    }


class ChatRequest(BaseModel):
    query: str
    context: Optional[str] = None


class RAGQuery(BaseModel):
    prompt: str
    file_uri: str


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "model": MODEL_NAME}


@app.post("/chat")
def chat(req: ChatRequest) -> dict:
    """Simple text generation endpoint."""
    prompt = req.query if not req.context else f"{req.query}\n\nContext:\n{req.context}"
    try:
        response = model.generate_content(prompt)
    except Exception as exc:  # pragma: no cover - surface API errors clearly
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"response": response.text}


@app.post("/files")
async def upload_to_file_search(file: UploadFile = File(...)) -> dict:
    """Uploads a file to Gemini's File Search API and returns its URI."""
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        uploaded_file = genai.upload_file(path=tmp_path, display_name=file.filename)
    except Exception as exc:  # pragma: no cover - surface API errors clearly
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"file_uri": uploaded_file.uri, "display_name": uploaded_file.display_name}


@app.post("/rag")
def rag(req: RAGQuery) -> dict:
    """Retrieval-augmented generation that grounds responses on a previously uploaded file."""
    try:
        file_handle = genai.get_file(req.file_uri)
        response = model.generate_content([file_handle, req.prompt])
    except Exception as exc:  # pragma: no cover - surface API errors clearly
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"response": response.text}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
