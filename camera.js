/**
 * AI Smart Interview System — Camera Module
 * Handles candidate webcam feed using WebRTC (navigator.mediaDevices.getUserMedia)
 * No video is stored or uploaded — stream is purely local for the interview experience.
 */

// ── Camera State ─────────────────────────────────────────
let cameraStream = null;
let isCameraOn = true;
let previewStream = null;
let selectedCameraDeviceId = null;
let blackFrameCheckInterval = null;

// ── DOM References (resolved lazily) ─────────────────────
function getCameraElements() {
    return {
        video: document.getElementById('candidate-video'),
        fallback: document.getElementById('candidate-fallback'),
        fallbackMsg: document.getElementById('candidate-fallback-msg'),
        fallbackActions: document.getElementById('candidate-fallback-actions'),
        statusDot: document.getElementById('camera-status-dot'),
        statusText: document.getElementById('camera-status-text'),
        toggleBtn: document.getElementById('camera-toggle-btn'),
        deviceSelect: document.getElementById('camera-device-select'),
        blackAlert: document.getElementById('camera-black-frame-alert'),
        topStatusCamera: document.getElementById('top-status-camera'),
        topStatusListening: document.getElementById('top-status-listening'),
        leftPanel: document.getElementById('interview-left-panel'),
        rightPanel: document.getElementById('interview-right-panel'),
    };
}

// ── Helper: Check Secure Context ─────────────────────────
function checkSecureContext() {
    const isLocalhost = window.location.hostname === 'localhost' ||
                        window.location.hostname === '127.0.0.1' ||
                        window.location.hostname === '[::1]';
    return window.isSecureContext || isLocalhost || window.location.protocol === 'https:';
}

// ── Camera Device Ranking ────────────────────────────────
// Helps avoid picking pitch-black IR or virtual cameras automatically
function rankCameraDevice(device) {
    const label = (device.label || '').toLowerCase();
    if (label.includes('ir ') || label.includes(' ir') || label.includes('hello') || label.includes('face') || label.includes('infra')) {
        return -1; // Lower priority (often pitch-black IR face unlock sensors)
    }
    if (label.includes('obs') || label.includes('virtual')) {
        return 0; // Virtual camera (may be offline/black)
    }
    if (label.includes('integrated') || label.includes('hd') || label.includes('webcam') || label.includes('usb') || label.includes('camera')) {
        return 2; // Preferred real RGB color webcams
    }
    return 1;
}

// ── Populate Camera Devices Dropdown ─────────────────────
async function populateCameraDevices() {
    try {
        if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) return;
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(d => d.kind === 'videoinput');
        
        // Sort devices so real RGB webcams are prioritized over IR sensors
        videoDevices.sort((a, b) => rankCameraDevice(b) - rankCameraDevice(a));

        if (!selectedCameraDeviceId && videoDevices.length > 0) {
            selectedCameraDeviceId = videoDevices[0].deviceId;
        }

        const selects = [
            document.getElementById('camera-device-select'),
            document.getElementById('setup-camera-device-select')
        ];

        selects.forEach(sel => {
            if (!sel) return;
            sel.innerHTML = '';
            if (videoDevices.length > 0) {
                videoDevices.forEach((d, i) => {
                    const opt = document.createElement('option');
                    opt.value = d.deviceId;
                    opt.textContent = d.label || `Camera ${i + 1}`;
                    if (selectedCameraDeviceId && selectedCameraDeviceId === d.deviceId) {
                        opt.selected = true;
                    }
                    sel.appendChild(opt);
                });
                if (videoDevices.length > 1) {
                    sel.classList.remove('hidden');
                } else {
                    sel.classList.add('hidden');
                }
            } else {
                sel.classList.add('hidden');
            }
        });
    } catch(e) {
        console.warn('[Camera] enumerateDevices error:', e);
    }
}

// ── Black Frame Monitor ──────────────────────────────────
// Detects if the webcam stream is active but transmitting pure black frames (shutter closed, IR camera, etc.)
function startBlackFrameMonitor(videoEl) {
    stopBlackFrameMonitor();
    let blackCounter = 0;

    blackFrameCheckInterval = setInterval(() => {
        if (!videoEl || !cameraStream || !isCameraOn) {
            stopBlackFrameMonitor();
            return;
        }
        if (videoEl.videoWidth === 0 || videoEl.videoHeight === 0 || videoEl.paused) {
            return;
        }

        try {
            const canvas = document.createElement('canvas');
            canvas.width = 16;
            canvas.height = 12;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(videoEl, 0, 0, 16, 12);
            const imgData = ctx.getImageData(0, 0, 16, 12).data;
            let sum = 0;
            for (let i = 0; i < imgData.length; i += 4) {
                sum += (imgData[i] + imgData[i+1] + imgData[i+2]) / 3;
            }
            const avg = sum / (imgData.length / 4);

            const alertEl = document.getElementById('camera-black-frame-alert');
            if (avg < 1.0) { // Pitch black
                blackCounter++;
                if (blackCounter >= 2 && alertEl) {
                    alertEl.classList.remove('hidden');
                }
            } else {
                blackCounter = 0;
                if (alertEl) {
                    alertEl.classList.add('hidden');
                }
            }
        } catch (e) {
            stopBlackFrameMonitor();
        }
    }, 1500);
}

function stopBlackFrameMonitor() {
    if (blackFrameCheckInterval) {
        clearInterval(blackFrameCheckInterval);
        blackFrameCheckInterval = null;
    }
    const alertEl = document.getElementById('camera-black-frame-alert');
    if (alertEl) alertEl.classList.add('hidden');
}

// ── Initialize Camera ────────────────────────────────────
async function initCamera(preferredDeviceId = null) {
    if (preferredDeviceId) {
        selectedCameraDeviceId = preferredDeviceId;
    }
    const el = getCameraElements();
    if (!el.video) return;

    // Check secure context requirement
    if (!checkSecureContext()) {
        const portStr = window.location.port ? `:${window.location.port}` : '';
        const targetUrl = `http://localhost${portStr}${window.location.pathname}`;
        showCameraFallback(
            `<div style="font-weight:600;margin-bottom:6px;color:#f59e0b">Secure Context Required</div>` +
            `<div style="font-size:0.813rem;line-height:1.5;color:var(--text-secondary)">` +
            `Chrome & Edge only permit webcam access on <code>http://localhost:5000</code>.<br>` +
            `You are currently accessing via <code>${escapeHtml(window.location.host)}</code>.` +
            `</div>`,
            true, // isSecureContextIssue
            false,
            targetUrl
        );
        return;
    }

    // Check browser mediaDevices support
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showCameraFallback(
            `<div style="font-weight:600;margin-bottom:6px;color:#f87171">Camera Not Supported</div>` +
            `<div style="font-size:0.813rem;line-height:1.5;color:var(--text-secondary)">` +
            `Your browser does not permit camera access on this connection. ` +
            `Please open <strong>http://localhost:5000</strong> directly in Chrome or Edge.` +
            `</div>`,
            true
        );
        return;
    }

    // Clean up any existing stream before requesting a fresh one
    stopCamera();

    let stream = null;
    let lastError = null;

    // Strategy 1: Specific or ideal constraints
    try {
        const c1 = selectedCameraDeviceId
            ? { video: { deviceId: { exact: selectedCameraDeviceId }, width: { ideal: 640 }, height: { ideal: 480 } }, audio: false }
            : { video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' }, audio: false };
        stream = await navigator.mediaDevices.getUserMedia(c1);
    } catch (err1) {
        console.warn('[Camera] Strategy 1 failed:', err1.name, err1.message);
        lastError = err1;

        // Strategy 2: Relaxed resolution
        try {
            const c2 = selectedCameraDeviceId
                ? { video: { deviceId: { exact: selectedCameraDeviceId } }, audio: false }
                : { video: { width: { ideal: 640 }, height: { ideal: 480 } }, audio: false };
            stream = await navigator.mediaDevices.getUserMedia(c2);
        } catch (err2) {
            console.warn('[Camera] Strategy 2 failed:', err2.name, err2.message);
            lastError = err2;

            // Strategy 3: Minimal universal video constraint
            try {
                stream = await navigator.mediaDevices.getUserMedia({
                    video: true,
                    audio: false
                });
            } catch (err3) {
                console.error('[Camera] Strategy 3 failed:', err3.name, err3.message);
                lastError = err3;
            }
        }
    }

    if (stream) {
        cameraStream = stream;

        // Configure video element attributes and properties for reliable playback
        el.video.muted = true;
        el.video.playsInline = true;
        el.video.setAttribute('muted', '');
        el.video.setAttribute('playsinline', '');
        el.video.setAttribute('autoplay', '');
        el.video.srcObject = stream;

        // Explicitly trigger play to prevent frozen/blank video
        try {
            await el.video.play();
        } catch (playError) {
            console.warn('[Camera] Autoplay play() rejected:', playError);
            const onUserInteract = () => {
                if (el.video && el.video.srcObject) {
                    el.video.play().catch(() => {});
                }
            };
            document.addEventListener('click', onUserInteract, { once: true });
        }

        el.video.onloadedmetadata = () => {
            el.video.play().catch(() => {});
        };

        // Listen for hardware disconnect & hardware mute
        const videoTrack = stream.getVideoTracks()[0];
        if (videoTrack) {
            if (videoTrack.getSettings && videoTrack.getSettings().deviceId) {
                selectedCameraDeviceId = videoTrack.getSettings().deviceId;
            }
            videoTrack.onended = () => {
                console.warn('[Camera] Video track ended unexpectedly.');
                showCameraFallback('Camera was disconnected or turned off in system settings.');
            };
            videoTrack.onmute = () => {
                console.warn('[Camera] Video track was muted by hardware or Windows shutter.');
                const alertEl = document.getElementById('camera-black-frame-alert');
                if (alertEl) alertEl.classList.remove('hidden');
            };
            videoTrack.onunmute = () => {
                console.log('[Camera] Video track unmuted.');
                const alertEl = document.getElementById('camera-black-frame-alert');
                if (alertEl) alertEl.classList.add('hidden');
            };
        }

        el.video.classList.remove('hidden', 'camera-paused');
        if (el.fallback) el.fallback.classList.add('hidden');

        isCameraOn = true;
        updateCameraStatus(true);
        updateTopStatus();

        // Refresh device list and start monitor
        populateCameraDevices();
        startBlackFrameMonitor(el.video);
        initCandidateAudioWaveform();

    } else {
        handleCameraError(lastError);
    }
}

// ── Stop Camera (full cleanup) ───────────────────────────
function stopCamera() {
    stopBlackFrameMonitor();
    stopCandidateAudioWaveform();

    if (cameraStream) {
        cameraStream.getTracks().forEach(track => {
            track.stop();
        });
        cameraStream = null;
    }

    const el = getCameraElements();
    if (el.video) {
        el.video.srcObject = null;
        el.video.classList.add('hidden');
    }

    isCameraOn = false;
    updateCameraStatus(false);
}

// ── Toggle Camera On/Off ─────────────────────────────────
function toggleCamera() {
    const el = getCameraElements();

    if (!cameraStream) {
        initCamera(selectedCameraDeviceId);
        return;
    }

    const videoTrack = cameraStream.getVideoTracks()[0];
    if (!videoTrack || videoTrack.readyState === 'ended') {
        initCamera(selectedCameraDeviceId);
        return;
    }

    if (videoTrack.enabled) {
        // Turn camera off
        videoTrack.enabled = false;
        isCameraOn = false;
        updateCameraStatus(false);

        if (el.video) el.video.classList.add('camera-paused');
        showCameraFallback('Camera is paused', false, true);
    } else {
        // Turn camera back on
        videoTrack.enabled = true;
        isCameraOn = true;
        updateCameraStatus(true);

        if (el.video) {
            el.video.classList.remove('camera-paused', 'hidden');
            el.video.play().catch(() => {});
        }
        if (el.fallback) el.fallback.classList.add('hidden');
    }

    updateTopStatus();
}

// ── Switch Camera ────────────────────────────────────────
function switchCamera(deviceId) {
    selectedCameraDeviceId = deviceId;
    initCamera(deviceId);
}

// ── Update Camera Status Indicators ──────────────────────
function updateCameraStatus(isOn) {
    const el = getCameraElements();

    if (el.statusDot) {
        el.statusDot.className = 'camera-status-dot ' + (isOn ? 'on' : 'off');
    }
    if (el.statusText) {
        el.statusText.textContent = isOn ? 'Camera On' : 'Camera Off';
    }
    if (el.toggleBtn) {
        el.toggleBtn.innerHTML = isOn ? '📷' : '🚫';
        el.toggleBtn.title = isOn ? 'Turn camera off' : 'Turn camera on';
        el.toggleBtn.setAttribute('aria-label', isOn ? 'Turn camera off' : 'Turn camera on');
    }
}

// ── Update Top Status Bar ────────────────────────────────
function updateTopStatus() {
    const el = getCameraElements();
    if (el.topStatusCamera) {
        el.topStatusCamera.textContent = isCameraOn ? '📷 Camera On' : '📷 Camera Off';
        el.topStatusCamera.className = 'top-status-item ' + (isCameraOn ? 'active' : '');
    }
}

// ── Show Fallback UI with Action Buttons ─────────────────
function showCameraFallback(message, isSecureContextIssue = false, isPaused = false, targetUrl = '') {
    const el = getCameraElements();

    if (el.video) {
        if (!isPaused) {
            el.video.classList.add('hidden');
        }
    }
    if (el.fallback) el.fallback.classList.remove('hidden');
    if (el.fallbackMsg) el.fallbackMsg.innerHTML = message || 'Camera unavailable';

    // Populate dynamic action buttons inside the card
    const actionsContainer = el.fallbackActions || document.getElementById('candidate-fallback-actions');
    if (actionsContainer) {
        if (isSecureContextIssue && targetUrl) {
            actionsContainer.innerHTML = `
                <a href="${targetUrl}" class="btn btn-primary btn-sm mt-xs" style="text-decoration:none">
                    🚀 Switch to Localhost URL
                </a>
            `;
        } else if (isPaused) {
            actionsContainer.innerHTML = `
                <button type="button" class="btn btn-secondary btn-sm mt-xs" onclick="toggleCamera()">
                    ▶️ Resume Camera
                </button>
            `;
        } else {
            actionsContainer.innerHTML = `
                <button type="button" class="btn btn-primary btn-sm mt-xs" onclick="initCamera(selectedCameraDeviceId)">
                    🔄 Try Again
                </button>
            `;
        }
    }

    isCameraOn = false;
    updateCameraStatus(false);
    updateTopStatus();
}

// ── Handle Camera Errors with Detailed Instructions ───────
function handleCameraError(error) {
    console.error('[Camera] Camera initialization error:', error);

    const errName = error ? (error.name || '') : '';
    const errMsg = error ? (error.message || '') : '';
    let message = '';

    if (errName === 'NotAllowedError' || errName === 'PermissionDeniedError') {
        message = `
            <div style="font-weight:600;margin-bottom:6px;color:#f87171">Camera Permission Blocked</div>
            <div style="font-size:0.75rem;line-height:1.5;color:var(--text-secondary);text-align:left;margin-bottom:6px">
                • Look at the top left of Chrome's address bar next to <code>http://localhost:5000</code>.<br>
                • Click the <strong>tune / site settings</strong> icon and set <strong>Camera</strong> to <strong>Allow</strong>.<br>
                • Check Windows Settings &rarr; <em>Privacy & Security &rarr; Camera</em> and ensure desktop apps have access.
            </div>
        `;
    } else if (errName === 'NotReadableError' || errName === 'TrackStartError') {
        message = `
            <div style="font-weight:600;margin-bottom:6px;color:#f87171">Camera In Use by Another App</div>
            <div style="font-size:0.75rem;line-height:1.5;color:var(--text-secondary);text-align:left;margin-bottom:6px">
                Another application is currently using your webcam (Windows Camera app, Zoom, Teams, Skype, OBS, or another browser tab).<br>
                Please close other apps using the camera and click <strong>Try Again</strong>.
            </div>
        `;
    } else if (errName === 'NotFoundError' || errName === 'DevicesNotFoundError') {
        message = `
            <div style="font-weight:600;margin-bottom:6px;color:#f87171">No Camera Detected</div>
            <div style="font-size:0.75rem;line-height:1.5;color:var(--text-secondary);text-align:left;margin-bottom:6px">
                Windows did not find an active camera. Check that your webcam is plugged in, or you can continue the interview using voice and text.
            </div>
        `;
    } else {
        message = `
            <div style="font-weight:600;margin-bottom:6px;color:#f87171">Camera Unavailable (${escapeHtml(errName || 'Error')})</div>
            <div style="font-size:0.75rem;line-height:1.5;color:var(--text-secondary);text-align:left;margin-bottom:6px">
                ${escapeHtml(errMsg || 'Could not start webcam stream.')}<br>
                Please check camera permissions and click <strong>Try Again</strong>.
            </div>
        `;
    }

    showCameraFallback(message);
    if (typeof showToast === 'function') {
        showToast(errName === 'NotAllowedError' ? 'Please grant camera permission in your browser address bar' : (errName || 'Camera unavailable'), 'info');
    }
}

// ── Camera Preview for Setup Screen ──────────────────────
async function initCameraPreview(targetVideoId = 'setup-camera-preview') {
    const video = document.getElementById(targetVideoId);
    const fallback = document.getElementById('setup-camera-fallback');
    const msg = document.getElementById('setup-camera-msg');
    if (!video) return;

    if (!checkSecureContext()) {
        if (msg) msg.textContent = 'Camera requires http://localhost:5000 in Chrome/Edge.';
        return;
    }

    stopCameraPreview();

    try {
        const c = selectedCameraDeviceId
            ? { video: { deviceId: { exact: selectedCameraDeviceId }, width: { ideal: 640 }, height: { ideal: 480 } }, audio: false }
            : { video: { width: { ideal: 640 }, height: { ideal: 480 } }, audio: false };
        previewStream = await navigator.mediaDevices.getUserMedia(c);
        video.muted = true;
        video.playsInline = true;
        video.setAttribute('muted', '');
        video.setAttribute('playsinline', '');
        video.setAttribute('autoplay', '');
        video.srcObject = previewStream;
        await video.play().catch(() => {});
        video.classList.remove('hidden');
        if (fallback) fallback.classList.add('hidden');
        populateCameraDevices();
    } catch (err) {
        console.warn('[Camera Preview] Ideal preview init failed:', err);
        try {
            previewStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
            video.muted = true;
            video.playsInline = true;
            video.srcObject = previewStream;
            await video.play().catch(() => {});
            video.classList.remove('hidden');
            if (fallback) fallback.classList.add('hidden');
            populateCameraDevices();
        } catch (e) {
            console.error('[Camera Preview] All preview attempts failed:', e);
            if (msg) {
                if (e.name === 'NotAllowedError') {
                    msg.innerHTML = '<span style="color:#f87171">Permission blocked</span>. Allow camera in address bar.';
                } else if (e.name === 'NotReadableError') {
                    msg.innerHTML = '<span style="color:#f87171">Camera in use</span> by another application.';
                } else {
                    msg.textContent = 'Camera unavailable or not detected.';
                }
            }
            if (fallback) fallback.classList.remove('hidden');
            video.classList.add('hidden');
        }
    }
}

function stopCameraPreview() {
    if (previewStream) {
        previewStream.getTracks().forEach(t => t.stop());
        previewStream = null;
    }
    const video = document.getElementById('setup-camera-preview');
    if (video) {
        video.srcObject = null;
        video.classList.add('hidden');
    }
    const fallback = document.getElementById('setup-camera-fallback');
    if (fallback) fallback.classList.remove('hidden');
}

// ── Candidate Microphone Audio Waveform ──────────────────
let candidateAudioCtx = null;
let candidateAnalyser = null;
let candidateMicStream = null;
let candidateWaveformAnim = null;
let candidateHasSpoken = false;
let candidateSilenceTimeout = null;

async function initCandidateAudioWaveform() {
    stopCandidateAudioWaveform();

    const canvas = document.getElementById('candidate-audio-waveform');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const statusEl = document.getElementById('audio-waveform-status');

    // Request microphone audio stream
    try {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            candidateMicStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            candidateAudioCtx = new AudioContextClass();
            const source = candidateAudioCtx.createMediaStreamSource(candidateMicStream);
            candidateAnalyser = candidateAudioCtx.createAnalyser();
            candidateAnalyser.fftSize = 64;
            candidateAnalyser.smoothingTimeConstant = 0.8;
            source.connect(candidateAnalyser);

            if (candidateAudioCtx && candidateAudioCtx.state === 'suspended') {
                const resumeCtx = () => {
                    if (candidateAudioCtx && candidateAudioCtx.state === 'suspended') {
                        candidateAudioCtx.resume().catch(() => {});
                    }
                };
                ['click', 'keydown', 'touchstart'].forEach(evt => {
                    document.addEventListener(evt, resumeCtx, { once: true });
                });
            }
        }
    } catch(err) {
        console.warn('[Waveform] Mic access error or not yet granted:', err);
    }

    const bufferLength = candidateAnalyser ? candidateAnalyser.frequencyBinCount : 32;
    const dataArray = new Uint8Array(bufferLength);

    function draw() {
        candidateWaveformAnim = requestAnimationFrame(draw);
        if (!canvas) return;

        const width = canvas.width;
        const height = canvas.height;
        ctx.clearRect(0, 0, width, height);

        let energy = 0;
        if (candidateAnalyser) {
            candidateAnalyser.getByteFrequencyData(dataArray);
            for (let i = 0; i < bufferLength; i++) {
                energy += dataArray[i];
            }
            energy = energy / bufferLength;
        }

        const isSpeaking = energy > 16;
        const rightPanel = document.getElementById('interview-right-panel');

        if (isSpeaking) {
            candidateHasSpoken = true;
            if (statusEl) {
                statusEl.textContent = 'Speaking...';
                statusEl.style.color = '#34d399';
            }
            if (rightPanel) rightPanel.classList.add('active-speaker');
            if (candidateSilenceTimeout) {
                clearTimeout(candidateSilenceTimeout);
                candidateSilenceTimeout = null;
            }
        } else {
            if (statusEl) {
                statusEl.textContent = 'Listening for voice...';
                statusEl.style.color = 'var(--text-muted)';
            }
            if (rightPanel && !document.getElementById('answer-input')?.matches(':focus')) {
                rightPanel.classList.remove('active-speaker');
            }

            // Detect natural pause after speaking
            if (candidateHasSpoken && !candidateSilenceTimeout) {
                candidateSilenceTimeout = setTimeout(() => {
                    const doneBtn = document.getElementById('done-speaking-btn');
                    if (doneBtn && !doneBtn.classList.contains('hidden')) {
                        doneBtn.style.animation = 'status-pulse 1.5s infinite';
                    }
                }, 2400);
            }
        }

        // Draw audio spectrum equalizer bars
        const numBars = 32;
        const barWidth = Math.max(3, Math.floor((width - (numBars * 3)) / numBars));
        let x = 4;

        for (let i = 0; i < numBars; i++) {
            let barHeight = 4;
            if (candidateAnalyser && energy > 4) {
                const sampleIndex = Math.floor((i / numBars) * bufferLength);
                const val = dataArray[sampleIndex] || 0;
                barHeight = Math.max(4, (val / 255) * (height - 6));
            } else {
                // Subtle idle breathing pulse
                const wave = Math.sin(Date.now() * 0.003 + i * 0.25);
                barHeight = 4 + (wave + 1) * 2;
            }

            const y = (height - barHeight) / 2;

            // Gradient: cyan to emerald
            const grad = ctx.createLinearGradient(0, y, 0, y + barHeight);
            if (isSpeaking) {
                grad.addColorStop(0, '#34d399');
                grad.addColorStop(1, '#059669');
            } else {
                grad.addColorStop(0, '#06b6d4');
                grad.addColorStop(1, '#0284c7');
            }

            ctx.fillStyle = grad;
            ctx.beginPath();
            if (ctx.roundRect) {
                ctx.roundRect(x, y, barWidth, barHeight, 2);
            } else {
                ctx.rect(x, y, barWidth, barHeight);
            }
            ctx.fill();

            x += barWidth + 3;
            if (x >= width - 4) break;
        }
    }

    draw();
}

function stopCandidateAudioWaveform() {
    if (candidateWaveformAnim) {
        cancelAnimationFrame(candidateWaveformAnim);
        candidateWaveformAnim = null;
    }
    if (candidateSilenceTimeout) {
        clearTimeout(candidateSilenceTimeout);
        candidateSilenceTimeout = null;
    }
    if (candidateMicStream) {
        candidateMicStream.getTracks().forEach(t => t.stop());
        candidateMicStream = null;
    }
    if (candidateAudioCtx) {
        candidateAudioCtx.close().catch(() => {});
        candidateAudioCtx = null;
    }
    candidateAnalyser = null;
    candidateHasSpoken = false;

    const canvas = document.getElementById('candidate-audio-waveform');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
}

// ── Active Speaker Highlighting ──────────────────────────
function setupActiveSpeakerObserver() {
    const el = getCameraElements();
    const robotStatePill = document.getElementById('robot-state-pill');

    function checkAiSpeaking() {
        const isSpeaking = (window.aiRobot && window.aiRobot.currentState === 'speaking') ||
                           (robotStatePill && robotStatePill.classList.contains('state-speaking'));

        if (el.leftPanel && el.rightPanel) {
            if (isSpeaking) {
                el.leftPanel.classList.add('active-speaker');
                el.rightPanel.classList.remove('active-speaker');
            } else {
                el.leftPanel.classList.remove('active-speaker');
            }
        }
    }

    if (robotStatePill) {
        const observer = new MutationObserver(checkAiSpeaking);
        observer.observe(robotStatePill, { attributes: true, attributeFilter: ['class'] });
    }

    // Observe candidate typing in answer input
    const answerInput = document.getElementById('answer-input');
    if (answerInput && el.rightPanel && el.leftPanel) {
        answerInput.addEventListener('focus', () => {
            el.rightPanel.classList.add('active-speaker');
            el.leftPanel.classList.remove('active-speaker');
            if (el.topStatusListening) {
                el.topStatusListening.textContent = '🎙️ Answering';
                el.topStatusListening.classList.add('active');
            }
        });
        answerInput.addEventListener('blur', () => {
            el.rightPanel.classList.remove('active-speaker');
            if (el.topStatusListening) {
                el.topStatusListening.textContent = '🎙️ Listening';
                el.topStatusListening.classList.remove('active');
            }
        });
    }
}

// ── Cleanup on page unload ───────────────────────────────
window.addEventListener('beforeunload', () => {
    stopCamera();
    stopCameraPreview();
    stopCandidateAudioWaveform();
});

// ── Setup camera controls on DOM ready ───────────────────
document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('camera-toggle-btn');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', toggleCamera);
    }

    // Camera device selectors
    const sel = document.getElementById('camera-device-select');
    if (sel) {
        sel.addEventListener('change', (e) => {
            selectedCameraDeviceId = e.target.value;
            initCamera(selectedCameraDeviceId);
        });
    }
    const setupSel = document.getElementById('setup-camera-device-select');
    if (setupSel) {
        setupSel.addEventListener('change', (e) => {
            selectedCameraDeviceId = e.target.value;
            initCameraPreview();
        });
    }

    // Initial enumeration check
    populateCameraDevices();
});
