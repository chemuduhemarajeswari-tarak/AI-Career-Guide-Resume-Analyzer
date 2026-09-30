import random


QUESTION_BANK = {
    'python developer': [
        {'question': 'Explain how Python handles memory and scope in functions.', 'type': 'technical'},
        {'question': 'How would you build a REST API endpoint that reads and updates a database?', 'type': 'scenario'},
    ],
    'data analyst': [
        {'question': 'How do you decide which metrics are most useful for a business dashboard?', 'type': 'technical'},
        {'question': 'Describe a time you cleaned inconsistent data before analysis.', 'type': 'behavioral'},
    ],
    'web developer': [
        {'question': 'How do you make a layout responsive across screen sizes?', 'type': 'technical'},
        {'question': 'How do you structure a modern frontend project for maintainability?', 'type': 'project'},
    ],
    'software developer': [
        {'question': 'Describe a small project you built and explain your design choices.', 'type': 'project'},
        {'question': 'How would you debug a failing API request in a production system?', 'type': 'scenario'},
    ],
}


def generate_questions(target_role, resume_text=''):
    questions = QUESTION_BANK.get((target_role or 'software developer').lower(), QUESTION_BANK['software developer'])
    list_of_questions = []
    for index, item in enumerate(questions[:5], start=1):
        list_of_questions.append({
            'id': index,
            'category': item['type'],
            'question': item['question'],
            'what_interviewer_checks': 'The interviewer is checking clarity, technical understanding, and practical thinking.',
            'answer_structure': 'Start with a brief summary, explain the process, and close with the outcome and key lessons.',
            'important_points': ['Show relevant technical knowledge', 'Be concise', 'Use examples from real work or learning']
        })
    return list_of_questions


def evaluate_answer(question, answer):
    text = (answer or '').lower()
    score = min(100, max(30, len(text.split()) * 2))
    relevance = 85 if len(text) > 40 else 60
    clarity = 75 if len(text) > 50 else 55
    technical = min(95, max(40, (score + relevance) // 2))
    communication = min(96, max(35, (clarity + relevance) // 2))
    return {
        'relevance': relevance,
        'clarity': clarity,
        'technical_content': technical,
        'communication': communication,
        'structure': 72,
        'missing_points': ['Include more concrete project details', 'Mention the exact tools you used', 'Explain your contribution in more depth'],
        'improvement': 'Keep your answer structured by starting with the problem, process, and result. Mention tools and your personal contribution.'
    }
