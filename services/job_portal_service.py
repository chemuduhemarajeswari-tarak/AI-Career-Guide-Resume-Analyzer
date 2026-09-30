JOB_PORTALS = [
    {
        'portal': 'LinkedIn',
        'purpose': 'Professional networking and full-time roles',
        'keywords': ['Python Developer Fresher', 'Junior Python Developer', 'Software Developer Entry Level'],
        'official_url': 'https://www.linkedin.com/jobs/'
    },
    {
        'portal': 'Naukri',
        'purpose': 'Indian job portal for internships and entry roles',
        'keywords': ['Python Developer Fresher', 'Intern Python Developer', 'Backend Developer Intern'],
        'official_url': 'https://www.naukri.com/'
    },
    {
        'portal': 'Indeed',
        'purpose': 'Global job search across many industries',
        'keywords': ['Junior Software Developer', 'Python Intern', 'Data Analyst Fresher'],
        'official_url': 'https://www.indeed.com/'
    },
    {
        'portal': 'Internshala',
        'purpose': 'Internships and student-focused opportunities',
        'keywords': ['Web Development Internship', 'Python Internship', 'Machine Learning Intern'],
        'official_url': 'https://internshala.com/'
    },
    {
        'portal': 'Glassdoor',
        'purpose': 'Company reviews and job listings',
        'keywords': ['Junior Developer', 'Freshers IT Jobs', 'Data Analyst Entry Level'],
        'official_url': 'https://www.glassdoor.com/'
    },
    {
        'portal': 'Wellfound',
        'purpose': 'Startup and product jobs',
        'keywords': ['Frontend Developer Junior', 'Backend Intern', 'Product Engineer Entry Level'],
        'official_url': 'https://wellfound.com/'
    },
]


def get_portals_for_role(target_role):
    role = (target_role or 'Software Developer').lower()
    portals = []
    for entry in JOB_PORTALS:
        keywords = entry['keywords']
        if 'python' in role and 'python' not in entry['portal'].lower():
            keywords = ['Python Developer Fresher', 'Junior Python Developer', 'Python Flask Intern'] + keywords
        portals.append({
            'portal': entry['portal'],
            'purpose': entry['purpose'],
            'keywords': keywords[:4],
            'official_url': entry['official_url']
        })
    return portals


def generate_search_keywords(target_role):
    base = {
        'python developer': ['Python Developer Fresher', 'Junior Python Developer', 'Python Flask Intern', 'Backend Developer Intern', 'Python Developer Entry Level'],
        'data analyst': ['Data Analyst Fresher', 'Junior Data Analyst', 'Business Analyst Intern', 'SQL Analyst Entry Level'],
        'web developer': ['Web Developer Fresher', 'Frontend Developer Intern', 'Junior Frontend Developer', 'HTML CSS Developer'],
        'software developer': ['Software Developer Fresher', 'Junior Software Engineer', 'Entry Level Software Developer', 'Software Intern'],
    }
    role_key = (target_role or 'software developer').lower()
    return base.get(role_key, ['Junior Developer', 'Entry Level Developer', 'Software Intern', 'Technology Intern'])
