/**
 * J.A.R.V.I.S. Holographic Reactive HUD Orb Engine
 * Precision vector & canvas rendering of the multi-ring concentric holographic reactor.
 * Supports 9 reactive operational states and real-time Web Audio API frequency reactivity.
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

    // Rotation angles
    this.angleOuter = 0;
    this.angleInner1 = 0;
    this.angleInner2 = 0;
    this.angleSegments = 0;
    this.pulsePhase = 0;

    // Audio reactivity
    this.analyser = null;
    this.audioData = new Uint8Array(64);
    this.audioLevel = 0;

    // Palette per state
    this.colorSchemes = {
      idle: {
        primary: '#00e5ff',
        secondary: '#00838f',
        accent: '#e0f7fa',
        glow: 'rgba(0, 229, 255, 0.45)',
        core: '#006064',
      },
      listening: {
        primary: '#00ffff',
        secondary: '#0288d1',
        accent: '#ffffff',
        glow: 'rgba(0, 255, 255, 0.85)',
        core: '#00838f',
      },
      thinking: {
        primary: '#38bdf8',
        secondary: '#6366f1',
        accent: '#c084fc',
        glow: 'rgba(99, 102, 241, 0.65)',
        core: '#1e1b4b',
      },
      speaking: {
        primary: '#22d3ee',
        secondary: '#06b6d4',
        accent: '#ffffff',
        glow: 'rgba(34, 211, 238, 0.8)',
        core: '#083344',
      },
      executing: {
        primary: '#f59e0b',
        secondary: '#06b6d4',
        accent: '#fbbf24',
        glow: 'rgba(245, 158, 11, 0.7)',
        core: '#451a03',
      },
      waiting_for_approval: {
        primary: '#fbbf24',
        secondary: '#d97706',
        accent: '#fef08a',
        glow: 'rgba(251, 191, 36, 0.85)',
        core: '#78350f',
      },
      error: {
        primary: '#ef4444',
        secondary: '#dc2626',
        accent: '#fca5a5',
        glow: 'rgba(239, 68, 68, 0.85)',
        core: '#450a0a',
      },
      paused: {
        primary: '#f59e0b',
        secondary: '#78716c',
        accent: '#fde68a',
        glow: 'rgba(120, 113, 108, 0.4)',
        core: '#292524',
      },
      offline: {
        primary: '#64748b',
        secondary: '#334155',
        accent: '#94a3b8',
        glow: 'rgba(100, 116, 139, 0.2)',
        core: '#0f172a',
      },
    };

    this.animate = this.animate.bind(this);
    requestAnimationFrame(this.animate);
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
      // Simulated audio waveform pulse if Web Audio not connected
      this.audioLevel = 0.2 + 0.3 * Math.sin(this.pulsePhase * 4) + 0.15 * Math.cos(this.pulsePhase * 7);
    } else {
      this.audioLevel = 0;
    }
  }

  drawRing(cx, cy, radius, width, color, dash = []) {
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, Math.max(0, radius), 0, Math.PI * 2);
    this.ctx.lineWidth = width;
    this.ctx.strokeStyle = color;
    this.ctx.setLineDash(dash);
    this.ctx.stroke();
    this.ctx.setLineDash([]);
  }

  drawTickMarks(cx, cy, radius, count, tickLength, angleOffset, color) {
    this.ctx.strokeStyle = color;
    this.ctx.lineWidth = 1.2;
    for (let i = 0; i < count; i++) {
      const angle = (i * 2 * Math.PI) / count + angleOffset;
      const x1 = cx + Math.cos(angle) * radius;
      const y1 = cy + Math.sin(angle) * radius;
      const x2 = cx + Math.cos(angle) * (radius - tickLength);
      const y2 = cy + Math.sin(angle) * (radius - tickLength);
      this.ctx.beginPath();
      this.ctx.moveTo(x1, y1);
      this.ctx.lineTo(x2, y2);
      this.ctx.stroke();
    }
  }

  drawSegmentedArc(cx, cy, radius, width, segments, angleOffset, color) {
    this.ctx.strokeStyle = color;
    this.ctx.lineWidth = width;
    const arcLen = (2 * Math.PI) / segments;
    const pad = arcLen * 0.32;
    for (let i = 0; i < segments; i++) {
      const start = i * arcLen + angleOffset;
      const end = start + arcLen - pad;
      this.ctx.beginPath();
      this.ctx.arc(cx, cy, radius, start, end);
      this.ctx.stroke();
    }
  }

  animate() {
    this.ctx.clearRect(0, 0, this.width, this.height);
    const cx = this.width / 2;
    const cy = this.height / 2;
    const baseR = Math.min(cx, cy) * 0.88;
    const theme = this.colorSchemes[this.state] || this.colorSchemes.idle;

    this.updateAudioLevel();

    // Rotation speeds based on state
    let speedMult = 1.0;
    if (this.state === 'listening') speedMult = 1.8;
    else if (this.state === 'thinking') speedMult = 3.2;
    else if (this.state === 'speaking') speedMult = 1.6;
    else if (this.state === 'paused' || this.state === 'offline') speedMult = 0.08;

    this.angleOuter += 0.005 * speedMult;
    this.angleInner1 -= 0.009 * speedMult;
    this.angleInner2 += 0.014 * speedMult;
    this.angleSegments -= 0.007 * speedMult;
    this.pulsePhase += 0.04;

    const dynamicPulse = Math.sin(this.pulsePhase) * 2.5 + this.audioLevel * 14;

    // ── 1. Deep Core Ambient Glow ──
    const grad = this.ctx.createRadialGradient(cx, cy, baseR * 0.1, cx, cy, baseR * 1.15);
    grad.addColorStop(0, theme.glow);
    grad.addColorStop(0.5, theme.glow.replace(/[\d\.]+\)$/, '0.12)'));
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    this.ctx.fillStyle = grad;
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, baseR * 1.15, 0, Math.PI * 2);
    this.ctx.fill();

    // ── 2. Outer Precision Ring with 72 Ticks ──
    this.drawRing(cx, cy, baseR, 1.2, theme.secondary);
    this.drawTickMarks(cx, cy, baseR, 72, 5, this.angleOuter, theme.primary);

    // ── 3. Four Major Cardinal Markers ──
    this.drawTickMarks(cx, cy, baseR + 4, 4, 10, this.angleOuter, theme.accent);

    // ── 4. Secondary Counter-Rotating Segmented Arcs ──
    this.drawSegmentedArc(cx, cy, baseR * 0.86 + dynamicPulse * 0.3, 2.5, 4, this.angleSegments, theme.primary);

    // ── 5. Fine Calibrated Dotted Track ──
    this.drawRing(cx, cy, baseR * 0.74, 1.0, theme.secondary, [4, 6]);

    // ── 6. Inner Fast Gyroscopic Ring (36 Ticks) ──
    this.drawTickMarks(cx, cy, baseR * 0.62, 36, 4, this.angleInner1, theme.primary);
    this.drawSegmentedArc(cx, cy, baseR * 0.62, 1.5, 3, this.angleInner2, theme.accent);

    // ── 7. Reactor Core Boundary with Audio-Reactive Pulse ──
    const coreR = Math.max(12, baseR * 0.44 + dynamicPulse);
    this.drawRing(cx, cy, coreR, 2.8, theme.primary);

    // Audio Waveform Petals around core when active
    if (this.audioLevel > 0.05) {
      this.ctx.strokeStyle = theme.accent;
      this.ctx.lineWidth = 1.6;
      const petals = 24;
      for (let i = 0; i < petals; i++) {
        const a = (i * 2 * Math.PI) / petals + this.angleInner2;
        const waveAmp = (this.audioData[i % 32] || (this.audioLevel * 180)) * 0.12;
        const x1 = cx + Math.cos(a) * coreR;
        const y1 = cy + Math.sin(a) * coreR;
        const x2 = cx + Math.cos(a) * (coreR + waveAmp + 4);
        const y2 = cy + Math.sin(a) * (coreR + waveAmp + 4);
        this.ctx.beginPath();
        this.ctx.moveTo(x1, y1);
        this.ctx.lineTo(x2, y2);
        this.ctx.stroke();
      }
    }

    // ── 8. Inner Reactor Hub Circle ──
    const innerCoreGrad = this.ctx.createRadialGradient(cx, cy, 2, cx, cy, coreR * 0.85);
    innerCoreGrad.addColorStop(0, theme.primary);
    innerCoreGrad.addColorStop(0.7, theme.core);
    innerCoreGrad.addColorStop(1, 'rgba(0,0,0,0.85)');
    this.ctx.fillStyle = innerCoreGrad;
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, coreR * 0.85, 0, Math.PI * 2);
    this.ctx.fill();

    // ── 9. Holographic J.A.R.V.I.S. Typography ──
    this.ctx.save();
    this.ctx.shadowColor = theme.primary;
    this.ctx.shadowBlur = 12;
    this.ctx.fillStyle = '#ffffff';
    this.ctx.font = '700 13px "Segoe UI", Inter, sans-serif';
    this.ctx.textAlign = 'center';
    this.ctx.textBaseline = 'middle';
    this.ctx.letterSpacing = '3px';
    this.ctx.fillText('J.A.R.V.I.S.', cx, cy - 2);

    // Technical State Indicator below center
    this.ctx.font = '600 8.5px "Segoe UI", Inter, sans-serif';
    this.ctx.fillStyle = theme.accent;
    this.ctx.shadowBlur = 6;
    this.ctx.fillText(this.stateText, cx, cy + 15);
    this.ctx.restore();

    requestAnimationFrame(this.animate);
  }
}

window.JarvisOrb = JarvisOrb;
