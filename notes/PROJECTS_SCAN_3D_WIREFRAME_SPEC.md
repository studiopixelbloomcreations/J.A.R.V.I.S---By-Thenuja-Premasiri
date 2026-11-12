# Reference Analysis: Download (3).mp4 (Huw Prosser Rose UI -> Jarvis Cyan 1:1 Port)
**Slice**: Projects Scan, Folder Inspection HUD Card, and 3D Wireframe Preview Modal

---

## 1. Executive Summary & Scene Breakdown
- **Source Video**: `Download (3).mp4` (28.68s, 30fps, 576x1024 native 9:16 vertical recording of Huw Prosser's dual-monitor workstation).
- **Workstation Layout**:
  - **Left Screen (Main Display)**: Ultrawide / 16:9 Dell monitor running the fullscreen holographic Rose UI web application with top navigation pills, central exploded orb, and dynamic floating HUD cards.
  - **Right Screen (Vertical Display)**: Portrait monitor running VS Code with terminal prompt (`zsh`, branch `main`) and modified file trees including `system.py`, `scanner.py`, `commands.py`, `city.blend/blender`, `rendering/lighting/public/lighting`, `plugin.py`, and `settings.py`.
- **Audio Transcript & Dialogue Timeline**:
  - `00:00 - 00:04`: **User Query 1**: *"What is the largest folder inside of Desktop/projects?"*
  - `00:04 - 00:06`: **Rose AI Response 1** (British female voice): *"One sec. On it boss. Measuring the lot in there. Sizes per project, biggest wins. I'll come back with the name and the weight."*
  - `00:06.0 - 00:06.8`: **Orb Docking**: The central exploded orb smoothly glides to the bottom-right corner and scales down to docked size (`0.50x`).
  - `00:06.8 - 00:18.0`: **Folder Inspection HUD Card Reveal**: Holographic card fades and scales in at left-center (`top: 30%`, `left: 14%`). Displays real-time directory scanning stream with file sizes, timestamps, and synthesized summary.
  - `00:18.5 - 00:22.0`: **User Query 2**: *"Great, and can you show me a 3D model of a dog?"*
  - `00:22.0 - 00:23.5`: **Rose AI Response 2**: *"Checking..."*
  - `00:24.5 - 00:28.0`: **3D Wireframe Preview Modal Pop**: Next to the folder inspection card, a 3D wireframe preview modal pops open (`top: 26%`, `left: 52%`). An abstract glowing Trefoil Torus Knot wireframe mesh rotates continuously in WebGL space instead of a dog.
  - `00:28.0 - 00:28.68`: **User Punchline**: *"That is not a dog."* (workstation cut).

---

## 2. Pillar 1: Orb Kinetics & Docking Behavior
### Visual & Kinematic Specifications:
1. **Initial Idle State (00:00 - 00:06)**:
   - **Position**: Dead center `left: 50%; top: 50%; transform: translate(-50%, -50%)`.
   - **Diameter**: ~240px - 260px.
   - **Rotation**: Dual counter-rotating 3D exploded rings (outer ring counter-clockwise at ~18s/rev, inner ring clockwise at ~12s/rev).
   - **Core Label**: Central typography `"ROSE"` (in Jarvis port: `"J.A.R.V.I.S."` in electric cyan `#00e5ff`).

2. **Glide-to-Dock Animation (00:06.0 - 00:06.8)**:
   - **Duration**: `800ms`.
   - **Timing Function**: `cubic-bezier(0.16, 1.0, 0.3, 1.0)` (ultra-smooth ease-out deceleration with no overshoot).
   - **Dock Target Coordinates**:
     - `bottom: 35px; right: 35px;` (or `transform: translate(calc(50vw - 140px), calc(50vh - 140px)) scale(0.48)`).
   - **Scale Reduction**: `1.0 -> 0.48` (orb ring diameter scales from ~250px to ~120px).
   - **Z-Index**: `z-index: 50` (stays floating above background grid, non-obscuring HUD cards).
   - **Undocking Trigger**: Returns to center screen upon `[CLEAR HUD]`, speech `clear/dismiss`, or report card close.

---

## 3. Pillar 2: Folder Inspection HUD Card (`projects scan`)
### Visual Styling & Anatomy:
- **Card Placement**:
  - Floating left-center: `top: 30%; left: 14%;` (relative to viewport).
  - Dimensions: `width: 440px; min-height: 290px;`.
- **Card Framing & Glassmorphism**:
  - Background: `rgba(6, 14, 26, 0.88)` with `backdrop-filter: blur(14px)`.
  - Border: Thin 1px solid `rgba(0, 229, 255, 0.38)`.
  - Corner Brackets: Crisp 10px L-accents on all 4 corners (`border-top: 2px solid #00e5ff; border-left: 2px solid #00e5ff;`, etc.).
  - Scanline Texture: Faint 2px horizontal scanlines (`repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0, 229, 255, 0.03) 3px)`).
  - Outer Glow: `box-shadow: 0 8px 32px rgba(0, 0, 0, 0.65), 0 0 16px rgba(0, 229, 255, 0.18)`.

### Header Bar Anatomy:
- **Top Header Line**:
  - Left Title: `SCAN // DIR: ~/DESKTOP/PROJECTS`
    - Font: Monospace (`'JetBrains Mono'`, `'Fira Code'`, `'Courier New'`), `font-size: 11px; font-weight: 700; letter-spacing: 1.6px; color: #00e5ff;`.
  - Right Status Badge:
    - Initial state: Amber badge `[ SCANNING... ]` with blinking dot (`color: #ffaa00; background: rgba(255, 170, 0, 0.15); border: 1px solid rgba(255, 170, 0, 0.5)`).
    - Completion state: Emerald/Cyan badge `[ 14 DIRS SCANNED ]` (`color: #00ffcc; background: rgba(0, 255, 204, 0.12); border: 1px solid rgba(0, 255, 204, 0.4)`).
  - Divider: 1px horizontal rule `rgba(0, 229, 255, 0.25)` across card width.

### Body Layout (Split Telemetry & Synthesis):
1. **Left Telemetry Log Stream**:
   - Monospace directory entries streamed line-by-line:
     ```text
     21:27:14  [ 4.8 GB]  project-alpha/
     21:27:15  [12.4 GB]  blender-renders/
     21:27:16  [18.9 GB]  unreal-assets/
     21:27:17  [24.1 GB]  dataset-archive/  ◄ MAX
     ```
   - Micro-bars / size meters: Horizontal progress bars showing relative disk usage per directory.
   - Text color: `#e2e8f0` for paths, `#00e5ff` for size badges, `#ffaa00` for the peak/largest directory.

2. **Right Natural Language Assistant Synthesis**:
   - Synthesized speech caption matching the spoken audio:
     ```text
     "Find the largest directory within Desktop/projects.
      Measuring sizes per project...
      Largest folder identified: 'dataset-archive' at 24.1 GB."
     ```
   - Typography: Clean sans-serif / monospace hybrid, `font-size: 12px; line-height: 1.6; color: rgba(240, 246, 252, 0.9);`.

3. **Bottom Micro-Status Bar**:
   - Micro-text: `ENTRIES: 14 | TOTAL: 60.2 GB | DISK: NVME-0 | SPEED: 1.4 GB/S`
   - Font: `9px monospace; color: rgba(0, 229, 255, 0.6); letter-spacing: 1.2px;`.

---

## 4. Pillar 3: 3D Wireframe Preview Modal (`torus knot modal`)
### Visual & Interactive Specifications:
- **Card Placement & Pop Timing**:
  - Pops at `00:24.5` following user voice query *"Can you show me a 3D model of a dog?"*.
  - Coordinates: Floating right-center `top: 24%; left: 52%;`.
  - Dimensions: `width: 410px; height: 320px;`.
  - Entrance Animation: `280ms cubic-bezier(0.16, 1.0, 0.3, 1.0)` scale fade (`transform: scale(0.92) -> scale(1.0); opacity: 0 -> 1;`).

### Modal Window Anatomy:
1. **Title Bar**:
   - Left Title: `MODEL // 3D - WIREFRAME [ACTIVE]` (or `MESH // TORUS-KNOT-01`).
   - Font: Monospace `10.5px`, bold, uppercase, `letter-spacing: 1.5px`, `#00e5ff`.
   - Right Controls:
     - `[ 🗖 EXPAND ]` / `[ ✕ CLOSE ]` micro-action buttons.
     - Dimensions: `height: 18px; padding: 0 6px; font-size: 9px; border: 1px solid rgba(0, 229, 255, 0.4); border-radius: 3px; color: #00e5ff;`.

2. **3D WebGL Viewport (Three.js Engine)**:
   - Geometry: **Trefoil Torus Knot**
     - Three.js constructor: `new THREE.TorusKnotGeometry(radius=1.8, tube=0.52, tubularSegments=128, radialSegments=32, p=2, q=3)`.
   - Material:
     - Luminous cyan wireframe shader:
       ```javascript
       new THREE.MeshBasicMaterial({
         color: 0x00e5ff,
         wireframe: true,
         transparent: true,
         opacity: 0.88
       })
       ```
     - Volumetric inner core glow: Secondary inner mesh or point light `new THREE.PointLight(0x00ffff, 2.5, 50)` giving intense bloom to intersecting loops.
   - 3-Axis Continuous Rotation Dynamics:
     ```javascript
     mesh.rotation.x += 0.008;
     mesh.rotation.y += 0.013;
     mesh.rotation.z += 0.005;
     ```
   - Interactive Orbit Drag:
     - Mouse drag / touch rotation allows the user to tilt, spin, and orbit the 3D wireframe freely.
     - Double click resets auto-rotation.

3. **Bottom Viewport Telemetry & Poly Count**:
   - Inside bottom-right corner overlay:
     `VERTS: 8,420 | POLYS: 16,840 | FPS: 60.0 | SHADER: GL_LINES`
   - Font: `9px monospace; color: rgba(0, 229, 255, 0.7); background: rgba(0, 10, 20, 0.6); padding: 2px 6px; border-radius: 2px;`.

---

## 5. Pillar 4: Top HUD Navigation Pills & System Telemetry
- **Top Navigation Bar (`top: 18px; right: 40px;`)**:
  - Horizontal flex pill group with 6px gap:
    1. `[PLAYLIST]` - Outline pill, rounded-full (`border-radius: 9999px; height: 26px; padding: 2px 14px; font-size: 10px; font-weight: 700; letter-spacing: 1.2px; border: 1px solid rgba(0, 229, 255, 0.45); color: #00e5ff;`).
    2. `[PLAY]` - Outline pill.
    3. `[CLEAR HUD]` - Outline pill. Resets all floating cards and un-docks orb back to center screen.
    4. `[SAVED]` - Outline pill.
    5. Telemetry divider dashes: `--- ---` (`color: rgba(0, 229, 255, 0.3); font-size: 12px; margin: 0 4px;`).
    6. `[REPORT: CARDS ▾]` - Dropdown selector pill with chevron.
    7. `[METADATA: DEFAULT ▾]` - Mode selector pill.
    8. `[FULLSCREEN]` - Square / pill window expander.
- **Active State Styling**:
  - Background: `rgba(0, 229, 255, 0.22)`.
  - Border: `1.5px solid #00e5ff`.
  - Text color: `#ffffff`.
  - Outer Glow: `box-shadow: 0 0 10px rgba(0, 229, 255, 0.6)`.

- **Bottom Status Telemetry Bar (`bottom: 12px; left: 30px;`)**:
  - Mic & Analyser Telemetry: `MIC: ON // L: -45.0 dB  R: -46.7 dB [● 24/7 REC]`
  - Audio VU meter bar: Dual horizontal micro-bars animating with live audio volume.

---

## 6. Motion Timings & Curve Summary
| Element / Action | Trigger | Start Time | Duration | Transition Curve | Start State | End State |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Orb Glide-to-Dock** | Assistant begins answer | `00:06.0` | `800ms` | `cubic-bezier(0.16, 1, 0.3, 1)` | Center `(50%, 50%)`, scale `1.0` | Bottom-Right `(R:35, B:35)`, scale `0.48` |
| **Folder Inspection Card Entrance** | Orb reaches dock | `00:06.8` | `400ms` | `cubic-bezier(0.16, 1, 0.3, 1)` | `opacity: 0; translateY(14px); scale(0.96)` | `opacity: 1; translateY(0); scale(1.0)` |
| **Directory Scan Rows Stagger** | Card mounted | `00:07.2` | `250ms/row` | `ease-out` | `opacity: 0; translateX(-8px)` | `opacity: 1; translateX(0)` |
| **3D Wireframe Modal Pop** | Speech *"show me 3D model"* | `00:24.5` | `320ms` | `cubic-bezier(0.16, 1, 0.3, 1)` | `opacity: 0; scale(0.92)` | `opacity: 1; scale(1.0)` |
| **3D Torus Knot Spin** | Three.js RAF Loop | `00:24.8` | Continuous | Linear loop | `rotX: 0, rotY: 0, rotZ: 0` | Smooth 3-axis precession |
| **Clear HUD / Reset** | `[CLEAR HUD]` pill / voice | Instant | `650ms` | `cubic-bezier(0.16, 1, 0.3, 1)` | Cards visible, orb docked | Cards fade out, orb glides to center `(50%, 50%)` |

---

## 7. Direct Implementation Blueprints for `viewer/index.html`

### A. Folder Inspection HUD Card HTML Template
```html
<!-- FOLDER INSPECTION HUD CARD -->
<div id="hud-folder-inspection-card" class="hud-holo-card" style="display: none; position: absolute; top: 28%; left: 12%; width: 440px; z-index: 40;">
  <div class="hud-card-header">
    <div class="hud-card-title"><span class="hud-accent">//</span> SCAN // DIR: ~/DESKTOP/PROJECTS</div>
    <div id="folder-scan-status-badge" class="hud-badge hud-badge-scanning">SCANNING...</div>
  </div>
  <div class="hud-card-divider"></div>
  <div class="hud-card-body" style="padding: 14px 16px;">
    <!-- Telemetry stream -->
    <div class="folder-scan-stream" style="font-family: 'JetBrains Mono', monospace; font-size: 11px; margin-bottom: 14px;">
      <div class="scan-row" style="display: flex; justify-content: space-between; margin-bottom: 6px;">
        <span style="color: #64748b;">21:27:14</span>
        <span style="color: #00e5ff; font-weight: bold;">[ 4.8 GB]</span>
        <span style="color: #cbd5e1; flex: 1; margin-left: 10px;">project-alpha/</span>
      </div>
      <div class="scan-row" style="display: flex; justify-content: space-between; margin-bottom: 6px;">
        <span style="color: #64748b;">21:27:15</span>
        <span style="color: #00e5ff; font-weight: bold;">[12.4 GB]</span>
        <span style="color: #cbd5e1; flex: 1; margin-left: 10px;">blender-renders/</span>
      </div>
      <div class="scan-row" style="display: flex; justify-content: space-between; margin-bottom: 6px;">
        <span style="color: #64748b;">21:27:16</span>
        <span style="color: #00e5ff; font-weight: bold;">[18.9 GB]</span>
        <span style="color: #cbd5e1; flex: 1; margin-left: 10px;">unreal-assets/</span>
      </div>
      <div class="scan-row scan-row-highlight" style="display: flex; justify-content: space-between; margin-bottom: 6px; background: rgba(0, 229, 255, 0.08); padding: 2px 4px; border-left: 2px solid #ffaa00;">
        <span style="color: #ffaa00;">21:27:17</span>
        <span style="color: #ffaa00; font-weight: bold;">[24.1 GB]</span>
        <span style="color: #ffffff; flex: 1; margin-left: 10px; font-weight: bold;">dataset-archive/ ◄ MAX</span>
      </div>
    </div>
    <!-- Synthesized caption -->
    <div class="folder-scan-summary" style="font-size: 11.5px; line-height: 1.5; color: rgba(226, 232, 240, 0.9); border-top: 1px dashed rgba(0, 229, 255, 0.2); padding-top: 10px;">
      "Scanned 14 project directories inside Desktop/projects. The largest identified directory is <strong>dataset-archive/</strong> measuring <strong>24.1 GB</strong>."
    </div>
  </div>
  <div class="hud-card-footer" style="padding: 6px 14px; font-family: monospace; font-size: 9px; color: rgba(0, 229, 255, 0.6); display: flex; justify-content: space-between; border-top: 1px solid rgba(0, 229, 255, 0.15);">
    <span>ENTRIES: 14</span>
    <span>TOTAL: 60.2 GB</span>
    <span>SPEED: 1.4 GB/S</span>
  </div>
</div>
```

### B. 3D Wireframe Preview Modal HTML & Three.js Hook
```html
<!-- 3D WIREFRAME PREVIEW MODAL -->
<div id="hud-3d-wireframe-modal" class="hud-holo-card" style="display: none; position: absolute; top: 22%; left: 50%; width: 420px; height: 340px; z-index: 45;">
  <div class="hud-card-header">
    <div class="hud-card-title"><span class="hud-accent">//</span> MODEL // 3D - WIREFRAME [ACTIVE]</div>
    <div style="display: flex; gap: 6px;">
      <button class="hud-btn-pill" onclick="window.toggle3DWireframe(false)" style="height: 18px; padding: 0 6px; font-size: 9px;">✕</button>
    </div>
  </div>
  <div class="hud-card-divider"></div>
  <div id="wireframe-3d-canvas-container" style="width: 100%; height: 260px; position: relative; overflow: hidden; background: radial-gradient(circle at center, rgba(0, 229, 255, 0.06) 0%, rgba(3, 7, 18, 0.95) 75%);">
    <canvas id="wireframe-3d-canvas" style="width: 100%; height: 100%; display: block;"></canvas>
    <div style="position: absolute; bottom: 8px; right: 10px; font-family: monospace; font-size: 8.5px; color: rgba(0, 229, 255, 0.7); background: rgba(0, 10, 20, 0.6); padding: 2px 6px; border-radius: 2px; pointer-events: none;">
      VERTS: 8,420 | POLYS: 16,840 | FPS: 60.0
    </div>
  </div>
  <div class="hud-card-footer" style="padding: 4px 12px; font-family: monospace; font-size: 9px; color: rgba(0, 229, 255, 0.6); display: flex; justify-content: space-between; border-top: 1px solid rgba(0, 229, 255, 0.15);">
    <span>GEO: TREFOIL TORUS KNOT</span>
    <span>SCALE: 1.0</span>
    <span>RENDER: THREE.JS WEBGL</span>
  </div>
</div>
```

### C. Three.js Wireframe Controller JS Blueprint
```javascript
// 3D Wireframe Controller
(function() {
  let scene, camera, renderer, knotMesh, animId;
  let isDragging = false, prevMouseX = 0, prevMouseY = 0;

  window.init3DWireframeModal = function() {
    const container = document.getElementById('wireframe-3d-canvas-container');
    const canvas = document.getElementById('wireframe-3d-canvas');
    if (!container || !canvas || scene) return;

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
    camera.position.z = 6.2;

    renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // Trefoil Torus Knot geometry (p=2, q=3)
    const geometry = new THREE.TorusKnotGeometry(1.6, 0.48, 128, 32, 2, 3);
    const material = new THREE.MeshBasicMaterial({
      color: 0x00e5ff,
      wireframe: true,
      transparent: true,
      opacity: 0.85
    });

    knotMesh = new THREE.Mesh(geometry, material);
    scene.add(knotMesh);

    // Mouse drag interaction
    canvas.addEventListener('mousedown', (e) => {
      isDragging = true;
      prevMouseX = e.clientX;
      prevMouseY = e.clientY;
    });
    window.addEventListener('mouseup', () => { isDragging = false; });
    window.addEventListener('mousemove', (e) => {
      if (!isDragging || !knotMesh) return;
      const deltaX = e.clientX - prevMouseX;
      const deltaY = e.clientY - prevMouseY;
      knotMesh.rotation.y += deltaX * 0.01;
      knotMesh.rotation.x += deltaY * 0.01;
      prevMouseX = e.clientX;
      prevMouseY = e.clientY;
    });

    function animate() {
      animId = requestAnimationFrame(animate);
      if (!isDragging && knotMesh) {
        knotMesh.rotation.x += 0.007;
        knotMesh.rotation.y += 0.012;
        knotMesh.rotation.z += 0.004;
      }
      renderer.render(scene, camera);
    }
    animate();
  };

  window.toggle3DWireframe = function(show) {
    const modal = document.getElementById('hud-3d-wireframe-modal');
    if (!modal) return;
    if (show) {
      modal.style.display = 'block';
      modal.classList.add('hud-card-pop-in');
      setTimeout(() => {
        if (!scene) window.init3DWireframeModal();
      }, 50);
    } else {
      modal.style.display = 'none';
      modal.classList.remove('hud-card-pop-in');
    }
  };

  window.toggleFolderScanCard = function(show) {
    const card = document.getElementById('hud-folder-inspection-card');
    if (!card) return;
    if (show) {
      card.style.display = 'block';
      card.classList.add('hud-card-pop-in');
      if (window.dockOrb) window.dockOrb(true);
    } else {
      card.style.display = 'none';
      card.classList.remove('hud-card-pop-in');
    }
  };
})();
```

---

## 8. Summary for Verification
- **Port Compliance**: Fully maps Rose UI red/amber palette to Jarvis electric neon cyan (`#00e5ff`) with amber warning accents (`#ffaa00`).
- **Timing Match**: Identical 800ms orb docking glide (`cubic-bezier(0.16, 1, 0.3, 1)`), 400ms folder inspection entrance, and 320ms 3D wireframe modal pop.
- **Voice / Pill Triggers**:
  - Voice query *"What is the largest folder inside Desktop/projects"* triggers `toggleFolderScanCard(true)` + `dockOrb(true)`.
  - Voice query *"Show me a 3D model"* triggers `toggle3DWireframe(true)`.
  - Pill `[CLEAR HUD]` or voice *"clear"* closes both cards and un-docks orb back to screen center.
