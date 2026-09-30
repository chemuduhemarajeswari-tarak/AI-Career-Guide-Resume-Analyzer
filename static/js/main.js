document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('form[data-endpoint]');

    const escapeHtml = (value) => {
        if (value === null || value === undefined) return 'Not provided';
        return String(value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    };

    const listToHtml = (items) => {
        const list = Array.isArray(items) ? items.filter(Boolean) : [];
        if (!list.length) return '<span class="muted-text">No items yet</span>';
        return `<ul class="detail-list">${list.map(item => `<li>${escapeHtml(item)}</li>`).join('')}</ul>`;
    };

    const renderError = (output, message) => {
        output.innerHTML = `<div class="error-box" role="alert"><strong>Request failed</strong><p>${escapeHtml(message)}</p></div>`;
    };

    const renderCareerDashboard = (data) => {
        const roadmapData = data && data.roadmap ? data.roadmap : {};
        const profile = data && data.profile ? data.profile : (roadmapData.profile || {});
        const priority = roadmapData.priority || {};
        const roadmap = Array.isArray(roadmapData.roadmap) ? roadmapData.roadmap : [];
        const totalDays = roadmap.length || 30;
        const completedDays = 0;
        const progressPercent = Math.round((completedDays / totalDays) * 100);
        const challenge = roadmapData.daily_challenge || 'Complete a short task related to your target role.';

        const mustLearn = Array.isArray(priority.must_learn) ? priority.must_learn : [];
        const important = Array.isArray(priority.important) ? priority.important : [];
        const optional = Array.isArray(priority.optional) ? priority.optional : [];

        const nextSteps = [
            mustLearn.length ? `Start with ${mustLearn[0]} and build one small project around it.` : 'Review your key skill gaps and choose one learning target.',
            important.length ? `Strengthen ${important[0]} with a daily exercise and short recap.` : 'Practice one topic from your roadmap today.',
            roadmap.length ? `Finish the next roadmap task: ${roadmap[0].topic || 'your next learning topic'}.` : 'Keep your learning streak going with one focused task.',
            'Update your resume with your latest project and skill improvements.',
            'Practice one mock interview question before your next application round.'
        ];

        const roadmapHtml = roadmap.length ? roadmap.map((day) => {
            const resources = Array.isArray(day.resources) ? day.resources : [];
            return `
                <article class="roadmap-card">
                    <div class="roadmap-header">
                        <span class="badge">Day ${escapeHtml(day.day || '')}</span>
                        <h4>${escapeHtml(day.topic || 'Learning Topic')}</h4>
                    </div>
                    <div class="roadmap-grid">
                        <div><strong>Estimated time</strong><p>${escapeHtml(day.estimated_time || 'Not provided')}</p></div>
                        <div><strong>What to learn</strong><p>${escapeHtml(day.what_to_learn || 'Not specified')}</p></div>
                        <div><strong>Today's task</strong><p>${escapeHtml(day.task || 'Complete a focused practice activity')}</p></div>
                        <div><strong>Why it matters</strong><p>${escapeHtml(day.why_it_matters || 'Build practical skills for the role')}</p></div>
                        <div><strong>Mini challenge</strong><p>${escapeHtml(day.mini_challenge || 'Apply what you learned in a small exercise')}</p></div>
                        <div><strong>Learning resources</strong><p>${resources.length ? resources.map(item => escapeHtml(item)).join(', ') : 'Use official documentation and beginner-friendly guides.'}</p></div>
                    </div>
                </article>
            `;
        }).join('') : '<div class="empty-box">Your roadmap will appear here once it is generated.</div>';

        output.innerHTML = `
            <div class="career-dashboard">
                <div class="dashboard-header">
                    <div>
                        <p class="eyebrow">Personalized Career Plan</p>
                        <h3>Career dashboard</h3>
                    </div>
                    <span class="badge success-badge">AI-guided roadmap</span>
                </div>

                <section class="career-section">
                    <h4>1. Personalized Career Plan</h4>
                    <div class="info-grid">
                        <div class="info-card"><span>Name</span><strong>${escapeHtml(profile.name || 'Not provided')}</strong></div>
                        <div class="info-card"><span>Target Role</span><strong>${escapeHtml(profile.target_role || roadmapData.target_role || 'Not provided')}</strong></div>
                        <div class="info-card"><span>Education</span><strong>${escapeHtml(profile.education || 'Not provided')}</strong></div>
                        <div class="info-card"><span>Current Skills</span><strong>${escapeHtml(profile.current_skills || 'Not provided')}</strong></div>
                        <div class="info-card"><span>Skill Level</span><strong>${escapeHtml(profile.skill_level || 'Not provided')}</strong></div>
                        <div class="info-card"><span>Preferred Domain</span><strong>${escapeHtml(profile.preferred_domain || 'Not provided')}</strong></div>
                        <div class="info-card"><span>Study Time</span><strong>${escapeHtml(profile.study_time || 'Not provided')}</strong></div>
                    </div>
                </section>

                <section class="career-section">
                    <h4>2. Skill Priorities</h4>
                    <div class="priority-grid">
                        <div class="priority-card must-card">
                            <h5>Must Learn</h5>
                            ${listToHtml(mustLearn)}
                        </div>
                        <div class="priority-card important-card">
                            <h5>Important</h5>
                            ${listToHtml(important)}
                        </div>
                        <div class="priority-card optional-card">
                            <h5>Optional</h5>
                            ${listToHtml(optional)}
                        </div>
                    </div>
                </section>

                <section class="career-section">
                    <h4>3. 30-Day Roadmap</h4>
                    <div class="roadmap-stack">${roadmapHtml}</div>
                </section>

                <section class="career-section">
                    <h4>4. Daily Career Challenge</h4>
                    <div class="challenge-box">
                        <span class="badge">Today’s challenge</span>
                        <p>${escapeHtml(challenge)}</p>
                    </div>
                </section>

                <section class="career-section">
                    <h4>5. Progress</h4>
                    <div class="progress-card">
                        <div class="progress-meta">
                            <span>${completedDays} / ${totalDays} Days Completed</span>
                            <strong>${progressPercent}%</strong>
                        </div>
                        <div class="progress-bar"><span style="width: ${progressPercent}%"></span></div>
                    </div>
                </section>

                <section class="career-section">
                    <h4>6. Next Steps</h4>
                    <ol class="next-steps">${nextSteps.map(step => `<li>${escapeHtml(step)}</li>`).join('')}</ol>
                </section>
            </div>
        `;
    };

    forms.forEach((form) => {
        form.addEventListener('submit', async function (event) {
            event.preventDefault();
            const endpoint = form.dataset.endpoint;
            const output = document.getElementById(form.id.replace('-form', '-output')) || document.querySelector('.result-box');
            if (!output) return;

            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'Processing...';
            }

            try {
                let response;
                if (form.enctype === 'multipart/form-data') {
                    const formData = new FormData(form);
                    response = await fetch(endpoint, { method: 'POST', body: formData });
                } else {
                    const payload = Object.fromEntries(new FormData(form).entries());
                    response = await fetch(endpoint, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                }

                const data = await response.json();
                if (!response.ok || data.success === false) {
                    const message = data.error || data.message || (Array.isArray(data.errors) ? data.errors.join(' ') : '') || `Request failed with status ${response.status}.`;
                    if (endpoint.includes('/api/career/generate')) {
                        console.error('Career plan API error:', data);
                    }
                    renderError(output, message);
                    return;
                }

                if (endpoint.includes('/api/career/generate')) {
                    renderCareerDashboard(data);
                } else if (endpoint.includes('/api/skill-gap')) {
                    const priority = data.priority || {};
                    output.innerHTML = `
                        <h3>Skill Priority</h3>
                        <p><strong>MUST LEARN:</strong> ${(priority.must_learn || []).join(', ') || 'None'}</p>
                        <p><strong>IMPORTANT:</strong> ${(priority.important || []).join(', ') || 'None'}</p>
                        <p><strong>OPTIONAL:</strong> ${(priority.optional || []).join(', ') || 'None'}</p>
                    `;
                } else if (endpoint.includes('/api/projects/recommend')) {
                    const projects = data.projects || [];
                    output.innerHTML = projects.map(project => `
                        <div class='list-item'>
                            <strong>${escapeHtml(project.project_name)}</strong><br>
                            Difficulty: ${escapeHtml(project.difficulty)}<br>
                            Duration: ${escapeHtml(project.estimated_duration)}<br>
                            Technologies: ${escapeHtml((project.technologies || []).join(', '))}
                        </div>
                    `).join('');
                } else if (endpoint.includes('/api/interview/start')) {
                    const questions = data.questions || [];
                    output.innerHTML = questions.map(q => `
                        <div class='list-item'><strong>Q${escapeHtml(q.id)}</strong> (${escapeHtml(q.category)})<br>${escapeHtml(q.question)}</div>
                    `).join('');
                } else if (endpoint.includes('/api/job-description/analyze')) {
                    const analysis = data.analysis || {};
                    output.innerHTML = `
                        <h3>Job Requirement vs Resume</h3>
                        <p>Matched: ${(analysis.resume_match || []).join(', ') || 'None'}</p>
                        <p>Missing: ${(analysis.resume_missing || []).join(', ') || 'None'}</p>
                        <p>Recommended actions: ${(analysis.recommended_actions || []).join(' | ')}</p>
                    `;
                } else {
                    output.innerHTML = '<div class="empty-box">Your result is ready.</div>';
                }
            } catch (error) {
                if (endpoint.includes('/api/career/generate')) {
                    console.error('Career plan request failed:', error);
                } else {
                    console.error('Request failed:', error);
                }
                renderError(output, error instanceof Error ? error.message : String(error));
            } finally {
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.textContent = submitButton.dataset.originalText || submitButton.textContent;
                }
            }
        });
    });

    const challengeButton = document.getElementById('completeChallengeBtn');
    if (challengeButton) {
        challengeButton.addEventListener('click', async function () {
            const response = await fetch('/api/challenge/complete', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ xp: 25 }) });
            const data = await response.json();
            const output = document.getElementById('roadmap-output');
            if (output) output.innerHTML = `<strong>Challenge complete.</strong> ${escapeHtml(data.message || 'XP awarded.')}`;
        });
    }

    const adaptForm = document.getElementById('roadmap-adapt-form');
    if (adaptForm) {
        adaptForm.addEventListener('submit', async function (event) {
            event.preventDefault();
            const payload = {
                completed_days: parseInt(document.getElementById('completed_days').value || '0', 10),
                missed_days: parseInt(document.getElementById('missed_days').value || '0', 10),
                available_time: document.getElementById('available_time').value,
                roadmap: []
            };
            const response = await fetch('/api/roadmap/adapt', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            const output = document.getElementById('roadmap-output');
            if (output) {
                output.innerHTML = `
                    <h3>Adjusted Roadmap</h3>
                    <p><strong>Completed days:</strong> ${escapeHtml(data.result.completed_days || 0)}</p>
                    <p><strong>Missed days:</strong> ${escapeHtml(data.result.missed_days || 0)}</p>
                    <p><strong>Remaining days:</strong> ${escapeHtml(data.result.remaining_days || 0)}</p>
                    <p><strong>What changed:</strong> ${escapeHtml(data.result.change_summary || 'No major changes were needed.')}</p>
                `;
            }
        });
    }

    const formsWithLabels = document.querySelectorAll('form');
    formsWithLabels.forEach(form => {
        form.querySelectorAll('button[type="submit"]').forEach(button => {
            button.dataset.originalText = button.textContent;
        });
    });
});
