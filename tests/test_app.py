import logging

import app as app_module
from app import app
from services.gemini_service import GeminiServiceError


CAREER_PROFILE = {
    'name': 'Test User',
    'target_role': 'Python Developer',
    'current_skills': 'Python',
    'education': 'BSc',
    'skill_level': 'Beginner',
    'preferred_domain': 'Backend',
    'study_time': '1 hour/day',
    'experience': '0 years',
    'projects': 'None',
}


def test_homepage_loads():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b'AI Career Guide' in response.data


def test_ai_status_route():
    client = app.test_client()
    response = client.get('/api/ai-status')
    assert response.status_code == 200
    data = response.get_json()
    assert 'configured' in data
    assert 'service' in data


def test_health_route():
    client = app.test_client()
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok'}


def test_career_route_returns_gemini_error_and_logs_traceback(monkeypatch, caplog):
    monkeypatch.setattr(app_module, 'generate_roadmap', lambda profile: {})
    monkeypatch.setattr(
        app_module.gemini_service,
        'generate_json',
        lambda prompt: (_ for _ in ()).throw(GeminiServiceError('GEMINI_API_KEY is missing.', 503)),
    )

    with caplog.at_level(logging.ERROR):
        response = app.test_client().post('/api/career/generate', json=CAREER_PROFILE)

    assert response.status_code == 503
    assert response.get_json() == {'success': False, 'error': 'GEMINI_API_KEY is missing.'}
    assert 'Career plan generation failed in Gemini service' in caplog.text
    assert 'Traceback (most recent call last)' in caplog.text


def test_career_route_returns_unexpected_backend_exception(monkeypatch, caplog):
    monkeypatch.setattr(
        app_module,
        'generate_roadmap',
        lambda profile: (_ for _ in ()).throw(RuntimeError('roadmap storage failed')),
    )

    with caplog.at_level(logging.ERROR):
        response = app.test_client().post('/api/career/generate', json=CAREER_PROFILE)

    assert response.status_code == 500
    assert response.get_json() == {'success': False, 'error': 'roadmap storage failed'}
    assert 'Traceback (most recent call last)' in caplog.text


def test_career_route_rejects_invalid_gemini_response(monkeypatch):
    monkeypatch.setattr(app_module, 'generate_roadmap', lambda profile: {})
    monkeypatch.setattr(app_module.gemini_service, 'generate_json', lambda prompt: {'priority': {}})

    response = app.test_client().post('/api/career/generate', json=CAREER_PROFILE)

    assert response.status_code == 502
    assert response.get_json() == {
        'success': False,
        'error': 'Gemini returned an invalid response. Expected the career plan to contain a roadmap list.',
    }


def test_career_route_returns_json_for_malformed_payload(caplog):
    with caplog.at_level(logging.ERROR):
        response = app.test_client().post('/api/career/generate', json=['not', 'an', 'object'])

    assert response.status_code == 500
    assert response.get_json()['success'] is False
    assert "'list' object has no attribute 'get'" in response.get_json()['error']
    assert 'Traceback (most recent call last)' in caplog.text
