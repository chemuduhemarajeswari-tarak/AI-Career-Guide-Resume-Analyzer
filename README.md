# AI Career Guide & Resume Analyzer

This project is a Flask-based platform for students and job seekers that blends career planning, skill-gap analysis, resume improvement, job matching, project recommendations, and interview preparation.

## Features

- Career guide and personalized 30-day roadmap
- Skill-priority engine with MUST LEARN, IMPORTANT, and OPTIONAL buckets
- Resume upload analysis for PDF, DOCX, and TXT files
- ATS compatibility estimation and keyword gap detection
- Job description comparison with resume
- Project recommendation engine
- Mock interview preparation and scoring
- Career Twin dashboard and readiness indicator
- Progress tracking, XP, badges, and learning streaks
- Demo mode when the AI service is unavailable

## Tech stack

- Flask
- Python
- HTML5, CSS3, Vanilla JavaScript
- JSON files for storage
- Google Gemini API integration
- PyPDF2 and python-docx for resume parsing

## Folder structure

- app.py
- requirements.txt
- .env
- services/
- utils/
- templates/
- static/
- data/
- tests/

## Installation

1. Create a virtual environment
2. Install dependencies
3. Add your Gemini API key to .env
4. Run the app

### Virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure Gemini

Edit .env and set:

```env
GEMINI_API_KEY=your_key_here
```

## Run locally

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000/
```

## Testing

```bash
pytest -q
```

## Deployment

The app can be deployed to any standard Python hosting environment with Flask support, such as Render, Railway, PythonAnywhere, or a VPS with Gunicorn.
