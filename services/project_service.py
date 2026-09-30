PROJECT_LIBRARY = {
    'python developer': [
        {
            'project_name': 'Student Placement Management API',
            'difficulty': 'Intermediate',
            'duration': '2-3 weeks',
            'features': ['Student profiles', 'Interview scheduling', 'Placement records'],
            'technologies': ['Python', 'Flask', 'REST API', 'SQL'],
            'skills_gained': ['Flask', 'REST APIs', 'Database design'],
            'resume_bullet': 'Built a student placement management API with role-based data flow and SQL-backed records.',
            'development_steps': ['Design endpoints', 'Implement CRUD operations', 'Connect to SQLite/PostgreSQL']
        },
        {
            'project_name': 'Job Board Backend',
            'difficulty': 'Intermediate',
            'duration': '3 weeks',
            'features': ['Job listings', 'Application tracking', 'Employer dashboard'],
            'technologies': ['Python', 'Flask', 'SQL', 'REST APIs'],
            'skills_gained': ['CRUD design', 'Authentication basics', 'API testing'],
            'resume_bullet': 'Developed a job board backend with listing, search, and application management flows.',
            'development_steps': ['Create data models', 'Add endpoints', 'Test full application flow']
        },
        {
            'project_name': 'Portfolio Analytics Dashboard',
            'difficulty': 'Advanced',
            'duration': '4 weeks',
            'features': ['Analytics summaries', 'Filtering views', 'Charts'],
            'technologies': ['Python', 'Flask', 'SQL', 'Charts'],
            'skills_gained': ['Data handling', 'Dashboard design', 'API integration'],
            'resume_bullet': 'Built a dashboard that displayed key metrics and business summaries from structured data.',
            'development_steps': ['Plan data schema', 'Create report endpoints', 'Connect visual widgets']
        }
    ],
    'web developer': [
        {
            'project_name': 'Campus Event Platform',
            'difficulty': 'Beginner',
            'duration': '2 weeks',
            'features': ['Event listing', 'Registration form', 'Responsive design'],
            'technologies': ['HTML', 'CSS', 'JavaScript'],
            'skills_gained': ['Responsive layout', 'Form handling', 'UI design'],
            'resume_bullet': 'Created a responsive event website with registration and event information sections.',
            'development_steps': ['Create page sections', 'Style responsive UI', 'Add form validation']
        }
    ],
    'data analyst': [
        {
            'project_name': 'Sales Performance Dashboard',
            'difficulty': 'Intermediate',
            'duration': '2-3 weeks',
            'features': ['Data cleaning', 'Regional comparison', 'Charts'],
            'technologies': ['Excel', 'SQL', 'Python', 'Power BI'],
            'skills_gained': ['Data cleaning', 'Dashboarding', 'Insights generation'],
            'resume_bullet': 'Analyzed sales performance data and converted findings into a structured dashboard and summary.',
            'development_steps': ['Clean source data', 'Write queries', 'Create charts']
        }
    ],
}


def recommend_projects(target_role, missing_skills, current_skills, skill_level='Beginner'):
    projects = PROJECT_LIBRARY.get((target_role or 'python developer').lower(), PROJECT_LIBRARY['python developer'])
    final = []
    for idx, item in enumerate(projects[:3], start=1):
        final.append({
            'project_name': item['project_name'],
            'difficulty': item['difficulty'],
            'estimated_duration': item['duration'],
            'features': item['features'],
            'technologies': item['technologies'],
            'skills_gained': item['skills_gained'],
            'resume_bullet': item['resume_bullet'],
            'development_steps': item['development_steps'],
            'project_number': idx,
        })
    return final


def generate_project_explanation(project_name, technologies, description, contribution):
    return {
        'project_name': project_name,
        'thirty_second_explanation': f'{project_name} was built using {technologies}. It focused on solving a problem with a practical workflow and a simple user-facing result.',
        'one_minute_explanation': f'I created {project_name} to apply {technologies} in a real-world scenario. I focused on implementing core functionality, structuring the project, and validating the result.',
        'technical_explanation': f'The project used {technologies} to build a functional feature set around {description}. My work included {contribution}.',
        'resume_bullet_points': [
            f'Developed {project_name} using {technologies}.',
            f'Implemented core features for {description}.',
            f'Contributed by {contribution}.'
        ],
        'interview_questions': [
            f'What problem did {project_name} solve?',
            f'Which technologies did you use and why?',
            f'What was your main contribution to this project?'
        ],
        'viva_questions': [
            'Explain the architecture of the project.',
            'What challenges did you face during development?',
            'How would you improve the project further?'
        ]
    }
