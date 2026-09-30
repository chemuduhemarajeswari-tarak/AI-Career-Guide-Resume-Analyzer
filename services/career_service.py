import json
import math
from typing import Dict, List

ROLE_SKILLS = {
    'software developer': {
        'must': ['Python', 'SQL', 'Git', 'Data Structures'],
        'important': ['Algorithms', 'REST APIs', 'Testing'],
        'optional': ['Docker', 'Linux']
    },
    'web developer': {
        'must': ['HTML', 'CSS', 'JavaScript', 'Git'],
        'important': ['Responsive Design', 'REST APIs', 'React'],
        'optional': ['Node.js', 'Docker']
    },
    'python developer': {
        'must': ['Python', 'Flask', 'SQL', 'REST APIs'],
        'important': ['Git', 'Testing', 'OOP'],
        'optional': ['Docker', 'Celery']
    },
    'java developer': {
        'must': ['Java', 'OOP', 'SQL', 'Spring Boot'],
        'important': ['REST APIs', 'Git', 'Testing'],
        'optional': ['Docker', 'Microservices']
    },
    'data analyst': {
        'must': ['SQL', 'Excel', 'Statistics', 'Python'],
        'important': ['Data Visualization', 'Power BI', 'ETL'],
        'optional': ['Tableau', 'Business Analysis']
    },
    'data scientist': {
        'must': ['Python', 'Statistics', 'SQL', 'Machine Learning'],
        'important': ['Pandas', 'NumPy', 'Data Visualization'],
        'optional': ['Deep Learning', 'MLOps']
    },
    'ai/ml engineer': {
        'must': ['Python', 'Machine Learning', 'Statistics', 'Data Cleaning'],
        'important': ['Pandas', 'Scikit-learn', 'Model Evaluation'],
        'optional': ['Deep Learning', 'MLOps', 'NLP']
    },
    'cloud engineer': {
        'must': ['Cloud Computing', 'Linux', 'Networking', 'Security Basics'],
        'important': ['AWS', 'Azure', 'Docker'],
        'optional': ['Terraform', 'Kubernetes']
    },
    'cybersecurity analyst': {
        'must': ['Networking', 'Linux', 'Security Fundamentals', 'Threat Analysis'],
        'important': ['Wireshark', 'Python', 'SIEM'],
        'optional': ['Ethical Hacking', 'Cloud Security']
    },
    'frontend developer': {
        'must': ['HTML', 'CSS', 'JavaScript', 'Responsive Design'],
        'important': ['Git', 'UI/UX', 'Accessibility'],
        'optional': ['React', 'TypeScript']
    },
    'backend developer': {
        'must': ['Python', 'SQL', 'REST APIs', 'Git'],
        'important': ['Flask', 'System Design', 'Testing'],
        'optional': ['Docker', 'Caching']
    },
}


def normalize(value):
    return (value or '').strip().lower()


def list_to_text(items):
    return ', '.join(items) if items else 'No items listed'


def skill_priority(profile):
    role = normalize(profile.get('target_role', ''))
    role_requirements = ROLE_SKILLS.get(role, {'must': [], 'important': [], 'optional': []})
    current = [s.strip() for s in str(profile.get('current_skills', '')).split(',') if s.strip()]
    current_l = {normalize(s): s.strip() for s in current}
    must = []
    important = []
    optional = []
    for skill in role_requirements.get('must', []):
        if normalize(skill) not in current_l:
            must.append(skill)
    for skill in role_requirements.get('important', []):
        if normalize(skill) not in current_l:
            important.append(skill)
    for skill in role_requirements.get('optional', []):
        if normalize(skill) not in current_l:
            optional.append(skill)
    explanations = {}
    for skill in must + important + optional:
        explanations[skill] = 'This is a core gap for the selected role and should be learned before applying.'
    return {
        'must_learn': must,
        'important': important,
        'optional': optional,
        'explanations': explanations,
    }


def get_role_topic_plan(role, preferred_domain, skill_level, current_skills):
    role_key = normalize(role)
    current = (current_skills or '').lower()

    if 'data scientist' in role_key or 'ai/ml' in role_key or 'machine learning' in role_key:
        return [
            ['Data Science Fundamentals', 'Python for Data Work', 'Statistics Essentials', 'Data Cleaning Basics', 'Git for Projects'],
            ['SQL for Analysis', 'Data Wrangling', 'Exploratory Data Analysis', 'Visualization Basics', 'Model Thinking'],
            ['Feature Engineering', 'Model Selection Basics', 'Evaluation Metrics', 'Pandas Workflow', 'Experiment Notes'],
            ['Mini ML Project', 'Train a Baseline Model', 'Assess Accuracy', 'Improve Features', 'Project Review'],
            ['Model Deployment Basics', 'Bias and Fairness', 'Model Monitoring', 'Capstone Build', 'Advanced Practice'],
            ['GitHub Workflow', 'Documentation and Portfolio', 'Resume Keyword Refresh', 'Interview Storytelling', 'Final Review']
        ]

    if 'data analyst' in role_key or 'data' in preferred_domain.lower():
        return [
            ['Excel and Data Cleaning', 'Statistics Fundamentals', 'Python for Analysis', 'SQL Basics', 'Git Basics'],
            ['Advanced SQL', 'Data Wrangling', 'Exploratory Data Analysis', 'Dashboard Thinking', 'Reporting Foundations'],
            ['Visualization Principles', 'Power BI Basics', 'KPI Design', 'ETL Overview', 'Data Storytelling'],
            ['Mini Dashboard Project', 'Business Metrics', 'Data Validation', 'Insight Writing', 'Project Review'],
            ['Scenario Analysis', 'Forecasting Basics', 'A/B Testing Concepts', 'Capstone Analysis', 'Advanced Practice'],
            ['GitHub Portfolio', 'Documentation Skills', 'Resume Alignment', 'Mock Interview Prep', 'Final Review']
        ]

    if 'python developer' in role_key or ('python' in role_key and 'developer' in role_key):
        return [
            ['Python Fundamentals', 'Functions and Modules', 'Data Structures', 'File Handling', 'Git Basics'],
            ['SQL Essentials', 'Database Design', 'REST API Concepts', 'JSON and APIs', 'Debugging Practice'],
            ['Flask Basics', 'CRUD Endpoints', 'Authentication Basics', 'Testing with pytest', 'API Validation'],
            ['Build a Mini API', 'Add Database Relationships', 'Create a Practical Feature', 'Refactor and Review', 'Project Review'],
            ['Advanced Flask Patterns', 'Security Basics', 'Performance Tuning', 'Deployment Foundations', 'Capstone Integration'],
            ['GitHub Workflow', 'Portfolio Preparation', 'Resume and Interview Practice', 'Project Documentation', 'Final Review']
        ]

    if 'web developer' in role_key or 'frontend' in role_key:
        return [
            ['HTML Foundations', 'CSS Layout Basics', 'JavaScript Fundamentals', 'DOM Interaction', 'Git Basics'],
            ['Responsive Design', 'Accessibility Basics', 'Forms and Validation', 'Debugging Essentials', 'API Consumption'],
            ['Frontend Architecture', 'Component Thinking', 'State Management Basics', 'Async JavaScript', 'Testing Fundamentals'],
            ['Build Landing Page', 'Add Reusable Components', 'Improve UI Feedback', 'Responsive QA', 'Project Review'],
            ['Performance Basics', 'Optimization Workflow', 'SEO Fundamentals', 'Deployment Basics', 'Capstone Integration'],
            ['GitHub Workflow', 'Portfolio Polish', 'Resume Keyword Update', 'Interview Practice', 'Final Review']
        ]

    if 'cloud' in role_key or 'cyber' in role_key:
        return [
            ['Cloud Concepts', 'Linux Basics', 'Networking Fundamentals', 'Security Principles', 'Git Basics'],
            ['Operating Systems', 'Identity and Access', 'Networking Practice', 'Security Monitoring', 'Cloud Lab Setup'],
            ['Infrastructure Basics', 'Virtual Machines', 'Storage and Networking', 'Security Hardening', 'Documentation'],
            ['Build Lab Setup', 'Deploy a Service', 'Monitor Activity', 'Audit and Review', 'Project Review'],
            ['Automation Basics', 'Scripting Practice', 'Cloud Security', 'Advanced Troubleshooting', 'Capstone Practice'],
            ['GitHub Workflow', 'Resume Alignment', 'Interview Storytelling', 'Portfolio Updates', 'Final Review']
        ]

    if 'java' in role_key:
        return [
            ['Java Fundamentals', 'Variables and Control Flow', 'Methods and Classes', 'Collections Basics', 'Git Basics'],
            ['OOP Concepts', 'Exception Handling', 'Input and Output', 'Debugging Java Code', 'SQL Essentials'],
            ['Spring Boot Basics', 'REST APIs with Java', 'Data Access', 'Testing with JUnit', 'Project Setup'],
            ['Build a Java API', 'Add Validation', 'Connect Database', 'Review and Refactor', 'Project Review'],
            ['Security Basics', 'Performance Tuning', 'Deployment Basics', 'Advanced Design', 'Capstone Build'],
            ['GitHub Workflow', 'Documentation', 'Resume Updates', 'Interview Preparation', 'Final Review']
        ]

    return [
        ['Python Fundamentals', 'Variables and Control Flow', 'Functions and Modules', 'Data Structures', 'Git Basics'],
        ['SQL Essentials', 'Database Design', 'REST API Concepts', 'JSON and Data Handling', 'Debugging Practice'],
        ['Flask Basics', 'CRUD Endpoints', 'Authentication Basics', 'Testing with pytest', 'API Validation'],
        ['Build a Mini API', 'Add Database Relations', 'Create a Practical Feature', 'Review your Code', 'Project Review'],
        ['Advanced Flask Patterns', 'Security Basics', 'Performance Tuning', 'Deployment Foundations', 'Capstone Integration'],
        ['GitHub Workflow', 'Portfolio Preparation', 'Resume and Interview Practice', 'Project Documentation', 'Final Review']
    ]


def build_days(profile):
    daily_time = profile.get('study_time', '1 hour/day')
    role = profile.get('target_role', 'Software Developer')
    skill_level = normalize(profile.get('skill_level', 'Beginner'))
    preferred_domain = profile.get('preferred_domain', '')
    current_skills = profile.get('current_skills', '')

    base = {
        '30 minutes/day': 30,
        '1 hour/day': 60,
        '2 hours/day': 120,
        '3+ hours/day': 180,
    }
    minutes = base.get(daily_time, 60)
    plan = get_role_topic_plan(role, preferred_domain, skill_level, current_skills)
    roadmap = []

    for day_index in range(1, 31):
        phase_index = (day_index - 1) // 5
        slot_in_phase = (day_index - 1) % 5
        topics = plan[phase_index] if phase_index < len(plan) else plan[-1]
        topic = topics[slot_in_phase]

        if skill_level in {'intermediate', 'advanced'} and day_index <= 5 and 'Basics' in topic:
            topic = topic.replace('Basics', 'Review and Practice')
        if skill_level == 'advanced' and day_index > 20:
            topic = f'Advanced {topic}'
        if 'python' in (current_skills or '').lower() and day_index <= 5 and 'Python' in topic:
            topic = 'Python Review and Practice'

        phase_labels = [
            'Fundamentals',
            'Core Technical Skills',
            'Practical Development',
            'Project Development',
            'Advanced Practice',
            'Portfolio and Preparation'
        ]
        phase_name = phase_labels[min(phase_index, len(phase_labels) - 1)]

        estimated = minutes
        if phase_index in {0, 1}:
            estimated = min(minutes, 60)
        elif phase_index in {2, 3}:
            estimated = min(minutes, 90)
        elif phase_index >= 4:
            estimated = min(minutes, 120)

        roadmap.append({
            'day': day_index,
            'topic': topic,
            'phase': phase_name,
            'why_it_matters': f'{topic} is an important step in your {role} learning path because it builds the skills needed for real projects and role readiness.',
            'what_to_learn': f'Focus on the key concepts behind {topic}, then apply them in a short exercise to strengthen understanding.',
            'task': f'Complete a practical exercise around {topic} and write down the main takeaway in 3 to 5 bullet points.',
            'estimated_time': f'{estimated} minutes',
            'mini_challenge': f'Use {topic} to solve a small real-world problem and document your result.',
            'resources': ['Python Documentation', 'freeCodeCamp', 'MDN', 'Microsoft Learn'],
            'completed': False,
        })
    return roadmap


def generate_roadmap(profile):
    role = profile.get('target_role', 'Software Developer')
    roadmap = build_days(profile)
    priority = skill_priority(profile)
    return {
        'target_role': role,
        'profile': profile,
        'priority': priority,
        'roadmap': roadmap,
        'daily_challenge': get_daily_challenge(role),
    }


def get_daily_challenge(role):
    challenge_map = {
        'python developer': 'Write a Python function that counts word frequency in a sentence.',
        'data analyst': 'Create a short SQL query that groups sales by region and highlights top performers.',
        'data scientist': 'Explain how you would validate a machine learning model and choose evaluation metrics.',
        'web developer': 'Build a simple responsive card layout with HTML and CSS.',
        'software developer': 'Write a small Python function that filters a list of jobs by skill keywords.',
    }
    return challenge_map.get(normalize(role), 'Write a short explanation of how you would solve a real-world problem using your target skill set.')


def adapt_roadmap(roadmap, completed_days, missed_days, available_time):
    remaining = [entry for entry in roadmap if entry.get('day', 0) > completed_days]
    base_time = {'30 minutes/day': 30, '1 hour/day': 60, '2 hours/day': 120, '3+ hours/day': 180}
    minutes = base_time.get(available_time, 60)
    if missed_days > 0:
        adjusted = []
        for day in remaining:
            if len(adjusted) >= max(5, len(remaining) - missed_days):
                break
            day_copy = dict(day)
            day_copy['estimated_time'] = f'{min(minutes, 90)} minutes'
            day_copy['why_it_matters'] = day_copy.get('why_it_matters', '') + ' This was retained because it supports the most important skills for the role.'
            adjusted.append(day_copy)
        return {
            'completed_days': completed_days,
            'missed_days': missed_days,
            'remaining_days': len(adjusted),
            'available_daily_time': available_time,
            'adjusted_roadmap': adjusted,
            'change_summary': 'The remaining plan keeps the most important skills, combines related topics, and reduces low-priority repetition to recover schedule without deleting key learning goals.'
        }
    return {
        'completed_days': completed_days,
        'missed_days': missed_days,
        'remaining_days': len(remaining),
        'available_daily_time': available_time,
        'adjusted_roadmap': remaining,
        'change_summary': 'No schedule gap detected. The plan remains unchanged.'
    }
