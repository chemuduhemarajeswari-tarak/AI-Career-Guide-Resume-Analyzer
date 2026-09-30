# AI Career Guide & Resume Analyzer

A local-first career planning platform for students and job seekers. It combines a role-specific skill-gap engine, a time-bounded 30-day roadmap, resume and job-description analysis, project prompts, interview practice, verified learning links, career readiness guidance, and progress tracking.

Gemini is optional. The core workflows work without an API key and identify results as demo guidance. No Gemini key is sent to browser code. Resume files are parsed in memory; only the analysis summary is stored.

## Features

- Career profile with role, skills, education, experience, study time, and project context.
- Role-aware MUST LEARN / IMPORTANT / OPTIONAL priorities and a 30-day plan with tasks, time limits, challenges, and verified resources.
- Roadmap completion, local learning streak, Career XP, badges, and an adaptive plan that keeps unfinished topics.
- PDF, DOCX, and TXT resume extraction; estimated ATS compatibility breakdown, skill matching, issue suggestions, and a truth-preserving bullet improver.
- Job-description skill comparison, role-specific project recommendations, and a project explanation generator.
- Interactive mock interviews, per-answer feedback, saved practice history, and recurring feedback themes.
- Career Twin, career readiness guidance, typical career path stages, job search portals/queries, saved resources, and history.
- Responsive browser interface; JSON persistence under `data/`.

All scores are guidance only. ATS scores are not employer scores; readiness is not a prediction of hiring success; career stages do not guarantee job titles or advancement. Users should only add skills, work, and achievements that are accurate.

## Technology

- Python 3.10+
- Flask
- Vanilla JavaScript, HTML, and CSS
- JSON files for local persistence
- Optional Google Gemini through the `google-genai` SDK
- `python-dotenv`, `PyPDF2`, and `python-docx`

## Run locally

From this project directory:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Open <http://127.0.0.1:5000/>. On macOS/Linux, activate with `source .venv/bin/activate` instead. The app binds to localhost and runs without Gemini in demo mode.

## Gemini setup

Create a Google AI Studio API key, then put it only in your local, git-ignored `.env` file:

```dotenv
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```

Restart the Flask process after changing `.env`. The `/api/ai-status` endpoint reports whether a key is configured, never its value. AI-dependent features fall back to clearly labeled demo guidance when Gemini is missing or unavailable. Technical errors are logged in the Flask terminal; user-facing messages do not include secrets.

## Test

```powershell
python -m unittest discover -s tests -v
```

The tests use a temporary JSON directory and do not alter your local career history.

## Project layout

```text
app.py                     Flask routes and application entry point
services/                  Career logic, Gemini gateway, resume extraction
utils/                     Input validation and JSON persistence
static/css/style.css       Responsive application design
static/js/main.js          Browser navigation and API workflows
templates/index.html       Career Studio interface
data/                      Local JSON records and verified resources
tests/                     Flask workflow tests
uploads/                    Reserved; resume uploads are not persisted
```

## API overview

- `GET /api/health`, `GET /api/ai-status`, `GET /api/dashboard`, `GET /api/history`
- `POST /api/career/generate`, `POST /api/roadmap/progress`, `POST /api/roadmap/adapt`
- `POST /api/resume/analyze`, `POST /api/resume/bullet`, `POST /api/job-description/analyze`
- `POST /api/skill-gap`, `GET /api/career-path`, `POST /api/projects/recommend`, `POST /api/projects/explain`, `POST /api/projects/log`
- `POST /api/interview/start`, `POST /api/interview/answer`, `POST /api/interview/complete`
- `GET /api/jobs`, `GET /api/resources`, `POST /api/resources/save`, `POST /api/challenge/start`, `POST /api/challenge/complete`

## Deployment notes

Use a production WSGI server behind HTTPS for deployment; do not expose Flask's development server to the public internet. Configure `GEMINI_API_KEY` as a deployment secret, not a committed file or frontend variable. JSON storage is intended for a local, single-instance app; use a transactional database before running multiple application workers.
