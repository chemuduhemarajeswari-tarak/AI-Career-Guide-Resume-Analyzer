const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
const state = { interview: null, questionIndex: 0, weaknesses: [], showSaved: false };
const API_TIMEOUT_MS = 25000;

function icons() { if (window.lucide) window.lucide.createIcons(); }
function notify(message, kind = "") {
  const notice = $("#notice");
  notice.textContent = message;
  notice.className = `notice ${kind}`;
  notice.hidden = false;
  window.clearTimeout(notify.timer);
  notify.timer = window.setTimeout(() => { notice.hidden = true; }, 4200);
}
function busy(label, action) {
  const overlay = $("#loading");
  $("#loading-label").textContent = label;
  overlay.hidden = false;
  return Promise.resolve().then(action).catch((error) => notify(error.message || "Something went wrong. Please try again.", "error")).finally(() => { overlay.hidden = true; });
}
async function api(url, options = {}) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), API_TIMEOUT_MS);
  try {
    const response = await fetch(url, { ...options, signal: controller.signal });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || "Request failed. Please try again.");
    return data;
  } catch (error) {
    if (error.name === "AbortError") throw new Error("This request timed out. Refresh to check for results, then try again.");
    if (error instanceof TypeError) throw new Error("Can't reach the career app. Confirm Flask is running at http://127.0.0.1:5001/");
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}
function jsonOptions(body) { return { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }; }
function addOptionalControls() {
  const careerGrid = $("#career-form .form-grid");
  careerGrid.insertAdjacentHTML("beforeend", '<label class="full-field">Certifications (optional)<input name="certifications" maxlength="500" placeholder="Only list certifications you have earned"></label>');
  $("#project-list").insertAdjacentHTML("afterend", '<form class="panel project-log-form" id="project-log-form"><div class="form-heading"><h3>Log a completed project</h3><p>Only include work you actually completed. This portfolio entry contributes to career readiness.</p></div><div class="form-grid"><label>Project name *<input name="name" required maxlength="120" placeholder="e.g. Campus events API"></label><label>Technologies *<input name="technologies" required maxlength="500" placeholder="e.g. Python, Flask, SQLite"></label><label class="full-field">What does it do? *<textarea name="description" required rows="2" maxlength="1500" placeholder="Describe the project accurately"></textarea></label></div><div class="form-footer"><span class="privacy-note">Earn +40 Career XP</span><button class="button button-outline" type="submit"><i data-lucide="folder-plus"></i> Add to my portfolio</button></div></form>');
  $(".bottom-grid").insertAdjacentHTML("afterend", '<div class="dashboard-grid progression-grid"><article class="panel"><div class="panel-heading"><div><p class="eyebrow">MILESTONES</p><h3>Badges you\'ve earned</h3></div></div><div id="badge-list" class="badge-list"><p class="empty-note">Your first badge is one useful step away.</p></div></article><article class="panel"><div class="panel-heading"><div><p class="eyebrow">PICK UP WHERE YOU LEFT OFF</p><h3>Saved resources</h3></div><button class="text-button" data-go="resources">Browse library <i data-lucide="arrow-up-right"></i></button></div><div id="saved-preview" class="saved-preview"><p class="empty-note">Save a resource to keep it close.</p></div></article></div>');
  $("#project-log-form").addEventListener("submit", (event) => {
    event.preventDefault();
    busy("Saving your project...", async () => {
      const result = await api("/api/projects/log", jsonOptions(Object.fromEntries(new FormData(event.currentTarget).entries())));
      notify(result.message, "success");
      event.currentTarget.reset();
      await loadDashboard();
    });
  });
  icons();
}
function go(view) {
  $$(".view").forEach((section) => section.classList.toggle("active", section.id === `view-${view}`));
  $$(".nav-link").forEach((button) => button.classList.toggle("active", button.dataset.view === view));
  const active = $(`.nav-link[data-view="${view}"] span`);
  $("#crumb-current").textContent = active?.textContent || (view === "overview" ? "Overview" : view);
  $("#sidebar").classList.remove("open");
  window.scrollTo({ top: 0, behavior: "smooth" });
  if (view === "resources") loadResources();
  if (view === "history") loadHistory();
  if (view === "jobs") loadJobs();
  if (view === "skill-gap") loadCareerPath();
  if (view === "twin") loadDashboard();
  icons();
}

$$(".nav-link").forEach((button) => button.addEventListener("click", () => go(button.dataset.view)));
$$('[data-go]').forEach((button) => button.addEventListener("click", () => go(button.dataset.go)));
$("#menu-toggle").addEventListener("click", () => $("#sidebar").classList.toggle("open"));
$("#refresh-dashboard").addEventListener("click", loadDashboard);

async function loadDashboard() {
  try {
    const data = await api("/api/dashboard");
    const profile = data.profile || {};
    const plan = data.plan || {};
    const progress = data.progress || {};
    const achievement = data.achievements || {};
    const days = plan.roadmap || [];
    const completed = progress.completed_days || [];
    const percent = Math.round(completed.length / Math.max(1, days.length) * 100);
    const name = profile.name || "Your profile";
    const role = profile.target_role || "Your next role";
    $("#side-name").textContent = name;
    $("#avatar-initial").textContent = name.slice(0, 1).toUpperCase();
    $("#side-role").textContent = role;
    $("#side-progress").style.width = `${percent}%`;
    $("#side-progress-label").textContent = days.length ? `${completed.length} of ${days.length} days complete` : "Set up your career profile";
    $("#xp-label").textContent = `${achievement.xp || 0} Career XP`;
    $("#hero-role").textContent = profile.target_role ? `Growing into ${profile.target_role}.` : "Your next chapter starts here.";
    $("#hero-summary").textContent = plan.summary || "Map the skills, habits, and small wins that move you toward work you want.";
    $("#welcome-copy").textContent = profile.name ? `Good to have you here, ${profile.name}. Keep your next step in view.` : "A little direction goes a long way. Start with your career profile.";
    $("#readiness-value").textContent = data.readiness_score || 0;
    $("#readiness-bar").style.width = `${data.readiness_score || 0}%`;
    $("#roadmap-value").textContent = completed.length;
    $("#roadmap-total").textContent = `/ ${days.length || 30} days`;
    $("#roadmap-caption").textContent = days.length ? `${percent}% of your plan` : "Create your 30-day plan";
    $("#roadmap-bar").style.width = `${percent}%`;
    $("#streak-value").textContent = progress.streak || 0;
    $("#xp-value").textContent = achievement.xp || 0;
    $("#level-value").textContent = `${achievement.level || "Beginner"} level`;
    const readiness = data.readiness || {};
    $("#readiness-list").innerHTML = Object.entries(readiness).map(([label, value]) => `<div class="readiness-item"><span>${escapeHtml(label)}</span><div class="thin-track"><span style="width:${Math.max(0, Math.min(100, Number(value) || 0))}%"></span></div><strong>${Number(value) || 0}%</strong></div>`).join("");
    const actions = plan.next_actions || [];
    $("#next-actions").innerHTML = actions.length ? actions.slice(0, 5).map((item) => `<li>${escapeHtml(item)}</li>`).join("") : "<li>Create your career profile to get tailored next steps.</li>";
    const gaps = plan.gaps || {};
    const missing = gaps.need_to_learn || [];
    const have = gaps.already_have || [];
    $("#skill-preview").innerHTML = [...have.slice(0, 4).map((skill) => `<span class="skill-pill">${escapeHtml(skill)} · have</span>`), ...missing.slice(0, 6).map((skill) => `<span class="skill-pill missing">${escapeHtml(skill)}</span>`)].join("") || '<p class="empty-note">Your role-specific skills will show here.</p>';
    $("#challenge-title").textContent = profile.target_role ? `A ${profile.target_role} practice prompt` : "A small challenge, a useful habit.";
    $("#challenge-copy").textContent = profile.target_role ? `Write down one real problem a ${profile.target_role.toLowerCase()} might solve, then outline your first three steps.` : "Create your profile to get a challenge for your target role.";
    const challengeDone = progress.challenge_completed === new Date().toISOString().slice(0, 10);
    const challengeStarted = progress.challenge_started === new Date().toISOString().slice(0, 10);
    $("#start-challenge").disabled = !profile.target_role || challengeStarted || challengeDone;
    $("#start-challenge").innerHTML = `<i data-lucide="${challengeStarted || challengeDone ? "check" : "play"}"></i> ${challengeDone ? "Completed today" : challengeStarted ? "Challenge started" : "Start challenge"}`;
    $("#complete-challenge").disabled = !challengeStarted || challengeDone;
    $("#complete-challenge").innerHTML = `<i data-lucide="check"></i> ${challengeDone ? "Challenge completed" : "Complete challenge"}`;
    $("#gap-role").value = profile.target_role || $("#gap-role").value;
    $("#gap-skills").value = (profile.current_skills || []).join(", ") || $("#gap-skills").value;
    $("#job-role").value = profile.target_role || $("#job-role").value;
    const aligned = gaps.already_have || [];
    $("#twin-role").textContent = profile.target_role || "Build your profile to begin.";
    $("#twin-summary").textContent = plan.summary || "Your skill alignment and progress will appear here.";
    $("#twin-readiness").textContent = `${data.readiness_score || 0}%`;
    $("#twin-skills").textContent = String(Math.round(aligned.length / Math.max(1, gaps.required?.length || 1) * 100));
    $("#twin-skill-count").textContent = `${aligned.length} role skills detected`;
    $("#twin-roadmap").textContent = completed.length;
    $("#twin-roadmap-bar").style.width = `${percent}%`;
    $("#twin-resume").textContent = data.latest_resume ? data.latest_resume.score : "—";
    $("#twin-resume-unit").textContent = data.latest_resume ? "/ 100" : "";
    $("#twin-xp").textContent = achievement.xp || 0;
    $("#twin-level").textContent = `${achievement.level || "Beginner"} level`;
    $("#twin-gaps").innerHTML = [...(gaps.need_to_learn || []).map((skill) => `<span class="skill-pill missing">${escapeHtml(skill)}</span>`), ...(gaps.need_to_improve || []).map((skill) => `<span class="skill-pill">Refresh · ${escapeHtml(skill)}</span>`)].join("") || '<p class="empty-note">Create your career profile to see next skills.</p>';
    $("#twin-actions").innerHTML = actions.length ? actions.slice(0, 5).map((item) => `<li>${escapeHtml(item)}</li>`).join("") : "<li>Create your career profile to get tailored next steps.</li>";
    const badges = achievement.badges || [];
    $("#badge-list").innerHTML = badges.length ? badges.map((badge) => `<span class="badge-chip"><i data-lucide="award"></i>${escapeHtml(badge)}</span>`).join("") : '<p class="empty-note">Your first badge is one useful step away.</p>';
    const saved = data.saved_resources || [];
    $("#saved-preview").innerHTML = saved.length ? saved.slice(0, 3).map((resource) => `<a href="${escapeHtml(resource.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(resource.name)} <i data-lucide="arrow-up-right"></i></a>`).join("") : '<p class="empty-note">Save a resource to keep it close.</p>';
    if (days.length) renderRoadmap(plan, progress);
    $("#roadmap-intro").textContent = profile.target_role ? `A practical learning rhythm for becoming a ${profile.target_role}, within your ${profile.available_time || "daily"} study window.` : "A practical learning rhythm, shaped around your target role.";
    $("#roadmap-done").textContent = completed.length;
    $("#roadmap-streak").textContent = `${progress.streak || 0} day streak`;
    $("#roadmap-detail-bar").style.width = `${percent}%`;
    $("#roadmap-detail-caption").textContent = days.length ? `${completed.length} complete · ${days.length - completed.length} remaining` : "Generate a career profile to begin";
    const status = await api("/api/ai-status");
    $("#ai-label").textContent = status.configured ? "Gemini connected" : "Demo mode · AI not configured";
    $("#ai-dot").style.background = status.configured ? "#57a477" : "#e2a34b";
    icons();
  } catch (error) { notify(error.message, "error"); }
}

function renderRoadmap(plan, progress) {
  const done = new Set(progress.completed_days || []);
  $("#roadmap-list").innerHTML = plan.roadmap.map((day) => `<article class="roadmap-day ${done.has(day.day) ? "completed" : ""}"><span class="day-number">${String(day.day).padStart(2, "0")}</span><div class="day-content"><h3>${escapeHtml(day.topic)}</h3><p><strong>Why:</strong> ${escapeHtml(day.why)}</p><p><strong>Learn:</strong> ${escapeHtml(day.learn)}</p><p><strong>Try:</strong> ${escapeHtml(day.task)}</p><p><strong>Challenge:</strong> ${escapeHtml(day.challenge)}</p><div class="day-meta"><span><i data-lucide="clock-3"></i> ${day.estimated_minutes} min</span><a href="${escapeHtml(day.resource.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(day.resource.name)} ↗</a></div></div><button class="button button-outline complete-day" data-day="${day.day}" ${done.has(day.day) ? "disabled" : ""}><i data-lucide="${done.has(day.day) ? "check" : "circle-check"}"></i> ${done.has(day.day) ? "Complete" : "Mark complete"}</button></article>`).join("");
  icons();
}

$("#career-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(event.currentTarget).entries());
  busy("Generating your personalized roadmap...", async () => {
    const plan = await api("/api/career/generate", jsonOptions(payload));
    const result = $("#career-result");
    result.hidden = false;
    result.innerHTML = `<h3>${escapeHtml(plan.profile.target_role)} · your learning direction</h3><p>${escapeHtml(plan.summary)}</p><p><strong>${plan.demo ? "DEMO DATA" : "AI-GUIDED"}</strong>${plan.ai_message ? ` · ${escapeHtml(plan.ai_message)}` : ""}</p><p>${plan.gaps.priorities.length} role-related skill gaps prioritized. Your 30-day roadmap is ready.</p>`;
    notify("Career plan created. Your roadmap is ready.", "success");
    await loadDashboard();
    go("roadmap");
  });
});

$("#roadmap-list").addEventListener("click", (event) => {
  const button = event.target.closest(".complete-day");
  if (!button || button.disabled) return;
  busy("Saving your roadmap progress...", async () => {
    const result = await api("/api/roadmap/progress", jsonOptions({ day: Number(button.dataset.day) }));
    notify(result.message, "success");
    await loadDashboard();
  });
});

$("#skill-gap-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const values = Object.fromEntries(new FormData(event.currentTarget).entries());
  busy("Comparing your skills with role requirements...", async () => {
    const result = await api("/api/skill-gap", jsonOptions(values));
    const priorities = result.priorities || [];
    $("#gap-result").innerHTML = `<div class="result-content"><p class="eyebrow">ROLE SKILLS · ${escapeHtml(values.target_role)}</p><h3>Start with what matters most.</h3><h3>Already have</h3><div class="result-tags">${result.already_have.map((skill) => `<span class="result-tag">${escapeHtml(skill)}</span>`).join("") || "<span class='muted'>No matching skills detected yet.</span>"}</div><h3>Need to improve</h3><div class="result-tags">${result.need_to_improve.map((skill) => `<span class="skill-pill">${escapeHtml(skill)}</span>`).join("") || "<span class='muted'>Keep practicing the skills you have.</span>"}</div><h3>Learning priorities</h3>${priorities.map((item, index) => `<div class="priority-line"><span class="priority-number">${String(index + 1).padStart(2, "0")}</span><div><strong>${escapeHtml(item.skill)}</strong><small>${escapeHtml(item.reason)}</small></div><span class="priority-label">${escapeHtml(item.level)}</span></div>`).join("")}</div>`;
    icons();
  });
});
async function loadCareerPath() {
  try {
    const role = $("#gap-role").value || $("#side-role").textContent;
    const result = await api(`/api/career-path?role=${encodeURIComponent(role)}`);
    $("#career-path").innerHTML = `<p class="muted small-copy">Typical stages for a ${escapeHtml(result.role)}. Titles and timing differ across teams and careers.</p><div class="path-steps">${result.stages.map((stage, index) => `<article class="path-step"><span class="path-step-index">0${index + 1}</span><h4>${escapeHtml(stage.stage)}</h4><p>${escapeHtml(stage.focus)}</p><div class="result-tags">${stage.skills.map((skill) => `<span class="skill-pill">${escapeHtml(skill)}</span>`).join("")}</div><small>${escapeHtml(stage.next)}</small></article>`).join("")}</div>`;
  } catch (error) { notify(error.message, "error"); }
}
$("#load-career-path").addEventListener("click", loadCareerPath);

$("#adapt-roadmap").addEventListener("click", () => busy("Adapting your roadmap...", async () => {
  const result = await api("/api/roadmap/adapt", jsonOptions({}));
  const panel = $("#adapt-result");
  panel.hidden = false;
  panel.innerHTML = `<h3>Your adjusted plan</h3><p>${result.completed_count} complete · ${result.missed_count} missed · ${result.remaining_count} still to work through</p>${result.changes.map((change) => `<p>• ${escapeHtml(change)}</p>`).join("")}<p>Incomplete topics remain on your roadmap; use the focused practice tasks to catch up at your own pace.</p>`;
  notify("Roadmap adapted. Incomplete topics are still included.", "success");
}));

$("#resume-file").addEventListener("change", (event) => { $("#resume-file-name").textContent = event.target.files[0]?.name || "No file selected"; });
$("#resume-form").addEventListener("submit", (event) => {
  event.preventDefault();
  busy("Analyzing your resume...", async () => {
    const result = await api("/api/resume/analyze", { method: "POST", body: new FormData(event.currentTarget) });
    renderResume(result);
    await loadDashboard();
    notify(result.demo ? "Resume analyzed with local demo guidance." : "Resume analysis complete.", "success");
  });
});
function renderResume(result) {
  const tags = (values, missing = false) => (values || []).map((item) => `<span class="result-tag ${missing ? "missing" : ""}">${escapeHtml(item)}</span>`).join("") || '<span class="muted">None detected</span>';
  const breakdown = Object.entries(result.breakdown || {}).map(([key, value]) => `<div class="breakdown-row"><span>${escapeHtml(key)}</span><div class="thin-track"><span style="width:${value}%"></span></div><strong>${value}%</strong></div>`).join("");
  const issues = (result.issues || []).map((issue) => `<article class="issue-row"><strong>${escapeHtml(issue.problem)}</strong><p><b>Why it matters:</b> ${escapeHtml(issue.why)}</p><p><b>Try:</b> ${escapeHtml(issue.improve)}</p></article>`).join("") || '<p class="muted">No common layout issues were detected by these simple checks.</p>';
  $("#resume-result").innerHTML = `<div class="result-content"><div class="result-head"><div><p class="eyebrow">${result.demo ? "DEMO DATA · " : "ANALYSIS · "}${escapeHtml(result.target_role)}</p><h3>${escapeHtml(result.summary)}</h3></div><div class="score-ring">${result.score}<small>/100</small></div></div><h3>Already present</h3><div class="result-tags">${tags(result.matching_skills)}</div><h3>Potential gaps · add only if genuinely applicable</h3><div class="result-tags">${tags(result.missing_skills, true)}</div><h3>Compatibility breakdown</h3>${breakdown}<h3>ATS issues to review</h3>${issues}<h3>Practical improvements</h3>${(result.improvements || []).map((item) => `<p>• ${escapeHtml(item)}</p>`).join("")}<h3>Skills to build (only if they match your goals)</h3><div class="result-tags">${tags(result.recommended_skills, true)}</div><h3>Certifications</h3><div class="result-tags">${tags(result.certifications)}</div><p class="disclaimer">${escapeHtml(result.disclaimer)}</p>${result.ai_message ? `<p class="disclaimer">${escapeHtml(result.ai_message)}</p>` : ""}</div>`;
}

$("#bullet-form").addEventListener("submit", (event) => {
  event.preventDefault();
  busy("Improving your wording...", async () => {
    const result = await api("/api/resume/bullet", jsonOptions({ bullet: new FormData(event.currentTarget).get("bullet") }));
    const panel = $("#bullet-result");
    panel.hidden = false;
    panel.innerHTML = `<p><strong>Original:</strong> ${escapeHtml(result.original)}</p><p><strong>Improved:</strong> ${escapeHtml(result.improved)}</p><small>${result.demo ? "DEMO DATA · " : ""}Wording only; verify it accurately reflects your work.</small>`;
  });
});

$("#job-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(event.currentTarget).entries());
  busy("Analyzing the job description...", async () => {
    const result = await api("/api/job-description/analyze", jsonOptions(payload));
    $("#job-result").innerHTML = `<div class="result-content"><div class="result-head"><div><p class="eyebrow">JOB REQUIREMENTS · ${escapeHtml(result.role)}</p><h3>${result.matched.length} of ${result.requirements.length} detected in your resume text</h3></div><span class="count-pill">${result.demo ? "DEMO DATA" : "AI-GUIDED"}</span></div>${result.requirements.map((item) => `<div class="history-entry"><strong>${escapeHtml(item.skill)}</strong><span>${item.status}</span></div>`).join("")}<h3>Suggested actions</h3>${result.actions.map((item) => `<p>• ${escapeHtml(item)}</p>`).join("")}<p class="disclaimer">This comparison does not determine whether you qualify for the job.</p></div>`;
  });
});

async function loadJobs() {
  const role = $("#job-role").value || "";
  try {
    const result = await api(`/api/jobs?role=${encodeURIComponent(role)}`);
    $("#job-portals").innerHTML = `<div class="portal-results">${result.portals.map((portal) => `<article class="portal-card"><a href="${escapeHtml(portal.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(portal.name)} ↗</a><p>${escapeHtml(portal.purpose)}</p></article>`).join("")}</div><p class="eyebrow" style="margin:14px 0 5px">SEARCH QUERIES${role ? ` · ${escapeHtml(role)}` : ""}</p><div class="keyword-list">${result.keywords.map((keyword) => `<span class="keyword-chip">${escapeHtml(keyword)}</span>`).join("")}<span class="keyword-chip">${escapeHtml(role || "Target role")} Remote</span></div>`;
  } catch (error) { notify(error.message, "error"); }
}
$("#load-jobs").addEventListener("click", loadJobs);

$("#recommend-projects").addEventListener("click", () => busy("Finding projects for your skill gaps...", async () => {
  const dash = await api("/api/dashboard");
  const result = await api("/api/projects/recommend", jsonOptions({ target_role: dash.profile.target_role, current_skills: dash.profile.current_skills || [] }));
  $("#project-list").innerHTML = result.projects.map((project, index) => `<article class="project-card"><div class="project-card-top"><span class="eyebrow">PROJECT 0${index + 1}</span><span class="difficulty ${project.difficulty.toLowerCase()}">${escapeHtml(project.difficulty)}</span></div><h3>${escapeHtml(project.name)}</h3><p>${escapeHtml(project.idea)}</p><p><strong>${escapeHtml(project.duration)}</strong></p><div class="result-tags">${project.technologies.map((tech) => `<span class="skill-pill">${escapeHtml(tech)}</span>`).join("")}</div><details><summary>Steps & resume idea</summary><ul>${project.steps.map((step) => `<li>${escapeHtml(step)}</li>`).join("")}</ul><p>${escapeHtml(project.resume_bullet)}</p><small>Add only what you actually build.</small></details></article>`).join("");
  icons();
}));

$("#explain-form").addEventListener("submit", (event) => {
  event.preventDefault();
  busy("Preparing your project explanation...", async () => {
    const result = await api("/api/projects/explain", jsonOptions(Object.fromEntries(new FormData(event.currentTarget).entries())));
    const panel = $("#explain-result");
    panel.hidden = false;
    panel.innerHTML = `<h3>${result.demo ? "DEMO DATA · " : ""}30-second explanation</h3><p>${escapeHtml(result.thirty_second)}</p><h3>One minute</h3><p>${escapeHtml(result.one_minute)}</p><h3>Technical explanation</h3><p>${escapeHtml(result.technical)}</p><h3>Resume bullets</h3>${result.resume_bullets.map((line) => `<p>• ${escapeHtml(line)}</p>`).join("")}<h3>Practice questions</h3>${result.questions.map((line) => `<p>• ${escapeHtml(line)}</p>`).join("")}<small>Review carefully so it stays true to what you did.</small>`;
  });
});

$("#start-interview").addEventListener("click", () => busy("Preparing interview questions...", async () => {
  state.interview = await api("/api/interview/start", jsonOptions({}));
  state.questionIndex = 0;
  state.weaknesses = [];
  showQuestion();
}));
function showQuestion() {
  const question = state.interview.questions[state.questionIndex];
  $("#interview-prompt").hidden = true;
  $("#answer-form").hidden = false;
  $("#interview-feedback").hidden = true;
  $("#next-question").hidden = true;
  $("#question-count").textContent = `QUESTION ${state.questionIndex + 1} OF ${state.interview.questions.length}`;
  $("#question-category").textContent = question.category.toUpperCase();
  $("#question-text").textContent = question.question;
  $("#question-checks").textContent = `What this checks: ${question.checks}`;
  $("#answer-structure").textContent = `Try: ${question.structure}`;
  $("#answer-form").reset();
  icons();
}
$("#answer-form").addEventListener("submit", (event) => {
  event.preventDefault();
  busy("Reviewing your answer...", async () => {
    const question = state.interview.questions[state.questionIndex];
    const result = await api("/api/interview/answer", jsonOptions({ session_id: state.interview.id, question_index: state.questionIndex, question: question.question, answer: new FormData(event.currentTarget).get("answer") }));
    const scores = [["Relevance", result.relevance], ["Clarity", result.clarity], ["Technical content", result.technical_knowledge], ["Structure", result.structure]];
    $("#interview-feedback").hidden = false;
    $("#interview-feedback").innerHTML = `<h3>${result.demo ? "DEMO FEEDBACK · " : "FEEDBACK · "}What is working and what to sharpen</h3><div class="feedback-bars">${scores.map(([label, value]) => `<div class="feedback-score"><span>${label}</span><div class="thin-track"><span style="width:${Math.max(0, Math.min(100, Number(value) || 0))}%"></span></div><strong>${Number(value) || 0}%</strong></div>`).join("")}</div><p>${escapeHtml(result.improve)}</p>${result.ai_message ? `<small>${escapeHtml(result.ai_message)}</small>` : ""}`;
    state.weaknesses.push(result.improve);
    $("#answer-form").hidden = true;
    const finalQuestion = state.questionIndex >= state.interview.questions.length - 1;
    $("#next-question").hidden = false;
    $("#next-question").textContent = finalQuestion ? "Finish practice session" : "Next question →";
    if (state.weaknesses.length >= 3) {
      const recurring = [...new Set(state.weaknesses)].slice(0, 3);
      $("#weakness-note").hidden = false;
      $("#weakness-note").innerHTML = `<strong>Practice themes to revisit</strong><br>${recurring.map(escapeHtml).join("<br>")}`;
    }
  });
});
$("#next-question").addEventListener("click", () => {
  if (state.questionIndex < state.interview.questions.length - 1) { state.questionIndex += 1; showQuestion(); return; }
  $("#answer-form").hidden = true;
  $("#interview-prompt").hidden = false;
  $("#interview-prompt").innerHTML = `<span class="question-mark"><i data-lucide="check-check"></i></span><h2>Practice session complete.</h2><p>You earned 30 Career XP. Come back to another question when you're ready.</p><button class="button button-dark" id="restart-interview"><i data-lucide="rotate-ccw"></i> Start another session</button>`;
  $("#next-question").hidden = true;
  busy("Saving your practice progress...", async () => { const result = await api("/api/interview/complete", jsonOptions({ session_id: state.interview.id })); notify(result.message, "success"); await loadDashboard(); });
  $("#restart-interview").addEventListener("click", () => $("#start-interview").click());
  icons();
});

$("#complete-challenge").addEventListener("click", () => busy("Saving your challenge...", async () => {
  const result = await api("/api/challenge/complete", jsonOptions({}));
  notify(result.message, "success");
  await loadDashboard();
}));
$("#start-challenge").addEventListener("click", () => busy("Starting today's challenge...", async () => {
  const result = await api("/api/challenge/start", jsonOptions({}));
  notify(result.message, "success");
  await loadDashboard();
}));

async function loadResources() {
  try {
    const result = await api("/api/resources");
    const items = state.showSaved ? result.saved : result.resources;
    $("#resource-count").textContent = state.showSaved ? `${items.length} saved resources` : `${items.length} verified learning resources`;
    $("#resource-list").innerHTML = items.length ? items.map((resource) => `<article class="resource-card"><div class="resource-top"><span class="resource-icon"><i data-lucide="book-open-check"></i></span><span class="resource-topic">${escapeHtml(resource.topic)}</span></div><h3>${escapeHtml(resource.name)}</h3><p>${escapeHtml(resource.description)}</p><div class="resource-card-foot"><a href="${escapeHtml(resource.url)}" target="_blank" rel="noopener noreferrer">Open resource ↗</a><button class="save-resource" data-url="${escapeHtml(resource.url)}"><i data-lucide="bookmark-plus"></i> Save</button></div></article>`).join("") : '<div class="empty-state"><span><i data-lucide="bookmark"></i></span><h3>No saved resources yet.</h3><p>Save a resource from the library to keep it here.</p></div>';
    icons();
  } catch (error) { notify(error.message, "error"); }
}
$("#show-saved").addEventListener("click", (event) => { state.showSaved = !state.showSaved; event.currentTarget.innerHTML = `<i data-lucide="${state.showSaved ? "library-big" : "bookmark"}"></i> ${state.showSaved ? "All resources" : "Saved resources"}`; loadResources(); icons(); });
$("#resource-list").addEventListener("click", (event) => {
  const button = event.target.closest(".save-resource");
  if (!button) return;
  busy("Saving resource...", async () => {
    const result = await api("/api/resources/save", jsonOptions({ url: button.dataset.url }));
    notify(result.message, "success");
    await loadResources();
    await loadDashboard();
  });
});

async function loadHistory() {
  try {
    const data = await api("/api/history");
    const groups = [["Career plans", data.career_plans, (item) => `${item.profile?.target_role || "Career plan"} · ${item.created_at || ""}`], ["Resume analyses", data.resume_analyses, (item) => `${item.target_role} · score ${item.score}/100 · ${item.created_at || ""}`], ["Job description analyses", data.job_analyses, (item) => `${item.role} · ${item.matched?.length || 0} requirements matched`], ["Project recommendations", data.project_recommendations, (item) => `${item.role} · ${(item.projects || []).length} project ideas · ${item.created_at || ""}`], ["Projects", data.projects, (item) => `${item.name} · ${item.technologies}`], ["Interview practice", data.interviews, (item) => `${item.role} · ${(item.answers || []).length} answers · ${item.created_at || ""}`], ["Saved resources", data.saved_resources, (item) => item.name]];
    $("#history-content").innerHTML = groups.map(([title, items, label]) => `<article class="panel history-group"><h3>${title} <span class="count-pill">${items.length}</span></h3>${items.length ? items.slice().reverse().map((item) => `<div class="history-entry"><strong>${escapeHtml(label(item))}</strong><span>${escapeHtml(item.demo ? "Demo data" : "Saved locally")}</span></div>`).join("") : '<p class="empty-note">Nothing saved here yet.</p>'}</article>`).join("");
  } catch (error) { notify(error.message, "error"); }
}

addOptionalControls();
loadDashboard();
icons();
