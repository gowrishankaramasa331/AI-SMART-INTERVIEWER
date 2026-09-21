/**
 * AI Smart Interview System — Authentication Module
 * Login and registration form handling
 */

document.addEventListener('DOMContentLoaded', () => {
    // ── Tab Switching ────────────────────────────────────
    document.querySelectorAll('.auth-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
            tab.classList.add('active');
            const formId = tab.dataset.tab === 'login' ? 'login-form' : 'register-form';
            document.getElementById(formId).classList.add('active');
        });
    });

    // ── Login Form ───────────────────────────────────────
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value.trim();
        const password = document.getElementById('login-password').value;

        if (!email || !password) {
            showToast('Please fill in all fields', 'error');
            return;
        }

        const btn = document.getElementById('login-btn');
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Logging in...';

        try {
            const data = await api('/api/login', {
                method: 'POST',
                body: { email, password },
            });
            App.student = data.student;
            updateSidebarUser();
            showDashboardLayout();
            showToast('Welcome back, ' + (data.student.name || 'Student') + '!', 'success');
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = '🚀 Login';
        }
    });

    // ── Register Form ────────────────────────────────────
    document.getElementById('register-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('reg-name').value.trim();
        const college = document.getElementById('reg-college').value.trim();
        const email = document.getElementById('reg-email').value.trim();
        const password = document.getElementById('reg-password').value;

        if (!name || !email || !password) {
            showToast('Please fill in all required fields', 'error');
            return;
        }
        if (name.length < 2) {
            showToast('Name must be at least 2 characters', 'error');
            return;
        }
        if (!email.includes('@')) {
            showToast('Please enter a valid email', 'error');
            return;
        }
        if (password.length < 4) {
            showToast('Password must be at least 4 characters', 'error');
            return;
        }

        const btn = document.getElementById('register-btn');
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Creating account...';

        try {
            const data = await api('/api/register', {
                method: 'POST',
                body: { name, college, email, password },
            });
            App.student = data.student;
            updateSidebarUser();
            showDashboardLayout();
            showToast('Account created! Welcome, ' + name + '!', 'success');
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = '✨ Create Account';
        }
    });
});
