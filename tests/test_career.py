from services.career_service import generate_roadmap


def test_roadmap_has_logical_progression_for_python_role():
    profile = {
        'name': 'Aisha',
        'target_role': 'Python Developer',
        'current_skills': 'Python basics, Git',
        'education': 'B.Tech',
        'skill_level': 'Beginner',
        'preferred_domain': 'Backend',
        'study_time': '1 hour/day',
        'experience': '0 years',
        'projects': 'None'
    }

    plan = generate_roadmap(profile)
    roadmap = plan['roadmap']

    assert len(roadmap) == 30
    assert len({day['topic'] for day in roadmap}) >= 20
    assert any('Fundamentals' in road['topic'] or 'Basics' in road['topic'] for road in roadmap[:5])
    assert any('Database' in road['topic'] or 'API' in road['topic'] or 'Testing' in road['topic'] for road in roadmap[5:15])
    assert any('Project' in road['topic'] or 'Deployment' in road['topic'] for road in roadmap[15:25])
    assert any('Resume' in road['topic'] or 'Interview' in road['topic'] for road in roadmap[25:30])
