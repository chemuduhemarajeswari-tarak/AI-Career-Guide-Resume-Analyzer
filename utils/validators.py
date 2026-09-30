from utils.security import sanitize_text


def validate_profile(data):
    errors = []
    name = sanitize_text(data.get('name'))
    role = sanitize_text(data.get('target_role'))
    skills = sanitize_text(data.get('current_skills'))
    if not name:
        errors.append('Name is required.')
    if not role:
        errors.append('Target role is required.')
    if not skills:
        errors.append('Current skills are required.')
    return errors


def validate_resume_form(data):
    errors = []
    if not data.get('target_role'):
        errors.append('Target role is required.')
    if not data.get('resume_file'):
        errors.append('Resume file is required.')
    return errors
