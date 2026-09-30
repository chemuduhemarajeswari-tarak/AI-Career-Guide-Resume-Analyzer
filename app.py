import logging
import os
import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from services.gemini_service import GeminiService, GeminiServiceError
from services.career_service import generate_roadmap, adapt_roadmap, get_daily_challenge, skill_priority
from services.resume_parser import extract_resume_text_from_upload
from services.ats_service import analyze_resume_vs_role, analyze_job_description
from services.job_portal_service import get_portals_for_role, generate_search_keywords
from services.interview_service import generate_questions, evaluate_answer
from services.project_service import recommend_projects, generate_project_explanation
from services.career_twin_service import compute_career_twin, career_readiness_indicator
from utils.json_handler import append_json, read_json, write_json
from utils.validators import validate_profile, validate_resume_form
from utils.security import sanitize_text, safe_upload_name, is_allowed_extension, validate_file_size

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
UPLOAD_DIR = BASE_DIR / 'uploads'


def ensure_data_files():
    DATA_DIR.mkdir(exist_ok=True)
    UPLOAD_DIR.mkdir(exist_ok=True)
    defaults = {
        'users.json': [],
        'career_plans.json': [],
        'resume_history.json': [],
        'saved_resources.json': [],
        'resources.json': [],
        'progress.json': {'completed_days': 0, 'remaining_days': 30, 'percentage': 0, 'streak': 0},
        'interview_history.json': [],
        'achievements.json': [],
    }
    for file_name, default in defaults.items():
        file_path = DATA_DIR / file_name
        if not file_path.exists():
            write_json(str(file_path), default)


app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = str(UPLOAD_DIR)
ensure_data_files()

gemini_service = GeminiService()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/career')
def career_page():
    return render_template('career.html')


@app.route('/roadmap')
def roadmap_page():
    progress = read_json(str(DATA_DIR / 'progress.json'), {'completed_days': 0, 'remaining_days': 30, 'percentage': 0, 'streak': 0})
    return render_template('roadmap.html', progress=progress)


@app.route('/resume')
def resume_page():
    return render_template('resume.html')


@app.route('/skill-gap')
def skill_gap_page():
    return render_template('skill_gap.html')


@app.route('/job-analyzer')
def job_analyzer_page():
    return render_template('job_analyzer.html')


@app.route('/jobs')
def jobs_page():
    return render_template('jobs.html')


@app.route('/interview')
def interview_page():
    return render_template('interview.html')


@app.route('/projects')
def projects_page():
    return render_template('projects.html')


@app.route('/career-twin')
def career_twin_page():
    return render_template('career_twin.html')


@app.route('/dashboard')
def dashboard_page():
    progress = read_json(str(DATA_DIR / 'progress.json'), {'completed_days': 0, 'remaining_days': 30, 'percentage': 0, 'streak': 0})
    return render_template('dashboard.html', progress=progress)


@app.route('/history')
def history_page():
    history = {
        'career_plans': read_json(str(DATA_DIR / 'career_plans.json'), []),
        'resume_history': read_json(str(DATA_DIR / 'resume_history.json'), []),
        'interviews': read_json(str(DATA_DIR / 'interview_history.json'), []),
    }
    return render_template('history.html', history=history)


@app.route('/api/health')
def api_health():
    return jsonify({'status': 'ok'})


@app.route('/api/ai-status')
def ai_status():
    if gemini_service.enabled:
        return jsonify({'configured': True, 'service': 'Gemini'})
    return jsonify({'configured': False, 'service': 'Gemini', 'message': gemini_service.error or 'GEMINI_API_KEY is missing or invalid.'})


@app.route('/api/career/generate', methods=['POST'])
def generate_career_profile():
    try:
        payload = request.form.to_dict() if request.form else request.get_json(silent=True) or {}
        errors = validate_profile(payload)
        if errors:
            return jsonify({'success': False, 'error': ' '.join(errors), 'errors': errors}), 400

        profile = {
            'name': sanitize_text(payload.get('name')),
            'target_role': sanitize_text(payload.get('target_role')),
            'current_skills': sanitize_text(payload.get('current_skills')),
            'education': sanitize_text(payload.get('education')),
            'skill_level': sanitize_text(payload.get('skill_level')),
            'preferred_domain': sanitize_text(payload.get('preferred_domain')),
            'study_time': sanitize_text(payload.get('study_time')),
            'experience': sanitize_text(payload.get('experience')),
            'projects': sanitize_text(payload.get('projects')),
        }

        result = generate_roadmap(profile)
        prompt = (
            'Create a personalized career plan for this user. Return only a valid JSON object, without markdown. '
            'Include target_role, profile, priority, roadmap (30 daily entries), and daily_challenge. '
            'Each roadmap entry should include day, topic, why_it_matters, what_to_learn, task, estimated_time, '
            'mini_challenge, resources, and completed. User profile:\n'
            f'{json.dumps(profile, indent=2)}'
        )
        gemini_data = gemini_service.generate_json(prompt)
        if not isinstance(gemini_data, dict):
            raise GeminiServiceError('Gemini returned an invalid response. Expected a JSON object for the career plan.')
        if not isinstance(gemini_data.get('roadmap'), list):
            raise GeminiServiceError('Gemini returned an invalid response. Expected the career plan to contain a roadmap list.')
        result = {**result, **gemini_data}

        append_json(str(DATA_DIR / 'users.json'), profile)
        append_json(str(DATA_DIR / 'career_plans.json'), result)
        write_json(str(DATA_DIR / 'progress.json'), {'completed_days': 0, 'remaining_days': 30, 'percentage': 0, 'streak': 0})
        return jsonify({'success': True, 'profile': profile, 'roadmap': result, 'demo': False})
    except GeminiServiceError as exc:
        logger.exception('Career plan generation failed in Gemini service')
        return jsonify({'success': False, 'error': str(exc)}), getattr(exc, 'status_code', 502)
    except Exception as exc:
        logger.exception('Unexpected career plan backend exception')
        return jsonify({'success': False, 'error': str(exc) or 'Unexpected backend exception while generating the career plan.'}), 500


@app.route('/api/roadmap/adapt', methods=['POST'])
def adapt_roadmap_route():
    payload = request.get_json(silent=True) or {}
    roadmap = payload.get('roadmap', [])
    completed = int(payload.get('completed_days', 0))
    missed = int(payload.get('missed_days', 0))
    available = payload.get('available_time', '1 hour/day')
    result = adapt_roadmap(roadmap, completed, missed, available)
    return jsonify({'success': True, 'result': result})


@app.route('/api/roadmap/progress', methods=['POST'])
def progress_route():
    payload = request.get_json(silent=True) or {}
    completed_days = int(payload.get('completed_days', 0))
    total_days = int(payload.get('total_days', 30))
    streak = int(payload.get('streak', 0))
    if payload.get('mark_complete'):
        streak += 1
    elif payload.get('mark_incomplete'):
        streak = max(0, streak - 1)

    progress = {
        'completed_days': completed_days,
        'remaining_days': max(0, total_days - completed_days),
        'percentage': round((completed_days / total_days) * 100) if total_days else 0,
        'streak': streak,
    }
    write_json(str(DATA_DIR / 'progress.json'), progress)
    return jsonify({'success': True, 'progress': progress})


@app.route('/api/resume/analyze', methods=['POST'])
def resume_analyze():
    if 'resume_file' not in request.files:
        return jsonify({'success': False, 'errors': ['Resume file is required.']}), 400
    uploaded = request.files['resume_file']
    target_role = sanitize_text(request.form.get('target_role'))
    if not uploaded or uploaded.filename == '':
        return jsonify({'success': False, 'errors': ['Resume file is required.']}), 400
    if not is_allowed_extension(uploaded.filename):
        return jsonify({'success': False, 'errors': ['Only PDF, DOCX, and TXT resume files are allowed.']}), 400
    if not validate_file_size(uploaded):
        return jsonify({'success': False, 'errors': ['File size must be under 10MB.']}), 400
    if not target_role:
        return jsonify({'success': False, 'errors': ['Target role is required.']}), 400

    safe_name = safe_upload_name(uploaded.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
    uploaded.save(file_path)
    try:
        resume_text = extract_resume_text_from_upload(file_path)
    except Exception as exc:
        return jsonify({'success': False, 'errors': [f'Resume parsing failed: {exc}']}), 400

    analysis = analyze_resume_vs_role(resume_text, target_role)
    append_json(str(DATA_DIR / 'resume_history.json'), {'target_role': target_role, 'resume_path': file_path, 'analysis': analysis})
    return jsonify({'success': True, 'analysis': analysis, 'demo': not gemini_service.enabled})


@app.route('/api/job-description/analyze', methods=['POST'])
def job_description_analyze():
    data = request.get_json(silent=True) or {}
    description = sanitize_text(data.get('job_description'))
    resume_text = sanitize_text(data.get('resume_text')) or 'Python SQL Git REST API JavaScript HTML CSS'
    if not description:
        return jsonify({'success': False, 'errors': ['Job description is required.']}), 400
    analysis = analyze_job_description(description, resume_text)
    return jsonify({'success': True, 'analysis': analysis})


@app.route('/api/skill-gap', methods=['POST'])
def skill_gap_analyze():
    data = request.get_json(silent=True) or {}
    profile = {
        'target_role': sanitize_text(data.get('target_role', 'Python Developer')),
        'current_skills': sanitize_text(data.get('current_skills', '')),
    }
    priority = skill_priority(profile)
    return jsonify({'success': True, 'priority': priority, 'learning_order': ['Must Learn', 'Important', 'Optional']})


@app.route('/api/projects/recommend', methods=['POST'])
def recommend_projects_route():
    data = request.get_json(silent=True) or {}
    target_role = sanitize_text(data.get('target_role', 'Python Developer'))
    missing_skills = data.get('missing_skills', [])
    current_skills = data.get('current_skills', [])
    projects = recommend_projects(target_role, missing_skills, current_skills, data.get('skill_level', 'Beginner'))
    return jsonify({'success': True, 'projects': projects})


@app.route('/api/projects/generate-resume-bullets', methods=['POST'])
def generate_project_resume_bullets():
    data = request.get_json(silent=True) or {}
    result = generate_project_explanation(
        data.get('project_name', 'Project'),
        data.get('technologies', 'Python'),
        data.get('description', 'A practical project'),
        data.get('contribution', 'I worked on the core implementation and validation'),
    )
    return jsonify({'success': True, 'result': result})


@app.route('/api/interview/start', methods=['POST'])
def interview_start():
    data = request.get_json(silent=True) or {}
    target_role = sanitize_text(data.get('target_role', 'Software Developer'))
    questions = generate_questions(target_role)
    append_json(str(DATA_DIR / 'interview_history.json'), {'target_role': target_role, 'questions': questions})
    return jsonify({'success': True, 'questions': questions})


@app.route('/api/interview/answer', methods=['POST'])
def interview_answer():
    data = request.get_json(silent=True) or {}
    question = sanitize_text(data.get('question', ''))
    answer = sanitize_text(data.get('answer', ''))
    evaluation = evaluate_answer(question, answer)
    return jsonify({'success': True, 'evaluation': evaluation})


@app.route('/api/jobs', methods=['GET'])
def jobs_api():
    target_role = 'Python Developer'
    return jsonify({'success': True, 'portals': get_portals_for_role(target_role), 'keywords': generate_search_keywords(target_role)})


@app.route('/api/career-twin')
def career_twin_api():
    profile = {'target_role': 'Python Developer', 'current_skills': 'Python, SQL, Git'}
    twin = compute_career_twin(profile, {'completed_days': 7}, 78, 60)
    return jsonify({'success': True, 'twin': twin})


@app.route('/api/dashboard')
def dashboard_api():
    progress = read_json(str(DATA_DIR / 'progress.json'), {'completed_days': 0, 'remaining_days': 30, 'percentage': 0, 'streak': 0})
    readiness = career_readiness_indicator({'current_skills': 'Python, SQL'}, progress, 78, 60, 2)
    return jsonify({'success': True, 'progress': progress, 'readiness': readiness})


@app.route('/api/history')
def history_api():
    return jsonify({
        'career_plans': read_json(str(DATA_DIR / 'career_plans.json'), []),
        'resume_history': read_json(str(DATA_DIR / 'resume_history.json'), []),
        'interview_history': read_json(str(DATA_DIR / 'interview_history.json'), []),
    })


@app.route('/api/resources/save', methods=['POST'])
def save_resource():
    data = request.get_json(silent=True) or {}
    if not data.get('name'):
        return jsonify({'success': False, 'errors': ['Resource name is required.']}), 400
    append_json(str(DATA_DIR / 'saved_resources.json'), data)
    return jsonify({'success': True, 'saved': data})


@app.route('/api/challenge/complete', methods=['POST'])
def complete_challenge():
    payload = request.get_json(silent=True) or {}
    xp = int(payload.get('xp', 20))
    return jsonify({'success': True, 'xp_awarded': xp, 'message': 'Challenge completed. XP awarded.'})


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
