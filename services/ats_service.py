import re
from typing import Dict, List

ROLE_SKILLS = {
    'software developer': ['python', 'sql', 'git', 'data structures', 'algorithms', 'rest api', 'testing'],
    'web developer': ['html', 'css', 'javascript', 'git', 'responsive design', 'rest api', 'react'],
    'python developer': ['python', 'sql', 'flask', 'rest api', 'git', 'testing', 'oop'],
    'java developer': ['java', 'sql', 'spring boot', 'rest api', 'git', 'testing'],
    'data analyst': ['sql', 'excel', 'statistics', 'python', 'data visualization', 'power bi'],
    'data scientist': ['python', 'statistics', 'sql', 'machine learning', 'pandas', 'numpy', 'data visualization'],
    'ai/ml engineer': ['python', 'machine learning', 'statistics', 'pandas', 'scikit-learn', 'model evaluation'],
    'cloud engineer': ['cloud computing', 'linux', 'networking', 'security basics', 'aws', 'docker'],
    'cybersecurity analyst': ['networking', 'linux', 'security fundamentals', 'threat analysis', 'python', 'wireshark'],
    'frontend developer': ['html', 'css', 'javascript', 'responsive design', 'ui/ux', 'accessibility'],
    'backend developer': ['python', 'sql', 'rest api', 'git', 'flask', 'testing'],
}


def normalize_skill(skill):
    return re.sub(r'[^a-z0-9\s+/.-]', '', skill.lower()).strip()


def extract_skills(text):
    tokens = set()
    for skill in re.findall(r'[A-Za-z][A-Za-z0-9+/ .-]{2,}', text):
        cleaned = normalize_skill(skill)
        if cleaned:
            tokens.add(cleaned)
    return sorted(tokens)


def analyze_resume_vs_role(resume_text, target_role):
    role_skills = ROLE_SKILLS.get(target_role.lower(), [])
    resume_skills = extract_skills(resume_text)
    matching = [skill for skill in role_skills if skill in ' '.join(resume_skills)]
    missing = [skill for skill in role_skills if skill not in ' '.join(resume_skills)]
    score = max(0, min(100, round((len(matching) / max(len(role_skills), 1)) * 100)))
    return {
        'target_role': target_role,
        'resume_summary': f'Your resume is generally aligned with {target_role}, with a strong focus on {", ".join(matching[:3]) if matching else "foundational skills"}.',
        'matching_skills': matching,
        'missing_skills': missing,
        'recommended_skills': missing[:5],
        'recommended_certifications': ['Google Data Analytics', 'AWS Cloud Practitioner', 'Microsoft Azure Fundamentals'][:3],
        'resume_improvement_areas': [
            'Add measurable achievements for projects and work experience.',
            'Use clear section headings and target-role keywords.',
            'Highlight tools and technologies used in each project.'
        ],
        'ats_score': score,
        'ats_breakdown': {
            'keyword_match': min(100, max(0, score)),
            'skills_match': min(100, max(0, score - 5)),
            'experience_relevance': min(100, max(0, score + 3)),
            'resume_structure': 78,
            'formatting': 80,
            'education_certifications': 72,
        },
        'issues': [
            {
                'problem': 'Missing key keywords',
                'why_it_matters': 'ATS systems search for exact role-specific keywords.',
                'how_to_improve': 'Add skills that match the job description in a natural, truthful way.'
            },
            {
                'problem': 'Weak project summaries',
                'why_it_matters': 'Project descriptions help explain practical knowledge.',
                'how_to_improve': 'List tools, responsibilities, and outcomes in short bullet points.'
            },
            {
                'problem': 'Limited measurable results',
                'why_it_matters': 'Numbers improve credibility and clarity.',
                'how_to_improve': 'Use metrics when they are genuinely available.'
            }
        ],
        'keywords': {
            'present': matching,
            'missing': missing,
            'suggested': [skill for skill in missing if skill not in ['', ' ']][:5],
        },
        'demo': False,
    }


def analyze_job_description(job_description, resume_text):
    job_lower = job_description.lower()
    resume_lower = resume_text.lower()
    required_skills = []
    role_keywords = ['python', 'sql', 'flask', 'rest api', 'java', 'javascript', 'git', 'aws', 'docker', 'ai', 'ml', 'data', 'cloud']
    for keyword in role_keywords:
        if keyword in job_lower:
            required_skills.append(keyword)
    matching = [skill for skill in required_skills if skill in resume_lower]
    missing = [skill for skill in required_skills if skill not in resume_lower]
    return {
        'job_requirements': required_skills,
        'resume_match': matching,
        'resume_missing': missing,
        'requirements_matched': len(matching),
        'requirements_missing': len(missing),
        'recommended_actions': [
            'Add the relevant missing keywords to your resume.',
            'Improve the project section with concrete outcomes and tools used.',
            'Use a job-specific summary and customize your skills section.'
        ],
        'how_to_improve': 'Update your resume with skills and tools that match the job description; keep claims honest and based on real experience.',
    }
