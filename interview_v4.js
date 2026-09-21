/**
 * AI Smart Interview System — Interview Flow Module
 * Handles interview setup, question display, voice input, and submission
 */

// ── Interview State ──────────────────────────────────────
let interviewData = {
    sessionId: null,
    type: 'general',
    difficulty: 'medium',
    questions: [],
    currentIndex: 0,
    startTime: null,
    timerInterval: null,
    totalSeconds: 0
};

// ── Auto-Close Timer State ───────────────────────────────
let autoCloseTimer = null;
let autoCloseRemaining = 5;

function clearAutoCloseTimer() {
    if (autoCloseTimer) {
        clearInterval(autoCloseTimer);
        autoCloseTimer = null;
    }
}

function startAutoCloseCountdown(seconds = 5) {
    clearAutoCloseTimer();
    autoCloseRemaining = seconds;

    const topAlert = document.getElementById('eval-completion-top-alert');
    if (topAlert) {
        topAlert.classList.remove('hidden');
        const pauseBtn = document.getElementById('auto-close-pause-btn');
        if (pauseBtn) pauseBtn.style.display = 'inline-flex';
        const desc = topAlert.querySelector('.completion-alert-desc');
        if (desc) {
            desc.innerHTML = `Closing interview room and returning to Dashboard in <span class="countdown-seconds-badge" id="auto-close-countdown-num">${autoCloseRemaining}</span>s...`;
        }
    }

    const updateUI = () => {
        const numEl = document.getElementById('auto-close-countdown-num');
        if (numEl) numEl.textContent = autoCloseRemaining;

        const bottomEl = document.getElementById('eval-bottom-countdown');
        if (bottomEl) bottomEl.textContent = `${autoCloseRemaining}s`;

        const autoCloseDashBtn = document.getElementById('auto-close-dashboard-btn');
        if (autoCloseDashBtn) autoCloseDashBtn.innerHTML = `📊 Dashboard (${autoCloseRemaining}s)`;

        const finishDashBtn = document.getElementById('finish-dashboard-btn');
        if (finishDashBtn) finishDashBtn.innerHTML = `📊 Back to Dashboard (${autoCloseRemaining}s)`;

        const evalDashBtn = document.getElementById('eval-dashboard-btn');
        if (evalDashBtn) evalDashBtn.innerHTML = `📊 Back to Dashboard (${autoCloseRemaining}s)`;

        const finishBtn = document.getElementById('finish-interview-btn');
        if (finishBtn) finishBtn.innerHTML = `🏆 View Report (${autoCloseRemaining}s)`;

        const evalFinishBtn = document.getElementById('eval-finish-btn');
        if (evalFinishBtn) evalFinishBtn.innerHTML = `🏆 Full Report (${autoCloseRemaining}s)`;

        const hudExitBtn = document.getElementById('exit-interview-btn');
        if (hudExitBtn) hudExitBtn.textContent = `🏁 Dashboard (${autoCloseRemaining}s)`;
    };

    updateUI();

    autoCloseTimer = setInterval(() => {
        autoCloseRemaining--;
        if (autoCloseRemaining <= 0) {
            clearAutoCloseTimer();
            finishInterview('dashboard');
        } else {
            updateUI();
        }
    }, 1000);
}

function pauseAutoClose() {
    clearAutoCloseTimer();
    const desc = document.querySelector('.completion-alert-desc');
    if (desc) {
        desc.textContent = 'Auto-close paused. Review your feedback below and choose Dashboard or History when ready.';
    }
    const bottomBanner = document.getElementById('eval-completion-banner');
    if (bottomBanner) {
        bottomBanner.innerHTML = '<span>🎉 All questions answered! Click below to return to Dashboard or History.</span>';
    }
    const autoCloseDashBtn = document.getElementById('auto-close-dashboard-btn');
    if (autoCloseDashBtn) autoCloseDashBtn.innerHTML = '📊 Dashboard';

    const finishDashBtn = document.getElementById('finish-dashboard-btn');
    if (finishDashBtn) finishDashBtn.innerHTML = '📊 Back to Dashboard';

    const evalDashBtn = document.getElementById('eval-dashboard-btn');
    if (evalDashBtn) evalDashBtn.innerHTML = '📊 Back to Dashboard';

    const finishBtn = document.getElementById('finish-interview-btn');
    if (finishBtn) finishBtn.innerHTML = '🏆 View Report';

    const evalFinishBtn = document.getElementById('eval-finish-btn');
    if (evalFinishBtn) evalFinishBtn.innerHTML = '🏆 Full Report';

    const hudExitBtn = document.getElementById('exit-interview-btn');
    if (hudExitBtn) hudExitBtn.textContent = '🏁 Dashboard';

    const pauseBtn = document.getElementById('auto-close-pause-btn');
    if (pauseBtn) pauseBtn.style.display = 'none';

    showToast('Auto-close paused. Review your feedback at your own pace.', 'info');
}

// ── Setup Listeners ──────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    // Type selection
    document.querySelectorAll('.interview-type-card').forEach(card => {
        card.addEventListener('click', () => {
            document.querySelectorAll('.interview-type-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            validateSetup();
        });
    });

    // Difficulty selection
    document.querySelectorAll('.difficulty-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.difficulty-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
        });
    });

    // Question count slider
    const slider = document.getElementById('question-count-slider');
    const display = document.getElementById('question-count-display');
    if (slider && display) {
        slider.addEventListener('input', (e) => {
            display.textContent = e.target.value;
        });
    }

    // Begin interview button
    const beginBtn = document.getElementById('begin-interview-btn');
    if (beginBtn) {
        beginBtn.addEventListener('click', startInterview);
    }
});

function validateSetup() {
    const hasType = document.querySelector('.interview-type-card.selected');
    const beginBtn = document.getElementById('begin-interview-btn');
    if (beginBtn) {
        beginBtn.disabled = !hasType;
    }
}

// ── Start Interview API Call ─────────────────────────────
async function startInterview() {
    const typeCard = document.querySelector('.interview-type-card.selected');
    const diffBtn = document.querySelector('.difficulty-btn.selected');
    const countSlider = document.getElementById('question-count-slider');

    if (!typeCard || !diffBtn || !countSlider) return;

    const type = typeCard.dataset.type;
    const difficulty = diffBtn.dataset.difficulty;
    const num_questions = parseInt(countSlider.value, 10);

    showLoading('Generating personalized questions via AI...');

    try {
        const data = await api('/api/interview/start', {
            method: 'POST',
            body: { type, difficulty, num_questions }
        });

        // Initialize state
        interviewData = {
            sessionId: data.session_id,
            type: data.interview_type,
            difficulty: data.difficulty,
            questions: data.questions,
            totalQuestions: data.total_questions || num_questions,
            currentIndex: 0,
            startTime: Date.now(),
            totalSeconds: 0,
            isCompleted: false
        };
        try { sessionStorage.setItem('active_interview_session_id', data.session_id); } catch(e) {}

        // Prepare UI
        document.getElementById('interview-type-display').textContent = 
            `${capitalize(type)} Interview • ${capitalize(difficulty)}`;
        
        if (typeof stopCameraPreview === 'function') {
            stopCameraPreview();
        }

        navigateTo('interview');

        // Initialize 3D Robot Interviewer
        if (typeof RobotInterviewer !== 'undefined') {
            if (!window.aiRobot) {
                window.aiRobot = new RobotInterviewer();
            }
            window.aiRobot.init('robot-canvas-container');
        }

        initCamera();
        setupActiveSpeakerObserver();
        startTimer();

        // Immediately display first question with zero delay
        displayCurrentQuestion();

    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        hideLoading();
    }
}

// ── Display Question ─────────────────────────────────────
function displayCurrentQuestion() {
    const total = interviewData.totalQuestions || interviewData.questions.length;
    if (interviewData.currentIndex >= total) {
        finishInterview();
        return;
    }

    const question = interviewData.questions[interviewData.currentIndex];
    if (!question) {
        finishInterview();
        return;
    }
    const isLast = interviewData.currentIndex === total - 1;

    // Update UI elements
    document.getElementById('question-number').textContent = `Question ${question.number || (interviewData.currentIndex + 1)}`;
    document.getElementById('question-text').textContent = question.text;

    // Immediately enable inputs so candidate can type or speak freely
    const answerInput = document.getElementById('answer-input');
    if (answerInput) {
        answerInput.value = '';
        answerInput.disabled = false;
    }

    const transcriptContent = document.getElementById('transcript-content');
    const placeholder = document.getElementById('transcript-placeholder');
    if (transcriptContent) transcriptContent.textContent = '';
    if (placeholder) placeholder.classList.remove('hidden');

    // Reset microphone state for each question
    stopRecording();
    baseTranscript = '';

    const micBtn = document.getElementById('mic-btn');
    if (micBtn) {
        micBtn.disabled = false;
        micBtn.classList.remove('recording', 'btn-danger', 'hidden');
        micBtn.classList.add('btn-secondary');
        const icon = document.getElementById('mic-btn-icon');
        if (icon) icon.textContent = '🎤';
        const label = document.getElementById('mic-btn-label');
        if (label) label.textContent = 'Answer with Voice';
        micBtn.title = 'Click to speak your answer with microphone';
    }

    const listeningBadge = document.getElementById('mic-listening-indicator');
    if (listeningBadge) listeningBadge.classList.add('hidden');

    const submitBtn = document.getElementById('submit-answer-btn');
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.classList.remove('hidden');
        submitBtn.innerHTML = '✅ Submit Answer';
    }

    const doneBtn = document.getElementById('done-speaking-btn');
    if (doneBtn) {
        doneBtn.disabled = false;
        doneBtn.classList.remove('hidden');
    }
    
    // Follow-up / Adaptive badge
    const followupBadge = document.getElementById('followup-badge');
    if (followupBadge) {
        if (question.is_adaptive || question.is_followup || (question.number && question.number > 1) || interviewData.currentIndex > 0) {
            followupBadge.innerHTML = '🎯 Adaptive • Tailored to your previous answer';
            followupBadge.classList.remove('hidden');
        } else {
            followupBadge.classList.add('hidden');
        }
    }

    // Progress bar
    const pct = ((interviewData.currentIndex) / total) * 100;
    document.getElementById('progress-text').textContent = `Question ${interviewData.currentIndex + 1} of ${total}`;
    document.getElementById('progress-fill').style.width = `${pct}%`;

    // Buttons & controls
    clearAutoCloseTimer();
    document.getElementById('next-question-btn')?.classList.add('hidden');
    document.getElementById('finish-interview-btn')?.classList.add('hidden');
    document.getElementById('finish-dashboard-btn')?.classList.add('hidden');
    document.getElementById('finish-history-btn')?.classList.add('hidden');
    document.getElementById('eval-next-btn')?.classList.add('hidden');
    document.getElementById('eval-finish-btn')?.classList.add('hidden');
    document.getElementById('eval-dashboard-btn')?.classList.add('hidden');
    document.getElementById('eval-history-btn')?.classList.add('hidden');
    document.getElementById('eval-completion-banner')?.classList.add('hidden');
    document.getElementById('eval-completion-top-alert')?.classList.add('hidden');
    document.getElementById('voice-controls')?.classList.remove('hidden');
    document.getElementById('your-turn-indicator')?.classList.remove('hidden');
    
    // Reset Top HUD Exit button & status badge
    const hudExitBtn = document.getElementById('exit-interview-btn');
    if (hudExitBtn) {
        hudExitBtn.textContent = '✕ Exit';
        hudExitBtn.className = 'btn btn-ghost btn-sm exit-interview-btn';
        hudExitBtn.title = 'Exit interview';
        hudExitBtn.onclick = () => openExitModal();
    }
    const statusBadge = document.getElementById('interview-status-badge');
    if (statusBadge) {
        statusBadge.textContent = 'In Progress';
        statusBadge.className = 'badge badge-blue';
    }

    // Hide evaluation from previous question
    document.getElementById('answer-evaluation').classList.add('hidden');
    const mismatchBanner = document.getElementById('eval-mismatch-banner');
    if (mismatchBanner) mismatchBanner.classList.add('hidden');
    const adaptiveNoticeEl = document.getElementById('eval-adaptive-notice');
    if (adaptiveNoticeEl) adaptiveNoticeEl.classList.add('hidden');
    
    // Smooth auto-focus on the textarea so typing works out of the box
    setTimeout(() => {
        if (answerInput && document.activeElement !== answerInput) {
            answerInput.focus();
        }
    }, 150);

    // Callback when speech finishes
    const onQuestionSpoken = () => {
        if (window.aiRobot) {
            window.aiRobot.startListening();
        }
        document.getElementById('your-turn-indicator')?.classList.remove('hidden');
    };

    // Speak question with AI Robot
    if (window.aiRobot) {
        window.aiRobot.startSpeaking(question.text, onQuestionSpoken);
    } else {
        speakText(question.text, null, onQuestionSpoken);
    }
}


// ── TTS Logic ─────────────────────────────────────────────
let currentSpeech = null;
let speechSafetyTimeout = null;
let speechResumeHeartbeat = null;

function speakText(text, onStartCallback, onEndCallback) {
    if (!('speechSynthesis' in window)) {
        console.warn("Text-to-speech not supported.");
        if (onEndCallback) onEndCallback();
        return;
    }
    
    if (speechSafetyTimeout) {
        clearTimeout(speechSafetyTimeout);
        speechSafetyTimeout = null;
    }
    if (speechResumeHeartbeat) {
        clearInterval(speechResumeHeartbeat);
        speechResumeHeartbeat = null;
    }

    try {
        if (window.speechSynthesis.speaking || window.speechSynthesis.pending) {
            window.speechSynthesis.cancel();
        }
    } catch(e) {}
    
    let finished = false;
    const safeEnd = () => {
        if (finished) return;
        finished = true;
        if (speechSafetyTimeout) {
            clearTimeout(speechSafetyTimeout);
            speechSafetyTimeout = null;
        }
        if (speechResumeHeartbeat) {
            clearInterval(speechResumeHeartbeat);
            speechResumeHeartbeat = null;
        }
        const avatar = document.getElementById('ai-avatar-img');
        const indicator = document.getElementById('ai-speaking-indicator');
        if (avatar) avatar.classList.remove('speaking');
        if (indicator) indicator.classList.add('hidden');
        if (window.aiRobot && window.aiRobot.currentState === 'speaking') {
            window.aiRobot.isSpeaking = false;
            window.aiRobot.startListening();
        }
        if (onEndCallback) onEndCallback();
    };

    // Brief delay avoids collision with previous utterance in Chromium
    setTimeout(() => {
        try {
            const speech = new SpeechSynthesisUtterance(text);
            speech.lang = "en-US";
            speech.rate = 0.95;
            speech.pitch = 1.0;
            speech.volume = 1.0;
            
            speech.onstart = () => {
                const avatar = document.getElementById('ai-avatar-img');
                const indicator = document.getElementById('ai-speaking-indicator');
                if (avatar) avatar.classList.add('speaking');
                if (indicator) indicator.classList.remove('hidden');
                if (window.aiRobot) {
                    window.aiRobot.setState('speaking');
                    window.aiRobot.isSpeaking = true;
                }
                if (onStartCallback) onStartCallback();
            };
            
            speech.onend = safeEnd;
            speech.onerror = safeEnd;

            // Safety timeout
            const safetyDuration = Math.min(20000, Math.max(3000, (text ? text.length : 0) * 75));
            speechSafetyTimeout = setTimeout(() => {
                safeEnd();
            }, safetyDuration);

            // Chrome heartbeat to prevent silent speech synthesis stalling
            speechResumeHeartbeat = setInterval(() => {
                if (!window.speechSynthesis.speaking) {
                    clearInterval(speechResumeHeartbeat);
                    speechResumeHeartbeat = null;
                } else {
                    window.speechSynthesis.pause();
                    window.speechSynthesis.resume();
                }
            }, 4000);

            currentSpeech = speech;
            window._activeUtterance = speech; // Retain reference to prevent GC
            window.speechSynthesis.speak(speech);
        } catch(err) {
            console.warn('[TTS] Speak error:', err);
            safeEnd();
        }
    }, 40);
}

function stopSpeaking() {
    if (speechSafetyTimeout) {
        clearTimeout(speechSafetyTimeout);
        speechSafetyTimeout = null;
    }
    if (speechResumeHeartbeat) {
        clearInterval(speechResumeHeartbeat);
        speechResumeHeartbeat = null;
    }
    if ('speechSynthesis' in window) {
        try { window.speechSynthesis.cancel(); } catch(e) {}
    }
    if (window.aiRobot) {
        window.aiRobot.stopSpeaking();
    }
    const avatar = document.getElementById('ai-avatar-img');
    const indicator = document.getElementById('ai-speaking-indicator');
    if (avatar) avatar.classList.remove('speaking');
    if (indicator) indicator.classList.add('hidden');
}


// ── Voice Input (Web Speech API) ─────────────────────────
let recognition = null;
let isRecording = false;
let baseTranscript = '';
let recognitionRestartTimer = null;

function hasSpeechRecognition() {
    return ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window);
}

function initSpeechRecognition() {
    if (!hasSpeechRecognition()) return null;

    if (recognition) {
        try {
            recognition.abort();
        } catch (e) {}
        recognition = null;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    // Continuous = false on Windows Chromium gives sentence-by-sentence streaming
    // and eliminates silent audio capture stalls. We auto-restart instantly on onend.
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
        isRecording = true;
        updateMicUI(true);
    };

    recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalChunk = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalChunk += transcript;
            } else {
                interimTranscript += transcript;
            }
        }

        const input = document.getElementById('answer-input');

        if (finalChunk) {
            if (baseTranscript && !baseTranscript.endsWith(' ') && !baseTranscript.endsWith('\n')) {
                baseTranscript += ' ';
            }
            baseTranscript += finalChunk;
            if (input) input.value = baseTranscript;
        }

        // Live combined display: committed base text + interim speech
        const liveCombined = (baseTranscript + (interimTranscript ? (baseTranscript ? ' ' : '') + interimTranscript : '')).trim();
        if (input && interimTranscript) {
            input.value = liveCombined;
        }

        const transcriptEl = document.getElementById('transcript-content');
        const placeholderEl = document.getElementById('transcript-placeholder');
        if (transcriptEl) {
            if (liveCombined) {
                if (placeholderEl) placeholderEl.classList.add('hidden');
                transcriptEl.textContent = liveCombined;
            } else {
                if (placeholderEl) placeholderEl.classList.remove('hidden');
                transcriptEl.textContent = '';
            }
        }
    };

    recognition.onerror = (event) => {
        console.warn('[Speech] Recognition event error:', event.error);

        // 'no-speech' happens when candidate pauses to think; normal conversation behavior
        if (event.error === 'no-speech') {
            return;
        }

        if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
            showToast('❌ Microphone permission was denied. Please allow microphone access in your browser settings (click the lock icon in the address bar).', 'error');
            stopRecording();
        } else if (event.error === 'audio-capture') {
            showToast('❌ Microphone unavailable or device in use. Please check your audio settings.', 'error');
            stopRecording();
        } else if (event.error === 'network') {
            showToast('⚠️ Speech recognition network error. Please check your internet connection or type your answer.', 'error');
            stopRecording();
        } else if (event.error !== 'aborted') {
            console.error('[Speech] Error:', event.error);
            showToast('Speech error: ' + event.error, 'error');
            stopRecording();
        }
    };

    recognition.onend = () => {
        if (isRecording) {
            // Rapid auto-restart while candidate is in recording mode
            if (recognitionRestartTimer) clearTimeout(recognitionRestartTimer);
            recognitionRestartTimer = setTimeout(() => {
                if (isRecording && recognition) {
                    try {
                        recognition.start();
                    } catch (e) {
                        try {
                            initSpeechRecognition();
                            if (recognition) recognition.start();
                        } catch (err2) {
                            isRecording = false;
                            updateMicUI(false);
                        }
                    }
                }
            }, 50);
        } else {
            updateMicUI(false);
        }
    };

    return recognition;
}

function updateMicUI(recording) {
    const btn = document.getElementById('mic-btn');
    const icon = document.getElementById('mic-btn-icon');
    const label = document.getElementById('mic-btn-label');
    const listeningBadge = document.getElementById('mic-listening-indicator');
    const topStatus = document.getElementById('top-status-listening');
    const hudMicLabel = document.getElementById('hud-mic-label');
    const audioStatus = document.getElementById('audio-waveform-status');

    if (btn) {
        if (recording) {
            btn.classList.add('recording');
            btn.classList.remove('btn-secondary');
            btn.classList.add('btn-danger');
            if (icon) icon.textContent = '⏹️';
            if (label) label.textContent = 'Stop Microphone';
            btn.title = 'Recording active... Click to stop microphone';
        } else {
            btn.classList.remove('recording');
            btn.classList.remove('btn-danger');
            btn.classList.add('btn-secondary');
            if (icon) icon.textContent = '🎤';
            if (label) label.textContent = 'Answer with Voice';
            btn.title = 'Click to speak your answer with microphone';
        }
    }

    if (listeningBadge) {
        if (recording) {
            listeningBadge.classList.remove('hidden');
        } else {
            listeningBadge.classList.add('hidden');
        }
    }

    if (topStatus) {
        if (recording) {
            topStatus.classList.add('active');
            if (hudMicLabel) hudMicLabel.textContent = '🎙️ Recording Voice';
        } else {
            topStatus.classList.remove('active');
            if (hudMicLabel) hudMicLabel.textContent = '🎙️ Mic Inactive';
        }
    }

    if (audioStatus) {
        if (recording) {
            audioStatus.textContent = 'Recording live voice...';
            audioStatus.style.color = '#ef4444';
        } else {
            audioStatus.textContent = 'Listening for voice...';
            audioStatus.style.color = 'var(--text-muted)';
        }
    }
}

async function startRecording() {
    if (!hasSpeechRecognition()) {
        showToast('Speech recognition is not supported in this browser. Google Chrome or Microsoft Edge is recommended. You can type directly in the box below!', 'info');
        const input = document.getElementById('answer-input');
        if (input) {
            input.disabled = false;
            input.focus();
            input.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        return;
    }

    // Stop robot speech so candidate has quiet to speak
    stopSpeaking();

    // Check if microphone permission is explicitly denied via Permissions API
    if (navigator.permissions && navigator.permissions.query) {
        try {
            const perm = await navigator.permissions.query({ name: 'microphone' });
            if (perm.state === 'denied') {
                showToast('❌ Microphone permission denied. Please allow microphone access in your browser settings (click the lock icon in the address bar).', 'error');
                updateMicUI(false);
                return;
            }
        } catch(e) {}
    }

    initSpeechRecognition();

    const input = document.getElementById('answer-input');
    baseTranscript = input ? input.value : '';

    try {
        isRecording = true;
        recognition.start();
        updateMicUI(true);
        showToast('🎙️ Microphone active. Speak your answer now...', 'info');
    } catch (err) {
        console.warn('[Speech] Start error:', err);
        if (err.name === 'InvalidStateError') {
            isRecording = true;
            updateMicUI(true);
        } else if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
            isRecording = false;
            updateMicUI(false);
            showToast('❌ Microphone access was denied. Please allow microphone permissions in your browser.', 'error');
        } else {
            isRecording = false;
            updateMicUI(false);
            showToast('Could not start microphone: ' + (err.message || err.name), 'error');
        }
    }
}

function stopRecording() {
    isRecording = false;
    if (recognitionRestartTimer) {
        clearTimeout(recognitionRestartTimer);
        recognitionRestartTimer = null;
    }
    if (recognition) {
        try {
            recognition.stop();
        } catch (e) {}
    }
    updateMicUI(false);

    // Commit any interim text to input value and baseTranscript
    const input = document.getElementById('answer-input');
    const transcriptEl = document.getElementById('transcript-content');
    if (input && transcriptEl && transcriptEl.textContent && transcriptEl.textContent !== '...') {
        input.value = transcriptEl.textContent.trim();
        baseTranscript = input.value;
    }
}

function toggleMicRecording() {
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Answer input typing synchronization and shortcut
    const answerInput = document.getElementById('answer-input');
    if (answerInput) {
        answerInput.addEventListener('input', () => {
            baseTranscript = answerInput.value;
            const transcriptEl = document.getElementById('transcript-content');
            const placeholderEl = document.getElementById('transcript-placeholder');
            if (transcriptEl) {
                if (answerInput.value.trim()) {
                    if (placeholderEl) placeholderEl.classList.add('hidden');
                    transcriptEl.textContent = answerInput.value;
                } else {
                    if (placeholderEl) placeholderEl.classList.remove('hidden');
                    transcriptEl.textContent = '';
                }
            }
        });

        // When candidate focuses on typing, stop robot voice so candidate has quiet
        answerInput.addEventListener('focus', () => {
            stopSpeaking();
        });

        // Ctrl+Enter or Cmd+Enter to submit answer
        answerInput.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                submitAnswer();
            }
        });
    }

    // Done speaking submit button
    const doneBtn = document.getElementById('done-speaking-btn');
    if (doneBtn) {
        doneBtn.addEventListener('click', () => {
            stopRecording();
            setTimeout(() => {
                submitAnswer();
            }, 120);
        });
    }

    // Toggle textarea focus from transcript bubble
    const toggleEditBtn = document.getElementById('transcript-toggle-btn');
    if (toggleEditBtn) {
        toggleEditBtn.addEventListener('click', () => {
            const input = document.getElementById('answer-input');
            if (input) {
                input.disabled = false;
                input.focus();
                input.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
    }

    const replayBtn = document.getElementById('replay-voice-btn');
    if (replayBtn) {
        replayBtn.addEventListener('click', () => {
            if (interviewData.questions.length > interviewData.currentIndex) {
                if (isRecording) stopRecording();
                const text = interviewData.questions[interviewData.currentIndex].text;
                
                const onReplayDone = () => {
                    if (window.aiRobot) window.aiRobot.startListening();
                    document.getElementById('your-turn-indicator')?.classList.remove('hidden');
                };

                if (window.aiRobot) {
                    window.aiRobot.startSpeaking(text, onReplayDone);
                } else {
                    speakText(text, null, onReplayDone);
                }
            }
        });
    }

    const stopBtn = document.getElementById('stop-voice-btn');
    if (stopBtn) {
        stopBtn.addEventListener('click', () => {
            stopSpeaking();
            document.getElementById('your-turn-indicator')?.classList.remove('hidden');
            const input = document.getElementById('answer-input');
            if (input) {
                input.disabled = false;
                input.focus();
            }
            if (window.aiRobot) window.aiRobot.startListening();
        });
    }

    const micBtn = document.getElementById('mic-btn');
    if (micBtn) {
        micBtn.addEventListener('click', toggleMicRecording);
    }

    const submitBtn = document.getElementById('submit-answer-btn');
    if (submitBtn) {
        submitBtn.addEventListener('click', submitAnswer);
    }

    const nextBtn = document.getElementById('next-question-btn');
    if (nextBtn) {
        nextBtn.addEventListener('click', nextQuestionFromEval);
    }

    // Eval action footer buttons
    const evalNextBtn = document.getElementById('eval-next-btn');
    if (evalNextBtn) {
        evalNextBtn.addEventListener('click', nextQuestionFromEval);
    }
    const evalFinishBtn = document.getElementById('eval-finish-btn');
    if (evalFinishBtn) {
        evalFinishBtn.addEventListener('click', () => finishInterview('results'));
    }
    const evalDashBtn = document.getElementById('eval-dashboard-btn');
    if (evalDashBtn) {
        evalDashBtn.addEventListener('click', () => finishInterview('dashboard'));
    }
    const evalHistBtn = document.getElementById('eval-history-btn');
    if (evalHistBtn) {
        evalHistBtn.addEventListener('click', () => finishInterview('history'));
    }

    const finishDashBtn = document.getElementById('finish-dashboard-btn');
    if (finishDashBtn) {
        finishDashBtn.addEventListener('click', () => finishInterview('dashboard'));
    }
    const finishHistBtn = document.getElementById('finish-history-btn');
    if (finishHistBtn) {
        finishHistBtn.addEventListener('click', () => finishInterview('history'));
    }

    // Exit Interview Modal Controls
    const exitBtn = document.getElementById('exit-interview-btn');
    const exitConfirmBtn = document.getElementById('exit-modal-confirm');
    const exitCancelBtn = document.getElementById('exit-modal-cancel');
    const exitModalCancelBtn = document.getElementById('exit-modal-cancel-btn');
    const exitModalFinishBtn = document.getElementById('exit-modal-finish-btn');

    if (exitBtn) {
        exitBtn.addEventListener('click', openExitModal);
    }
    if (exitCancelBtn) {
        exitCancelBtn.addEventListener('click', closeExitModal);
    }
    if (exitModalCancelBtn) {
        exitModalCancelBtn.addEventListener('click', closeExitModal);
    }
    if (exitModalFinishBtn) {
        exitModalFinishBtn.addEventListener('click', () => finishInterview('dashboard'));
    }
    if (exitConfirmBtn) {
        exitConfirmBtn.addEventListener('click', quitInterview);
    }
});


// ── Evaluation Helpers ────────────────────────────────────
function getEvalScoreColor(score) {
    if (score >= 9) return '#10b981'; // 9-10 Excellent
    if (score >= 7) return '#06b6d4'; // 7-8 Good
    if (score >= 5) return '#f59e0b'; // 5-6 Average
    if (score >= 3) return '#f97316'; // 3-4 Needs Work
    if (score >= 1) return '#ef4444'; // 1-2 Needs Work
    return '#dc2626'; // 0 Not Good / Mismatched
}

function getStatusBadgeClass(status) {
    const s = (status || '').toLowerCase();
    if (s.includes('mismatch')) return 'status-badge-mismatched';
    if (s.includes('excellent')) return 'status-badge-excellent';
    if (s.includes('good') || (s.includes('correct') && !s.includes('partially') && !s.includes('incorrect'))) return 'status-badge-good';
    if (s.includes('partial') || s.includes('average')) return 'status-badge-partial';
    return 'status-badge-needs-work';
}

function getStatusFromScore(score) {
    if (score >= 9) return 'Excellent';
    if (score >= 7) return 'Good';
    if (score >= 5) return 'Average / Partially Correct';
    if (score >= 1) return 'Needs Improvement';
    return 'Not Good / Mismatched Answer';
}


// ── Submit Answer ────────────────────────────────────────
async function submitAnswer() {
    if (isRecording) stopRecording();

    // Ensure any spoken text in transcript preview is captured into answer-input
    const input = document.getElementById('answer-input');
    const transcriptEl = document.getElementById('transcript-content');
    if (input && !input.value.trim() && transcriptEl && transcriptEl.textContent.trim() && transcriptEl.textContent !== '...') {
        input.value = transcriptEl.textContent.trim();
        baseTranscript = input.value;
    }

    const answer = (input ? input.value : '').trim();
    if (!answer) {
        showToast('Please type or speak your answer before submitting', 'error');
        if (input) {
            input.disabled = false;
            input.focus();
        }
        return;
    }

    const question = interviewData.questions[interviewData.currentIndex];
    
    // UI Loading state
    const submitBtn = document.getElementById('submit-answer-btn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner"></span> Evaluating...';
    const doneBtn = document.getElementById('done-speaking-btn');
    if (doneBtn) doneBtn.disabled = true;
    document.getElementById('answer-input').disabled = true;
    document.getElementById('mic-btn').classList.add('hidden');
    
    // AI Thinking animation & state
    if (window.aiRobot) {
        window.aiRobot.startThinking();
    }
    const typingIndicator = document.getElementById('ai-typing');
    if (typingIndicator) typingIndicator.classList.remove('hidden');

    try {
        const data = await api('/api/interview/answer', {
            method: 'POST',
            body: {
                question_id: question.id,
                session_id: interviewData.sessionId,
                answer: answer
            }
        });

        if (window.aiRobot) {
            window.aiRobot.setState('idle');
        }

        const evalData = data.evaluation || {};
        const score = typeof evalData.score === 'number' ? evalData.score : 0;
        let status = evalData.status || getStatusFromScore(score);
        const isMismatched = score === 0 || status.toLowerCase().includes('mismatch');
        if (isMismatched && !status.toLowerCase().includes('mismatch')) {
            status = 'Not Good / Mismatched Answer';
        }

        // Show evaluation card
        const evalBox = document.getElementById('answer-evaluation');

        // Score display (0-10)
        const scoreEl = document.getElementById('eval-score');
        if (scoreEl) {
            scoreEl.textContent = `${score} / 10`;
            scoreEl.style.color = getEvalScoreColor(score);
        }

        // Status badge
        const statusBadge = document.getElementById('eval-status');
        if (statusBadge) {
            statusBadge.textContent = status;
            statusBadge.className = `badge eval-status-badge ${getStatusBadgeClass(status)}`;
        }

        // ── Populate Assessment Verdict Banner (Good vs Not Good) ──
        const verdictBanner = document.getElementById('eval-verdict-banner');
        const verdictIcon = document.getElementById('eval-verdict-icon');
        const verdictHeadline = document.getElementById('eval-verdict-headline');
        const verdictSubtext = document.getElementById('eval-verdict-subtext');
        const verdictTag = document.getElementById('eval-verdict-tag');

        if (verdictBanner) {
            verdictBanner.classList.remove(
                'eval-verdict-excellent',
                'eval-verdict-good',
                'eval-verdict-partial',
                'eval-verdict-needs-work',
                'eval-verdict-mismatched'
            );

            let spokenVerdict = '';

            if (score >= 9) {
                verdictBanner.classList.add('eval-verdict-excellent');
                if (verdictIcon) verdictIcon.textContent = '🌟';
                if (verdictHeadline) verdictHeadline.textContent = 'Result: Excellent Answer';
                if (verdictSubtext) verdictSubtext.textContent = 'Outstanding response! Thorough, accurate, and clearly expressed.';
                if (verdictTag) verdictTag.textContent = 'EXCELLENT';
                spokenVerdict = 'Excellent answer! Well articulated.';
            } else if (score >= 7) {
                verdictBanner.classList.add('eval-verdict-good');
                if (verdictIcon) verdictIcon.textContent = '👍';
                if (verdictHeadline) verdictHeadline.textContent = 'Result: Good Answer';
                if (verdictSubtext) verdictSubtext.textContent = 'Great job! Your answer is solid, relevant, and covers the key concepts.';
                if (verdictTag) verdictTag.textContent = 'GOOD';
                spokenVerdict = 'Good answer! You addressed the question well.';
            } else if (score >= 5) {
                verdictBanner.classList.add('eval-verdict-partial');
                if (verdictIcon) verdictIcon.textContent = '⚖️';
                if (verdictHeadline) verdictHeadline.textContent = 'Result: Partially Good (Average)';
                if (verdictSubtext) verdictSubtext.textContent = "You're on the right track! Adding more details or practical examples will make this stronger.";
                if (verdictTag) verdictTag.textContent = 'AVERAGE';
                spokenVerdict = 'Fair attempt. Review the suggestions below to strengthen your response.';
            } else if (score >= 1) {
                verdictBanner.classList.add('eval-verdict-needs-work');
                if (verdictIcon) verdictIcon.textContent = '⚠️';
                if (verdictHeadline) verdictHeadline.textContent = 'Result: Needs Improvement (Not Good)';
                if (verdictSubtext) verdictSubtext.textContent = 'Your answer is too brief or misses key concepts. Review the suggestions and ideal answer below.';
                if (verdictTag) verdictTag.textContent = 'NEEDS WORK';
                spokenVerdict = 'Your answer needs improvement. Review the ideal response below.';
            } else {
                verdictBanner.classList.add('eval-verdict-mismatched');
                if (verdictIcon) verdictIcon.textContent = '❌';
                if (verdictHeadline) verdictHeadline.textContent = 'Result: Not Good (Mismatched Answer)';
                if (verdictSubtext) verdictSubtext.textContent = 'Your answer does not address the question being asked. Check the question and focus on the topic.';
                if (verdictTag) verdictTag.textContent = 'NOT GOOD';
                spokenVerdict = 'Your answer did not address the question asked.';
            }

            // Update Robot Subtitles with verdict & score
            const subtitlesEl = document.getElementById('robot-subtitles');
            if (subtitlesEl) {
                subtitlesEl.textContent = `“${spokenVerdict} (Score: ${score}/10)”`;
            }
        }

        // Mismatched Alert Banner
        const mismatchBanner = document.getElementById('eval-mismatch-banner');
        if (mismatchBanner) {
            if (isMismatched) {
                mismatchBanner.classList.remove('hidden');
                const mismatchText = document.getElementById('eval-mismatch-text');
                if (mismatchText) mismatchText.textContent = 'Your answer does not address the question being asked.';
            } else {
                mismatchBanner.classList.add('hidden');
            }
        }

        // Question & Your Answer echo
        const questionTextEl = document.getElementById('eval-question-text');
        if (questionTextEl) questionTextEl.textContent = question.text;

        const userAnswerEl = document.getElementById('eval-user-answer');
        if (userAnswerEl) userAnswerEl.textContent = answer;

        // AI Evaluation Feedback
        const feedbackEl = document.getElementById('eval-feedback');
        if (feedbackEl) {
            feedbackEl.textContent = evalData.feedback || (isMismatched ? 'Your answer does not address the question being asked.' : 'Answer evaluated successfully.');
        }

        // Sub-scores
        const subTech = document.getElementById('sub-val-tech');
        if (subTech) subTech.textContent = `${evalData.technical_knowledge ?? score}/10`;
        const subComm = document.getElementById('sub-val-comm');
        if (subComm) subComm.textContent = `${evalData.communication ?? score}/10`;
        const subRel = document.getElementById('sub-val-rel');
        if (subRel) subRel.textContent = `${evalData.relevance ?? score}/10`;
        const subClarity = document.getElementById('sub-val-clarity');
        if (subClarity) subClarity.textContent = `${evalData.clarity ?? score}/10`;

        // Perfect Answer
        const perfectEl = document.getElementById('eval-perfect-answer');
        if (perfectEl) {
            perfectEl.textContent = evalData.perfect_answer || 'A comprehensive, structured answer demonstrating clear understanding of the core concept.';
        }

        // How to Improve
        const improveEl = document.getElementById('eval-improvement');
        if (improveEl) {
            improveEl.textContent = evalData.improvement || (isMismatched ? 'Please re-read the question carefully and directly address the concept being asked.' : 'Continue to structure answers with key definitions, clear examples, and structured explanations.');
        }

        evalBox.classList.remove('hidden');
        evalBox.scrollIntoView({ behavior: 'smooth', block: 'start' });

        // Handle dynamic adaptive next question generated by AI based on previous answer
        const adaptiveNotice = document.getElementById('eval-adaptive-notice');
        const adaptiveText = document.getElementById('eval-adaptive-notice-text');
        if (data.next_question) {
            interviewData.questions[interviewData.currentIndex + 1] = data.next_question;
            if (adaptiveNotice && adaptiveText) {
                adaptiveText.textContent = `🎯 Question ${data.next_question.number} has been dynamically generated based on what you discussed in your answer!`;
                adaptiveNotice.classList.remove('hidden');
            }
            showToast(`🎯 Question ${data.next_question.number} tailored to your answer!`, 'info');
        } else {
            if (adaptiveNotice) adaptiveNotice.classList.add('hidden');
        }
        if (!data.next_question && data.followup) {
            const followupQuestion = {
                id: null,
                number: interviewData.currentIndex + 2,
                text: typeof data.followup === 'string' ? data.followup : data.followup.text || data.followup,
                is_followup: true,
                is_adaptive: true
            };
            interviewData.questions.splice(interviewData.currentIndex + 1, 0, followupQuestion);
            showToast('AI generated a follow-up question!', 'info');
        }

        // Show Next or Finish button
        submitBtn.classList.add('hidden');
        const total = interviewData.totalQuestions || interviewData.questions.length;
        const isLastQuestion = (interviewData.currentIndex >= total - 1);

        const nextBtn = document.getElementById('next-question-btn');
        const finishBtn = document.getElementById('finish-interview-btn');
        const evalNextBtn = document.getElementById('eval-next-btn');
        const evalFinishBtn = document.getElementById('eval-finish-btn');
        const evalBanner = document.getElementById('eval-completion-banner');
        const hudExitBtn = document.getElementById('exit-interview-btn');
        const hudBadge = document.getElementById('interview-status-badge');

        if (isLastQuestion) {
            // Stop stopwatch timer and mic immediately upon completing the last question
            stopTimer();
            stopRecording();

            // Hide next buttons
            if (nextBtn) nextBtn.classList.add('hidden');
            if (evalNextBtn) evalNextBtn.classList.add('hidden');

            // Show finish & navigation buttons (Dashboard, History, Report)
            const finishDashBtn = document.getElementById('finish-dashboard-btn');
            const finishHistBtn = document.getElementById('finish-history-btn');
            const evalDashBtn = document.getElementById('eval-dashboard-btn');
            const evalHistBtn = document.getElementById('eval-history-btn');

            if (finishDashBtn) {
                finishDashBtn.classList.remove('hidden');
                finishDashBtn.innerHTML = '📊 Back to Dashboard (5s)';
                finishDashBtn.onclick = () => {
                    clearAutoCloseTimer();
                    finishInterview('dashboard');
                };
            }
            if (finishHistBtn) {
                finishHistBtn.classList.remove('hidden');
                finishHistBtn.onclick = () => {
                    clearAutoCloseTimer();
                    finishInterview('history');
                };
            }
            if (finishBtn) {
                finishBtn.classList.remove('hidden');
                finishBtn.innerHTML = '🏆 View Report (5s)';
                finishBtn.onclick = () => {
                    clearAutoCloseTimer();
                    finishInterview('results');
                };
            }

            if (evalDashBtn) {
                evalDashBtn.classList.remove('hidden');
                evalDashBtn.innerHTML = '📊 Back to Dashboard (5s)';
                evalDashBtn.onclick = () => {
                    clearAutoCloseTimer();
                    finishInterview('dashboard');
                };
            }
            if (evalHistBtn) {
                evalHistBtn.classList.remove('hidden');
                evalHistBtn.onclick = () => {
                    clearAutoCloseTimer();
                    finishInterview('history');
                };
            }
            if (evalFinishBtn) {
                evalFinishBtn.classList.remove('hidden');
                evalFinishBtn.innerHTML = '🏆 Full Report (5s)';
                evalFinishBtn.onclick = () => {
                    clearAutoCloseTimer();
                    finishInterview('results');
                };
            }
            if (evalBanner) {
                evalBanner.classList.remove('hidden');
            }

            // Transform top HUD Exit button into prominent Dashboard button
            if (hudExitBtn) {
                hudExitBtn.textContent = '🏁 Dashboard (5s)';
                hudExitBtn.className = 'btn btn-success btn-sm';
                hudExitBtn.onclick = () => {
                    clearAutoCloseTimer();
                    finishInterview('dashboard');
                };
                hudExitBtn.title = 'Complete interview and return to Dashboard';
            }
            if (hudBadge) {
                hudBadge.textContent = 'Completed';
                hudBadge.className = 'badge badge-green';
            }
            const total = interviewData.totalQuestions || interviewData.questions.length;
            const progressText = document.getElementById('progress-text');
            if (progressText) {
                progressText.textContent = `All ${total} Questions Completed! 🏁`;
            }

            // Subtitle on 3D robot
            if (window.aiRobot && typeof window.aiRobot.displaySubtitles === 'function') {
                window.aiRobot.displaySubtitles("Interview completed! Returning to your dashboard.");
            }

            // Start auto-close countdown (automatically closes the interview and returns to dashboard in 5 seconds)
            startAutoCloseCountdown(5);
        } else {
            if (nextBtn) {
                nextBtn.classList.remove('hidden');
            }
            if (evalNextBtn) {
                evalNextBtn.classList.remove('hidden');
            }
            if (finishBtn) finishBtn.classList.add('hidden');
            if (document.getElementById('finish-dashboard-btn')) document.getElementById('finish-dashboard-btn').classList.add('hidden');
            if (document.getElementById('finish-history-btn')) document.getElementById('finish-history-btn').classList.add('hidden');
            if (evalFinishBtn) evalFinishBtn.classList.add('hidden');
            if (document.getElementById('eval-dashboard-btn')) document.getElementById('eval-dashboard-btn').classList.add('hidden');
            if (document.getElementById('eval-history-btn')) document.getElementById('eval-history-btn').classList.add('hidden');
            if (evalBanner) evalBanner.classList.add('hidden');
        }

    } catch (error) {
        showToast(error.message, 'error');
        submitBtn.classList.remove('hidden');
        document.getElementById('answer-input').disabled = false;
        document.getElementById('mic-btn').classList.remove('hidden');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '✅ Submit Answer';
        const doneBtn = document.getElementById('done-speaking-btn');
        if (doneBtn) doneBtn.disabled = false;
        if (typingIndicator) typingIndicator.classList.add('hidden');
        if (window.aiRobot && window.aiRobot.currentState === 'thinking') {
            window.aiRobot.setState('idle');
        }
    }
}


// ── Finish Interview ─────────────────────────────────────
let isFinishing = false;
async function finishInterview(targetScreen = 'dashboard') {
    clearAutoCloseTimer();
    const topAlert = document.getElementById('eval-completion-top-alert');
    if (topAlert) topAlert.classList.add('hidden');

    // Guard against double calls (race between auto-timer and click)
    if (isFinishing) return;
    isFinishing = true;

    // Defensive teardowns: ensure no error in media/timer can block completion
    try { stopRecording(); } catch (e) { console.warn('[Finish] stopRecording error:', e); }
    try { stopSpeaking(); } catch (e) { console.warn('[Finish] stopSpeaking error:', e); }
    try { stopTimer(); } catch (e) { console.warn('[Finish] stopTimer error:', e); }
    try {
        if (typeof stopCamera === 'function') stopCamera();
    } catch (e) { console.warn('[Finish] stopCamera error:', e); }
    try {
        if (window.aiRobot) {
            if (typeof window.aiRobot.finishInterview === 'function') {
                window.aiRobot.finishInterview();
            } else if (typeof window.aiRobot.setState === 'function') {
                window.aiRobot.setState('finished');
            }
        }
    } catch (e) { console.warn('[Finish] aiRobot error:', e); }

    try { closeExitModal(); } catch (e) {}

    const targetLabel = (targetScreen === 'history') ? 'History' : (targetScreen === 'results' ? 'Report' : 'Dashboard');
    showLoading(`Finishing interview and returning to ${targetLabel}...`);

    const activeSessionId = interviewData.sessionId || parseInt(sessionStorage.getItem('active_interview_session_id') || '0');
    if (!activeSessionId) {
        console.warn('[Finish] No active session ID found.');
        hideLoading();
        isFinishing = false;
        navigateTo(targetScreen || 'dashboard');
        return;
    }

    try {
        const data = await api('/api/interview/complete', {
            method: 'POST',
            body: { session_id: activeSessionId }
        });

        // Store data globally to read it if viewing results
        App.interviewSession = data;
        interviewData.isCompleted = true;
        try { sessionStorage.removeItem('active_interview_session_id'); } catch(e) {}

        // Navigate cleanly to requested destination
        if (targetScreen === 'history') {
            navigateTo('history');
            if (typeof loadHistory === 'function') loadHistory();
            showToast('🎉 Interview completed! Past session recorded in history.', 'success');
        } else if (targetScreen === 'results') {
            navigateTo('results');
            if (typeof renderResults === 'function') {
                renderResults(data);
            }
            window.scrollTo({ top: 0, behavior: 'smooth' });
            showToast('🎉 Interview completed! Here is your performance report.', 'success');
        } else {
            // Default: back to dashboard
            navigateTo('dashboard');
            if (typeof loadDashboardStats === 'function') loadDashboardStats();
            showToast('🎉 Interview completed! Your dashboard has been updated.', 'success');
        }

    } catch (error) {
        console.error('[Finish] Complete error:', error);
        showToast(error.message || 'Error recording interview completion', 'error');
        // Even on error, NEVER leave user trapped in the interview room!
        navigateTo(targetScreen || 'dashboard');
        if (targetScreen === 'history' && typeof loadHistory === 'function') loadHistory();
        if (targetScreen === 'dashboard' && typeof loadDashboardStats === 'function') loadDashboardStats();
    } finally {
        hideLoading();
        isFinishing = false;
    }
}


// ── Timer Logic ──────────────────────────────────────────
function startTimer() {
    interviewData.totalSeconds = 0;
    const display = document.getElementById('timer-display');
    const container = document.getElementById('interview-timer');
    
    container.classList.remove('warning', 'danger');

    clearInterval(interviewData.timerInterval);
    interviewData.timerInterval = setInterval(() => {
        interviewData.totalSeconds++;
        const m = Math.floor(interviewData.totalSeconds / 60).toString().padStart(2, '0');
        const s = (interviewData.totalSeconds % 60).toString().padStart(2, '0');
        display.textContent = `${m}:${s}`;
        
        // Visual cues for long interviews
        if (interviewData.totalSeconds > 15 * 60) { // 15 mins
            container.classList.add('warning');
        }
        if (interviewData.totalSeconds > 30 * 60) { // 30 mins
            container.classList.remove('warning');
            container.classList.add('danger');
        }
    }, 1000);
}

function stopTimer() {
    clearInterval(interviewData.timerInterval);
}

// ── Quit Interview ───────────────────────────────────────
function quitInterview() {
    clearAutoCloseTimer();
    try { stopRecording(); } catch (e) {}
    try { stopSpeaking(); } catch (e) {}
    try { stopTimer(); } catch (e) {}
    try { if (typeof stopCamera === 'function') stopCamera(); } catch (e) {}
    try {
        if (window.aiRobot) {
            window.aiRobot.setState('idle');
            if (typeof window.aiRobot.stopSpeaking === 'function') window.aiRobot.stopSpeaking();
        }
    } catch (e) {}

    // Fully abort and nullify speech recognition
    if (recognition) {
        try { recognition.abort(); } catch(e) {}
        recognition = null;
    }
    isRecording = false;

    interviewData = {
        sessionId: null,
        type: 'general',
        difficulty: 'medium',
        questions: [],
        totalQuestions: 0,
        currentIndex: 0,
        startTime: null,
        timerInterval: null,
        totalSeconds: 0,
        isCompleted: false
    };
    try { sessionStorage.removeItem('active_interview_session_id'); } catch(e) {}

    closeExitModal();
    navigateTo('dashboard');
    showToast('Interview session ended', 'info');
}

// ── Next Question from Evaluation Footer ─────────────────
function nextQuestionFromEval() {
    interviewData.currentIndex++;
    displayCurrentQuestion();
    const questionCard = document.getElementById('question-card');
    if (questionCard) {
        questionCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// ── Exit Modal Controls ──────────────────────────────────
function openExitModal() {
    // If the interview has already been completed, clicking Exit should immediately return to the home/dashboard screen without asking for confirmation
    const total = interviewData ? (interviewData.totalQuestions || interviewData.questions.length) : 0;
    const isCompleted = (interviewData && (interviewData.isCompleted || (total > 0 && interviewData.currentIndex >= total))) || 
                        (document.getElementById('screen-results') && document.getElementById('screen-results').classList.contains('active')) ||
                        (document.getElementById('interview-status-badge') && document.getElementById('interview-status-badge').textContent.includes('Completed'));

    if (isCompleted) {
        quitInterview();
        return;
    }

    const exitModal = document.getElementById('exit-interview-modal');
    if (exitModal) {
        exitModal.classList.remove('hidden');
    }
}

function closeExitModal() {
    const exitModal = document.getElementById('exit-interview-modal');
    if (exitModal) {
        exitModal.classList.add('hidden');
    }
}

// Ensure camera, audio, speech and timers are stopped on page refresh or navigation
window.addEventListener('beforeunload', () => {
    try { stopRecording(); } catch(e) {}
    try { stopSpeaking(); } catch(e) {}
    try { stopCamera(); } catch(e) {}
    try { stopTimer(); } catch(e) {}
    try { clearAutoCloseTimer(); } catch(e) {}
});

// Close exit modal on Escape key or backdrop click
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const exitModal = document.getElementById('exit-interview-modal');
        if (exitModal && !exitModal.classList.contains('hidden')) {
            closeExitModal();
        }
    }
});

// Global window bindings for foolproof HTML inline onclick handlers
window.openExitModal = openExitModal;
window.closeExitModal = closeExitModal;
window.toggleMicRecording = toggleMicRecording;
window.nextQuestionFromEval = nextQuestionFromEval;
window.finishInterview = finishInterview;
window.quitInterview = quitInterview;
window.pauseAutoClose = pauseAutoClose;
window.startAutoCloseCountdown = startAutoCloseCountdown;
window.clearAutoCloseTimer = clearAutoCloseTimer;

