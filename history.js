/**
 * AI Smart Interview System — History Module
 * Fetches past interviews, renders history table, and draws progress chart
 */

async function loadHistory() {
    try {
        const data = await api('/api/interview/history');
        const sessions = data.sessions || [];
        
        renderHistoryTable(sessions);
        renderHistoryChart(sessions);

    } catch (error) {
        showToast('Failed to load interview history', 'error');
    }
}

function renderHistoryTable(sessions) {
    const wrapper = document.getElementById('history-table-wrapper');
    const emptyState = document.getElementById('history-empty');

    if (sessions.length === 0) {
        wrapper.parentElement.classList.add('hidden');
        emptyState.classList.remove('hidden');
        return;
    }

    wrapper.parentElement.classList.remove('hidden');
    emptyState.classList.add('hidden');

    let html = `
        <table class="history-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Difficulty</th>
                    <th>Questions</th>
                    <th>Score</th>
                    <th>Readiness</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
    `;

    sessions.forEach(session => {
        const score = Math.round(session.overall_score || 0);
        const readiness = Math.round(session.readiness_pct || 0);
        
        html += `
            <tr>
                <td>${formatDate(session.completed_at)}</td>
                <td><span class="badge badge-blue">${capitalize(session.interview_type)}</span></td>
                <td>${capitalize(session.difficulty)}</td>
                <td>${session.num_questions}</td>
                <td class="score-cell ${getScoreClass(score)}">${score}%</td>
                <td>
                    <div class="progress-bar">
                        <div class="progress-bar-fill" style="width: ${readiness}%; background: var(--gradient-success)"></div>
                    </div>
                </td>
                <td>
                    <div class="flex gap-xs">
                        <button class="btn btn-secondary btn-sm" onclick="viewDetailedResult(${session.id})">
                            Details
                        </button>
                        <button class="btn btn-ghost btn-sm" onclick="openReportForSession(${session.id})" title="View full visual performance report">
                            🏆 Report
                        </button>
                    </div>
                </td>
            </tr>
        `;
    });

    html += `</tbody></table>`;
    wrapper.innerHTML = html;
}

function renderHistoryChart(sessions) {
    const container = document.getElementById('history-chart');
    const chartWrapper = document.getElementById('history-chart-wrapper');
    
    if (sessions.length < 2) {
        chartWrapper.classList.add('hidden');
        return;
    }
    
    chartWrapper.classList.remove('hidden');
    container.innerHTML = '';

    // Take oldest to newest for chronological chart (up to last 15)
    const chartData = [...sessions].reverse().slice(-15);

    chartData.forEach((session, i) => {
        const score = Math.round(session.overall_score || 0);
        
        const bar = document.createElement('div');
        bar.className = 'chart-bar';
        bar.style.height = '0%'; // Start at 0 for animation
        bar.title = `${capitalize(session.interview_type)}: ${score}%`;
        
        bar.innerHTML = `
            <div class="chart-bar-value">${score}</div>
            <div class="chart-bar-label">#${i+1}</div>
        `;
        
        container.appendChild(bar);
        
        // Animate height
        setTimeout(() => {
            bar.style.height = `${score}%`;
        }, 100 + (i * 50));
    });
}

// ── Detail Modal ─────────────────────────────────────────

async function viewDetailedResult(sessionId) {
    showLoading('Loading details...');
    try {
        const data = await api(`/api/interview/${sessionId}`);
        
        const modal = document.getElementById('detail-modal');
        const body = document.getElementById('detail-modal-body');
        const session = data.session;
        
        let html = `
            <div class="flex justify-between items-center mb-lg">
                <div>
                    <h4 style="font-size:1.125rem;font-weight:700">${capitalize(session.interview_type)} Interview</h4>
                    <p style="color:var(--text-muted);font-size:0.875rem">${formatDate(session.completed_at)} • ${capitalize(session.difficulty)}</p>
                </div>
                <div class="score-circle" style="transform:scale(0.6);transform-origin:right center;margin:-20px 0">
                    <svg width="100" height="100">
                        <circle class="score-circle-bg" cx="50" cy="50" r="45" stroke-width="8"></circle>
                        <circle class="score-circle-fill" cx="50" cy="50" r="45" stroke-width="8"
                                stroke="${getScoreColor(session.overall_score)}"
                                stroke-dasharray="283"
                                stroke-dashoffset="${283 - (session.overall_score/100 * 283)}"></circle>
                    </svg>
                    <div class="score-circle-text">
                        <div class="score-circle-value" style="font-size:1.5rem">${Math.round(session.overall_score)}</div>
                    </div>
                </div>
            </div>
            
            <div class="mb-lg">
                <h4 style="font-size:0.875rem;font-weight:700;color:var(--blue-light);margin-bottom:var(--space-sm)">AI Summary</h4>
                <p style="font-size:0.875rem;color:var(--text-secondary);line-height:1.6">${session.feedback_summary}</p>
            </div>
            
            <h4 style="font-size:1rem;font-weight:700;margin-bottom:var(--space-md);border-bottom:1px solid var(--border-color);padding-bottom:var(--space-sm)">Questions & Answers</h4>
            <div style="display:flex;flex-direction:column;gap:var(--space-lg)">
        `;

        data.questions.forEach(q => {
            const rawScore = q.score || 0;
            const isTenScale = rawScore <= 10;
            const scoreVal = isTenScale ? rawScore : Math.round(rawScore);
            const scoreDisplay = isTenScale ? `${scoreVal} / 10` : `${scoreVal} / 100`;
            
            let badgeClass = 'badge-red';
            if (isTenScale) {
                if (scoreVal >= 9) badgeClass = 'badge-green';
                else if (scoreVal >= 7) badgeClass = 'badge-blue';
                else if (scoreVal >= 5) badgeClass = 'badge-orange';
            } else {
                if (scoreVal >= 70) badgeClass = 'badge-green';
                else if (scoreVal >= 40) badgeClass = 'badge-orange';
            }

            const statusText = q.status ? escapeHtml(q.status) : '';
            let statusBadgeClass = 'badge-purple';
            const sLower = statusText.toLowerCase();
            if (sLower.includes('excellent') || (sLower.includes('good') && !sLower.includes('not good'))) {
                statusBadgeClass = 'badge-green';
            } else if (sLower.includes('average') || sLower.includes('partially')) {
                statusBadgeClass = 'badge-orange';
            } else if (sLower.includes('mismatch') || sLower.includes('not good') || sLower.includes('needs')) {
                statusBadgeClass = 'badge-red';
            }
            const safeQuestion = escapeHtml(q.question_text || '');
            const safeAnswer = q.answer_text ? escapeHtml(q.answer_text) : '<em>No answer provided</em>';
            const safeFeedback = q.feedback ? escapeHtml(q.feedback) : '';
            const safePerfect = q.perfect_answer ? escapeHtml(q.perfect_answer) : '';
            const safeImprove = q.improvement ? escapeHtml(q.improvement) : '';

            html += `
                <div style="background:var(--bg-glass);padding:var(--space-md);border-radius:var(--radius-md);border:1px solid var(--border-color)">
                    <div class="flex justify-between items-center mb-sm">
                        <p style="font-weight:600;margin:0">
                            <span style="color:var(--blue-light)">Q${q.question_number}.</span> ${safeQuestion}
                        </p>
                        <div class="flex gap-xs items-center">
                            <span class="badge ${badgeClass}">${scoreDisplay}</span>
                            ${statusText ? `<span class="badge ${statusBadgeClass}" style="font-size:0.75rem">${statusText}</span>` : ''}
                        </div>
                    </div>
                    <div style="font-size:0.875rem;color:#93c5fd;margin-bottom:var(--space-sm);padding:var(--space-sm);background:rgba(0,0,0,0.25);border-radius:var(--radius-sm)">
                        <strong style="color:var(--text-muted);font-size:0.75rem;display:block;margin-bottom:2px">YOUR ANSWER:</strong>
                        ${safeAnswer}
                    </div>
                    ${safeFeedback ? `<p style="font-size:0.813rem;color:var(--text-secondary);margin-top:var(--space-xs);padding-top:var(--space-xs)">🤖 <strong>AI Evaluation:</strong> ${safeFeedback}</p>` : ''}
                    ${safePerfect ? `<div style="font-size:0.813rem;color:#d1fae5;background:rgba(16,185,129,0.08);border-left:3px solid #10b981;padding:6px 10px;border-radius:var(--radius-sm);margin-top:var(--space-xs)">⭐ <strong>Perfect Answer:</strong> ${safePerfect}</div>` : ''}
                    ${safeImprove ? `<div style="font-size:0.813rem;color:#ede9fe;background:rgba(139,92,246,0.08);border-left:3px solid #8b5cf6;padding:6px 10px;border-radius:var(--radius-sm);margin-top:var(--space-xs)">💡 <strong>How to Improve:</strong> ${safeImprove}</div>` : ''}
                </div>
            `;
        });

        html += `
            </div>
            <div style="margin-top:var(--space-lg);padding-top:var(--space-md);border-top:1px solid var(--border-color);display:flex;justify-content:flex-end;">
                <button type="button" class="btn btn-primary" onclick="openReportForSession(${session.id})">
                    🏆 View Full Performance Report
                </button>
            </div>
        `;
        
        body.innerHTML = html;
        modal.classList.remove('hidden');

    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function openReportForSession(sessionId) {
    const modal = document.getElementById('detail-modal');
    if (modal) modal.classList.add('hidden');
    showLoading('Loading performance report...');
    try {
        const data = await api(`/api/interview/${sessionId}`);
        navigateTo('results');
        if (typeof renderResults === 'function') {
            renderResults(data);
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
        showToast(err.message, 'error');
    } finally {
        hideLoading();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Empty state start button
    const startBtn = document.getElementById('history-start-btn');
    if (startBtn) {
        startBtn.addEventListener('click', () => navigateTo('interview-setup'));
    }

    // Modal close handlers
    const modal = document.getElementById('detail-modal');
    const closeBtn = document.getElementById('close-detail-modal');
    const footerBtn = document.getElementById('detail-modal-close-btn');

    if (modal && closeBtn && footerBtn) {
        const close = () => modal.classList.add('hidden');
        closeBtn.addEventListener('click', close);
        footerBtn.addEventListener('click', close);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) close();
        });
    }
});
