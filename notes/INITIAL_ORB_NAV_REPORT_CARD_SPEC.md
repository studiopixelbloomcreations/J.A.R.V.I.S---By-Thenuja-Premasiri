# Reference Analysis: Download.mp4 (Huw Prosser Rose UI -> Jarvis Cyan 1:1 Port)
**Slice**: Initial Exploded Orb Mechanics, Top Pill Navigation, Research Task Card, and 13-Block Report Card Layout

---

## 1. Executive Summary & Scene Timeline

- **Timestamp 00:00 - 00:02 (Exploded Orb Standby)**:
  - System is in idle listening state. The orb renders in a 3D isometric exploded kinetic view tilted along a diagonal ray (-35° tilt) with detached counter-rotating rings, an inner glowing torus, radial azimuth ticks, and floating embers.
  - Top HUD pill navigation bar is pinned at top: `[HISTORY]`, `[TEXT]`, `[CLEAR VIEW]`, `[CAMERA]`, `CAMERA SOURCE: [DEFAULT CAMERA v]`, `[SCREENSHARE]`.
  - Bottom telemetry bar shows live mic VU dB levels: `LVL -46.5 dB  PK -50.7 dB  [MUTE]`.
- **Timestamp 00:02 - 00:05 (Voice Trigger & Reticle Alignment)**:
  - User speaks: *"Hey Rose, can you uh, research..."*
  - The exploded isometric rings smoothly rotate and converge (650ms `cubic-bezier(0.16, 1, 0.3, 1)`) into a 2D face-on concentric HUD reticle (`rotateX(0deg) rotateY(0deg)`).
  - Center stencil text snaps in: `ROSE` (Jarvis: `J.A.R.V.I.S.`) with cardinal crosshairs, segmented notched ring, and diagonal `//` `\\` corner bracket marks.
- **Timestamp 00:05 - 00:13 (Task Formulation & Audio Reactive Glow)**:
  - User finishes query: *"...can you do another VR report for me? Just, the state of VR in late 2024: real hits, hard limits, all that."*
  - Orb rings pulse subtly to voice amplitude while transcription displays real-time at the bottom bar.
- **Timestamp 00:13.9 - 00:14.5 (Kinetic Orb Corner Docking)**:
  - System acknowledges task dispatch. The central reticle orb scales down from diameter ~220px to ~92px (scale `0.42x`) and glides diagonally to the bottom-right corner (`bottom: 24px; right: 28px`) over 400ms (`cubic-bezier(0.16, 1, 0.3, 1)`).
- **Timestamp 00:14.5 - 00:22 (Intermediate Research Task Card)**:
  - A research agent progress card fades in on the left:
    - Header: `RESEARCH //` (cyan) + `00:03` (live running stopwatch).
    - Title: `STATE OF VR`.
    - Status: `STARTING RESEARCH AGENT`.
    - Segmented progress bar: 20 discrete rectangular blocks filling sequentially left-to-right.
    - Sub-telemetry: `0 BLOCKS` | `0 SOURCES` and red status LED.
- **Timestamp 00:34.5 - 00:37.0 (Report Deck Reveal & Grid Materialization)**:
  - System completes synthesis: *"I've compiled the full report for you boss. Headsets, shipment trends, platform hits, and hardware specs."*
  - The 13-block holographic HUD report card deck cascades into view with staggered cybernetic entrance animations (opacity `0 -> 1`, translateY `12px -> 0px`).
  - Docked orb remains in bottom-right corner spinning and monitoring active state.

---

## 2. Pillar 1: Initial Exploded Orb Mechanics

### 3D Isometric Exploded State (Standby Mode)
In Huw Prosser's reference, the orb is not merely a flat circle; it is a layered 3D kinetic gyroscope exploded along a central projection vector:
- **Projection Vector / Axis Angle**: Tilted at approximately -35° from horizontal, with a 3D perspective depth of 400px (`transform: perspective(800px) rotateX(25deg) rotateY(-35deg)`).
- **Central Axis Ray**: A bright luminous line (`height: 1.5px; background: linear-gradient(90deg, transparent, #00e5ff 25%, #ffffff 50%, #00e5ff 75%, transparent); box-shadow: 0 0 8px #00e5ff`) piercing through the centers of all discs.
- **Layer 1 (Central Torus / Core Ring)**:
  - Thick glowing ring (stroke 8px - 12px), diameter 120px.
  - Rose Reference: Hot magenta/rose bloom `#ff0055`.
  - **Jarvis 1:1 Cyan Port**: Neon cyan `#00e5ff` with intense bloom `box-shadow: 0 0 20px #00e5ff, 0 0 40px rgba(0, 229, 255, 0.7)`.
  - Animated pulsing breath cycle (duration 2.8s, scale 0.95 -> 1.05).
- **Layer 2 (Secondary Concentric Reticle)**:
  - Thin solid circular ring (`stroke: rgba(224, 247, 250, 0.85); stroke-width: 1.2px`), diameter 140px.
- **Layer 3 (Left-Side Segmented Rings)**:
  - Two broken arc rings offset along the axis to the left (-40px and -75px Z-offset).
  - Contains dash patterns (`stroke-dasharray: 20 8 4 8`) with orbiting circular beads (diameter 3px).
- **Layer 4 (Right-Side Azimuth Compass Dial)**:
  - Large dial disc offset to the right (+55px Z-offset), diameter 170px.
  - Graduated compass tick marks around perimeter (60 fine radial tick marks).
  - Intermittent accent ticks in glowing cyan/alert red (`#ff2a5f`).
- **Layer 5 (Outer Dotted Field Ring)**:
  - Fine dotted perimeter ring, diameter 210px (`stroke-dasharray: 2 6`).
  - Rotates continuously clockwise at `20s / 360deg`.
- **Floating Particles / Embers**:
  - 16-24 ambient micro-dots floating around the assembly in 3D volume, drifting outward with low-speed velocity.

### Reticle Alignment Transition (Voice Activation)
When voice input is detected, the exploded 3D rings collapse into the 2D front HUD reticle:
- **Duration**: `650ms`.
- **Easing Curve**: `cubic-bezier(0.16, 1, 0.3, 1)`.
- **Kinematics**:
  - `transform: perspective(800px) rotateX(25deg) rotateY(-35deg) -> rotateX(0deg) rotateY(0deg)`.
  - All ring Z-offsets converge to `Z = 0`.
  - Center branding text snaps into center: `ROSE` -> `J.A.R.V.I.S.`.
  - Cardinal crosshair lines fade in at 12, 3, 6, and 9 o'clock.
  - 4 diagonal corner bracket tick sets `//` and `\\` snap in at 45° angles around the perimeter.
  - Bottom technical label displays: `J.A.R.V.I.S. // CORE 01`.

---

## 3. Pillar 2: Top HUD Navigation Bar

### Layout & Placement
- **Position**: Fixed top of viewport (`top: 16px; right: 28px; z-index: 1000`).
- **Flex Layout**: Horizontal row (`display: flex; align-items: center; gap: 8px;`).

### Exact Button Pills (from Download.mp4 Reference):
1. `[ HISTORY ]`: Opens prompt/interaction drawer.
2. `[ TEXT ]`: Toggles manual text command input prompt.
3. `[ CLEAR VIEW ]`: Dismisses active HUD report cards and restores idle centered view.
4. `[ CAMERA ]`: Toggles vision multimodal camera input.
5. `CAMERA SOURCE:`: Plain text label (`font-size: 9.5px; color: rgba(0, 229, 255, 0.65); letter-spacing: 1px;`).
6. `[ DEFAULT CAMERA v ]`: Dropdown selector pill with small down chevron.
7. `[ SCREENSHARE ]`: Toggles screen capture / HUD screen ingest.

*(Companion Playlist Pills from Board Brief #3 & Slices: `[PLAYLIST]`, `[PLAY]`, `[CLEAR HUD]`, `[SAVED]`, `[REPORT: CARDS]`, `[METADATA: DEFAULT]`)*.

### Pill Styling & CSS Specifications:
```css
.hud-pill-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 24px;
  padding: 2px 10px;
  background: rgba(4, 12, 22, 0.65);
  border: 1px solid rgba(0, 229, 255, 0.4);
  border-radius: 4px;
  color: #00e5ff;
  font-family: 'JetBrains Mono', 'Roboto Mono', monospace;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  backdrop-filter: blur(8px);
  cursor: pointer;
  transition: all 180ms ease;
  user-select: none;
}

.hud-pill-button:hover {
  background: rgba(0, 229, 255, 0.18);
  border-color: #00e5ff;
  box-shadow: 0 0 10px rgba(0, 229, 255, 0.4);
}

.hud-pill-button.active {
  background: #00e5ff;
  color: #02060c;
  font-weight: 800;
  border-color: #00e5ff;
  box-shadow: 0 0 14px rgba(0, 229, 255, 0.7);
}
```

---

## 4. Pillar 3: Intermediate Research Task Card (00:14 - 00:20)

Before the full 13-block report deck opens, Jarvis renders an active agent execution card:
- **Position**: Floating bottom-left (`left: 48px; bottom: 120px; width: 340px`).
- **Visual Styling**:
  - Background: `rgba(2, 6, 12, 0.88)` with `1px solid rgba(0, 229, 255, 0.35)`.
  - Header Row:
    - Left: `RESEARCH //` (cyan, `font-weight: 700; font-size: 11px`).
    - Right: `00:03` (monospace stopwatch counter incrementing live).
  - Title: `STATE OF VR` (font-size 18px, font-weight 800, color #ffffff).
  - Status Subtitle: `STARTING RESEARCH AGENT` (font-size 10px, color rgba(0, 229, 255, 0.75)).
  - Segmented Progress Bar:
    - 20 discrete rectangular blocks (`width: 12px; height: 8px; margin-right: 3px; border-radius: 1px`).
    - Inactive blocks: `background: rgba(255, 255, 255, 0.12)`.
    - Active/filled blocks: `background: #00e5ff; box-shadow: 0 0 6px #00e5ff`.
  - Telemetry Line: `0 BLOCKS` (left) | `0 SOURCES` (right).
  - Alert Beacon: Small red indicator square (`width: 6px; height: 6px; background: #ff2a5f; box-shadow: 0 0 8px #ff2a5f`) placed on right edge.

---

## 5. Pillar 4: Kinetic Orb Corner Docking Mechanics

### Docking Animation Specs:
- **Trigger**: Fired when task card launches or report deck is requested.
- **Duration**: `400ms`.
- **Easing**: `cubic-bezier(0.16, 1, 0.3, 1)`.
- **Start State (Center Reticle)**:
  - `top: 50%; left: 50%; transform: translate(-50%, -50%) scale(1.0);`
  - Diameter: ~220px.
- **Docked State (Bottom-Right Corner)**:
  - `top: auto; left: auto; bottom: 24px; right: 28px; transform: scale(0.42); transform-origin: bottom right;`
  - Rendered Diameter: ~92px.
- **Kinetics**:
  - The orb continues continuous inner rotation while gliding.
  - Rings remain interactive.
  - Sub-label beneath docked orb reads: `J.A.R.V.I.S. // CORE 01  ACTIVE`.
- **Undock / Return Transition**:
  - When report cards or active modes are cleared (`[CLEAR VIEW]` or voice "go to sleep / dismiss"), orb glides back to `(50%, 50%) scale(1.0)` over 500ms `cubic-bezier(0.16, 1, 0.3, 1)`.

---

## 6. Pillar 5: 13-Block Holographic HUD Report Card Deck Layout

The 13-block report deck forms an asymmetric HUD bento grid tailored for 1920x1080 screens (`padding: 60px 32px 36px 32px; display: grid; grid-template-columns: 240px 1.1fr 1.1fr 1fr; gap: 16px;`):

```
+-------------------------------------------------------------------------------------------------------+
|  TOP HUD PILLS: [HISTORY] [TEXT] [CLEAR VIEW] [CAMERA] CAMERA SOURCE: [DEFAULT CAMERA v] [SCREENSHARE] |
+-------------------------------------------------------------------------------------------------------+
|  COL 1 (Left):         |  COL 2 (Center-Left):     |  COL 3 (Center-Right):    |  COL 4 (Right):      |
|                        |                           |                           |                      |
|  [Card 1]              |  [Card 3: Stacked Notes]  |  [Card 6: Main Chart]     |  [Card 8: Video]     |
|  Mobile TikTok/Reels   |  META QUEST 3S / QUEST 3  |  CHART // SHIPMENT        |  VIDEO // META QUEST |
|  Vertical Video Player |  - SHIPPING (128GB...)    |  REALITY (3 Bars)         |  PRO BATTERY TEST    |
|  (Aspect 9:16)         |  (Pagination . . . .) [ ] |  [MILLION UNIT]           |  (Play Cue O)        |
|                        |                           |                           |                      |
|  [Card 2]              |  [Card 4: Bar Chart A]    |  [Card 7: Stat Box]       |  [Card 9: 3D Model]  |
|  Hardware Photo        |  4 Vertical Bars          |  FIGURE // 2023 [FACT]    |  Meta Quest 3        |
|  Meta Quest 3 on table |  Hardware Distribution    |  ≈20m                     |  Rotating 3D Mesh    |
|                        |                           |  QUEST HEADSETS SOLD...   |  Starfield Backing   |
|                        |  [Card 5: Bar Chart B]    |                           |                      |
|                        |  6 Vertical Bars          |                           |  [DOCKED ORB]        |
|                        |  Steam Hardware Survey    |                           |  Bottom Right Corner |
+-------------------------------------------------------------------------------------------------------+
|  BOTTOM BAR: LVL -46.5 dB  PK -50.7 dB  [MUTE]  "Yes, please. Uh, please present the report."         |
+-------------------------------------------------------------------------------------------------------+
```

### Individual Card Anatomy & Specifications:

1. **Card 1: Mobile Vertical Video Card (Column 1 Top)**:
   - Format: 9:16 vertical video player preview.
   - Elements: TikTok logo icon, user avatar circle, handle text `@huwprosser`, right action bar (hearts, comments, share, save icons).
   - Border: 1px cyan with corner brackets.

2. **Card 2: Hardware Photo Thumbnail (Column 1 Bottom)**:
   - Content: Real photography of Meta Quest 3 headset with controllers on wooden desk.
   - Header: Small monospace tag `PHOTO // QUEST 3 HARDWARE`.
   - Ratio: ~16:10 aspect.

3. **Card 3: Stacked Notes / Topic Summaries (Column 2 Top)**:
   - Header: `META QUEST 3S / QUEST 3 - SHIPPING` (or `HITS: SOCIAL, SANDBOX, FITNESS AND RHYTHM`).
   - Body Text: Clean monospace/sans paragraph detailing units sold, game metrics (*Beat Saber*, *Gorilla Tag* $100m revenue), and Qualcomm XR2 Gen 2 specs.
   - Footer Controls: 5 pagination dots (`. . . . .`) for cycling through stacked research cards + square maximize button `[ ]`.

4. **Cards 4 & 5: Dual Sub-Charts (Column 2 Bottom)**:
   - Card 4: 4-bar hardware distribution chart with x-axis labels.
   - Card 5: 6-bar Steam VR Hardware Survey comparison chart.
   - Styling: Solid vertical bars with neon cyan fill, faint horizontal grid lines, and technical footer notes.

5. **Card 6: Primary Shipment Reality Chart (Column 3 Top/Mid)**:
   - Header: `CHART // THE SHIPMENT REALITY BEHIND THE INSTALLED BASE` (left) + `MILLION UNIT` (right).
   - Visual: 3 prominent vertical bars (Meta Quest full years, Quest 2 1st qtr, Quest Pro 1Q 2023).
   - Indicator Lights: 2 red indicator squares docked right above top border.

6. **Card 7: Key Metric Stat Box (Column 3 Bottom)**:
   - Header: `FIGURE // 2023` (left) + `FACT` (right).
   - Title: `QUEST HEADSETS SOLD CUMULATIVELY BY EARLY 2023`.
   - Massive Metric: `≈20m` (`font-size: 38px; font-weight: 800; color: #ffffff; letter-spacing: -1px; text-shadow: 0 0 12px rgba(0, 229, 255, 0.4);`).
   - Description text underneath with source tag: `SOURCE // THE VERGE`.

7. **Card 8: Video Player Card (Column 4 Top)**:
   - Content: Meta Quest video demonstration with black preview and centered circular loading/play ring (`O`).
   - Header: `VIDEO // META QUEST 3 STANDALONE ELITE AND BATTERY TEST`.
   - Sub-label: `HOVER / EXPAND FOR SOUND`.

8. **Card 9: Interactive 3D Model Card (Column 4 Middle)**:
   - Header: `∞ Meta Quest`.
   - Content: Real-time 3D rotating white wireframe/shaded headset model floating over starry space particle background.

### Card Decorative & Structural Details:
- **Card Background**: `rgba(2, 6, 12, 0.85)` with `backdrop-filter: blur(12px)`.
- **Border**: `1px solid rgba(0, 229, 255, 0.35)`.
- **Corner Brackets**: 4 L-shaped tick brackets on each card:
  ```css
  .hud-card::before, .hud-card::after {
    content: '';
    position: absolute;
    width: 6px;
    height: 6px;
    border-color: #00e5ff;
    border-style: solid;
    pointer-events: none;
  }
  .hud-card::before { top: -1px; left: -1px; border-width: 2px 0 0 2px; }
  .hud-card::after  { bottom: -1px; right: -1px; border-width: 0 2px 2px 0; }
  ```
- **Red Alert Indicator Dots**: Placed strategically above specific cards (`width: 5px; height: 5px; background: #ff2a5f; box-shadow: 0 0 6px #ff2a5f; border-radius: 1px`).

---

## 7. Pillar 6: Live Audio Telemetry Bar (Bottom-Left)

- **Position**: Pinned bottom-left (`bottom: 20px; left: 32px; z-index: 1000`).
- **Telemetry Readout**:
  - Stereo VU Meter: Glowing red/cyan horizontal audio bar with 2.0s human silence debounce.
  - Decibel metrics: `LVL -46.5 dB  PK -50.7 dB` (font: 10px monospace, color: `#e0f7fa`).
  - Action pill: `[ MUTE ]` (height: 20px, 1px solid cyan border).
  - Live Speech Transcript: Directly following the mute button, italic text showing real-time transcribed user voice input.

---

## 8. Exact Color Palette & Design Tokens

| Token Name | Reference (Rose) | Jarvis 1:1 Cyan Port | Usage |
|---|---|---|---|
| `--hud-bg` | `#020005` | `#02060c` | Pitch black deep space background |
| `--hud-card-bg` | `rgba(10, 5, 12, 0.85)` | `rgba(2, 6, 12, 0.85)` | Semi-transparent card backing with blur |
| `--hud-cyan-primary` | `#ff0055` (Rose) | `#00e5ff` | Primary neon borders, active states, crosshairs |
| `--hud-cyan-glow` | `rgba(255, 0, 85, 0.6)` | `rgba(0, 229, 255, 0.65)` | Box-shadow bloom and particle aura |
| `--hud-cyan-subtle` | `rgba(255, 0, 85, 0.2)` | `rgba(0, 229, 255, 0.25)` | Inactive borders, grid dividers |
| `--hud-text-primary` | `#ffffff` | `#ffffff` | Primary card titles, massive metric numbers |
| `--hud-text-cyan` | `#ff80ab` | `#e0f7fa` | Monospace subheadings, labels, pill text |
| `--hud-text-muted` | `rgba(255,255,255,0.55)` | `rgba(224, 247, 250, 0.6)` | Paragraph explanations, citations |
| `--hud-indicator-red` | `#ff2a5f` | `#ff2a5f` / `#00e5ff` | Card status indicator dots / alert LEDs |
| `--hud-bar-fill` | `#ffffff` / `#ff0055` | `#00e5ff` / `#ffffff` | Vertical bar chart fills |

---

## 9. Transition & Motion Timing Matrix

| Phase | Duration | Easing | Kinematics & Property Changes |
|---|---|---|---|
| **Exploded Gyroscope Idle** | Continuous | Linear | Outer dotted ring 20s/360°, Azimuth dial -25s/360°, floating embers |
| **Reticle Alignment** | `650ms` | `cubic-bezier(0.16, 1, 0.3, 1)` | `rotateX(25deg) rotateY(-35deg) -> rotate(0)`, Z-offsets -> 0, J.A.R.V.I.S. snaps in |
| **Audio Reaction Pulse** | Real-time | Instant | Torus stroke glow expands with mic amplitude (`scale 1.0 -> 1.08`) |
| **Orb Corner Docking** | `400ms` | `cubic-bezier(0.16, 1, 0.3, 1)` | `translate(-50%, -50%) -> translate(calc(100vw - 120px), calc(100vh - 120px))`, scale `1.0 -> 0.42` |
| **Task Card Reveal** | `300ms` | `ease-out` | Left dock fade-in, segmented bar fills sequentially (20 blocks over 2s) |
| **Report Grid Staggered Entrance** | `450ms` total | `cubic-bezier(0.16, 1, 0.3, 1)` | 4 columns cascade in left-to-right (35ms stagger), `opacity 0 -> 1`, `translateY(12px -> 0)` |
| **Card Maximize Zoom** | `380ms` | `cubic-bezier(0.16, 1, 0.3, 1)` | Card scales to ~960x600px centered, background dims to 15% opacity + 12px blur |
| **Dismiss / Reset to Center** | `500ms` | `cubic-bezier(0.16, 1, 0.3, 1)` | Cards dissolve (`opacity 1 -> 0`), orb returns from corner to center `(50%, 50%) scale 1.0` |
