/**
 * AI Smart Interview System — Profile Module
 * Profile management, skills tags, and resume upload
 */

// ── Profile State ────────────────────────────────────────
let skillsList = [];

// ── Load Profile Data ────────────────────────────────────
async function loadProfile() {
    if (!App.student) return;

    try {
        const data = await api('/api/profile');
        const student = data.student;
        if (!student) return;

        // Populate form fields
        document.getElementById('profile-name').value = student.name || '';
        document.getElementById('profile-college').value = student.college || '';
        document.getElementById('profile-branch').value = student.branch || '';
        document.getElementById('profile-year').value = student.year || '';
        document.getElementById('profile-goal').value = student.career_goal || '';

        // Handle resume display
        if (student.resume_filename) {
            document.getElementById('resume-filename').textContent = `Current: ${student.resume_filename}`;
        }

        // Handle skills
        skillsList = student.skills ? student.skills.split(',').map(s => s.trim()).filter(Boolean) : [];
        renderSkills();

    } catch (error) {
        showToast('Failed to load profile details', 'error');
    }
}

// ── Skills Management ────────────────────────────────────
function renderSkills() {
    const container = document.getElementById('skills-tags');
    container.innerHTML = '';
    
    skillsList.forEach((skill, index) => {
        const tag = document.createElement('span');
        tag.className = 'tag';
        tag.innerHTML = `
            ${escapeHtml(skill)}
            <span class="tag-remove" data-index="${index}">&times;</span>
        `;
        container.appendChild(tag);
    });

    // Add remove listeners
    document.querySelectorAll('.tag-remove').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const index = parseInt(e.target.dataset.index, 10);
            skillsList.splice(index, 1);
            renderSkills();
        });
    });
}

function addSkill(skill) {
    const s = skill.trim();
    if (s && !skillsList.includes(s) && skillsList.length < 15) {
        skillsList.push(s);
        renderSkills();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Skills Input Event Listeners
    const skillInput = document.getElementById('skill-input');
    const addSkillBtn = document.getElementById('add-skill-btn');

    if (addSkillBtn && skillInput) {
        addSkillBtn.addEventListener('click', () => {
            addSkill(skillInput.value);
            skillInput.value = '';
            skillInput.focus();
        });

        skillInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                addSkill(skillInput.value);
                skillInput.value = '';
            }
        });
    }

    // ── Save Profile ─────────────────────────────────────────
    const profileForm = document.getElementById('profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const btn = document.getElementById('save-profile-btn');
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span> Saving...';

            const payload = {
                name: document.getElementById('profile-name').value.trim(),
                college: document.getElementById('profile-college').value.trim(),
                branch: document.getElementById('profile-branch').value.trim(),
                year: document.getElementById('profile-year').value.trim(),
                career_goal: document.getElementById('profile-goal').value.trim(),
                skills: skillsList.join(', '),
            };

            try {
                const data = await api('/api/profile', {
                    method: 'PUT',
                    body: payload
                });
                App.student = data.student;
                updateSidebarUser();
                showToast('Profile saved successfully', 'success');
            } catch (error) {
                showToast(error.message, 'error');
            } finally {
                btn.disabled = false;
                btn.innerHTML = '💾 Save Profile';
            }
        });
    }

    // ── Resume Upload ────────────────────────────────────────
    const dropZone = document.getElementById('resume-drop-zone');
    const fileInput = document.getElementById('resume-file');

    if (dropZone && fileInput) {
        dropZone.addEventListener('click', () => fileInput.click());

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = 'var(--blue-primary)';
            dropZone.style.background = 'var(--blue-subtle)';
        });

        dropZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = 'var(--border-color)';
            dropZone.style.background = 'transparent';
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = 'var(--border-color)';
            dropZone.style.background = 'transparent';
            
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                handleResumeUpload();
            }
        });

        fileInput.addEventListener('change', handleResumeUpload);
    }
});

async function handleResumeUpload() {
    const fileInput = document.getElementById('resume-file');
    if (!fileInput.files.length) return;

    const file = fileInput.files[0];
    const allowed = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    
    if (!allowed.includes(file.type) && !file.name.match(/\.(pdf|doc|docx)$/i)) {
        showToast('Please upload a PDF or Word document', 'error');
        fileInput.value = '';
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        showToast('File size must be less than 5MB', 'error');
        fileInput.value = '';
        return;
    }

    const formData = new FormData();
    formData.append('resume', file);

    const nameDisplay = document.getElementById('resume-filename');
    const originalText = nameDisplay.textContent;
    nameDisplay.textContent = `Uploading ${file.name}...`;

    try {
        const data = await api('/api/profile/resume', {
            method: 'POST',
            body: formData
        });
        nameDisplay.textContent = `Current: ${data.filename}`;
        showToast('Resume uploaded successfully', 'success');
        
        // Update local state
        if (App.student) {
            App.student.resume_filename = data.filename;
        }
    } catch (error) {
        nameDisplay.textContent = originalText;
        showToast(error.message, 'error');
    }
}
