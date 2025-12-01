"""Thin wrapper around the Gemini API to keep the FastAPI endpoint lean."""
from __future__ import annotations

import logging
import os
from typing import Optional


class GeminiClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = None,
    ) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        # Default to a generally available text model; allow override via env or init.
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self._fallback_model = "gemini-1.5-flash"

    def _pick_supported_model(self, genai) -> Optional[str]:
        """Return the first available model that supports generateContent."""
        try:
            models = list(genai.list_models())
        except Exception:
            return None

        candidates = [
            m.name
            for m in models
            if "supported_generation_methods" in m.__dict__
            and "generateContent" in getattr(m, "supported_generation_methods", [])
        ]
        if not candidates:
            return None

        preferred = [m for m in candidates if "1.5" in m] or candidates
        return preferred[0]

    def generate(self, prompt: str) -> str:
        """Send a prompt to Gemini and return the generated text."""
        if not prompt.strip():
            return ""

        try:
            import google.generativeai as genai  # type: ignore
        except ImportError as exc:  # pragma: no cover - dependency notice
            raise RuntimeError(
                "google-generativeai package is required. Install it with 'pip install google-generativeai'."
            ) from exc

        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable is not set.")

        genai.configure(api_key=self.api_key)
        try:
            response = genai.GenerativeModel(self.model).generate_content(prompt)
        except Exception as exc:  # pragma: no cover - runtime path
            message = str(exc)
            not_found = "not found for API version" in message or "is not supported for generateContent" in message
            if not_found:
                # Try auto-discovering a supported model.
                auto_model = self._pick_supported_model(genai)
                if auto_model and auto_model != self.model:
                    logging.warning("Model '%s' unavailable, auto-selecting '%s'.", self.model, auto_model)
                    response = genai.GenerativeModel(auto_model).generate_content(prompt)
                    self.model = auto_model
                else:
                    raise RuntimeError(
                        f"Model '{self.model}' is unavailable for generateContent. "
                        "Set GEMINI_MODEL to a supported model such as 'gemini-1.5-flash' or 'gemini-1.5-pro-latest'."
                    ) from exc
            else:
                raise
        return getattr(response, "text", "") or ""
