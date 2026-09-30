from services.interview_service import evaluate_answer


def test_evaluate_answer_returns_score():
    result = evaluate_answer('Explain your project', 'I built a Python API using Flask and SQL with a clear workflow and output.')
    assert 'relevance' in result
    assert 'technical_content' in result
    assert 'improvement' in result
