"""AI Career Guide & Resume Analyzer: a local-first Flask application."""

from __future__ import annotations

import logging
import os
import re
from datetime import date, datetime, timedelta
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from services import career_service, gemini_service, resume_parser
from utils.json_handler import append_json, read_json, update_json, write_json
from utils.validators import MAX_UPLOAD_BYTES, required_text, safe_upload

ROOT = Path(__file__).resolve().parent
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES + 128 * 1024
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def response_error(message: str, status: int = 400):
    return jsonify({"error": message}), status


def profile_data() -> dict:
    return read_json("users", {}).get("local", {})


def record_xp(amount: int, badge: str | None = None) -> dict:
    state = read_json("achievements", {})
    state["xp"] = int(state.get("xp", 0)) + amount
    state.setdefault("badges", [])
    if badge and badge not in state["badges"]:
        state["badges"].append(badge)
    state["level"] = next(name for threshold, name in reversed([(0, "Beginner"), (100, "Explorer"), (300, "Builder"), (600, "Job Ready"), (1000, "Career Pro")]) if state["xp"] >= threshold)
    write_json("achievements", state)
    return state


def ai_or_demo(prompt: str) -> tuple[dict | None, str | None]:
    try:
        return gemini_service.generate_json(prompt), None
    except gemini_service.GeminiError as error:
        return None, str(error)


def safe_resume_analysis(text: str, role: str, layout: dict | None = None) -> dict:
    gaps = career_service.skill_gaps(role, [])
    present = [skill for skill in gaps["required"] if skill.lower() in text.lower()]
    missing = [skill for skill in gaps["required"] if skill not in present]
    sections = sum(bool(re.search(rf"\b{heading}\b", text, re.I)) for heading in ["experience", "education", "skills", "projects"])
    score = min(100, round(35 + (len(present) / max(1, len(gaps["required"]))) * 45 + sections * 5))
    layout = layout or {}
    issues = resume_parser.inspect_text(text)
    if layout.get("tables"):
        issues.append({"problem": "Table-based layout detected", "why": "Some resume systems may read table content out of order.", "improve": "Use a simple, single-column layout when practical."})
    if layout.get("images"):
        issues.append({"problem": "Images detected in the document", "why": "Text embedded in an image may not be readable by resume systems.", "improve": "Keep important contact and skill information as selectable text."})
    if layout.get("excessive_formatting"):
        issues.append({"problem": "Many font styles were detected", "why": "Highly varied formatting can make a resume harder to scan.", "improve": "Use a small, consistent set of fonts and sizes."})
    formatting_score = 90 if not any(layout.get(key) for key in ("tables", "images", "excessive_formatting")) else 45
    return {
        "summary": f"The resume contains {len(present)} detected skills aligned with {role}. Review the suggestions and verify every detail before using them.",
        "target_role": role, "matching_skills": present, "missing_skills": missing,
        "experience_areas": ["Relevant experience should be supported by specific examples from your resume."],
        "recommended_skills": missing[:4], "certifications": [],
        "improvements": ["Use clear section headings." if sections < 3 else "Keep section headings consistent.", "Add measurable outcomes only when you can verify them.", "Use concise bullets that explain your contribution."],
        "issues": issues,
        "score": score, "breakdown": {"Keyword match": round(100 * len(present) / max(1, len(gaps["required"]))), "Skills match": round(100 * len(present) / max(1, len(gaps["required"]))), "Experience relevance": 50 if "experience" in text.lower() else 25, "Resume structure": min(100, sections * 25), "Formatting": formatting_score, "Education / certifications": 60 if "education" in text.lower() else 20},
        "disclaimer": "This is an AI-estimated ATS compatibility score. It is not an official score from an employer's ATS system.",
    }


def dashboard_data() -> dict:
    profile = profile_data()
    plan = read_json("career_plans", {}).get("local", {})
    progress = read_json("progress", {}).get("local", {})
    achievements = read_json("achievements", {})
    resume_history = read_json("resume_history", [])
    latest_resume = resume_history[-1] if resume_history else None
    completed = progress.get("completed_days", [])
    interviews = read_json("interview_history", [])
    answer_count = sum(len(session.get("answers", [])) for session in interviews)
    readiness = {
        "Skills": min(100, len(plan.get("gaps", {}).get("already_have", [])) * 15),
        "Resume": latest_resume.get("score", 0) if latest_resume else 0,
        "Projects": min(100, (len(read_json("project_history", [])) + bool(profile.get("projects"))) * 30),
        "Certifications": min(100, len(career_service.skill_list(profile.get("certifications", ""))) * 25),
        "Interview": min(100, answer_count * 10),
        "Roadmap": round(len(completed) / max(1, len(plan.get("roadmap", []))) * 100),
    }
    return {"profile": profile, "plan": plan, "progress": progress, "achievements": achievements,
            "readiness": readiness, "readiness_score": round(sum(readiness.values()) / len(readiness)),
            "saved_resources": read_json("saved_resources", []), "latest_resume": latest_resume}


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/ai-status")
def ai_status():
    return jsonify({"configured": gemini_service.configured(), "service": "Gemini", "mode": "AI" if gemini_service.configured() else "Demo"})


@app.get("/api/dashboard")
def dashboard():
    return jsonify(dashboard_data())


@app.get("/api/history")
def history():
    return jsonify({"career_plans": read_json("career_plan_history", []),
                    "resume_analyses": read_json("resume_history", []),
                    "job_analyses": read_json("job_analyses", []),
                    "interviews": read_json("interview_history", []),
                    "projects": read_json("project_history", []),
                    "project_recommendations": read_json("project_recommendations", []),
                    "saved_resources": read_json("saved_resources", [])})


@app.get("/api/jobs")
def jobs():
    return jsonify(career_service.job_search(request.args.get("role", profile_data().get("target_role", "Software Developer"))))


@app.get("/api/career-path")
def career_path():
    role = request.args.get("role", profile_data().get("target_role", "Software Developer"))
    return jsonify({"role": role, "stages": career_service.career_path(role)})


@app.post("/api/career/generate")
def career_generate():
    payload = request.get_json(silent=True) or {}
    try:
        profile = {
            "name": required_text(payload.get("name"), "Name", 100),
            "target_role": required_text(payload.get("target_role"), "Target role", 100),
            "current_skills": career_service.skill_list(required_text(payload.get("current_skills"), "Current skills", 1000)),
            "education": required_text(payload.get("education"), "Education", 200),
            "skill_level": required_text(payload.get("skill_level", "Beginner"), "Skill level", 40),
            "preferred_domain": required_text(payload.get("preferred_domain") or "General", "Preferred domain", 100),
            "available_time": required_text(payload.get("available_time", "1 hour/day"), "Study time", 40),
            "experience": str(payload.get("experience", ""))[:500],
            "projects": str(payload.get("projects", ""))[:1000],
            "certifications": str(payload.get("certifications", ""))[:500],
        }
        gaps = career_service.skill_gaps(profile["target_role"], profile["current_skills"], profile["experience"] + " " + profile["projects"])
        roadmap = career_service.build_roadmap(profile, gaps)
        ai_result, ai_error = ai_or_demo(f"Return JSON with a concise personalized_summary and next_actions (array of five strings). Do not invent user experience. Profile: {profile}. Skill gaps: {gaps}.")
        demo = ai_result is None
        summary = ai_result.get("personalized_summary") if ai_result and isinstance(ai_result.get("personalized_summary"), str) else f"A {profile['skill_level'].lower()}-friendly learning path for {profile['target_role']}, built around your current skills and {profile['available_time']} study schedule."
        next_actions = ai_result.get("next_actions") if ai_result and isinstance(ai_result.get("next_actions"), list) else [f"Learn {item['skill']}" for item in gaps["priorities"][:3]] + ["Build a small role-focused project", "Practice explaining your work"]
        plan = {"profile": profile, "gaps": gaps, "roadmap": roadmap, "summary": summary, "next_actions": next_actions[:5], "created_at": date.today().isoformat(), "demo": demo, "ai_message": ai_error}
        update_json("users", "local", profile)
        update_json("career_plans", "local", plan)
        append_json("career_plan_history", plan)
        write_json("progress", {**read_json("progress", {}), "local": {"completed_days": [], "completed_dates": [], "streak": 0, "last_active": None}})
        return jsonify(plan)
    except ValueError as error:
        return response_error(str(error))


@app.post("/api/roadmap/progress")
def roadmap_progress():
    payload = request.get_json(silent=True) or {}
    try:
        day = int(payload.get("day", 0))
    except (ValueError, TypeError):
        return response_error("Choose a valid roadmap day.")
    plan = read_json("career_plans", {}).get("local", {})
    if not plan or not 1 <= day <= len(plan.get("roadmap", [])):
        return response_error("Generate a career plan and choose a valid roadmap day.")
    all_progress = read_json("progress", {})
    progress = all_progress.get("local", {"completed_days": [], "completed_dates": [], "streak": 0})
    completed = set(progress.get("completed_days", []))
    if day in completed:
        return jsonify({"progress": progress, "message": "This day is already complete."})
    completed.add(day)
    today = date.today().isoformat()
    dates = set(progress.get("completed_dates", []))
    if today not in dates:
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        progress["streak"] = int(progress.get("streak", 0)) + 1 if progress.get("last_active") == yesterday else (int(progress.get("streak", 0)) if progress.get("last_active") == today else 1)
        progress["last_active"] = today
        dates.add(today)
    progress.update({"completed_days": sorted(completed), "completed_dates": sorted(dates)})
    all_progress["local"] = progress
    write_json("progress", all_progress)
    badge = "7-Day Streak" if progress["streak"] >= 7 else ("First Roadmap Completed" if len(completed) == len(plan["roadmap"]) else None)
    achievements = record_xp(25, badge)
    return jsonify({"progress": progress, "achievements": achievements, "message": "Day completed. +25 Career XP."})


@app.post("/api/roadmap/adapt")
def roadmap_adapt():
    plan = read_json("career_plans", {}).get("local", {})
    if not plan:
        return response_error("Generate a career plan before adapting your roadmap.")
    progress = read_json("progress", {}).get("local", {})
    started = date.fromisoformat(plan.get("created_at", date.today().isoformat()))
    elapsed = min(30, (date.today() - started).days + 1)
    result = career_service.adapt_roadmap(plan["roadmap"], progress.get("completed_days", []), plan["profile"].get("available_time", "1 hour/day"), elapsed)
    adapted_by_day = {item["day"]: item for item in result["remaining_roadmap"]}
    completed = set(progress.get("completed_days", []))
    plan["roadmap"] = [item if item["day"] in completed else adapted_by_day[item["day"]] for item in plan["roadmap"]]
    update_json("career_plans", "local", plan)
    result["roadmap"] = plan["roadmap"]
    return jsonify(result)


@app.post("/api/resume/analyze")
def resume_analyze():
    try:
        role = required_text(request.form.get("target_role"), "Target role", 100)
        uploaded = request.files.get("resume")
        if uploaded is None:
            raise ValueError("Choose a resume file to analyze.")
        filename, content = safe_upload(uploaded)
        text = resume_parser.extract_text(filename, content)[:100_000]
        if not text.strip():
            raise ValueError("No readable text was found in that resume. Try another file.")
        layout = resume_parser.inspect_layout(filename, content)
        analysis = safe_resume_analysis(text, role, layout)
        ai, ai_error = ai_or_demo(f"Analyze the resume text against {role}. Return JSON with summary, improvements (array), recommended_skills (array). Never invent experience, skills, metrics, or certifications. Resume text: {text[:12000]}")
        if ai:
            for key in ("summary", "improvements", "recommended_skills"):
                if isinstance(ai.get(key), type(analysis[key])):
                    analysis[key] = ai[key]
        analysis.update({"filename": filename, "created_at": datetime.now().isoformat(timespec="seconds"), "demo": ai is None, "ai_message": ai_error})
        append_json("resume_history", analysis)
        record_xp(15, "Resume Analyzer")
        return jsonify(analysis)
    except ValueError as error:
        return response_error(str(error))


@app.post("/api/job-description/analyze")
def job_description_analyze():
    payload = request.get_json(silent=True) or {}
    try:
        role = required_text(payload.get("target_role"), "Target role", 100)
        description = required_text(payload.get("job_description"), "Job description", 20_000)
        resume_text = str(payload.get("resume_text", ""))[:20_000]
        skills = list(dict.fromkeys(skill for values in career_service.ROLE_SKILLS.values() for skill in values))
        required = [skill for skill in skills if re.search(rf"\b{re.escape(skill)}\b", description, re.I)]
        required = required or career_service.role_requirements(role)[:5]
        matched = [skill for skill in required if re.search(rf"\b{re.escape(skill)}\b", resume_text, re.I)]
        missing = [skill for skill in required if skill not in matched]
        result = {"requirements": [{"skill": skill, "status": "MATCH" if skill in matched else "MISSING"} for skill in required], "matched": matched, "missing": missing, "education_requirements": "Review the pasted description for the employer's exact education criteria.", "experience_requirements": "Review the pasted description for the employer's exact experience criteria.", "keywords": required, "actions": [f"Add {skill} only if you genuinely have or learn it." for skill in missing[:5]] or ["Tailor your strongest relevant examples to the role."], "role": role, "demo": True}
        append_json("job_analyses", {**result, "created_at": datetime.now().isoformat(timespec="seconds")})
        return jsonify(result)
    except ValueError as error:
        return response_error(str(error))


@app.post("/api/skill-gap")
def skill_gap():
    payload = request.get_json(silent=True) or {}
    try:
        role = required_text(payload.get("target_role", profile_data().get("target_role")), "Target role", 100)
        skills = career_service.skill_list(required_text(payload.get("current_skills", ", ".join(profile_data().get("current_skills", []))), "Current skills", 1000))
        return jsonify(career_service.skill_gaps(role, skills, str(payload.get("job_description", ""))))
    except ValueError as error:
        return response_error(str(error))


@app.post("/api/projects/recommend")
def projects_recommend():
    payload = request.get_json(silent=True) or {}
    role = payload.get("target_role", profile_data().get("target_role", "Software Developer"))
    gaps = career_service.skill_gaps(str(role), career_service.skill_list(payload.get("current_skills", profile_data().get("current_skills", []))))
    projects = career_service.project_recommendations(str(role), gaps)
    append_json("project_recommendations", {"role": role, "projects": projects, "created_at": datetime.now().isoformat(timespec="seconds")})
    return jsonify({"projects": projects, "demo": True})


@app.post("/api/projects/explain")
def project_explain():
    payload = request.get_json(silent=True) or {}
    try:
        name = required_text(payload.get("name"), "Project name", 120)
        technologies = required_text(payload.get("technologies"), "Technologies", 500)
        description = required_text(payload.get("description"), "Project description", 1500)
        contribution = required_text(payload.get("contribution"), "Your contribution", 1000)
        answer = {"thirty_second": f"I built {name}, a project that {description}. I used {technologies}.", "one_minute": f"The project was created to {description}. My contribution was {contribution}. I chose {technologies} for this work and can explain the implementation decisions I made.", "technical": f"Discuss the architecture and implementation details you personally handled: {contribution}. Technologies: {technologies}.", "resume_bullets": [f"Built {name} using {technologies} to {description}.", f"Contributed {contribution} to {name}."], "questions": [f"What was the hardest part of {name}?", "How did you test your implementation?", "What would you change in a second version?"], "demo": True}
        ai, error = ai_or_demo(f"Return JSON with thirty_second, one_minute, technical, resume_bullets, questions. Explain only the facts supplied; invent no outcomes. Project: {name}; technologies: {technologies}; description: {description}; contribution: {contribution}.")
        if ai:
            answer.update({key: ai[key] for key in answer if key in ai})
            answer["demo"] = False
        answer["ai_message"] = error
        return jsonify(answer)
    except ValueError as error:
        return response_error(str(error))


@app.post("/api/projects/log")
def project_log():
    payload = request.get_json(silent=True) or {}
    try:
        name = required_text(payload.get("name"), "Project name", 120)
        technologies = required_text(payload.get("technologies"), "Technologies", 500)
        description = required_text(payload.get("description"), "Project description", 1500)
    except ValueError as error:
        return response_error(str(error))
    items = read_json("project_history", [])
    if any(item.get("name", "").casefold() == name.casefold() for item in items):
        return jsonify({"projects": items, "message": "This project is already in your portfolio."})
    project = {"name": name, "technologies": technologies, "description": description, "created_at": datetime.now().isoformat(timespec="seconds")}
    append_json("project_history", project)
    achievements = record_xp(40, "Project Builder")
    return jsonify({"projects": read_json("project_history", []), "achievements": achievements, "message": "Project added to your portfolio. +40 Career XP."})


@app.post("/api/resume/bullet")
def improve_bullet():
    payload = request.get_json(silent=True) or {}
    try:
        original = required_text(payload.get("bullet"), "Resume bullet", 1000)
        improved = original[0].upper() + original[1:].rstrip(".! ") + "."
        ai, error = ai_or_demo(f"Rewrite this resume bullet professionally without adding any facts, numbers, skills, employers, or outcomes. Return JSON {{\"improved\": \"...\"}}. Bullet: {original}")
        if ai and isinstance(ai.get("improved"), str):
            improved = ai["improved"]
        return jsonify({"original": original, "improved": improved, "demo": ai is None, "ai_message": error})
    except ValueError as error:
        return response_error(str(error))


@app.post("/api/interview/start")
def interview_start():
    payload = request.get_json(silent=True) or {}
    profile = profile_data()
    role = str(payload.get("target_role") or profile.get("target_role", "Software Developer"))
    questions = [
        {"category": "Technical", "question": f"What core technical skill would you use most in a {role} role, and how have you practiced it?", "checks": "Technical understanding and practical evidence", "structure": "Name the skill, explain your approach, then give a truthful example."},
        {"category": "Project", "question": "Tell me about a project you contributed to and one decision you made.", "checks": "Ownership and technical reasoning", "structure": "Context, your contribution, decision, result you can verify."},
        {"category": "Behavioral", "question": "Describe a time you had to learn something unfamiliar.", "checks": "Adaptability and communication", "structure": "Situation, action, what you learned."},
        {"category": "Scenario", "question": "How would you investigate a bug you could not reproduce consistently?", "checks": "Structured troubleshooting", "structure": "Clarify impact, collect evidence, isolate variables, communicate."},
        {"category": "HR", "question": "What kind of role are you hoping to grow into next?", "checks": "Motivation and self-awareness", "structure": "Connect your interests to concrete skills you want to build."},
    ]
    generated, ai_error = ai_or_demo(f"Return JSON with a questions array of exactly five objects. Each object has category, question, checks, structure. Categories: Technical, HR, Project, Behavioral, Scenario. Tailor questions to {role} and the user's stated skills only; do not invent projects or experience. Skills: {profile.get('current_skills', [])}; experience: {profile.get('experience', '')}; projects: {profile.get('projects', '')}.")
    if generated and isinstance(generated.get("questions"), list):
        candidate = generated["questions"][:5]
        required_keys = ("category", "question", "checks", "structure")
        if len(candidate) == 5 and all(all(isinstance(item.get(key), str) and item[key].strip() for key in required_keys) for item in candidate):
            questions = [{key: item[key].strip() for key in required_keys} for item in candidate]
            ai_error = None
        else:
            ai_error = gemini_service.MESSAGES["response"]
            generated = None
    interview = {"id": datetime.now().strftime("%Y%m%d%H%M%S%f"), "role": role, "questions": questions, "answers": [], "demo": generated is None, "ai_message": ai_error, "created_at": datetime.now().isoformat(timespec="seconds")}
    append_json("interview_history", interview)
    return jsonify(interview)


@app.post("/api/interview/answer")
def interview_answer():
    payload = request.get_json(silent=True) or {}
    try:
        answer = required_text(payload.get("answer"), "Your answer", 5000)
        question = required_text(payload.get("question"), "Interview question", 1000)
    except ValueError as error:
        return response_error(str(error))
    words = answer.split()
    structure = min(95, 35 + sum(1 for term in ("because", "for example", "result", "learned", "I ") if term.lower() in answer.lower()) * 12)
    relevance = min(95, 35 + min(45, len(words)) + (15 if any(word.lower() in answer.lower() for word in question.split() if len(word) > 5) else 0))
    clarity = min(95, 45 + min(40, len(words) // 3))
    feedback = {"relevance": relevance, "clarity": clarity, "technical_knowledge": min(95, 40 + min(50, len(words) // 2)), "structure": structure, "improve": "Add a specific example and clearly separate your own contribution from the team's work." if len(words) < 45 else "Make the result or lesson explicit, and support every claim with an example you can discuss.", "demo": True}
    ai, error = ai_or_demo(f"Evaluate this interview answer using JSON keys relevance, clarity, technical_knowledge, structure (integer scores 0-100), improve (string). Do not invent user achievements. Question: {question}; answer: {answer}")
    if ai:
        feedback.update({key: ai[key] for key in feedback if key in ai})
        feedback["demo"] = False
    feedback["ai_message"] = error
    session_id = payload.get("session_id")
    try:
        question_index = int(payload.get("question_index", -1))
    except (ValueError, TypeError):
        question_index = -1
    if session_id:
        sessions = read_json("interview_history", [])
        session = next((item for item in sessions if item.get("id") == session_id), None)
        if session and 0 <= question_index < len(session.get("questions", [])):
            answers = session.setdefault("answers", [])
            saved_answer = {"question_index": question_index, "question": question, "answer": answer, "feedback": feedback}
            existing = next((index for index, item in enumerate(answers) if item.get("question_index") == question_index), None)
            if existing is None:
                answers.append(saved_answer)
            else:
                answers[existing] = saved_answer
            write_json("interview_history", sessions)
    return jsonify(feedback)


@app.post("/api/interview/complete")
def interview_complete():
    payload = request.get_json(silent=True) or {}
    session_id = payload.get("session_id")
    sessions = read_json("interview_history", [])
    session = next((item for item in sessions if item.get("id") == session_id), None)
    if not session:
        return response_error("Interview session not found.")
    if not session.get("completed"):
        session["completed"] = True
        write_json("interview_history", sessions)
        achievements = record_xp(30, "Interview Practice")
    else:
        achievements = read_json("achievements", {})
    return jsonify({"achievements": achievements, "message": "Practice session saved. +30 Career XP."})


@app.post("/api/challenge/complete")
def challenge_complete():
    all_progress = read_json("progress", {})
    progress = all_progress.get("local", {})
    today = date.today().isoformat()
    if progress.get("challenge_completed") == today:
        return jsonify({"achievements": read_json("achievements", {}), "message": "Today's challenge is already complete."})
    if progress.get("challenge_started") != today:
        return response_error("Start today's challenge before completing it.")
    progress["challenge_completed"] = today
    all_progress["local"] = progress
    write_json("progress", all_progress)
    result = record_xp(20, "Daily Challenger")
    return jsonify({"achievements": result, "message": "Challenge completed. +20 Career XP."})


@app.post("/api/challenge/start")
def challenge_start():
    all_progress = read_json("progress", {})
    progress = all_progress.get("local", {})
    if not profile_data().get("target_role"):
        return response_error("Create a career profile before starting a challenge.")
    today = date.today().isoformat()
    if progress.get("challenge_completed") == today:
        return jsonify({"message": "Today's challenge is already complete.", "progress": progress})
    progress["challenge_started"] = today
    all_progress["local"] = progress
    write_json("progress", all_progress)
    return jsonify({"message": "Challenge started. Take a few minutes to work through it.", "progress": progress})


@app.post("/api/resources/save")
def resource_save():
    payload = request.get_json(silent=True) or {}
    url = str(payload.get("url", ""))
    resource = next((item for item in career_service.RESOURCES if item["url"] == url), None)
    if resource is None:
        return response_error("Choose a verified learning resource.")
    items = read_json("saved_resources", [])
    if not any(item.get("url") == url for item in items):
        append_json("saved_resources", resource)
        record_xp(5, "Resource Curator")
    return jsonify({"saved_resources": read_json("saved_resources", []), "message": "Resource saved."})


@app.get("/api/resources")
def resources():
    return jsonify({"resources": career_service.RESOURCES, "saved": read_json("saved_resources", [])})


@app.errorhandler(413)
def too_large(_error):
    return response_error("Resume files must be 5 MB or smaller.", 413)


@app.errorhandler(500)
def unexpected_error(error):
    logging.exception("Unhandled application error: %s", error)
    return response_error("Something went wrong. Please try again.", 500)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=False)
