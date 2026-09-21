/**
 * AI Smart Interview System — Results Module
 * Renders the final interview result screen with charts and feedback
 */

function renderResults(data) {
    if (!data || !data.session) return;
    
    const session = data.session;
    const rawScores = data.scores || {};
    const feedback = data.feedback || {};

    // ── Header & Info ──────────────────────────────────────
    document.getElementById('result-interview-info').innerHTML = `
        <strong>${capitalize(session.interview_type)} Interview</strong> • 
        ${capitalize(session.difficulty)} • 
        ${formatDate(session.completed_at)}
    `;

    // ── Calculate New 0-1000 Score ─────────────────────────
    const norm100 = (v) => {
        const n = Number(v) || 0;
        return (n <= 10 && n > 0) ? Math.round(n * 10) : Math.round(n);
    };

    const communication = norm100(rawScores.communication ?? session.communication);
    const technicalSkills = norm100(rawScores.technical_knowledge ?? session.technical_knowledge);
    const confidence = norm100(rawScores.confidence ?? session.confidence);
    const problemSolving = norm100(rawScores.problem_solving ?? session.problem_solving);
    const clarity = norm100(rawScores.clarity ?? session.clarity);
    const relevance = norm100(rawScores.relevance ?? session.relevance);
    const answerQuality = Math.round((clarity + relevance) / 2);

    const categoryAverage = (communication + technicalSkills + confidence + problemSolving + answerQuality) / 5;
    const overallScore1000 = Math.round(categoryAverage * 10);

    // Animate 1000 Score Number
    const scoreTextEl = document.getElementById('overall-score-1000');
    if (scoreTextEl) {
        let current = 0;
        const duration = 1500;
        const steps = 30;
        const stepTime = Math.abs(Math.floor(duration / steps));
        const increment = overallScore1000 / steps;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= overallScore1000) {
                current = overallScore1000;
                clearInterval(timer);
            }
            scoreTextEl.textContent = Math.round(current);
        }, stepTime);
    }

    // Update Status
    let status = "Excellent";
    let statusClass = "status-excellent";
    let statusIcon = "🟢";

    if (overallScore1000 < 500) {
        status = "Average";
        statusClass = "status-average";
        statusIcon = "🔴";
    } else if (overallScore1000 <= 700) {
        status = "Good";
        statusClass = "status-good";
        statusIcon = "🟡";
    }

    const statusBadge = document.getElementById('result-status-badge');
    if (statusBadge) {
        statusBadge.innerHTML = `${statusIcon} ${status.toUpperCase()}`;
        statusBadge.className = `result-status-container ${statusClass}`;
    }

    // Update Progress Bar
    setTimeout(() => {
        const scoreBar = document.getElementById('overall-score-bar');
        if (scoreBar) {
            scoreBar.style.width = (overallScore1000 / 10) + '%';
        }
    }, 300);

    // Update Feedback Message
    const feedbackSummary = feedback.feedback_summary || session.feedback_summary || 'Good effort. Keep practicing to improve your skills further.';
    const shortFeedbackEl = document.getElementById('result-short-feedback');
    if (shortFeedbackEl) {
        shortFeedbackEl.textContent = `"${feedbackSummary}"`;
    }

    // ── Readiness Gauge ────────────────────────────────────
    const readiness = feedback.readiness_pct || session.readiness_pct || 0;
    animateScoreCircle('readiness-circle-fill', 'readiness-value', readiness, 377, '%');

    // ── Score Breakdown Bars ───────────────────────────────
    const breakdownList = document.getElementById('score-breakdown-list');
    breakdownList.innerHTML = '';
    
    const categories = [
        { label: 'Technical Skills', val: technicalSkills },
        { label: 'Communication', val: communication },
        { label: 'Problem Solving', val: problemSolving },
        { label: 'Confidence', val: confidence },
        { label: 'Answer Quality', val: answerQuality }
    ];

    categories.forEach(cat => {
        const val = cat.val;
        let colorClass = 'progress-bar-danger';
        if (val >= 70) colorClass = 'progress-bar-success';
        else if (val >= 50) colorClass = 'progress-bar-purple';

        const item = document.createElement('div');
        item.className = 'score-item';
        item.innerHTML = `
            <div class="score-item-label">${cat.label}</div>
            <div class="score-item-bar progress-bar progress-bar-lg ${colorClass}">
                <div class="progress-bar-fill" style="width: 0%" data-target="${val}"></div>
            </div>
            <div class="score-item-value">${val}/100</div>
        `;
        breakdownList.appendChild(item);
    });

    // Animate bars after a short delay
    setTimeout(() => {
        document.querySelectorAll('.score-item-bar .progress-bar-fill').forEach(bar => {
            bar.style.width = bar.dataset.target + '%';
        });
    }, 300);

    // ── Feedback Lists ─────────────────────────────────────
    populateList('strengths-list', feedback.strengths || session.strengths, 'No explicit strengths identified.');
    populateList('weaknesses-list', feedback.weaknesses || session.weaknesses, 'No explicit weaknesses identified.');
    populateList('improvements-list', feedback.improvements || session.improvements, 'Keep practicing!');
    populateList('recommendations-list', feedback.recommendations || session.recommendations, 'Review general interview tips.');

    // ── Summary ────────────────────────────────────────────
    const summaryText = feedback.feedback_summary || session.feedback_summary || 'No overall feedback available.';
    document.getElementById('feedback-summary-text').textContent = summaryText;

    // Scroll to top
    window.scrollTo(0, 0);
}

// ── Helpers ──────────────────────────────────────────────
function populateList(elementId, items, emptyMsg) {
    const ul = document.getElementById(elementId);
    ul.innerHTML = '';
    
    let parsedItems = items;
    if (typeof items === 'string') {
        try { parsedItems = JSON.parse(items); } catch(e) { parsedItems = []; }
    }

    if (!parsedItems || parsedItems.length === 0) {
        ul.innerHTML = `<li style="color:var(--text-muted)">${emptyMsg}</li>`;
        return;
    }

    parsedItems.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item;
        ul.appendChild(li);
    });
}

function animateScoreCircle(circleId, textId, targetValue, circumference, suffix = '') {
    const circle = document.getElementById(circleId);
    const text = document.getElementById(textId);
    
    if (!circle || !text) return;

    // Reset
    circle.style.strokeDashoffset = circumference;
    text.textContent = `0${suffix}`;

    // Animate
    setTimeout(() => {
        const offset = circumference - (targetValue / 100) * circumference;
        circle.style.strokeDashoffset = offset;
        
        // Counter animation
        let current = 0;
        const duration = 1500;
        const steps = 30;
        const stepTime = Math.abs(Math.floor(duration / steps));
        const increment = targetValue / steps;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= targetValue) {
                current = targetValue;
                clearInterval(timer);
            }
            text.textContent = Math.round(current) + suffix;
        }, stepTime);
    }, 100);
}
