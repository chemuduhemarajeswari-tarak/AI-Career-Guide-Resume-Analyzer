import json
import logging
import os
from typing import Any, Dict

from dotenv import load_dotenv


load_dotenv()
logger = logging.getLogger(__name__)


class GeminiServiceError(RuntimeError):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


class GeminiService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY', '').strip()
        self.client = None
        self.error = None
        self.enabled = bool(self.api_key and self.api_key != 'your_key_here')
        if self.enabled:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as exc:
                self.enabled = False
                self.error = str(exc)
                logger.exception('Gemini client initialization failed')

    def health(self):
        return {
            'configured': self.enabled,
            'service': 'Gemini'
        }

    def _parse_response(self, response):
        if response is None:
            raise GeminiServiceError('Gemini returned an invalid AI response: the response was empty.')
        text = getattr(response, 'text', None)
        if not isinstance(text, str):
            raise GeminiServiceError('Gemini returned an invalid AI response: expected a text response.')
        cleaned = text.strip()
        if not cleaned:
            raise GeminiServiceError('Gemini returned an invalid AI response: the response was empty.')
        if cleaned.startswith('```'):
            lines = cleaned.splitlines()
            if lines and lines[0].lower().startswith('```json'):
                lines = lines[1:]
            elif lines and lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            cleaned = '\n'.join(lines).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as first_error:
            start = cleaned.find('{')
            end = cleaned.rfind('}')
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(cleaned[start:end + 1])
                except json.JSONDecodeError as exc:
                    raise GeminiServiceError(
                        f'Gemini response JSON parsing error: {exc.msg} at line {exc.lineno}, column {exc.colno}.'
                    ) from exc
            raise GeminiServiceError(
                f'Gemini response JSON parsing error: {first_error.msg} at line {first_error.lineno}, column {first_error.colno}.'
            ) from first_error

    def generate_json(self, prompt: str, fallback: Any = None):
        if not self.enabled:
            if not self.api_key or self.api_key == 'your_key_here':
                raise GeminiServiceError('GEMINI_API_KEY is missing. Add a valid key to your .env file.', 503)
            raise GeminiServiceError(f'Gemini client could not be initialized: {self.error or "unknown initialization error"}', 502)
        try:
            response = self.client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
            )
            return self._parse_response(response)
        except GeminiServiceError:
            raise
        except Exception as exc:
            message = str(exc)
            lowered = message.lower()
            if 'quota' in lowered or 'resource exhausted' in lowered:
                raise GeminiServiceError(f'Gemini quota exceeded: {message}', 429) from exc
            if 'rate limit' in lowered or 'too many requests' in lowered or '429' in lowered:
                raise GeminiServiceError(f'Gemini rate limit reached: {message}', 429) from exc
            if 'api key' in lowered or 'authentication' in lowered or 'unauthorized' in lowered or 'forbidden' in lowered or '401' in lowered or '403' in lowered:
                raise GeminiServiceError(f'Gemini API key is invalid or unauthorized: {message}', 401) from exc
            if 'network' in lowered or 'connection' in lowered or 'timeout' in lowered:
                raise GeminiServiceError(f'Gemini network error: {message}', 502) from exc
            if 'permission' in lowered or 'denied' in lowered:
                raise GeminiServiceError(f'Gemini permission denied: {message}', 403) from exc
            raise GeminiServiceError(f'Gemini API error: {message}', 502) from exc


def get_gemini_service():
    return GeminiService()
