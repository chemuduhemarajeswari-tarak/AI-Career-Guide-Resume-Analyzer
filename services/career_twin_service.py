def compute_career_twin(profile, roadmap_progress, resume_score, interview_score):
    skills = min(100, max(0, 55 + (len((profile.get('current_skills') or '').split(',')) * 4)))
    projects = min(100, max(0, 40 + (roadmap_progress.get('completed_days', 0) * 2)))
    resume = max(0, min(100, resume_score or 72))
    interview = max(0, min(100, interview_score or 60))
    readiness = round((skills + resume + projects + interview) / 4)
    return {
        'target_role': profile.get('target_role', 'Software Developer'),
        'skills_alignment': round(skills),
        'projects': max(1, roadmap_progress.get('completed_days', 1) // 3),
        'resume_status': round(resume),
        'interview_status': round(interview),
        'skill_gaps': max(1, 8 - (len((profile.get('current_skills') or '').split(',')) // 2)),
        'career_readiness': readiness,
        'next_actions': [
            'Finish the next roadmap task',
            'Improve resume keywords for your target role',
            'Practice one mock interview question today'
        ]
    }


def career_readiness_indicator(profile, roadmap_progress, resume_score, interview_score, projects_count=2):
    return {
        'skills': min(100, max(0, 50 + (len((profile.get('current_skills') or '').split(',')) * 3))),
        'resume': max(0, min(100, resume_score or 78)),
        'projects': min(100, max(0, 45 + projects_count * 15)),
        'interview': max(0, min(100, interview_score or 55)),
        'roadmap': min(100, max(0, roadmap_progress.get('percentage', 20))),
        'note': 'This is an AI-generated guidance indicator and is not a prediction of hiring success.'
    }
