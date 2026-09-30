from app import app


def test_resume_route_requires_file():
    client = app.test_client()
    response = client.post('/api/resume/analyze', data={'target_role': 'Python Developer'})
    assert response.status_code == 400
