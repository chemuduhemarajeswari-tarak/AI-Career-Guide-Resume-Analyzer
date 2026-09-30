"""Role-aware career guidance, learning resources, and local demo generators."""

from __future__ import annotations

import re

from utils.json_handler import read_json

ROLE_SKILLS = {
    "software developer": ["Python", "Data structures", "SQL", "Git", "REST APIs", "Testing", "Problem solving"],
    "web developer": ["HTML", "CSS", "JavaScript", "Git", "Responsive design", "REST APIs", "Accessibility"],
    "frontend developer": ["HTML", "CSS", "JavaScript", "React", "Git", "Responsive design", "Accessibility"],
    "backend developer": ["Python", "SQL", "REST APIs", "Git", "Testing", "Authentication", "Docker"],
    "python developer": ["Python", "SQL", "REST APIs", "Git", "Testing", "Flask", "Data structures"],
    "java developer": ["Java", "OOP", "SQL", "Git", "REST APIs", "Testing", "Spring Boot"],
    "data analyst": ["SQL", "Excel", "Python", "Data visualization", "Statistics", "Power BI", "Communication"],
    "data scientist": ["Python", "Statistics", "SQL", "Machine learning", "Data visualization", "Pandas", "Experiment design"],
    "ai/ml engineer": ["Python", "Statistics", "Machine learning", "Deep learning", "SQL", "Model evaluation", "Git"],
    "cloud engineer": ["Linux", "Networking", "AWS", "Cloud architecture", "Security", "Terraform", "Docker"],
    "cybersecurity analyst": ["Networking", "Linux", "Security fundamentals", "Incident response", "Python", "SIEM", "Risk analysis"],
}

RESOURCES = read_json("resources", [])


def role_requirements(role: str) -> list[str]:
    normalized = role.strip().lower()
    return ROLE_SKILLS.get(normalized, ["Problem solving", "Communication", "Git", "Role-specific fundamentals", "Projects"])


def skill_list(value: str | list[str]) -> list[str]:
    items = value if isinstance(value, list) else re.split(r"[,\n;]", value)
    return list(dict.fromkeys(item.strip() for item in items if isinstance(item, str) and item.strip()))


def skill_gaps(role: str, skills: list[str], job_description: str = "") -> dict:
    required = role_requirements(role)
    resume_text = " ".join(skills + [job_description]).lower()
    present = [skill for skill in required if skill.lower() in resume_text]
    missing = [skill for skill in required if skill not in present]
    must_count = max(2, len(required) // 3)
    return {
        "required": required,
        "already_have": present,
        "need_to_improve": present[:2],
        "need_to_learn": missing,
        "priorities": [
            {"skill": skill, "level": "MUST LEARN" if index < must_count else "IMPORTANT" if index < must_count + 3 else "OPTIONAL", "reason": f"{skill} is a core requirement for {role}."}
            for index, skill in enumerate(missing)
        ],
    }


def study_minutes(available_time: str) -> int:
    value = (available_time or "").lower()
    match = re.search(r"\d+", value)
    amount = int(match.group()) if match else 1
    if "3+" in value:
        return 180
    if "minute" in value:
        return max(30, min(amount, 180))
    return max(30, min(amount * 60, 180))


def build_roadmap(profile: dict, gaps: dict) -> list[dict]:
    minutes = study_minutes(profile.get("available_time", "1 hour/day"))
    skills = gaps["need_to_learn"] + gaps["already_have"]
    if not skills:
        skills = role_requirements(profile.get("target_role", "Software Developer"))
    level = profile.get("skill_level", "Beginner")
    resources = RESOURCES
    roadmap = []
    for day in range(1, 31):
        skill = skills[(day - 1) % len(skills)]
        matching = next((resource for resource in resources if skill.lower() in resource["topic"].lower() or resource["topic"].lower() in skill.lower()), resources[(day - 1) % len(resources)])
        estimated = min(minutes, 25 if minutes == 30 else 50 if minutes == 60 else minutes)
        roadmap.append({
            "day": day,
            "topic": f"{skill}: {['core concepts', 'guided practice', 'applied exercise'][((day - 1) // len(skills)) % 3]}",
            "why": f"{skill} helps build the skills expected for a {profile.get('target_role', 'target role')}.",
            "learn": f"Study {skill} at a {level.lower()} level, then summarize one concept in your own words.",
            "task": f"Complete a small {skill} exercise and record what worked and what you would improve.",
            "estimated_minutes": estimated,
            "resource": matching,
            "challenge": f"Use {skill} to solve one practical problem without copying a complete solution.",
        })
    return roadmap


def adapt_roadmap(roadmap: list[dict], completed: list[int], available_time: str, elapsed_days: int) -> dict:
    remaining = [day for day in roadmap if day["day"] not in completed]
    limit = study_minutes(available_time)
    for item in remaining:
        item["estimated_minutes"] = min(item.get("estimated_minutes", limit), limit)
        item["task"] = f"Focused practice: {item['task']}"
    missed = max(0, min(elapsed_days, len(roadmap)) - len(completed))
    return {"remaining_roadmap": remaining, "completed_count": len(completed), "missed_count": missed, "remaining_count": len(remaining), "changes": ["Kept every incomplete topic on the plan.", "Shortened practice blocks to fit your selected daily study time.", "Prioritized focused exercises over extra reading."]}


def project_recommendations(role: str, gaps: dict) -> list[dict]:
    skills = gaps["need_to_learn"] or role_requirements(role)[:3]
    names = ["Skill-gap practice tool", "Role-focused portfolio project", "Production-ready team workflow"]
    levels = ["Beginner", "Intermediate", "Advanced"]
    return [{
        "name": names[index], "difficulty": levels[index], "duration": ["2-3 days", "1-2 weeks", "2-4 weeks"][index],
        "idea": f"Build a {role.lower()} project that puts {', '.join(skills[:index + 1])} into practice.",
        "technologies": skills[:index + 2], "skills_gained": skills[:index + 2],
        "features": ["A clear user problem", "Input validation", "A concise project README"],
        "steps": [f"Define a small {role.lower()} use case", "Build and test the core workflow", "Document decisions and next steps"],
        "resume_bullet": "Add a truthful bullet describing the feature you implemented and the tools you personally used.",
    } for index in range(3)]


def job_search(role: str) -> dict:
    portals = [
        {"name": "LinkedIn Jobs", "purpose": "Professional roles and networking", "url": "https://www.linkedin.com/jobs/"},
        {"name": "Naukri", "purpose": "India-focused professional job listings", "url": "https://www.naukri.com/"},
        {"name": "Indeed", "purpose": "Broad job listings", "url": "https://www.indeed.com/"},
        {"name": "Glassdoor", "purpose": "Job listings and employer research", "url": "https://www.glassdoor.com/Jobs/index.htm"},
        {"name": "Wellfound", "purpose": "Startup roles", "url": "https://wellfound.com/jobs"},
        {"name": "Internshala", "purpose": "Internships and entry-level opportunities", "url": "https://internshala.com/"},
    ]
    keywords = [role, f"Junior {role}", f"{role} Intern", f"{role} Entry Level", f"Remote {role}"]
    return {"portals": portals, "keywords": keywords}


def career_path(role: str) -> list[dict]:
    return [
        {"stage": "Learning", "focus": "Build fundamentals", "skills": role_requirements(role)[:3], "next": "Practice with a small project and get feedback."},
        {"stage": "First experience", "focus": "Apply skills in a real context", "skills": role_requirements(role)[2:5], "next": "Document your own contribution and keep learning from teammates."},
        {"stage": "Growing practitioner", "focus": "Own increasingly complex work", "skills": role_requirements(role)[3:6], "next": "Build depth in an area that interests you and support others."},
        {"stage": "Experienced contributor", "focus": "Share expertise and shape solutions", "skills": role_requirements(role)[-3:], "next": "Possible directions depend on your interests, opportunities, and experience."},
    ]
