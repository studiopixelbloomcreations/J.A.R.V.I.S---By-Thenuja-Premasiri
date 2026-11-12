# Reference Analysis: Download (5).mp4 (Huw Prosser Rose UI -> Jarvis Cyan 1:1 Port)
**Slice**: Map Telemetry HUD, Crawley Route Card, Photo Gallery Carousel, Maximize Action

---

## 1. Executive Summary & Scene Breakdown
- **Timestamp 00:00 - 00:04**: User asks: *"Hey Rose, where can I take my fiancée for a super serious Halloween night?"* Rose orb pulses and speaks: *"I know just the place."*
- **Timestamp 00:05 - 00:06**: Full-screen Dark Vector Map Telemetry transitions in. Road vectors render in high contrast. Telemetry beacon pulses red at Turners Hill / Tulleys Farm. Route card displays bottom-left: `TULLEYS FARM, CRAWLEY`.
- **Timestamp 00:07**: User queries: *"What is this place? Maximise that for me."* Holographic Photo Gallery card pops above map with header `TULLEYS FARM - (THE MECCA OF HALLOWEEN)` and thumbnail carousel strip. Top-right HUD pills active: `[DEFAULT] [TEMP] [CLEAR HUD] [LIVE] [AUTO]`.
- **Timestamp 00:08**: Maximize action triggers! The gallery expands into a panoramic multi-photo modal with backdrop dimming and smooth 380ms cubic-bezier zoom.
- **Timestamp 00:09 - 00:25**: Real-world drive and experience cutaways.

---

## 2. Pillar 1: Map Telemetry HUD (Vector Dark Mode & Beacon System)
### Visual & Structural Specs:
- **Background**: Deep pitch black `#000000` / `#040810` with subtle vignette `radial-gradient(circle, rgba(0,229,255,0.03) 0%, rgba(0,0,0,0.85) 100%)`.
- **Top Accent Line**: 1px horizontal line across top screen border with center dual notch indicators (`width: 30px; height: 3px; background: rgba(0, 229, 255, 0.4)`).
- **Road Network Vectors**:
  - Primary Highways / Arteries: Solid crisp lines, `stroke: #d0d7de`, `stroke-width: 1.8px`.
  - Secondary Connecting Roads: Muted white/grey lines, `stroke: rgba(255,255,255,0.45)`, `stroke-width: 1.2px`.
  - Minor Roads & Links: Faint dark lines, `stroke: rgba(255,255,255,0.2)`, `stroke-width: 0.8px`.
- **Landmark & Town Typography**:
  - Font: Clean geometric sans-serif (`Inter`, `Segoe UI`, or `system-ui`).
  - Size: 10px - 11px, `font-weight: 600`, `letter-spacing: 0.8px`.
  - Color: Off-white (`#e2e8f0`) with dark 2px text-shadow/halo for legibility over road lines.
  - Active Labels shown in slice: `Copthorne`, `Felbridge`, `Crawley Down`, `Crawley`, `Worth`, `Rowfant`, `Turners Hill`, `South Hill`, `Wakehurst Place`, `Ardingly Reservoir`.
- **Destination Beacon (Target Pin)**:
  - Located at Turners Hill (`Tulleys Farm`).
  - Rose Reference: Neon red core dot with expanding red sonar ring.
  - **Jarvis 1:1 Cyan Port**:
    - Core Dot: 8px diameter circle `#00e5ff`, `box-shadow: 0 0 12px #00e5ff, 0 0 24px rgba(0,229,255,0.8)`.
    - Pulse Halo: CSS keyframe `pulseBeacon` expanding 8px -> 36px, `border: 1.5px solid rgba(0, 229, 255, 0.6)`, `opacity: 1 -> 0`, animation duration `1.8s infinite ease-out`.
    - Crosshair Target: 4 thin 4px tick marks aligned orthogonally around beacon.

---

## 3. Pillar 2: Crawley Route Card & Telemetry Controls
### Position & Layout:
- **Location**: Bottom-left corner, docked `left: 48px; bottom: 42px;`.
- **Card Hierarchy**:
  1. **Primary Title**: `TULLEYS FARM, CRAWLEY`
     - Typography: Heavy uppercase sans-serif (`font-family: 'Inter', sans-serif; font-size: 20px; font-weight: 800; letter-spacing: 1.8px; color: #ffffff;`).
  2. **Scrubber / Route Telemetry Bar**:
     - Immediately beneath the title (margin-top: 8px).
     - Full width thin track: `height: 2px; background: rgba(255, 255, 255, 0.25)`.
     - Active progress indicator: White / Cyan dot (`width: 6px; height: 6px; border-radius: 50%`) with tick intervals.
  3. **Control Button Pills (Bottom Row)**:
     - Button label: `[AUTO]` (alongside `[ROUTE]`, `[INFO]`).
     - Dimensions: `height: 22px; padding: 2px 10px; border-radius: 12px; font-size: 9.5px; font-family: monospace; font-weight: 700;`.
     - Style: `border: 1px solid rgba(0, 229, 255, 0.4); color: #00e5ff; background: rgba(0, 229, 255, 0.08);`.

---

## 4. Pillar 3: Photo Gallery Carousel Architecture
### Unmaximized State:
- **Position**: Floating modal centered/upper-mid (`top: 18%; left: 32%; width: 480px;`).
- **Card Header**:
  - Monospace tech title: `TULLEYS FARM - (THE MECCA OF HALLOWEEN)`.
  - Font: 11px monospace, `letter-spacing: 1.2px`, color `#ffffff` or `rgba(0, 229, 255, 0.9)`.
  - Corner brackets: `[ + ]` or `┌ ┐ └ ┘` tech HUD bounding accents.
- **Photo Strip Layout**:
  - Primary Left Feature Thumbnail: 220px x 140px, haunted barn exterior with pumpkins and purple/warm illumination.
  - Secondary Event Poster Thumbnail (below feature): 110px x 140px vertical poster (`SHOCKTOBER FEST / PUMPKIN FESTIVAL`).
  - Horizontal Thumbnail Row (right of feature): 3 thumbnails (90px x 65px each) showing spooky outdoor night lights, festival crowds, and lake skeleton.
  - Borders: 1px crisp solid border `rgba(0, 229, 255, 0.35)` with subtle 8px cyan outer drop-shadow.

---

## 5. Pillar 4: "Maximize That For Me" Motion Choreography & Transitions
### Trigger & Interaction:
- **Speech Command**: *"Maximise that for me"* or *"Maximize photo gallery"* or click on gallery card.
- **Motion Timing & Curve**:
  - Duration: `380ms` (0.38s).
  - Easing: `cubic-bezier(0.16, 1, 0.3, 1)` (spring-damped deceleration, signature Huw Prosser feel).
- **Maximized Modal Layout**:
  - Modal Dimensions: `width: 960px; max-width: 92vw; height: 520px;`.
  - Backdrop: `background: rgba(0, 5, 12, 0.82); backdrop-filter: blur(14px);`.
  - Border: `1px solid rgba(0, 229, 255, 0.5); box-shadow: 0 0 40px rgba(0, 229, 255, 0.2);`.
  - Expanded Carousel Structure:
    - Top Header Bar: `TULLEYS FARM // THE MECCA OF HALLOWEEN` + `[ ✕ CLOSE / MINIMIZE ]` button at top-right.
    - 5-Photo Panoramic Strip:
      1. Main Barn & Pumpkin Field (`flex: 1.4; height: 320px;`)
      2. Shocktober Festival Ferris Wheel & Night Crowds (`flex: 1; height: 320px;`)
      3. Haunted Trail Laser & Fog (`flex: 1; height: 320px;`)
      4. Spooky Lake Skeleton Installation (`flex: 1; height: 320px;`)
      5. Shocktober Fest Event Banner / Pricing Card (`flex: 0.9; height: 320px;`)
    - Hover Interaction: Photos elevate with `transform: translateY(-4px) scale(1.02);` and intensified cyan border glow `box-shadow: 0 0 16px rgba(0, 229, 255, 0.6);`.

---

## 6. Top HUD Navigation Pills (Video 5 Context)
In Download (5).mp4 at timestamp 00:07, the top-right pill group displays:
`[DEFAULT]` `[TEMP]` `[CLEAR HUD]` `[LIVE]` `[AUTO]`
- **Dimensions**: Height `26px`, Padding `3px 12px`, Border-radius `4px`.
- **Font**: Monospace, `10px`, `font-weight: 700`, `letter-spacing: 1px`.
- **Jarvis 1:1 Cyan Palette**:
  - Inactive Pill: `border: 1px solid rgba(0, 229, 255, 0.25); background: rgba(0, 229, 255, 0.05); color: rgba(255, 255, 255, 0.7);`
  - Active / Hover Pill: `border: 1px solid #00e5ff; background: rgba(0, 229, 255, 0.18); color: #00e5ff; box-shadow: 0 0 10px rgba(0, 229, 255, 0.35);`

---

## 7. 1:1 Rose -> Jarvis Cyan Color & Token Translation Table
| Element | Huw Prosser Rose (Original) | J.A.R.V.I.S. Cyan Port (1:1) |
| :--- | :--- | :--- |
| Map Background | `#000000` pitch black | `#02060c` to `#000000` deep obsidian |
| Arterial Roads | `#ffffff` | `#e0f7fa` (crisp white with faint cyan tint) |
| Secondary Roads | `rgba(255,255,255,0.4)` | `rgba(0, 229, 255, 0.35)` |
| Destination Beacon | Neon Red `#ff0033` / `#ff2244` | Neon Cyan `#00e5ff` + `#00b4d8` |
| Beacon Pulse Glow | `rgba(255, 0, 50, 0.4)` | `rgba(0, 229, 255, 0.5)` |
| Route Card Title | White `#ffffff` | White `#ffffff` with cyan shadow |
| Card Glass Backing | `rgba(15, 5, 8, 0.85)` | `rgba(4, 10, 20, 0.88)` |
| Card Border & Brackets | Rose Red `rgba(255, 60, 80, 0.4)` | Cyan `rgba(0, 229, 255, 0.45)` |
| Top Pill Accents | Rose Red / White | Electric Cyan `#00e5ff` |
