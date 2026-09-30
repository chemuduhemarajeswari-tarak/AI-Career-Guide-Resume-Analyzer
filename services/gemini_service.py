"""The sole integration point for Google Gemini; failures never expose secrets."""

from __future__ import annotations

import json
import logging
import os

from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()


class GeminiError(RuntimeError):
    """Safe, user-facing AI service failure."""


MESSAGES = {
    "missing": "Gemini API key is not configured. Add GEMINI_API_KEY to your .env file.",
    "auth": "Gemini authentication failed. Please verify your API key.",
    "quota": "Gemini API usage limit has been reached. Please try again later.",
    "network": "Unable to connect to the AI service. Check your internet connection and try again.",
    "response": "The AI response could not be processed. Please try again.",
    "unavailable": "The AI service is temporarily unavailable. Please try again later.",
}


def configured() -> bool:
    return bool(GEMINI_API_KEY)


def generate_json(prompt: str) -> dict:
    if not configured():
        raise GeminiError(MESSAGES["missing"])
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_API_KEY, http_options=types.HttpOptions(timeout=15_000))
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        result = json.loads(response.text or "")
        if not isinstance(result, dict):
            raise ValueError("Expected a JSON object")
        return result
    except GeminiError:
        raise
    except Exception as error:
        logging.exception("Gemini request failed")
        detail = str(error).lower()
        if any(term in detail for term in ("api_key_invalid", "api key not valid", "unauthorized", "401")):
            category = "auth"
        elif any(term in detail for term in ("quota", "resource_exhausted", "429", "rate limit")):
            category = "quota"
        elif any(term in detail for term in ("timeout", "connection", "network", "dns")):
            category = "network"
        elif isinstance(error, (json.JSONDecodeError, AttributeError, ValueError)):
            category = "response"
        else:
            category = "unavailable"
        raise GeminiError(MESSAGES[category]) from error
