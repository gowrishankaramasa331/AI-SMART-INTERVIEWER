/**
 * AI Smart Interview System — Core Application
 * SPA navigation, API helpers, toast notifications, utilities
 */

// ═══════════════════════════════════════════════════════════
//  GLOBAL STATE
// ═══════════════════════════════════════════════════════════

const App = {
    student: null,
    currentScreen: 'dashboard',
    interviewSession: null,
};


// ═══════════════════════════════════════════════════════════
//  API HELPER
// ═══════════════════════════════════════════════════════════

async function api(url, options = {}) {
    const defaults = {
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
    };
    if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
        options.body = JSON.stringify(options.body);
    }
    if (options.body instanceof FormData) {
        delete defaults.headers['Content-Type'];
    }
    const config = { ...defaults, ...options, headers: { ...defaults.headers, ...(options.headers || {}) } };
    if (options.body instanceof FormData) {
        delete config.headers['Content-Type'];
    }
    try {
        const response = await fetch(url, config);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || `Request failed (${response.status})`);
        }
        return data;
    } catch (error) {
        if (error.message.includes('Failed to fetch')) {
            throw new Error('Cannot connect to server. Make sure the server is running.');
        }
        throw error;
    }
}


// ═══════════════════════════════════════════════════════════
//  TOAST NOTIFICATIONS
// ═══════════════════════════════════════════════════════════

function showToast(message, type = 'info', duration = 4000) {
    const container = document.getElementById('toast-container');
    const icons = { success: '✅', error: '❌', info: 'ℹ️' };
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span>${icons[type] || ''}</span> ${escapeHtml(message)}`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('toast-exit');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}


// ═══════════════════════════════════════════════════════════
//  LOADING OVERLAY
// ═══════════════════════════════════════════════════════════

function showLoading(text = 'Loading...') {
    const overlay = document.getElementById('loading-overlay');
    document.getElementById('loading-text').textContent = text;
    overlay.classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading-overlay').classList.add('hidden');
}


// ═══════════════════════════════════════════════════════════
//  NAVIGATION
// ═══════════════════════════════════════════════════════════

function showAuthScreen() {
    document.getElementById('auth-screen').classList.add('active');
    document.getElementById('auth-screen').classList.remove('hidden');
    document.getElementById('dashboard-layout').classList.add('hidden');
}

function showDashboardLayout() {
    document.getElementById('auth-screen').classList.remove('active');
    document.getElementById('auth-screen').classList.add('hidden');
    document.getElementById('dashboard-layout').classList.remove('hidden');
    navigateTo('dashboard');
}

function navigateTo(screenName) {
    // Stop camera and ongoing processes when leaving active interview
    if (App.currentScreen === 'interview' && screenName !== 'interview') {
        if (typeof stopCamera === 'function') stopCamera();
        if (typeof stopRecording === 'function') stopRecording();
        if (typeof stopSpeaking === 'function') stopSpeaking();
        if (typeof stopTimer === 'function') stopTimer();
        if (typeof clearAutoCloseTimer === 'function') clearAutoCloseTimer();
    }
    // Stop camera preview if leaving setup screen
    if (App.currentScreen === 'interview-setup' && screenName !== 'interview-setup') {
        if (typeof stopCameraPreview === 'function') stopCameraPreview();
    }

    // Hide all screens in main-content
    document.querySelectorAll('.main-content > .screen').forEach(s => {
        s.classList.remove('active');
    });

    // Show target screen
    const target = document.getElementById('screen-' + screenName);
    if (target) {
        target.classList.add('active');
    }

    // Update nav active state
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const navItem = document.querySelector(`.nav-item[data-screen="${screenName}"]`);
    if (navItem) navItem.classList.add('active');

    // Close mobile sidebar
    document.getElementById('sidebar').classList.remove('open');

    App.currentScreen = screenName;

    // Trigger screen-specific load
    if (screenName === 'dashboard') loadDashboardStats();
    if (screenName === 'profile') loadProfile();
    if (screenName === 'history') loadHistory();
}


// ═══════════════════════════════════════════════════════════
//  SIDEBAR & NAVIGATION SETUP
// ═══════════════════════════════════════════════════════════

function setupNavigation() {
    // Sidebar nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            const screen = item.dataset.screen;
            if (screen) {
                if (App.currentScreen === 'interview' && screen !== 'interview') {
                    e.preventDefault();
                    if (typeof openExitModal === 'function') {
                        openExitModal();
                        return;
                    }
                }
                navigateTo(screen);
            }
        });
    });

    // Mobile toggle
    document.getElementById('mobile-toggle').addEventListener('click', () => {
        document.getElementById('sidebar').classList.toggle('open');
    });

    // Close sidebar on click outside (mobile)
    document.addEventListener('click', (e) => {
        const sidebar = document.getElementById('sidebar');
        const toggle = document.getElementById('mobile-toggle');
        if (sidebar.classList.contains('open') &&
            !sidebar.contains(e.target) &&
            !toggle.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    });

    // Logout
    document.getElementById('logout-btn').addEventListener('click', async () => {
        if (typeof stopCamera === 'function') stopCamera();
        if (typeof stopCameraPreview === 'function') stopCameraPreview();
        if (typeof stopRecording === 'function') stopRecording();
        if (typeof stopSpeaking === 'function') stopSpeaking();
        try {
            await api('/api/logout', { method: 'POST' });
        } catch (e) { /* ignore */ }
        App.student = null;
        showAuthScreen();
        showToast('Logged out successfully', 'info');
    });

    // Quick action cards on dashboard
    document.querySelectorAll('.quick-action-card').forEach(card => {
        card.addEventListener('click', () => {
            if (card.dataset.action === 'interview') {
                navigateTo('interview-setup');
                // Pre-select the type
                setTimeout(() => {
                    const typeCard = document.querySelector(`.interview-type-card[data-type="${card.dataset.type}"]`);
                    if (typeCard) typeCard.click();
                }, 100);
            }
        });
    });

    // Start practice button
    document.getElementById('start-practice-btn').addEventListener('click', () => {
        navigateTo('interview-setup');
    });

    // Result page buttons
    document.getElementById('results-new-interview-btn').addEventListener('click', () => navigateTo('interview-setup'));
    document.getElementById('results-dashboard-btn').addEventListener('click', () => navigateTo('dashboard'));
    document.getElementById('results-history-btn').addEventListener('click', () => navigateTo('history'));
}


// ═══════════════════════════════════════════════════════════
//  UPDATE USER INFO IN SIDEBAR
// ═══════════════════════════════════════════════════════════

function updateSidebarUser() {
    if (!App.student) return;
    const name = App.student.name || 'Student';
    document.getElementById('sidebar-name').textContent = name;
    document.getElementById('sidebar-email').textContent = App.student.email || '';
    document.getElementById('sidebar-avatar').textContent = name.charAt(0).toUpperCase();
    document.getElementById('welcome-heading').textContent = `Welcome, ${name.split(' ')[0]}! 👋`;
}


// ═══════════════════════════════════════════════════════════
//  DASHBOARD STATS
// ═══════════════════════════════════════════════════════════

async function loadDashboardStats() {
    try {
        const data = await api('/api/interview/history');
        const sessions = data.sessions || [];

        document.getElementById('stat-total').textContent = sessions.length;

        if (sessions.length > 0) {
            const scores = sessions.map(s => s.overall_score || 0);
            const avg = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
            const best = Math.round(Math.max(...scores));
            const readiness = sessions[0] ? Math.round(sessions[0].readiness_pct || 0) : 0;

            document.getElementById('stat-avg').textContent = avg + '%';
            document.getElementById('stat-best').textContent = best + '%';
            document.getElementById('stat-readiness').textContent = readiness + '%';
        } else {
            document.getElementById('stat-avg').textContent = '—';
            document.getElementById('stat-best').textContent = '—';
            document.getElementById('stat-readiness').textContent = '—';
        }
    } catch (e) {
        console.error('Failed to load stats:', e);
    }
}


// ═══════════════════════════════════════════════════════════
//  UTILITIES
// ═══════════════════════════════════════════════════════════

function escapeHtml(text) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}

function formatDate(dateStr) {
    if (!dateStr) return '—';
    try {
        const d = new Date(dateStr);
        if (isNaN(d.getTime())) return dateStr;
        return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
    } catch {
        return dateStr;
    }
}

function getScoreClass(score) {
    if (score >= 70) return 'score-good';
    if (score >= 40) return 'score-ok';
    return 'score-poor';
}

function getScoreColor(score) {
    if (score >= 70) return 'var(--green)';
    if (score >= 40) return 'var(--orange)';
    return 'var(--red)';
}

function capitalize(str) {
    return str ? str.charAt(0).toUpperCase() + str.slice(1) : '';
}


// ═══════════════════════════════════════════════════════════
//  INITIALIZATION
// ═══════════════════════════════════════════════════════════

function checkInsecureOriginBanner() {
    const isLocal = window.location.hostname === 'localhost' ||
                    window.location.hostname === '127.0.0.1' ||
                    window.location.hostname === '[::1]';
    if (!window.isSecureContext && !isLocal && window.location.protocol !== 'https:') {
        const banner = document.getElementById('insecure-origin-banner');
        if (banner) {
            const portStr = window.location.port ? `:${window.location.port}` : '';
            const target = `http://localhost${portStr}${window.location.pathname}`;
            const link = document.getElementById('insecure-origin-link');
            if (link) link.href = target;
            banner.classList.remove('hidden');
        }
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    setupNavigation();
    checkInsecureOriginBanner();

    // Check if user is already logged in
    try {
        const data = await api('/api/session-check');
        if (data.authenticated && data.student) {
            App.student = data.student;
            updateSidebarUser();
            showDashboardLayout();
            return;
        }
    } catch (e) {
        console.log('Not authenticated');
    }

    showAuthScreen();
});

