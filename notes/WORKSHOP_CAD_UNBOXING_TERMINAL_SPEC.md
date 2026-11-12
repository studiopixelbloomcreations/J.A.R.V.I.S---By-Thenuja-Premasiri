# SPECIFICATION: Workshop Cutting Mat CAD Desk Layout, Unboxing HUD, and Terminal Log Card
**Reference Video**: `Download (2).mp4` (75.37s, 2261 frames @ 30fps)  
**Port**: 1:1 Rose (Huw Prosser) to Jarvis Neon Cyan (#00e5ff)  
**Author**: @video-analyst-3  
**Target Audience**: @coordinator, @hud-builder, @cards-architect, @orb-engineer  

---

## 1. Executive Summary & Scene Progression

`Download (2).mp4` showcases Huw Prosser's signature hardware engineering workflow. The video consists of two distinct continuous modes:
1. **Physical Desk & Computer Vision Unboxing Mode (00:00 - 00:27)**:
   - Huw unboxes the Busy Bar hardware device on top of a physical black & white CAD cutting mat.
   - Left monitor shows an overhead camera feed of the desk with live computer vision tracking: a 3D perspective wireframe bounding box tightly encloses the device, with dynamic telemetry overlays (`↓ DOWN 97 Mb/s ↑ UP 15 Mb/s`).
   - The top HUD displays navigation pills (`[HISTORY]`, `[SCAN VIEW]`, `[UNBOXING VIEW]`, `[CAMERA OFF]`, `[DEFAULT CAMERA ▼]`, `[SCREENSAVER]`).
2. **Radial 13-Block Holographic Report Cards Cascade (00:28 - 00:75)**:
   - Triggered at 00:28 (duration ~400ms): The HUD transitions smoothly. The central Rose orb glides to the bottom-right corner.
   - A multi-card holographic deck cascades outward in a staggered radial arrangement around the central camera PIP.
   - Features a tall, dedicated **Terminal Log Card** on the far-left edge, structured bulleted dossiers with checkmark status tags, live CSS descending bar charts, price badges (`$199 USD`), stacked card depth indicators, hardware teardown PIPs, and social video previews (TikTok 9:16 + YouTube 16:9).

---

## 2. Workshop Cutting Mat CAD Desk Layout

### 2.1 Aesthetic & Visual Structure
The cutting mat provides the tactile engineering CAD aesthetic that anchors both the physical desk and the digital HUD background.

* **Base Surface**:
  - Color: Deep obsidian matte charcoal `#06090e` / `#0a0d14`.
  - Subtle noise texture / fine grid surface grain.
* **Grid Intervals**:
  - **Minor Grid**: 10mm (1cm) square pitch. Stroke: `0.75px` solid. Color: `rgba(0, 229, 255, 0.12)`.
  - **Major Grid**: 50mm (5cm) square pitch. Stroke: `1.25px` solid. Color: `rgba(0, 229, 255, 0.35)`.
  - **Intersection Crosshairs**: 4px `+` crosshair marks at each 5cm intersection. Color: `rgba(0, 229, 255, 0.6)`.
* **Polar / Protractor Arc Guidance**:
  - Concentric circular arcs radiating from baseline focal point at radii `r = 50px, 100px, 150px, 200px, 250px`. Stroke: `1px` dashed/solid `rgba(0, 229, 255, 0.15)`.
  - Radial angle guide rays at: `10°`, `20°`, `30°`, `45°`, `60°`, `75°`, `90°`, `105°`, `120°`, `135°`, `150°`, `160°`, `170°`.
  - Angle degree labels: `9px` monospace font (`Space Mono` / `JetBrains Mono`), uppercase, `rgba(0, 229, 255, 0.5)`.
* **Border Graduation Rulers**:
  - 18px ruler strip running along bottom and left borders.
  - Graduation ticks:
    - 1mm minor ticks: `3px` height, `0.5px` stroke.
    - 5mm mid ticks: `6px` height, `1px` stroke.
    - 10mm major ticks: `10px` height, `1.25px` stroke.
  - Numerals: Centimeter markings (`31, 32, 33 ... 60`) aligned exactly to major ticks. Font: `9px` monospace.
* **Digital HUD Integration**:
  - CSS implementation: A dedicated `<div class="cad-cutting-mat-grid">` layered beneath or over the video canvas.
  - CRT / HUD Scanlines: 2px alternating scanlines (`rgba(0, 229, 255, 0.03)`).
  - Vignette: `radial-gradient(ellipse at center, transparent 65%, rgba(2, 6, 12, 0.85) 100%)`.

---

## 3. Unboxing HUD Styling & Telemetry Overlays

### 3.1 3D Perspective Bounding Box & Leader Lines
* **Bounding Cuboid**:
  - 8-vertex 3D perspective wireframe box framing tracked objects in the camera feed.
  - Stroke: `1.5px` bright neon cyan `#00e5ff` (replaces Rose red `#ff0033`).
  - Corner brackets: 4px L-shaped bracket accents on all 8 corners, thickness `2px`.
* **Telemetry Leader Lines & Badges**:
  - Leader line: `1px` diagonal connecting vector from bounding box vertex to floating HUD pill.
  - Terminal anchor: `3px` solid cyan dot at origin vertex.
  - Floating Tag: `[WHITE PLASTIC DEVICE]` or `[BUSY BAR MULTI-TOOL]`.
    - Background: `rgba(2, 8, 16, 0.9)`.
    - Border: `1px solid #00e5ff`.
    - Typography: `10px` bold uppercase monospace, `#00e5ff`.
  - Telemetry Pill: `↓ DOWN 97 Mb/s  ↑ UP 15 Mb/s` in digital LED font styling.

### 3.2 Top HUD Navigation Pills
Fixed at top header bar (`height: 48px`, `padding: 12px 24px`, flex layout):
* `[HISTORY]`: `height: 24px`, border `1px solid rgba(0, 229, 255, 0.4)`, font `10px Inter Heavy Uppercase`, letter-spacing `0.08em`.
* `[SCAN VIEW]`: Pill button with hover glow.
* `[UNBOXING VIEW]` / `[REPORT CARDS]`: **Active state** -> solid neon cyan `#00e5ff` background, pitch-black bold text `#02060c`, box-shadow `0 0 14px rgba(0, 229, 255, 0.6)`.
* `[CLEAR HUD]`: Standard outlined action button.
* `[CAMERA: ON/OFF]`: Toggle pill with status indicator.
* `CAMERA DEVICE: [DEFAULT CAMERA ▼]`: Dropdown selector with cyan border and custom caret.
* `[SCREENSAVER]`: Action button.

### 3.3 The 13-Block Holographic Card Architecture
Each card features:
* **Container**: Obsidian glass background `rgba(4, 12, 22, 0.85)`, `backdrop-filter: blur(12px)`.
* **Borders**: `1px` subtle cyan border `rgba(0, 229, 255, 0.35)`.
* **Corner Brackets**: 4 corner L-bracket ticks (`6px` leg length, `1.5px` stroke, bright cyan `#00e5ff`).
* **Card Roster & Layout Coordinates**:
  1. **Top-Left (Card 1)**: `CONSUMER PRODUCT OR DEV KIT?` (Dossier header, bullet points, index `01 / 10`).
  2. **Mid-Left Upper (Card 2)**: `BUSY BAR: A $249 FOCUS TIMER THAT IS...` with 20-block segmented progress meter (`COMPLETED`, `81 NOTES`, `12 SOURCES`).
  3. **Mid-Left Lower (Card 3)**: `OTHER LABS` (Community reverse-engineering dossiers).
  4. **Bottom-Left (Card 4)**: `PRICE // ENTRY` -> `$199 USD` (Huge 36px metric + glowing cyan `[JOIN THE WAITLIST]` button).
  5. **Lower Mid-Left (Card 5)**: TikTok Preview Card (Vertical 9:16 aspect ratio video card, creator avatar, sound wave icon).
  6. **Center PIP (Card 6)**: Live setup thumbnail with stacked card depth indicator (3 card layers behind), showing real-time network throughput (`DOWN 97 Mb/s UP 15 Mb/s`, `02 / 10`).
  7. **Center Lower (Card 7)**: 16:9 YouTube video embed (`FOUND IN YOUTUBE: FLIPPER ZERO CEO TALKS ABOUT THE BUSY BAR...`).
  8. **Top Center-Right (Card 8)**: `FLIPPER DEVICES (FLIPPER FZCO)` with bold cyan banner header, device photo, manufacturer table (HQ, Shipping, Domains), and buttons `[+ LINK]`, `[+ STAR]`.
  9. **Top-Right (Card 9)**: `CHART // BUSY BAR HTTP API ENDPOINTS BY NAMESPACE` (13 descending stair-step CSS vertical bars, labeled X-axis, y-axis gridlines).
  10. **Mid-Right (Card 10)**: `BRAINS AND POWER` (Hardware technical specs: STM32H7A3VI, Cortex-M7 @ 280MHz, FreeRTOS, 18650 cell, etc.).
  11. **Bottom-Right (Card 11)**: `81 endpoints` metric card (36px numeral, `OPENAPI 3.1` badge).
  12. **Bottom-Right Corner**: Concentric docked kinetic Orb with rotating rings and `J.A.R.V.I.S.` cyan core.

---

## 4. Terminal Log Card Styling (Deep-Dive)

The **Terminal Log Card** is located on the far-left edge of the screen, acting as the live engineering dossier log stream.

### 4.1 Card Geometry & Container
* **Position**: Docked left (`left: 20px`, `top: 72px`, `bottom: 40px`).
* **Width**: `270px` (fluid responsive up to `320px`).
* **Height**: Spanning almost full viewport height (~`85vh`).
* **Background**: Deep obsidian glass `rgba(2, 8, 16, 0.92)` with `backdrop-filter: blur(14px)`.
* **Border**: `1px solid rgba(0, 229, 255, 0.35)`.
* **Corner Brackets**: 4 corner L-bracket accents in bright cyan `#00e5ff`.
* **Shadow**: `box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6), inset 0 0 16px rgba(0, 229, 255, 0.05)`.

### 4.2 Header Bar
* **Title**: `NOTES // 10 ITEMS` or `SYSTEM LOG // LIVE`.
* **Font**: `10px Inter Heavy Uppercase`, letter-spacing `0.1em`, color `#00e5ff`.
* **Status Pill**: Pulsing cyan dot (`4px`) with `LIVE` tag.

### 4.3 Log Entries Specification
Each item inside the terminal card represents an analyzed subsystem:
* **Item Container**: `padding: 8px 10px`, `margin-bottom: 8px`, border-bottom `1px dashed rgba(0, 229, 255, 0.15)`.
* **Bullet Node**: Glowing bullet `•` in `#00e5ff` at top-left.
* **Status Checkmark**: Small verification badge `✓` in `#00e5ff` docked at top-right of each entry block.
* **Typography**:
  - Font family: `'JetBrains Mono', 'Space Mono', monospace`.
  - Font size: `11px`, `line-height: 1.4`.
  - Prefix / Subject: Bold `#ffffff` (`font-weight: 700`).
  - Technical Body: High-contrast cyan-tinted white `rgba(220, 245, 255, 0.85)`.
  - Code / URIs (`http://...`, `/api/v1/...`): Inline code badge styling, color `#00e5ff`, background `rgba(0, 229, 255, 0.08)`.

### 4.4 Exact Data Entries (from Reference Video)
1. `• Open HTTP API (OpenAPI 3.1) [✓]`
   `Device is an HTTP server, http://10.0.0.42/api/v1/ (local WEB UI at :80). http://api.log/ vs 127.0.0.1:4711/ OpenAPI /api/v1/docs/json`
2. `• Scripts for Python (offline, no cloud) [✓]`
   `pip install pybusybar (requests, image/media conversion, mDNS discovery, Websocket state stream, API version checks, JSON)`
3. `• Scripts for TypeScript (offline, Dev. repo: @busy/api-ts) [✓]`
   `Typed client for every namespace, Free Dispatch functions, standalone terminal and Websocket`
4. `• Insults/app actions (Audio, Animations, etc.) [✓]`
   `Powers the hilarious custom audio and visual insults/reactions. IoT download tools to integrate deep alpha.`
5. `• All apps that run on the device [✓]`
   `Scrollpage routines, app bundles, fonts/icons/sound/image, 128 KB heap default (128 KB max), no file/stream, new app id is 101.`
6. `• Community SDKs [✓]`
   `Docker/Go/client - all API endpoints in Go client on OpenAPI-generated Swagger schema/sdk, and general home assistant integrations.`
7. `• Open Firmware [✓]`
   `Busy-open/Free-RTOS (Source code, LAN controls, binary and code OTA, fast query mode, BLE hub, 10-30 ms latency, no cloud/phone app/pin)`

---

## 5. Animation Dynamics & Motion Timings

| Animation Event | Duration | Timing Function | Behavior / Keyframes |
| :--- | :--- | :--- | :--- |
| **Orb Glide to Dock** | 600ms | `cubic-bezier(0.25, 1, 0.5, 1)` | Center -> `right: 48px, bottom: 42px`, scale 1.0 -> 0.65 |
| **Card Deck Cascade** | 380ms | `cubic-bezier(0.16, 1, 0.3, 1)` | Radial expansion from center, 40ms stagger per card |
| **Terminal Log Slide-in** | 350ms | `cubic-bezier(0.16, 1, 0.3, 1)` | `translateY(-16px) -> translateY(0)`, opacity 0 -> 1 |
| **Card Hover Lift** | 200ms | `ease-out` | `translateY(-4px) scale(1.02)`, cyan glow `box-shadow` |
| **Maximize Zoom Modal** | 380ms | `cubic-bezier(0.16, 1, 0.3, 1)` | Width expands to `940px`, backdrop dims to `rgba(1,4,10,0.85)` with `14px` blur |
| **CAD Protractor Arc Pulse** | 3000ms | `ease-in-out` | Faint opacity breathing `0.10 <-> 0.22` |
| **Segmented Progress Meter**| 800ms | `steps(20, end)` | Fill 20 green/cyan blocks progressively upon card load |

---

## 6. Color Tokens (1:1 Cyan Port)

```css
:root {
  --hud-cyan-primary: #00e5ff;
  --hud-cyan-glow: rgba(0, 229, 255, 0.6);
  --hud-cyan-border: rgba(0, 229, 255, 0.35);
  --hud-cyan-faint: rgba(0, 229, 255, 0.12);
  --hud-bg-glass: rgba(4, 12, 22, 0.88);
  --hud-bg-dark: #02060c;
  --hud-text-primary: #ffffff;
  --hud-text-secondary: rgba(220, 245, 255, 0.82);
  --hud-text-muted: rgba(0, 229, 255, 0.6);
  --hud-accent-green: #00ff88;
  --hud-accent-red: #ff3366;
}
```
