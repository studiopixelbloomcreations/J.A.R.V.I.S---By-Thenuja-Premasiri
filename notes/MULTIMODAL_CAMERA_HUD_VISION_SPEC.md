# Multimodal Camera HUD Vision, Bounding Boxes, Target Tracking & Clear Command Specification
**Reference Video**: `Download (4).mp4` (57.54s, 576x1024 portrait capture of 16:9 widescreen desk environment)  
**System Target**: 1:1 Rose-to-Jarvis Cyan Port (`#00e5ff`)  
**Author**: @video-analyst-5  

---

## 1. Overview & Scene Architecture
In `Download (4).mp4`, Huw Prosser demonstrates the multimodal computer vision mode of the Rose HUD:
1. **Initial Idle State (00:00 - 00:09)**:
   - Exploded kinetic orb resides in the screen center.
   - Top HUD bar displays navigation pills.
   - Bottom-left HUD displays live audio decibel meter and streaming voice transcript bar.
   - Physical desk features an overhead camera mounted pointing down at an A3/A2 cutting mat, mechanical keyboard, small decorative pumpkin, coffee cup, and accessories.
2. **Vision Activation Transition (00:10 - 00:14)**:
   - Voice trigger: *"Good morning, Rose. I've got something for you."*
   - Kinetic orb shrinks from full size (~380px) to docked corner badge (~88-96px) and glides to the bottom-right corner over `1.2s cubic-bezier(0.16, 1, 0.3, 1)`.
   - A glowing horizontal laser scanline splits horizontally across the display and expands open, revealing the live overhead camera feed.
   - Background camera feed has subtle CRT scanline texturing (tactical sci-fi aesthetic).
3. **Target Tracking & Bounding Boxes (00:22 - 00:46)**:
   - HUD vision engine locks onto detected objects in the camera feed:
     - Target 1: `[PUMPKIN]` (center object on cutting mat)
     - Target 2: `[KEYBOARD]` (Keychron mechanical keyboard)
     - Target 3: `[COFFEE CUP]` (white ceramic mug with latte art on right)
     - Target 4: `[PHONE]` / device (left accessory)
   - Bounding boxes feature neon borders, subtle semi-transparent background tinting, and uppercase monospace label tabs attached to the top-left edge.
4. **Natural Language Clear / Target Isolation (00:47 - 00:52)**:
   - Voice command transcribed on bottom-left HUD: *"Yeah, that's right. Clear out everything other than the pumpkin."*
   - Non-target bounding boxes (`KEYBOARD`, `COFFEE CUP`, `PHONE`) smoothly fade out with a slight scale reduction over `0.25s`.
   - The isolated target (`PUMPKIN`) retains its active lock and bounding box.
   - Clicking `[CLEAR VIEW]` in the top HUD instantly clears all active bounding boxes and resets vision state.

---

## 2. Top Navigation Bar (HUD Pills)

### Layout & Placement
- **Position**: `fixed`, `top: 16px`, `right: 24px` (or flex-right layout)
- **Container**: Flex row, `gap: 8px`, `align-items: center`, `z-index: 1000`

### Design Tokens & Button Styling
```css
.hud-pill-button {
  height: 28px;
  padding: 0 12px;
  background: rgba(10, 16, 26, 0.75);
  border: 1px solid rgba(0, 229, 255, 0.35);
  border-radius: 3px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  color: #e2e8f0;
  cursor: pointer;
  backdrop-filter: blur(12px);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.hud-pill-button:hover {
  border-color: #00e5ff;
  color: #00e5ff;
  box-shadow: 0 0 10px rgba(0, 229, 255, 0.35);
}

/* Active Camera Toggle Pill (matches Rose solid red -> Jarvis solid cyan) */
.hud-pill-button.active-camera {
  background: #00e5ff;
  border-color: #00ffff;
  color: #030712;
  font-weight: 700;
  box-shadow: 0 0 14px rgba(0, 229, 255, 0.65);
}

.camera-source-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 1px;
  color: rgba(226, 232, 240, 0.55);
  text-transform: uppercase;
  margin-left: 4px;
}
```

### Exact Navigation Controls Sequence
1. `[HISTORY]`: Opens past query and session log drawer.
2. `[TIDY]`: Auto-arranges / re-docks open HUD cards and widgets.
3. `[CLEAR VIEW]`: Immediate clear trigger — wipes all active vision bounding boxes, resets detection filters, and clears temporary HUD overlays.
4. `[CAMERA ON / CAMERA OFF]`: Primary camera toggle. When active, solid neon cyan `#00e5ff` with dark text `#030712`.
5. `CAMERA SOURCE`: Inline sub-label preceding source picker.
6. `[DEFAULT TOP CAMERA 2.5K ▼]`: Camera input selector dropdown (selects between USB webcams, overhead desk cameras, Obsbot Tail, etc.).
7. `[SCREENGRABBER]`: Toggle to switch vision input from camera to active screen capture stream.

---

## 3. Multimodal Camera Vision Layer

### Layer Structure
- **Video Canvas / Element**: Full-screen or viewport container pinned at `z-index: 10`, behind holographic HUD elements (`z-index: 100+`).
- **Aspect Ratio**: Fits display container or maintains native camera aspect ratio (16:9 / 4:3).
- **Scanline & CRT Holographic Overlay**:
```css
.vision-crt-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: repeating-linear-gradient(
    0deg,
    rgba(0, 0, 0, 0.16) 0px,
    rgba(0, 0, 0, 0.16) 1px,
    transparent 1px,
    transparent 2px
  );
  z-index: 15;
}

.vision-vignette {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: radial-gradient(circle at center, transparent 45%, rgba(3, 7, 18, 0.65) 100%);
  z-index: 16;
}
```

### Activation Laser Sweep Animation
When vision mode activates:
1. Orb glides from screen center to bottom-right corner:
   - Duration: `1.2s`
   - Timing function: `cubic-bezier(0.16, 1, 0.3, 1)`
   - Scale: `1.0` -> `0.25` (~380px -> ~92px)
2. Laser Scanline Wipe:
   - A bright cyan laser line (`height: 2px`, `background: #00ffff`, `box-shadow: 0 0 15px #00e5ff, 0 0 35px #00e5ff`) sweeps across the screen vertically or expands horizontally from center in `0.6s`.
   - The camera layer fades in from `opacity: 0` to `opacity: 1` as the wipe completes.

---

## 4. Target Tracking Bounding Boxes & Brackets

### Coordinate System & Structure
The tracking overlay is rendered on an SVG or absolute-positioned DIV overlay directly matching the video stream dimensions:

```html
<div class="hud-target-box" style="top: 240px; left: 320px; width: 140px; height: 120px;">
  <div class="hud-target-tab">PUMPKIN</div>
  <div class="hud-target-corner tl"></div>
  <div class="hud-target-corner tr"></div>
  <div class="hud-target-corner bl"></div>
  <div class="hud-target-corner br"></div>
</div>
```

### CSS Specifications (Jarvis Cyan Port)
```css
.hud-target-box {
  position: absolute;
  border: 1.5px solid #00e5ff;
  background: rgba(0, 229, 255, 0.06);
  box-shadow: 0 0 12px rgba(0, 229, 255, 0.4), inset 0 0 8px rgba(0, 229, 255, 0.12);
  transition: opacity 0.25s cubic-bezier(0.16, 1, 0.3, 1),
              transform 0.25s cubic-bezier(0.16, 1, 0.3, 1),
              top 0.1s linear, left 0.1s linear, width 0.1s linear, height 0.1s linear;
  pointer-events: none;
}

/* Header Label Tab */
.hud-target-tab {
  position: absolute;
  top: -18px;
  left: -1.5px;
  height: 18px;
  padding: 0 8px;
  background: #00e5ff;
  color: #030712;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  border-radius: 2px 2px 0 0;
  box-shadow: 0 0 8px rgba(0, 229, 255, 0.5);
  white-space: nowrap;
}

/* Optional Tactical Corner L-Brackets */
.hud-target-corner {
  position: absolute;
  width: 8px;
  height: 8px;
  border-color: #00ffff;
}
.hud-target-corner.tl { top: -2px; left: -2px; border-top: 2px solid; border-left: 2px solid; }
.hud-target-corner.tr { top: -2px; right: -2px; border-top: 2px solid; border-right: 2px solid; }
.hud-target-corner.bl { bottom: -2px; left: -2px; border-bottom: 2px solid; border-left: 2px solid; }
.hud-target-corner.br { bottom: -2px; right: -2px; border-bottom: 2px solid; border-right: 2px solid; }

/* Removal / Clear Animation */
.hud-target-box.clearing {
  opacity: 0;
  transform: scale(0.96);
}

/* Isolated Target Lock Highlight */
.hud-target-box.locked-focus {
  border-color: #00ffff;
  box-shadow: 0 0 20px rgba(0, 229, 255, 0.8), inset 0 0 14px rgba(0, 229, 255, 0.25);
  animation: hudPulse 2s infinite ease-in-out;
}

@keyframes hudPulse {
  0%, 100% { box-shadow: 0 0 14px rgba(0, 229, 255, 0.6); }
  50% { box-shadow: 0 0 24px rgba(0, 229, 255, 0.95); }
}
```

---

## 5. Voice & Clear Command Mechanics

### Voice Commands Identified in Reference Video
1. **Activation**:
   - `"Good morning, Rose. I've got something for you."`
   - Trigger: Activates vision mode, glides orb to corner, and enables camera stream.
2. **Detection & Labeling**:
   - HUD vision engine automatically attaches tracking brackets to prominent desk objects: `KEYBOARD`, `PUMPKIN`, `COFFEE CUP`, `PHONE`.
3. **Filtering & Isolation**:
   - User command: `"Yeah, that's right. Clear out everything other than the pumpkin."`
   - Parser logic:
     - Identifies target keyword: `pumpkin`
     - Matches against tracked labels: keeps `PUMPKIN`
     - Filters out non-matching targets: `KEYBOARD`, `COFFEE CUP`, `PHONE`
     - Applies `.clearing` class (`opacity: 0; transform: scale(0.96)`) to non-matching boxes over `250ms`, then removes them from DOM.
     - Adds `.locked-focus` to `PUMPKIN`.
4. **Full Clear Trigger**:
   - Voice: `"Clear HUD"`, `"Clear view"`, `"Reset vision"`
   - UI: Clicking `[CLEAR VIEW]` pill in top navigation.
   - Action: Clears all boxes, returns orb to center if no other cards exist, or resets tracking state.

---

## 6. Bottom-Left Telemetry & Audio Bar

### Components
- **Audio dB Meter**:
  - Format: `-45.0 dB` (live real-time Web Audio API Analyser decibel readout).
  - Dynamic micro-bar level visualizer: 12px height, cyan bar height proportional to rms/dB.
- **Speaker Pill Tag**:
  - `[YOU]`: 1px cyan border, dark background, 10px monospace uppercase.
- **Streaming Transcription Line**:
  - Real-time text display showing incoming speech-to-text tokens.
  - Font: `JetBrains Mono` / `Inter`, 13px, color `#e2e8f0`.
  - Position: `bottom: 18px, left: 24px`, sitting directly on the HUD margin.

---

## 7. Complete Color & Timing Mapping (Rose -> Jarvis)

| UI Element | Rose UI Reference | Jarvis Cyan Port | Timing / Curve |
| :--- | :--- | :--- | :--- |
| **HUD Theme Accent** | Crimson Red (`#ff0033` / `#ff3b30`) | Electric Neon Cyan (`#00e5ff` / `#00ffff`) | Instant / CSS Token |
| **Pill Background** | `rgba(18, 12, 16, 0.8)` | `rgba(10, 16, 26, 0.75)` | 200ms ease |
| **Pill Border** | `1px solid rgba(255, 59, 48, 0.3)` | `1px solid rgba(0, 229, 255, 0.35)` | 200ms ease |
| **Active Camera Pill** | Solid Red (`#e53935`), White Text | Solid Cyan (`#00e5ff`), Dark Text (`#030712`) | 200ms cubic-bezier |
| **Bounding Box Outline** | `1.5px solid #ff3b30` | `1.5px solid #00e5ff` | 100ms tracking |
| **Bounding Box Fill** | `rgba(255, 0, 50, 0.08)` | `rgba(0, 229, 255, 0.06)` | Constant |
| **Label Tab Background** | Solid Red (`#ff3b30`) | Solid Cyan (`#00e5ff`) | Constant |
| **Label Tab Text** | White (`#ffffff`), 10px Monospace | Dark Navy (`#030712`), 10px Monospace | Constant |
| **Laser Scanline Sweep** | Red 2px beam, glow `0 0 15px #ff3b30` | Cyan 2px beam, glow `0 0 18px #00ffff` | 600ms linear |
| **Orb Corner Glide** | Center -> Bottom-Right (88px) | Center -> Bottom-Right (88px) | 1200ms cubic-bezier(0.16, 1, 0.3, 1) |
| **Target Clear Fade** | Opacity 1 -> 0, scale 1.0 -> 0.96 | Opacity 1 -> 0, scale 1.0 -> 0.96 | 250ms ease-out |
