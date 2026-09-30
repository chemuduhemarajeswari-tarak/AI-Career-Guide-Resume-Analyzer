from types import SimpleNamespace

import pytest

from services.gemini_service import GeminiService, GeminiServiceError


class RaisingModel:
    def __init__(self, error):
        self.error = error

    def generate_content(self, **kwargs):
        raise self.error


@pytest.mark.parametrize(
    ('api_error', 'status_code', 'message_part'),
    [
        ('API key not valid', 401, 'invalid or unauthorized'),
        ('429 quota exceeded', 429, 'quota exceeded'),
        ('rate limit 429', 429, 'rate limit reached'),
        ('connection timeout', 502, 'network error'),
        ('unexpected provider failure', 502, 'Gemini API error'),
    ],
)
def test_gemini_api_errors_are_classified(api_error, status_code, message_part):
    service = GeminiService.__new__(GeminiService)
    service.enabled = True
    service.api_key = 'configured'
    service.error = None
    service.client = SimpleNamespace(models=RaisingModel(RuntimeError(api_error)))

    with pytest.raises(GeminiServiceError) as error:
        service.generate_json('{}')

    assert error.value.status_code == status_code
    assert message_part in str(error.value)
    assert api_error in str(error.value)


def test_missing_gemini_api_key_has_specific_error():
    service = GeminiService.__new__(GeminiService)
    service.enabled = False
    service.api_key = ''
    service.error = None

    with pytest.raises(GeminiServiceError) as error:
        service.generate_json('{}')

    assert error.value.status_code == 503
    assert 'GEMINI_API_KEY is missing' in str(error.value)


def test_invalid_json_response_has_parsing_error():
    service = GeminiService.__new__(GeminiService)

    with pytest.raises(GeminiServiceError, match='JSON parsing error'):
        service._parse_response(SimpleNamespace(text='not valid json'))


def test_empty_ai_response_has_invalid_response_error():
    service = GeminiService.__new__(GeminiService)

    with pytest.raises(GeminiServiceError, match='invalid AI response'):
        service._parse_response(None)