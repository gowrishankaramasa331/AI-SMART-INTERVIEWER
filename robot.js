/**
 * AI Smart Interview System — 3D Robot Interviewer Component
 * Implements a realistic, friendly, professional humanoid robot interviewer
 * with procedural Three.js 3D rendering, alive kinematics, and clear interview states.
 */

class RobotInterviewer {
    constructor() {
        this.container = null;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.animFrameId = null;

        // Current state: 'idle' | 'listening' | 'thinking' | 'speaking' | 'finished'
        this.currentState = 'idle';
        this.previousState = null;

        // Kinematics & Animation variables
        this.clock = null;
        this.elapsed = 0;
        this.robotRoot = null;
        this.headGroup = null;
        this.neckGroup = null;
        this.torsoGroup = null;
        this.eyes = [];
        this.eyelids = [];
        this.mouthBars = [];
        this.thinkingHalo = null;
        this.thinkingHaloInner = null;
        this.voiceRings = [];
        this.particles = null;

        // Head orientation targets (for smooth slerp/lerp)
        this.targetHeadRotation = { x: 0, y: 0, z: 0 };
        this.currentHeadRotation = { x: 0, y: 0, z: 0 };

        // Eye gaze targets
        this.targetGaze = { x: 0, y: 0 };
        this.currentGaze = { x: 0, y: 0 };

        // Blinking system
        this.blinkState = 0; // 0 = open, 1 = closing, 2 = closed, 3 = opening
        this.blinkProgress = 0;
        this.nextBlinkTime = 2.5;

        // Speaking audio animation
        this.isSpeaking = false;
        this.speakingCadence = 0;
        this.speechVoiceFrequency = 0;

        // Lighting refs
        this.coreLight = null;
        this.rimLight = null;
        this.keyLight = null;

        // Bound render loop
        this.animate = this.animate.bind(this);
        this.onResize = this.onResize.bind(this);
    }

    /**
     * Initialize the 3D scene inside container
     */
    init(container) {
        if (typeof container === 'string') {
            this.container = document.getElementById(container);
        } else {
            this.container = container;
        }

        if (!this.container) {
            console.error('[Robot] Container not found');
            return false;
        }

        if (typeof THREE === 'undefined') {
            console.error('[Robot] Three.js is not loaded');
            return false;
        }

        // Clean any existing canvas in container
        this.destroy();

        const width = this.container.clientWidth || 480;
        const height = this.container.clientHeight || 360;

        // Scene setup
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x060913); // Dark cybernetic studio background
        this.scene.fog = new THREE.FogExp2(0x060913, 0.045);

        // Camera setup
        this.camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 100);
        this.camera.position.set(0, 0.15, 3.4);
        this.camera.lookAt(0, 0.05, 0);

        // Renderer setup
        this.renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: true,
            powerPreference: 'high-performance'
        });
        this.renderer.setSize(width, height);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        if (this.renderer.outputEncoding !== undefined) {
            this.renderer.outputEncoding = THREE.sRGBEncoding;
        }
        this.container.appendChild(this.renderer.domElement);

        this.clock = new THREE.Clock();

        // Build Studio Lighting
        this.setupLighting();

        // Build 3D Robot Humanoid Model
        this.buildRobot();

        // Build Atmospheric Cyber Particles
        this.buildAtmosphere();

        // Start render loop
        window.addEventListener('resize', this.onResize);
        this.animate();

        // Set initial state
        this.setState('idle');

        return true;
    }

    /**
     * Dark futuristic studio 3-point lighting with glowing rim & cyber accents
     */
    setupLighting() {
        // Deep ambient tone
        const ambient = new THREE.AmbientLight(0x1a2642, 0.85);
        this.scene.add(ambient);

        // Key light: cool cyan-white spotlight from upper-front
        this.keyLight = new THREE.DirectionalLight(0xa5f3fc, 1.4);
        this.keyLight.position.set(1.5, 3.0, 3.5);
        this.scene.add(this.keyLight);

        // Fill light: soft electric violet from left
        const fillLight = new THREE.DirectionalLight(0x818cf8, 0.8);
        fillLight.position.set(-2.5, 1.5, 2.0);
        this.scene.add(fillLight);

        // Rim / Kick light: intense vibrant blue from behind robot silhouette
        this.rimLight = new THREE.DirectionalLight(0x38bdf8, 1.8);
        this.rimLight.position.set(0, 2.5, -3.0);
        this.scene.add(this.rimLight);

        // Subtle under-glow from console/desk
        const bottomGlow = new THREE.PointLight(0x3b82f6, 1.0, 6);
        bottomGlow.position.set(0, -2.0, 1.5);
        this.scene.add(bottomGlow);
    }

    /**
     * Procedural Humanoid Robot Android Bust
     */
    buildRobot() {
        this.robotRoot = new THREE.Group();
        this.scene.add(this.robotRoot);

        // Common Materials
        const darkArmorMat = new THREE.MeshStandardMaterial({
            color: 0x0f172a, // Deep obsidian slate
            metalness: 0.85,
            roughness: 0.22,
        });

        const titaniumMat = new THREE.MeshStandardMaterial({
            color: 0x334155, // Silver-gray titanium alloy
            metalness: 0.90,
            roughness: 0.35,
        });

        const chromeAccentMat = new THREE.MeshStandardMaterial({
            color: 0x94a3b8, // Polished chrome joints
            metalness: 0.95,
            roughness: 0.15,
        });

        const glowingCyanMat = new THREE.MeshBasicMaterial({
            color: 0x38bdf8, // Electric cyan LED glow
        });

        // ══════════════════════════════════════════
        // 1. TORSO & CHEST
        // ══════════════════════════════════════════
        this.torsoGroup = new THREE.Group();
        this.robotRoot.add(this.torsoGroup);

        // Main chest plate
        const chestGeo = new THREE.CylinderGeometry(0.72, 0.58, 0.9, 12);
        chestGeo.scale(1.2, 1, 0.65);
        const chest = new THREE.Mesh(chestGeo, darkArmorMat);
        chest.position.set(0, -0.9, 0);
        this.torsoGroup.add(chest);

        // Titanium chest contour armor bevels
        const bevelGeo = new THREE.BoxGeometry(0.9, 0.55, 0.15);
        const leftBevel = new THREE.Mesh(bevelGeo, titaniumMat);
        leftBevel.position.set(-0.35, -0.85, 0.28);
        leftBevel.rotation.set(0.1, -0.2, 0.1);
        this.torsoGroup.add(leftBevel);

        const rightBevel = new THREE.Mesh(bevelGeo, titaniumMat);
        rightBevel.position.set(0.35, -0.85, 0.28);
        rightBevel.rotation.set(0.1, 0.2, -0.1);
        this.torsoGroup.add(rightBevel);

        // Chest Cyber-Core (Arc Reactor / Power Core)
        const coreOuterRingGeo = new THREE.TorusGeometry(0.14, 0.022, 16, 32);
        const coreRing = new THREE.Mesh(coreOuterRingGeo, chromeAccentMat);
        coreRing.position.set(0, -0.8, 0.35);
        this.torsoGroup.add(coreRing);

        const coreLensGeo = new THREE.CylinderGeometry(0.10, 0.10, 0.04, 24);
        coreLensGeo.rotateX(Math.PI / 2);
        this.coreLens = new THREE.Mesh(coreLensGeo, glowingCyanMat);
        this.coreLens.position.set(0, -0.8, 0.35);
        this.torsoGroup.add(this.coreLens);

        this.coreLight = new THREE.PointLight(0x38bdf8, 1.2, 3.5);
        this.coreLight.position.set(0, -0.8, 0.45);
        this.torsoGroup.add(this.coreLight);

        // Shoulder Pauldrons / Plates
        const shoulderGeo = new THREE.SphereGeometry(0.36, 16, 16, 0, Math.PI * 2, 0, Math.PI * 0.5);
        const leftShoulder = new THREE.Mesh(shoulderGeo, darkArmorMat);
        leftShoulder.position.set(-0.95, -0.65, -0.05);
        leftShoulder.rotation.set(0, 0, 0.6);
        this.torsoGroup.add(leftShoulder);

        const rightShoulder = new THREE.Mesh(shoulderGeo, darkArmorMat);
        rightShoulder.position.set(0.95, -0.65, -0.05);
        rightShoulder.rotation.set(0, 0, -0.6);
        this.torsoGroup.add(rightShoulder);

        // ══════════════════════════════════════════
        // 2. NECK & HYDRAULICS
        // ══════════════════════════════════════════
        this.neckGroup = new THREE.Group();
        this.robotRoot.add(this.neckGroup);

        // Central neck cylinder column
        const neckGeo = new THREE.CylinderGeometry(0.20, 0.24, 0.45, 16);
        const neck = new THREE.Mesh(neckGeo, titaniumMat);
        neck.position.set(0, -0.28, -0.04);
        this.neckGroup.add(neck);

        // Hydraulic neck pistons (left & right)
        const pistonGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.42, 12);
        this.leftPiston = new THREE.Mesh(pistonGeo, chromeAccentMat);
        this.leftPiston.position.set(-0.22, -0.28, 0.05);
        this.neckGroup.add(this.leftPiston);

        this.rightPiston = new THREE.Mesh(pistonGeo, chromeAccentMat);
        this.rightPiston.position.set(0.22, -0.28, 0.05);
        this.neckGroup.add(this.rightPiston);

        // ══════════════════════════════════════════
        // 3. HEAD & FACE
        // ══════════════════════════════════════════
        this.headGroup = new THREE.Group();
        this.headGroup.position.set(0, 0.12, 0);
        this.robotRoot.add(this.headGroup);

        // Main Head Helmet Shell (Humanoid contour)
        const skullGeo = new THREE.SphereGeometry(0.55, 32, 24);
        skullGeo.scale(0.88, 1.05, 0.95);
        const skull = new THREE.Mesh(skullGeo, darkArmorMat);
        this.headGroup.add(skull);

        // Titanium Jaw & Cheekbone Plates
        const jawGeo = new THREE.BoxGeometry(0.58, 0.38, 0.48);
        const jaw = new THREE.Mesh(jawGeo, titaniumMat);
        jaw.position.set(0, -0.22, 0.16);
        jaw.rotation.x = 0.18;
        this.headGroup.add(jaw);

        // Sleek Visor Faceplate (Smoked Glass / Cyber Surface)
        const visorGeo = new THREE.SphereGeometry(0.51, 24, 16, 0, Math.PI, 0, Math.PI * 0.75);
        visorGeo.scale(0.85, 0.85, 0.96);
        const visorMat = new THREE.MeshStandardMaterial({
            color: 0x050a18,
            metalness: 0.95,
            roughness: 0.08,
            transparent: true,
            opacity: 0.92
        });
        const visor = new THREE.Mesh(visorGeo, visorMat);
        visor.rotation.x = Math.PI * 0.05;
        visor.position.set(0, 0.04, 0.08);
        this.headGroup.add(visor);

        // Ear Audio Sensors (Side Cylinders with LED indicators)
        const earGeo = new THREE.CylinderGeometry(0.12, 0.12, 0.16, 16);
        earGeo.rotateZ(Math.PI / 2);

        const leftEar = new THREE.Mesh(earGeo, titaniumMat);
        leftEar.position.set(-0.52, 0.08, -0.02);
        this.headGroup.add(leftEar);

        const rightEar = new THREE.Mesh(earGeo, titaniumMat);
        rightEar.position.set(0.52, 0.08, -0.02);
        this.headGroup.add(rightEar);

        // Ear LED Rings
        const earRingGeo = new THREE.TorusGeometry(0.09, 0.015, 12, 24);
        earRingGeo.rotateY(Math.PI / 2);

        this.leftEarLed = new THREE.Mesh(earRingGeo, glowingCyanMat);
        this.leftEarLed.position.set(-0.59, 0.08, -0.02);
        this.headGroup.add(this.leftEarLed);

        this.rightEarLed = new THREE.Mesh(earRingGeo, glowingCyanMat);
        this.rightEarLed.position.set(0.59, 0.08, -0.02);
        this.headGroup.add(this.rightEarLed);

        // ══════════════════════════════════════════
        // 4. EYES & BLINKING EYELIDS
        // ══════════════════════════════════════════
        const eyeSpacing = 0.19;
        const eyeY = 0.10;
        const eyeZ = 0.44;

        [-1, 1].forEach((side) => {
            const eyeContainer = new THREE.Group();
            eyeContainer.position.set(side * eyeSpacing, eyeY, eyeZ);
            this.headGroup.add(eyeContainer);

            // Eye socket bezel
            const socketRingGeo = new THREE.TorusGeometry(0.08, 0.018, 12, 24);
            const socketRing = new THREE.Mesh(socketRingGeo, chromeAccentMat);
            eyeContainer.add(socketRing);

            // Glowing Eye Pupil/Iris
            const pupilGeo = new THREE.SphereGeometry(0.055, 16, 16);
            pupilGeo.scale(1, 1, 0.5);
            const eyeMat = new THREE.MeshBasicMaterial({
                color: 0x38bdf8
            });
            const pupil = new THREE.Mesh(pupilGeo, eyeMat);
            eyeContainer.add(pupil);
            this.eyes.push(eyeMat);

            // Iris aperture ring
            const irisRingGeo = new THREE.RingGeometry(0.052, 0.075, 24);
            const irisRing = new THREE.Mesh(irisRingGeo, new THREE.MeshBasicMaterial({
                color: 0x0ea5e9,
                side: THREE.DoubleSide
            }));
            irisRing.position.z = 0.015;
            eyeContainer.add(irisRing);

            // Upper Eyelid (metallic shutter for natural blinks)
            const eyelidGeo = new THREE.SphereGeometry(0.085, 16, 12, 0, Math.PI * 2, 0, Math.PI * 0.5);
            const eyelidMat = new THREE.MeshStandardMaterial({
                color: 0x1e293b,
                metalness: 0.85,
                roughness: 0.3
            });
            const upperEyelid = new THREE.Mesh(eyelidGeo, eyelidMat);
            upperEyelid.rotation.x = -Math.PI * 0.5; // Initially open (pulled up)
            upperEyelid.position.z = 0.01;
            eyeContainer.add(upperEyelid);
            this.eyelids.push(upperEyelid);
        });

        // ══════════════════════════════════════════
        // 5. MOUTH / VOICE FREQUENCY EQUALIZER
        // ══════════════════════════════════════════
        const mouthContainer = new THREE.Group();
        mouthContainer.position.set(0, -0.22, 0.44);
        mouthContainer.rotation.x = 0.15;
        this.headGroup.add(mouthContainer);

        // Mouth base plate groove
        const mouthBackingGeo = new THREE.PlaneGeometry(0.38, 0.08);
        const mouthBacking = new THREE.Mesh(mouthBackingGeo, new THREE.MeshBasicMaterial({
            color: 0x050811
        }));
        mouthContainer.add(mouthBacking);

        // 9 Segmented LED frequency equalizer bars
        const numBars = 9;
        const barWidth = 0.022;
        const barSpacing = 0.038;
        const startX = -((numBars - 1) * barSpacing) / 2;

        this.mouthBars = [];
        for (let i = 0; i < numBars; i++) {
            const barGeo = new THREE.BoxGeometry(barWidth, 0.06, 0.015);
            const barMat = new THREE.MeshBasicMaterial({
                color: 0x38bdf8,
                transparent: true,
                opacity: 0.7
            });
            const bar = new THREE.Mesh(barGeo, barMat);
            bar.position.set(startX + i * barSpacing, 0, 0.01);
            mouthContainer.add(bar);
            this.mouthBars.push({ mesh: bar, mat: barMat, baseHeight: 0.06, index: i });
        }

        // ══════════════════════════════════════════
        // 6. THINKING CRANIAL HALO RINGS
        // ══════════════════════════════════════════
        const haloOuterGeo = new THREE.TorusGeometry(0.68, 0.016, 16, 48);
        haloOuterGeo.rotateX(Math.PI / 2);
        this.haloMat = new THREE.MeshBasicMaterial({
            color: 0x8b5cf6, // Vibrant violet thinking aura
            transparent: true,
            opacity: 0.0,
            wireframe: false
        });
        this.thinkingHalo = new THREE.Mesh(haloOuterGeo, this.haloMat);
        this.thinkingHalo.position.set(0, 0.65, 0);
        this.headGroup.add(this.thinkingHalo);

        const haloInnerGeo = new THREE.TorusGeometry(0.54, 0.012, 16, 36);
        haloInnerGeo.rotateX(Math.PI / 2);
        haloInnerGeo.rotateZ(0.4);
        this.haloInnerMat = new THREE.MeshBasicMaterial({
            color: 0x06b6d4, // Cyan inner counter-ring
            transparent: true,
            opacity: 0.0
        });
        this.thinkingHaloInner = new THREE.Mesh(haloInnerGeo, this.haloInnerMat);
        this.thinkingHaloInner.position.set(0, 0.62, 0);
        this.headGroup.add(this.thinkingHaloInner);

        // ══════════════════════════════════════════
        // 7. VOICE AURA SHOCKWAVE RINGS
        // ══════════════════════════════════════════
        for (let i = 0; i < 3; i++) {
            const ringGeo = new THREE.RingGeometry(0.85 + i * 0.15, 0.88 + i * 0.15, 32);
            const ringMat = new THREE.MeshBasicMaterial({
                color: 0x38bdf8,
                transparent: true,
                opacity: 0.0,
                side: THREE.DoubleSide
            });
            const ring = new THREE.Mesh(ringGeo, ringMat);
            ring.position.set(0, 0.1, -0.3);
            this.robotRoot.add(ring);
            this.voiceRings.push({ mesh: ring, mat: ringMat, delay: i * 0.35, scale: 1 });
        }
    }

    /**
     * Subtle floating atmospheric dust particles for premium studio depth
     */
    buildAtmosphere() {
        const count = 100;
        const positions = new Float32Array(count * 3);
        for (let i = 0; i < count; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 6;
            positions[i * 3 + 1] = (Math.random() - 0.5) * 4;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 4;
        }

        const particleGeo = new THREE.BufferGeometry();
        particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));

        const particleMat = new THREE.PointsMaterial({
            color: 0x38bdf8,
            size: 0.035,
            transparent: true,
            opacity: 0.35,
            blending: THREE.AdditiveBlending
        });

        this.particles = new THREE.Points(particleGeo, particleMat);
        this.scene.add(this.particles);
    }

    /**
     * Change visual & behavioral interview state
     * States: 'idle' | 'listening' | 'thinking' | 'speaking' | 'finished'
     */
    setState(state) {
        if (!['idle', 'listening', 'thinking', 'speaking', 'finished'].includes(state)) {
            console.warn('[Robot] Unknown state:', state);
            return;
        }

        this.previousState = this.currentState;
        this.currentState = state;

        // Update UI pill badges & texts if present in DOM
        this.updateDOMState(state);

        switch (state) {
            case 'idle':
                this.isSpeaking = false;
                // Facing front, relaxed posture
                this.targetHeadRotation = { x: 0.02, y: 0, z: 0 };
                this.setEyeColors(0x38bdf8); // calm sky blue
                this.setHaloOpacity(0.0);
                break;

            case 'listening':
                this.isSpeaking = false;
                // Attentive turn: head turns slightly to the right (towards candidate video) and tilts slightly
                this.targetHeadRotation = { x: 0.08, y: 0.22, z: -0.04 };
                this.setEyeColors(0x06b6d4); // focused cyan
                this.setHaloOpacity(0.0);
                break;

            case 'thinking':
                this.isSpeaking = false;
                // Pensive posture: head tilts slightly up and to the side
                this.targetHeadRotation = { x: -0.08, y: -0.12, z: 0.05 };
                this.setEyeColors(0xa855f7); // deep processing violet
                this.setHaloOpacity(0.9);
                break;

            case 'speaking':
                this.isSpeaking = true;
                // Active communication: facing candidate with dynamic micro-nods
                this.targetHeadRotation = { x: 0.03, y: 0.05, z: 0 };
                this.setEyeColors(0x38bdf8); // vibrant electric blue
                this.setHaloOpacity(0.0);
                break;

            case 'finished':
                this.isSpeaking = false;
                // Warm nod of congratulation
                this.targetHeadRotation = { x: 0.12, y: 0, z: 0 };
                this.setEyeColors(0x10b981); // emerald victory green
                this.setHaloOpacity(0.4);
                if (this.haloMat) this.haloMat.color.setHex(0x10b981);
                break;
        }
    }

    /**
     * Updates DOM indicators (state pill, subtitles, status texts)
     */
    updateDOMState(state) {
        const stateBadge = document.getElementById('robot-state-pill');
        const stateText = document.getElementById('robot-state-text');
        const statusIndicator = document.getElementById('top-status-listening');

        const stateInfo = {
            idle: { label: 'Ready for your interview', class: 'state-idle', icon: '🤖' },
            listening: { label: 'Listening…', class: 'state-listening', icon: '🎙️' },
            thinking: { label: 'Thinking…', class: 'state-thinking', icon: '⚡' },
            speaking: { label: 'AI Interviewer', class: 'state-speaking', icon: '🔊' },
            finished: { label: 'Great job!', class: 'state-finished', icon: '🏆' }
        };

        const info = stateInfo[state] || stateInfo.idle;

        if (stateBadge) {
            stateBadge.className = `robot-state-pill ${info.class}`;
        }
        if (stateText) {
            stateText.textContent = `${info.icon} ${info.label}`;
        }

        // Keep top status sync
        if (statusIndicator) {
            if (state === 'listening') {
                statusIndicator.textContent = '🎙️ Listening to Candidate';
                statusIndicator.classList.add('active');
            } else if (state === 'speaking') {
                statusIndicator.textContent = '🔊 AI Speaking';
                statusIndicator.classList.add('active');
            } else if (state === 'thinking') {
                statusIndicator.textContent = '⚡ AI Processing';
                statusIndicator.classList.add('active');
            } else {
                statusIndicator.textContent = '🤖 AI Ready';
                statusIndicator.classList.remove('active');
            }
        }
    }

    /**
     * Start speaking animation and synchronize with text-to-speech
     */
    startSpeaking(text, onEndCallback) {
        this.setState('speaking');

        // Subtitles display in DOM
        this.displaySubtitles(text);

        // Fallback or external speech synthesis hook
        if (typeof speakText === 'function') {
            speakText(text, null, () => {
                this.stopSpeaking();
                if (onEndCallback) onEndCallback();
            });
        } else {
            // Simulated speech duration if speakText is not yet connected
            const duration = Math.max(2500, (text ? text.length : 20) * 65);
            setTimeout(() => {
                this.stopSpeaking();
                if (onEndCallback) onEndCallback();
            }, duration);
        }
    }

    /**
     * Stop speaking animation and transition to listening
     */
    stopSpeaking() {
        this.isSpeaking = false;
        // Reset mouth equalizer bars
        if (this.mouthBars && this.mouthBars.length) {
            this.mouthBars.forEach(b => {
                b.mesh.scale.y = 1;
                b.mat.opacity = 0.5;
            });
        }
    }

    startListening() {
        this.setState('listening');
    }

    startThinking() {
        this.setState('thinking');
    }

    finishInterview() {
        this.setState('finished');
    }

    /**
     * Show live subtitles under the robot viewport
     */
    displaySubtitles(text) {
        const subBox = document.getElementById('robot-subtitles');
        if (!subBox) return;

        subBox.innerHTML = '';
        subBox.classList.remove('hidden');

        // Typewriter subtitle effect
        const words = (text || '').split(' ');
        let wordIndex = 0;

        if (this.subtitleTimer) clearInterval(this.subtitleTimer);

        this.subtitleTimer = setInterval(() => {
            if (wordIndex < words.length) {
                const span = document.createElement('span');
                span.className = 'sub-word';
                span.textContent = words[wordIndex] + ' ';
                subBox.appendChild(span);
                wordIndex++;
                subBox.scrollTop = subBox.scrollHeight;
            } else {
                clearInterval(this.subtitleTimer);
            }
        }, 120);
    }

    setEyeColors(hex) {
        if (!this.eyes) return;
        this.eyes.forEach(mat => mat.color.setHex(hex));
        if (this.leftEarLed) this.leftEarLed.material.color.setHex(hex);
        if (this.rightEarLed) this.rightEarLed.material.color.setHex(hex);
        if (this.coreLight) this.coreLight.color.setHex(hex);
    }

    setHaloOpacity(targetOpacity) {
        this.targetHaloOpacity = targetOpacity;
    }

    /**
     * Natural blinking animation logic
     */
    updateBlinking(delta) {
        this.nextBlinkTime -= delta;

        if (this.nextBlinkTime <= 0 && this.blinkState === 0) {
            this.blinkState = 1; // Start closing
            this.blinkProgress = 0;
        }

        if (this.blinkState === 1) { // Closing
            this.blinkProgress += delta * 12; // Fast blink ~80ms
            if (this.blinkProgress >= 1) {
                this.blinkProgress = 1;
                this.blinkState = 2; // Fully closed
            }
        } else if (this.blinkState === 2) { // Closed momentary pause
            this.blinkState = 3; // Reopening
        } else if (this.blinkState === 3) { // Opening
            this.blinkProgress -= delta * 10;
            if (this.blinkProgress <= 0) {
                this.blinkProgress = 0;
                this.blinkState = 0; // Fully open
                // Schedule next blink in 2.8 - 5.5 seconds naturally
                this.nextBlinkTime = 2.8 + Math.random() * 2.7;
            }
        }

        // Apply eyelid shutter rotation
        const eyelidRotation = -Math.PI * 0.5 + this.blinkProgress * (Math.PI * 0.52);
        this.eyelids.forEach(eyelid => {
            eyelid.rotation.x = eyelidRotation;
        });
    }

    /**
     * Main 60FPS animation loop
     */
    animate() {
        this.animFrameId = requestAnimationFrame(this.animate);

        const delta = this.clock.getDelta();
        this.elapsed += delta;

        // ── 1. Alive Idle Breathing Kinematics ─────────────────
        // Torso gently lifts and expands in a natural 4-second respiratory sine wave
        const breathSine = Math.sin(this.elapsed * 1.55);
        if (this.torsoGroup) {
            this.torsoGroup.position.y = breathSine * 0.018;
            this.torsoGroup.scale.set(
                1 + breathSine * 0.008,
                1 + breathSine * 0.012,
                1 + breathSine * 0.008
            );
        }
        if (this.neckGroup) {
            this.neckGroup.position.y = breathSine * 0.015;
        }

        // Core light breathing pulse
        if (this.coreLight) {
            this.coreLight.intensity = 1.0 + breathSine * 0.4;
        }

        // ── 2. Natural Head Movement & State Lerp ─────────────
        // Alive micro-saccades / human-like head drift
        let microDriftX = Math.sin(this.elapsed * 0.8) * 0.018;
        let microDriftY = Math.cos(this.elapsed * 0.6) * 0.022;

        if (this.currentState === 'speaking') {
            // Conversational head nods while speaking
            microDriftX += Math.sin(this.elapsed * 6.5) * 0.035;
            microDriftY += Math.cos(this.elapsed * 4.2) * 0.025;
        }

        // Smoothly interpolate current rotation to target
        const lerpFactor = delta * 4.5;
        this.currentHeadRotation.x += (this.targetHeadRotation.x + microDriftX - this.currentHeadRotation.x) * lerpFactor;
        this.currentHeadRotation.y += (this.targetHeadRotation.y + microDriftY - this.currentHeadRotation.y) * lerpFactor;
        this.currentHeadRotation.z += (this.targetHeadRotation.z - this.currentHeadRotation.z) * lerpFactor;

        if (this.headGroup) {
            this.headGroup.rotation.set(
                this.currentHeadRotation.x,
                this.currentHeadRotation.y,
                this.currentHeadRotation.z
            );
            this.headGroup.position.y = 0.12 + breathSine * 0.015;
        }

        // Neck hydraulic compression reacts to head pitch
        if (this.leftPiston && this.rightPiston) {
            const pitchAdjust = 1.0 + this.currentHeadRotation.x * 0.4;
            this.leftPiston.scale.y = pitchAdjust;
            this.rightPiston.scale.y = pitchAdjust;
        }

        // ── 3. Blinking Eye Eyelid Logic ──────────────────────
        this.updateBlinking(delta);

        // ── 4. Speaking Voice Equalizer Animation ────────────
        if (this.isSpeaking) {
            this.speakingCadence += delta * 18;
            this.mouthBars.forEach((bar, idx) => {
                // Syllable wave combined with bar index offset
                const wave = Math.sin(this.speakingCadence + idx * 0.75);
                const secondHarmonic = Math.cos(this.speakingCadence * 1.8 - idx * 0.4);
                const scale = Math.max(0.4, (wave * 0.5 + secondHarmonic * 0.5 + 1.2) * 1.4);
                bar.mesh.scale.y = scale;
                bar.mat.opacity = Math.min(1.0, 0.4 + scale * 0.35);
            });

            // Voice rings expand and pulse outward
            this.voiceRings.forEach(ring => {
                ring.scale += delta * 1.2;
                ring.mesh.scale.set(ring.scale, ring.scale, 1);
                ring.mat.opacity = Math.max(0, (2.2 - ring.scale) * 0.35);
                if (ring.scale > 2.2) {
                    ring.scale = 0.8;
                }
            });
        } else {
            // Calm idle murmur in equalizer
            const idleWave = (Math.sin(this.elapsed * 2.0) + 1) * 0.5;
            this.mouthBars.forEach((bar, idx) => {
                const subtleScale = 0.45 + Math.sin(this.elapsed * 3.0 + idx * 0.5) * 0.15;
                bar.mesh.scale.y = subtleScale;
                bar.mat.opacity = 0.3 + idleWave * 0.2;
            });

            this.voiceRings.forEach(ring => {
                ring.mat.opacity = 0.0;
            });
        }

        // ── 5. Thinking Holographic Halo Rotation ─────────────
        if (this.thinkingHalo && this.thinkingHaloInner) {
            const targetOpacity = this.targetHaloOpacity || 0.0;
            this.haloMat.opacity += (targetOpacity - this.haloMat.opacity) * (delta * 4);
            this.haloInnerMat.opacity += (targetOpacity - this.haloInnerMat.opacity) * (delta * 4);

            if (this.haloMat.opacity > 0.02) {
                // Outer ring spins clockwise, inner ring counter-clockwise
                this.thinkingHalo.rotation.z += delta * 1.8;
                this.thinkingHaloInner.rotation.z -= delta * 2.4;
                // Subtle holographic vertical bob
                this.thinkingHalo.position.y = 0.65 + Math.sin(this.elapsed * 4.0) * 0.025;
                this.thinkingHaloInner.position.y = 0.62 + Math.cos(this.elapsed * 3.5) * 0.02;
            }
        }

        // ── 6. Ambient Cyber Dust Drift ───────────────────────
        if (this.particles) {
            this.particles.rotation.y = this.elapsed * 0.025;
        }

        // Render scene
        this.renderer.render(this.scene, this.camera);
    }

    /**
     * Responsive container resize
     */
    onResize() {
        if (!this.container || !this.renderer || !this.camera) return;
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        if (width === 0 || height === 0) return;

        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }

    /**
     * Destroy & clean up WebGL resources
     */
    destroy() {
        if (this.animFrameId) {
            cancelAnimationFrame(this.animFrameId);
            this.animFrameId = null;
        }
        window.removeEventListener('resize', this.onResize);
        if (this.subtitleTimer) {
            clearInterval(this.subtitleTimer);
            this.subtitleTimer = null;
        }
        if (this.renderer && this.renderer.domElement && this.renderer.domElement.parentNode) {
            this.renderer.domElement.parentNode.removeChild(this.renderer.domElement);
            this.renderer.dispose();
            this.renderer = null;
        }
    }
}

// Global instance
window.RobotInterviewer = RobotInterviewer;
window.aiRobot = null;
