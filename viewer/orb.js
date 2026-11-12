/**
 * J.A.R.V.I.S. Holographic Reactive HUD Orb Engine
 * High-precision vector & 3D kinetic canvas rendering of the multi-ring concentric holographic reactor.
 * Features Rose UI Kinetic Mechanical Disassembly & 3D Gimbal Perspectives (Exploded Arc Reactor).
 * Central J.A.R.V.I.S. HUD typography in electric neon cyan (#00e5ff / #00ffff).
 * Supports 9 reactive operational states, real-time Web Audio API frequency reactivity,
 * and seamless docking to bottom-right corner when holographic report cards are active.
 */

class JarvisOrb {
  constructor(canvasId, options = {}) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.width = options.width || 320;
    this.height = options.height || 320;
    this.canvas.width = this.width;
    this.canvas.height = this.height;

    // State machine: idle, listening, thinking, speaking, executing, waiting_for_approval, error, paused, offline
    this.state = 'idle';
    this.stateText = 'SYSTEM READY';
    this.progress = 0; // 0 to 100 for executing

    // Dynamic rotation and gimbal angles
    this.angleOuter = 0;
    this.angleDial = 0;
    this.angleInner1 = 0;
    this.angleInner2 = 0;
    this.angleSegments = 0;
    this.pulsePhase = 0;
    this.laserPhase = 0;
    this.gimbalWobble = 0;

    // Kinetic Disassembly & 3D Perspective State (Rose UI)
    this.isMainUI = true;
    this.isDocked = false;
    this.disassembly = 0.0;        // 0.0 (compact) -> 1.0 (fully exploded)
    this.targetDisassembly = 0.0;  // Interpolation target
    this.lockPulse = 0.0;          // Energy shockwave snap upon reassembly

    // Real-time Web Audio reactivity
    this.analyser = null;
    this.audioData = new Uint8Array(64);
    this.audioLevel = 0;
    this.smoothedAudioLevel = 0;

    // High-tech Neon Cyan Color Schemes per State
    this.colorSchemes = {
      idle: {
        primary: '#00e5ff',
        secondary: '#00838f',
        accent: '#00ffff',
        glow: 'rgba(0, 229, 255, 0.45)',
        core: '#002733',
        flash: 'rgba(0, 229, 255, 0.95)',
      },
      listening: {
        primary: '#00ffff',
        secondary: '#00b4d8',
        accent: '#ffffff',
        glow: 'rgba(0, 255, 255, 0.85)',
        core: '#00364a',
        flash: 'rgba(255, 255, 255, 0.95)',
      },
      thinking: {
        primary: '#00e5ff',
        secondary: '#38bdf8',
        accent: '#c084fc',
        glow: 'rgba(0, 229, 255, 0.70)',
        core: '#0f172a',
        flash: 'rgba(192, 132, 252, 0.85)',
      },
      speaking: {
        primary: '#00ffff',
        secondary: '#00e5ff',
        accent: '#ffffff',
        glow: 'rgba(0, 255, 255, 0.85)',
        core: '#00364a',
        flash: 'rgba(0, 255, 255, 0.95)',
      },
      executing: {
        primary: '#00e5ff',
        secondary: '#f59e0b',
        accent: '#fbbf24',
        glow: 'rgba(0, 229, 255, 0.65)',
        core: '#002733',
        flash: 'rgba(251, 191, 36, 0.85)',
      },
      waiting_for_approval: {
        primary: '#fbbf24',
        secondary: '#00e5ff',
        accent: '#fef08a',
        glow: 'rgba(251, 191, 36, 0.80)',
        core: '#1f1b0a',
        flash: 'rgba(254, 240, 138, 0.85)',
      },
      error: {
        primary: '#ef4444',
        secondary: '#dc2626',
        accent: '#00e5ff',
        glow: 'rgba(239, 68, 68, 0.85)',
        core: '#2b0c0c',
        flash: 'rgba(239, 68, 68, 0.95)',
      },
      paused: {
        primary: '#00e5ff',
        secondary: '#546e7a',
        accent: '#b0bec5',
        glow: 'rgba(0, 229, 255, 0.30)',
        core: '#0a1922',
        flash: 'rgba(0, 229, 255, 0.50)',
      },
      offline: {
        primary: '#455a64',
        secondary: '#263238',
        accent: '#78909c',
        glow: 'rgba(69, 90, 100, 0.20)',
        core: '#070d12',
        flash: 'rgba(69, 90, 100, 0.30)',
      },
    };

    this.animate = this.animate.bind(this);
    requestAnimationFrame(this.animate);
  }

  resize(width, height) {
    this.width = width;
    this.height = height;
    if (this.canvas) {
      this.canvas.width = width;
      this.canvas.height = height;
    }
  }

  setMainUI(isMain) {
    this.isMainUI = !!isMain;
    if (!this.isMainUI) {
      this.targetDisassembly = 0.0;
      this.disassembly = 0.0;
      this.lockPulse = 0.0;
    }
  }

  setDisassembled(active) {
    if (!this.isMainUI) {
      this.targetDisassembly = 0.0;
      return;
    }
    this.targetDisassembly = active ? 1.0 : 0.0;
  }

  setDocked(docked) {
    this.isDocked = !!docked;
  }

  setState(newState, label = null) {
    if (this.colorSchemes[newState]) {
      this.state = newState;
    }
    if (label) {
      this.stateText = label.toUpperCase();
    } else {
      this.stateText = newState.replace(/_/g, ' ').toUpperCase();
    }
    if (this.isMainUI) {
      if (['listening', 'thinking', 'speaking', 'executing', 'waiting_for_approval'].includes(newState)) {
        this.targetDisassembly = 1.0;
      } else if (newState === 'idle' || newState === 'paused' || newState === 'offline') {
        this.targetDisassembly = 0.0;
      }
    } else {
      this.targetDisassembly = 0.0;
    }
  }

  setAudioAnalyser(analyser) {
    this.analyser = analyser;
  }

  setProgress(percent) {
    this.progress = Math.max(0, Math.min(100, percent));
  }

  updateAudioLevel() {
    if (this.analyser) {
      this.analyser.getByteFrequencyData(this.audioData);
      let sum = 0;
      for (let i = 0; i < 32; i++) {
        sum += this.audioData[i];
      }
      const avg = sum / 32;
      this.audioLevel = avg / 255; // 0.0 to 1.0
    } else if (this.state === 'speaking' || this.state === 'listening') {
      // High-resolution simulated vocal audio harmonic pulse
      const t = this.pulsePhase * 3.8;
      this.audioLevel = 0.18 + 0.28 * Math.sin(t) + 0.14 * Math.sin(t * 2.3) + 0.08 * Math.cos(t * 4.1);
    } else {
      this.audioLevel = 0;
    }
    // Smooth audio reactivity to prevent visual jitter
    this.smoothedAudioLevel += (this.audioLevel - this.smoothedAudioLevel) * 0.25;
  }

  drawRing(cx, cy, radius, width, color, dash = []) {
    if (radius <= 0) return;
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, radius, 0, Math.PI * 2);
    this.ctx.lineWidth = width;
    this.ctx.strokeStyle = color;
    this.ctx.setLineDash(dash);
    this.ctx.stroke();
    this.ctx.setLineDash([]);
  }

  drawTickMarks(cx, cy, radius, count, tickLength, angleOffset, color, majorStep = 0) {
    if (radius <= 0) return;
    this.ctx.strokeStyle = color;
    for (let i = 0; i < count; i++) {
      const angle = (i * 2 * Math.PI) / count + angleOffset;
      const isMajor = majorStep > 0 && i % majorStep === 0;
      const curTick = isMajor ? tickLength * 1.6 : tickLength;
      this.ctx.lineWidth = isMajor ? 1.8 : 1.1;

      const x1 = cx + Math.cos(angle) * radius;
      const y1 = cy + Math.sin(angle) * radius;
      const x2 = cx + Math.cos(angle) * (radius - curTick);
      const y2 = cy + Math.sin(angle) * (radius - curTick);

      this.ctx.beginPath();
      this.ctx.moveTo(x1, y1);
      this.ctx.lineTo(x2, y2);
      this.ctx.stroke();
    }
  }

  drawSegmentedArc(cx, cy, radius, width, segments, angleOffset, color, padRatio = 0.32) {
    if (radius <= 0) return;
    this.ctx.strokeStyle = color;
    this.ctx.lineWidth = width;
    const arcLen = (2 * Math.PI) / segments;
    const pad = arcLen * padRatio;
    for (let i = 0; i < segments; i++) {
      const start = i * arcLen + angleOffset;
      const end = start + arcLen - pad;
      this.ctx.beginPath();
      this.ctx.arc(cx, cy, radius, start, end);
      this.ctx.stroke();
    }
  }

  /**
   * Render kinetic layer with simulated 3D perspective gimbal tilt (Pitch, Roll, Yaw)
   */
  draw3DGimbalRing(cx, cy, radius, pitchAngle, rollAngle, yawAngle, drawFn) {
    this.ctx.save();
    this.ctx.translate(cx, cy);
    if (yawAngle) this.ctx.rotate(yawAngle);
    // Perspective scale transforms: compress Y for pitch, compress X for roll
    const scaleY = Math.max(0.2, Math.cos(pitchAngle));
    const scaleX = Math.max(0.2, Math.cos(rollAngle));
    this.ctx.scale(scaleX, scaleY);
    drawFn(0, 0, radius);
    this.ctx.restore();
  }

  animate() {
    this.ctx.clearRect(0, 0, this.width, this.height);
    const cx = this.width / 2;
    const cy = this.height / 2;

    // Disassembly interpolation and reassembly locking snap
    const prevDis = this.disassembly;
    this.disassembly += (this.targetDisassembly - this.disassembly) * 0.085;
    if (prevDis > 0.05 && this.disassembly <= 0.05 && this.targetDisassembly === 0) {
      this.lockPulse = 1.0;
    }
    if (this.lockPulse > 0.01) {
      this.lockPulse -= 0.045;
    } else {
      this.lockPulse = 0;
    }

    this.laserPhase = (this.laserPhase + 0.05) % 1.0;
    this.pulsePhase += 0.04;
    this.gimbalWobble += 0.025;

    // Base radius adapts dynamically for main UI or docked scale
    const baseR = Math.min(cx, cy) * (this.isMainUI ? (this.isDocked ? 0.72 : 0.60) : 0.88);
    const theme = this.colorSchemes[this.state] || this.colorSchemes.idle;

    this.updateAudioLevel();

    // Rotational velocities adjusted for state kinetics
    let speedMult = 1.0;
    if (this.state === 'listening') speedMult = 1.8;
    else if (this.state === 'thinking') speedMult = 3.0;
    else if (this.state === 'speaking') speedMult = 1.7;
    else if (this.state === 'executing') speedMult = 2.4;
    else if (this.state === 'paused' || this.state === 'offline') speedMult = 0.08;

    this.angleOuter += 0.0055 * speedMult;
    this.angleDial -= 0.0035 * speedMult;
    this.angleInner1 -= 0.0095 * speedMult;
    this.angleInner2 += 0.0150 * speedMult;
    this.angleSegments -= 0.0075 * speedMult;

    const dynamicAudioPulse = this.smoothedAudioLevel * 16.0;
    const dynamicBreathPulse = Math.sin(this.pulsePhase) * 2.5;
    const dynamicPulse = dynamicBreathPulse + dynamicAudioPulse;

    // ── 0. KINETIC 3D DISASSEMBLY EXPANSION METRICS ──
    const dis = this.disassembly;
    const rOuter = baseR * (1.0 + 0.40 * dis);
    const rCalipers = baseR * (1.0 + 0.58 * dis);
    const rDial = baseR * (0.88 + 0.28 * dis);
    const rSegmented = baseR * (0.76 + 0.18 * dis) + dynamicPulse * 0.3;
    const rDotted = baseR * (0.64 + 0.12 * dis);
    const rInnerRotor = baseR * (0.54 + 0.08 * dis);
    const coreR = Math.max(14, baseR * 0.40 + dynamicPulse);

    // ── 1. Deep Core Ambient Cybernetic Glow (Neon Cyan Aura) ──
    const grad = this.ctx.createRadialGradient(cx, cy, baseR * 0.08, cx, cy, rOuter * 1.25);
    grad.addColorStop(0, theme.glow);
    grad.addColorStop(0.45, 'rgba(0, 229, 255, 0.18)');
    grad.addColorStop(0.85, 'rgba(0, 229, 255, 0.04)');
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    this.ctx.fillStyle = grad;
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, rOuter * 1.25, 0, Math.PI * 2);
    this.ctx.fill();

    // ── 2. Laser Struts / Sliding Telescopic Rails (Core to Calipers) ──
    if (dis > 0.01) {
      this.ctx.save();
      for (let i = 0; i < 4; i++) {
        const angle = (i * Math.PI) / 2 + this.angleOuter * 0.15;
        const cosA = Math.cos(angle);
        const sinA = Math.sin(angle);

        const xStart = cx + cosA * (coreR + 3);
        const yStart = cy + sinA * (coreR + 3);
        const xEnd = cx + cosA * rCalipers;
        const yEnd = cy + sinA * rCalipers;

        // Dual precision laser guide beam
        this.ctx.strokeStyle = 'rgba(0, 229, 255, 0.85)';
        this.ctx.lineWidth = 1.0;
        this.ctx.shadowBlur = 8 * dis;
        this.ctx.shadowColor = '#00e5ff';
        this.ctx.beginPath();
        this.ctx.moveTo(xStart, yStart);
        this.ctx.lineTo(xEnd, yEnd);
        this.ctx.stroke();

        // Traveling energy bead along each laser strut
        const beadT = (this.laserPhase + i * 0.25) % 1.0;
        const bx = xStart + (xEnd - xStart) * beadT;
        const by = yStart + (yEnd - yStart) * beadT;
        this.ctx.fillStyle = '#ffffff';
        this.ctx.shadowColor = '#00ffff';
        this.ctx.shadowBlur = 10;
        this.ctx.beginPath();
        this.ctx.arc(bx, by, 2.4 * dis, 0, Math.PI * 2);
        this.ctx.fill();

        // Mechanical vernier scale micro-ticks along the slide rails
        const steps = 5;
        this.ctx.strokeStyle = 'rgba(0, 229, 255, 0.55)';
        this.ctx.lineWidth = 1.0;
        this.ctx.shadowBlur = 0;
        for (let s = 1; s <= steps; s++) {
          const t = s / (steps + 1);
          const px = xStart + (xEnd - xStart) * t;
          const py = yStart + (yEnd - yStart) * t;
          const tickLen = 3.5 * dis;
          const nx = -sinA * tickLen;
          const ny = cosA * tickLen;
          this.ctx.beginPath();
          this.ctx.moveTo(px - nx, py - ny);
          this.ctx.lineTo(px + nx, py + ny);
          this.ctx.stroke();
        }
      }
      this.ctx.restore();
    }

    // ── 3. Cardinal Sliding Caliper Brackets [ + ] (Explodes Outward) ──
    this.ctx.save();
    for (let i = 0; i < 4; i++) {
      const angle = (i * Math.PI) / 2 + (dis > 0.01 ? this.angleOuter * 0.15 : this.angleOuter);
      const kx = cx + Math.cos(angle) * rCalipers;
      const ky = cy + Math.sin(angle) * rCalipers;

      if (dis > 0.02) {
        // Exploded caliper bracket with precision targeting arms
        this.ctx.strokeStyle = '#00ffff';
        this.ctx.lineWidth = 1.6;
        this.ctx.shadowBlur = 10;
        this.ctx.shadowColor = '#00e5ff';

        const crossSize = 7 + 4.5 * dis;
        // Horizontal bar
        this.ctx.beginPath();
        this.ctx.moveTo(kx - crossSize, ky);
        this.ctx.lineTo(kx + crossSize, ky);
        this.ctx.stroke();
        // Vertical bar
        this.ctx.beginPath();
        this.ctx.moveTo(kx, ky - crossSize);
        this.ctx.lineTo(kx, ky + crossSize);
        this.ctx.stroke();

        // Corner bracket guards
        this.ctx.strokeStyle = '#00e5ff';
        this.ctx.lineWidth = 1.2;
        const b = crossSize + 4;
        this.ctx.strokeRect(kx - b, ky - b, b * 2, b * 2);
      } else {
        // Sleek compact cardinal tick marks
        const x1 = cx + Math.cos(angle) * (baseR + 4);
        const y1 = cy + Math.sin(angle) * (baseR + 4);
        const x2 = cx + Math.cos(angle) * (baseR - 6);
        const y2 = cy + Math.sin(angle) * (baseR - 6);
        this.ctx.strokeStyle = '#00ffff';
        this.ctx.lineWidth = 1.8;
        this.ctx.beginPath();
        this.ctx.moveTo(x1, y1);
        this.ctx.lineTo(x2, y2);
        this.ctx.stroke();
      }
    }
    this.ctx.restore();

    // ── 4. 3D Kinetic Outer Dial Ring (Pitch Gimbal Tilt + 72 Ticks) ──
    const pitch1 = 0.38 * dis;
    const roll1 = -0.22 * dis;
    this.draw3DGimbalRing(cx, cy, rOuter, pitch1, roll1, 0, (ox, oy, r) => {
      this.drawRing(ox, oy, r, 1.2, 'rgba(0, 180, 216, 0.45)');
      this.drawTickMarks(ox, oy, r, 72, 5 + 3 * dis, this.angleOuter, '#00e5ff', 18);

      // Cardinal degree labels when disassembled
      if (dis > 0.25) {
        this.ctx.save();
        this.ctx.fillStyle = 'rgba(0, 229, 255, 0.75)';
        this.ctx.font = '700 7px "JetBrains Mono", monospace';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        const degLabels = ['000°', '090°', '180°', '270°'];
        for (let d = 0; d < 4; d++) {
          const a = (d * Math.PI) / 2 + this.angleOuter;
          const lx = ox + Math.cos(a) * (r + 10);
          const ly = oy + Math.sin(a) * (r + 10);
          this.ctx.fillText(degLabels[d], lx, ly);
        }
        this.ctx.restore();
      }
    });

    // ── 5. Secondary Segmented Rotor with 3D Gimbal & Wobble (Counter-Rotating) ──
    const pitch2 = -0.40 * dis + Math.sin(this.gimbalWobble) * 0.08 * dis;
    const roll2 = 0.32 * dis;
    this.draw3DGimbalRing(cx, cy, rSegmented, pitch2, roll2, 0, (ox, oy, r) => {
      this.ctx.shadowBlur = 8;
      this.ctx.shadowColor = '#00e5ff';
      this.drawSegmentedArc(ox, oy, r, 2.8, 4, this.angleSegments, '#00e5ff', 0.28);
      this.ctx.shadowBlur = 0;
      this.drawSegmentedArc(ox, oy, r - 4, 1.2, 4, this.angleSegments, 'rgba(0, 229, 255, 0.55)', 0.40);
    });

    // ── 6. Fine Calibrated Dotted Gyroscopic Horizon Track ──
    const gyroWobble = Math.sin(this.pulsePhase * 0.7) * 0.25 * dis;
    this.draw3DGimbalRing(cx, cy, rDotted, gyroWobble, -gyroWobble * 0.8, 0, (ox, oy, r) => {
      this.drawRing(ox, oy, r, 1.0, 'rgba(0, 229, 255, 0.45)', [4, 6]);
    });

    // ── 7. Inner High-Speed Gyroscopic Rotor (36 Ticks + Dual Notch Rings) ──
    this.drawTickMarks(cx, cy, rInnerRotor, 36, 4 + 2 * dis, this.angleInner1, '#00ffff', 9);
    this.drawSegmentedArc(cx, cy, rInnerRotor, 1.8, 3, this.angleInner2, '#00e5ff', 0.30);
    this.drawRing(cx, cy, rInnerRotor - 5, 1.0, 'rgba(0, 229, 255, 0.35)');

    // ── 8. Exploded HUD Telemetry Leader Lines & Technical Callouts ──
    if (dis > 0.15) {
      this.ctx.save();
      const alpha = Math.min(1.0, (dis - 0.15) * 1.6);
      this.ctx.fillStyle = `rgba(0, 229, 255, ${alpha * 0.95})`;
      this.ctx.strokeStyle = `rgba(0, 229, 255, ${alpha * 0.55})`;
      this.ctx.lineWidth = 1.0;
      this.ctx.font = '600 8px "JetBrains Mono", monospace';

      // Top-Right Leader Line: Expansion + Z-Axis Displacement
      const aTR = -Math.PI / 4;
      const xTR = cx + Math.cos(aTR) * rOuter;
      const yTR = cy + Math.sin(aTR) * rOuter;
      this.ctx.beginPath();
      this.ctx.moveTo(xTR, yTR);
      this.ctx.lineTo(xTR + 20, yTR - 20);
      this.ctx.lineTo(xTR + 80, yTR - 20);
      this.ctx.stroke();
      this.ctx.fillText(`EXP: +${(dis * 48.0).toFixed(1)}mm`, xTR + 22, yTR - 24);
      this.ctx.fillText(`Z-AXIS: +${(dis * 16.5).toFixed(1)}mm`, xTR + 22, yTR - 12);

      // Bottom-Left Leader Line: Core Plasma Flux & Frequency
      const aBL = (3 * Math.PI) / 4;
      const xBL = cx + Math.cos(aBL) * (coreR + 6);
      const yBL = cy + Math.sin(aBL) * (coreR + 6);
      this.ctx.beginPath();
      this.ctx.moveTo(xBL, yBL);
      this.ctx.lineTo(xBL - 20, yBL + 20);
      this.ctx.lineTo(xBL - 80, yBL + 20);
      this.ctx.stroke();
      this.ctx.textAlign = 'right';
      const fluxVal = (96.2 + 3.8 * Math.sin(this.pulsePhase)).toFixed(1);
      this.ctx.fillText(`CORE FLUX: ${fluxVal}%`, xBL - 22, yBL + 16);
      this.ctx.fillText(`FREQ: 142.8 HZ // 3D GIMBAL`, xBL - 22, yBL + 28);

      // Top-Left Leader Line: 3D Gimbal Pitch & Roll Metrics
      const aTL = (-3 * Math.PI) / 4;
      const xTL = cx + Math.cos(aTL) * rSegmented;
      const yTL = cy + Math.sin(aTL) * rSegmented;
      this.ctx.beginPath();
      this.ctx.moveTo(xTL, yTL);
      this.ctx.lineTo(xTL - 18, yTL - 18);
      this.ctx.lineTo(xTL - 75, yTL - 18);
      this.ctx.stroke();
      this.ctx.textAlign = 'right';
      this.ctx.fillText(`GIMBAL-3D: [P:${(dis * 22).toFixed(0)}° R:${(-dis * 16).toFixed(0)}°]`, xTL - 20, yTL - 22);

      this.ctx.restore();
    }

    // ── 9. Reactor Core Boundary with Audio-Reactive Plasma Petals ──
    this.ctx.save();
    this.ctx.shadowBlur = 12;
    this.ctx.shadowColor = '#00e5ff';
    this.drawRing(cx, cy, coreR, 2.8, '#00e5ff');
    this.ctx.restore();

    // Audio-reactive spectrum waveform petals around the core
    if (this.smoothedAudioLevel > 0.04 || this.state === 'speaking' || this.state === 'listening') {
      this.ctx.save();
      this.ctx.strokeStyle = '#00ffff';
      this.ctx.lineWidth = 1.6;
      this.ctx.shadowBlur = 8;
      this.ctx.shadowColor = '#00e5ff';
      const petals = 28;
      for (let i = 0; i < petals; i++) {
        const a = (i * 2 * Math.PI) / petals + this.angleInner2;
        const freqByte = this.audioData[i % 32] || 0;
        const waveAmp = (freqByte > 0 ? freqByte * 0.16 : this.smoothedAudioLevel * 22.0) + 2.0;
        const x1 = cx + Math.cos(a) * coreR;
        const y1 = cy + Math.sin(a) * coreR;
        const x2 = cx + Math.cos(a) * (coreR + waveAmp);
        const y2 = cy + Math.sin(a) * (coreR + waveAmp);
        this.ctx.beginPath();
        this.ctx.moveTo(x1, y1);
        this.ctx.lineTo(x2, y2);
        this.ctx.stroke();
      }
      this.ctx.restore();
    }

    // ── 10. Inner Reactor Core Plasma Hub & Well ──
    const innerCoreGrad = this.ctx.createRadialGradient(cx, cy, 2, cx, cy, coreR * 0.88);
    innerCoreGrad.addColorStop(0, '#00e5ff');
    innerCoreGrad.addColorStop(0.35, 'rgba(0, 180, 216, 0.85)');
    innerCoreGrad.addColorStop(0.70, theme.core || '#002733');
    innerCoreGrad.addColorStop(1, 'rgba(1, 10, 18, 0.95)');
    this.ctx.fillStyle = innerCoreGrad;
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, coreR * 0.88, 0, Math.PI * 2);
    this.ctx.fill();

    // Inner containment ring
    this.drawRing(cx, cy, coreR * 0.72, 1.0, 'rgba(0, 229, 255, 0.40)');

    // ── 11. Holographic J.A.R.V.I.S. Typography in Electric Neon Cyan ──
    this.ctx.save();
    this.ctx.shadowColor = '#00e5ff';
    this.ctx.shadowBlur = 16;
    this.ctx.fillStyle = '#00ffff';
    this.ctx.font = '900 13px "JetBrains Mono", "Segoe UI", sans-serif';
    this.ctx.textAlign = 'center';
    this.ctx.textBaseline = 'middle';
    this.ctx.letterSpacing = '3.5px';
    this.ctx.fillText('J.A.R.V.I.S.', cx, cy - 2);

    // Glowing Technical Operational State Indicator below center
    this.ctx.font = '700 8.5px "JetBrains Mono", "Segoe UI", monospace';
    this.ctx.fillStyle = '#00e5ff';
    this.ctx.shadowBlur = 8;
    this.ctx.letterSpacing = '1.8px';
    this.ctx.fillText(this.stateText, cx, cy + 15);

    // Subtle state indicator dot
    this.ctx.fillStyle = '#ffffff';
    this.ctx.shadowColor = '#00ffff';
    this.ctx.shadowBlur = 6;
    this.ctx.beginPath();
    this.ctx.arc(cx - (this.ctx.measureText(this.stateText).width / 2) - 6, cy + 15, 1.8, 0, Math.PI * 2);
    this.ctx.fill();

    this.ctx.restore();

    // ── 12. Reassembly Lock Snap Kinetic Energy Shockwave Pulse (Rose UI) ──
    if (this.lockPulse > 0.01) {
      this.ctx.save();
      const p = this.lockPulse;
      // High-speed expanding neon cyan shockwave collar
      const pulseR = baseR * (1.0 + (1.0 - p) * 0.50);
      this.drawRing(cx, cy, pulseR, 2.8 * p, `rgba(0, 255, 255, ${p * 0.95})`);

      // Core electric flash
      const flashGrad = this.ctx.createRadialGradient(cx, cy, 2, cx, cy, baseR * 0.75);
      flashGrad.addColorStop(0, `rgba(255, 255, 255, ${p * 0.85})`);
      flashGrad.addColorStop(0.35, `rgba(0, 229, 255, ${p * 0.55})`);
      flashGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
      this.ctx.fillStyle = flashGrad;
      this.ctx.beginPath();
      this.ctx.arc(cx, cy, baseR * 0.75, 0, Math.PI * 2);
      this.ctx.fill();
      this.ctx.restore();
    }

    requestAnimationFrame(this.animate);
  }
}

window.JarvisOrb = JarvisOrb;
