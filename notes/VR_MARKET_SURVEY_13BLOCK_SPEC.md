# Reference Analysis: Download (6).mp4 (Huw Prosser Rose UI -> Jarvis Cyan 1:1 Port)
**Slice**: VR Market Survey 13-Block Report Grid, Live Bar Charts, Stacked Notes, and Maximize Card Zoom

---

## 1. Executive Summary & Scene Breakdown
- **Timestamp 00:00 - 00:03**: Standby State. Rose's kinetic orb is idling in the center of the primary display. Concentric multi-layer rings rotate with central illuminated branding (`ROSE` -> Jarvis `J.A.R.V.I.S.`). User speaks: *"Hey Rose, are you there?"*
- **Timestamp 00:04 - 00:07**: Voice Activation & Status. Rose acknowledges: *"I'm here boss. Screen's still down from the sign off, so nothing's in front of you."*
- **Timestamp 00:08 - 00:12**: Report Request. User commands: *"Can you bring up that VR report you gave me earlier?"* Rose responds: *"Let me find it. It's up, boss. Headsets, chart, the lot."*
- **Timestamp 00:13 - 00:17**: Holographic Deck Reveal & Orb Docking. The central orb smoothly scales down from ~180px to ~72px diameter and glides to the bottom-right corner (`bottom: 24px; right: 28px`). Simultaneously, an asymmetrical 13-block holographic HUD report grid cascades into view with staggered cybernetic entry transitions.
- **Timestamp 00:18 - 00:36**: Contextual Q&A & Board Telemetry. User asks: *"How many headsets are there right now across Quest 2, Quest 3, and Quest 3S?"* Rose checks live telemetry: *"Checking. Careful boss, that's not a number anyone actually has. What's on the board is 63.77%. Quest 2, Quest 3, and Quest 3S together make up that share."*
- **Timestamp 00:39 - 00:46**: Maximize Card Zoom Action. User commands: *"Can you maximize the headset share chart, please?"* The 12 background cards dim down to 15% opacity with 6px blur. Card 4 (`CHART // HEADSET MARKET SHARE 2024 H1, QUEST DOMINANCE`) smoothly zooms from its grid slot to an enlarged centered modal (~820px x 510px) over 420ms with `cubic-bezier(0.16, 1, 0.3, 1)`.
- **Timestamp 00:47 - 00:51**: Sleep & Dismissal Transition. User says: *"Lovely. Thank you very much. All right, thanks Rose. You can go to sleep again."* The maximized card and grid cards dissolve/fade out, and the mini docked orb glides back to screen center, expanding into its standby idle breathing state.

---

## 2. Pillar 1: Top Navigation Bar & Kinetic Orb Docking
### Top Navigation Bar (HUD Pills):
- **Location**: Pinned top-right corner (`top: 18px; right: 28px; z-index: 100`).
- **Button Group**:
  - `[PLAYLIST]`
  - `[PLAY]`
  - `[CLEAR HUD]`
  - `[SAVED]`
  - `[REPORT: CARDS]` (Active state: filled cyan background `rgba(0, 229, 255, 0.2)` with cyan border glow)
  - `[METADATA: DEFAULT]`
- **Styling**:
  - Dimensions: `height: 24px; padding: 2px 10px; border-radius: 12px;`
  - Font: `font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; letter-spacing: 1.2px;`
  - Colors (Jarvis Cyan): `border: 1px solid rgba(0, 229, 255, 0.4); color: #00e5ff; background: rgba(6, 15, 25, 0.6); backdrop-filter: blur(8px);`
  - Hover: `background: rgba(0, 229, 255, 0.15); box-shadow: 0 0 8px rgba(0, 229, 255, 0.3);`

### Kinetic Orb Docking Kinetics:
- **Center Idle State**:
  - Position: `top: 50%; left: 50%; transform: translate(-50%, -50%);`
  - Diameter: ~180px.
  - Structure: 3 counter-rotating SVG/Canvas rings, dashed orbital ticks, pulsing cyan core with `J.A.R.V.I.S.` text.
- **Docked State (When Report Grid is Active)**:
  - Position: `bottom: 24px; right: 28px;`
  - Diameter: ~72px (scales to 0.4x).
  - Animation: `transition: all 500ms cubic-bezier(0.16, 1, 0.3, 1);`
  - Sub-label below docked orb: `J.A.R.V.I.S. // ACTIVE` in 9px monospace.

---

## 3. Pillar 2: The 13-Block VR Market Survey Report Grid Architecture
The report canvas is laid out in an asymmetrical 4-column HUD bento grid designed for 1080p / ultrawide displays (`margin: 50px 32px 32px 32px`).

### Exact Identification of All 13 Blocks:

| # | Block Name | Grid Position | Type | Dimensions (px) | Key Content & Labels |
|---|------------|---------------|------|-----------------|----------------------|
| **1** | Executive Summary Stat | Col 1 (Top Left) | Stat Highlight | 290 x 170 | `METRICS // 2024`, Huge `100+` (44px bold), Subtitle: `TITLES GENERATING >$1M GROSS REVENUE` |
| **2** | Market Trajectory Stacked Log | Col 1 (Mid Left) | Stacked Notes | 290 x 240 | `NOTES // MARKET TRAJECTORY`, 3 timestamped milestone cards (`Q1`, `Q2`, `Q4`) with tag badges |
| **3** | Platform Telemetry & Sparkline | Col 1 (Bottom Left) | Mini Telemetry | 290 x 130 | `TELEMETRY // CONVERSION RATE`, mini sparkline + active conversion stats (`8.4%`) |
| **4** | **Quest Dominance Bar Chart** | Col 2 (Top Mid-Left) | **Live Bar Chart** | 380 x 240 | `CHART // HEADSET MARKET SHARE 2024 H1, QUEST DOMINANCE`, 6 bars, **63.77%** stat, **MAXIMIZABLE** |
| **5** | Platform MAU & Retention Chart | Col 3 (Top Mid-Right) | Live Bar Chart | 380 x 240 | `CHART // ECOSYSTEM MAU & RETENTION`, 5 platform bars (SteamVR, Meta, Viveport, PSVR, Pico) |
| **6** | Center Stage Hero Viewport | Col 2-3 (Center Mid) | Hero 16:9 Media | 520 x 210 | High-fidelity VR Corridor scene (Half-Life Alyx sci-fi environment) with HUD corner crosshairs `+` |
| **7** | Star Wars VR Graphic Banner | Col 4 (Top Right Mid) | Promo Media | 280 x 110 | `A NEW STAR WARS ADVENTURE` promotional game graphic banner |
| **8** | Meta Quest 3 Hardware Specs | Col 4 (Top Right) | Hardware Spec | 280 x 140 | Quest 3 hardware wireframe/photo with pancake lens callouts & FOV telemetry |
| **9** | VR Live Gameplay Stream Feed | Col 4 (Mid Right) | Media Stream | 280 x 130 | Real-time first-person player VR perspective feed (Beat Saber / Shooter) |
| **10** | Pancake Optical Engine Specs | Col 4 (Bottom Right) | Hardware Spec | 280 x 120 | Dual optical pancake lens schematics, focal depth & resolution metrics |
| **11** | Economics Long Tail Note Card | Col 2 (Bottom Mid-Left) | Stacked Note | 380 x 140 | `ECONOMICS: LONG TAIL MEETS LIVE SERVICE`, Steam survey retention text |
| **12** | Enterprise Premier Note Card | Col 3 (Bottom Mid-Right) | Stacked Note | 380 x 140 | `ENTERPRISE: PREMIER TREND, NOT A UNIVERSAL APEX`, $3,500+ spatial enterprise vs consumer pricing text |
| **13** | Revenue Tier Distribution Chart | Col 2 (Bottom Left-Mid) | Live Bar Chart | 380 x 150 | `CHART // REVENUE TIER DISTRIBUTION`, 5 revenue tier bars (`>$10M`, `$5M-$10M`, `$1M-$5M`, etc.) |

---

## 4. Pillar 3: Live Bar Charts Specifications (Cyan Port)
All charts feature live CSS/SVG bars, horizontal reference gridlines (25%, 50%, 75%, 100%), crisp monospace typography, and interactive hover tooltips.

### Chart 4: Quest Dominance (Steam Hardware Survey) — The Primary Showcase
- **Header**: `[CHART // HEADSET MARKET SHARE 2024 H1, QUEST DOMINANCE]`
  - Controls on Right: `[ _ ] [ 🗖 ] [ ✕ ]`
- **Data Series (6 Bars)**:
  1. `QUEST 2`: **38.4%** (Tallest bar, 150px height in unmaximized view)
  2. `QUEST 3`: **21.6%** (Second tallest, 85px)
  3. `QUEST 3S`: **3.8%** (15px) — *Note: Sum of Quest 2 + Quest 3 + Quest 3S = **63.77%***!
  4. `INDEX`: **14.2%** (Valve Index, 55px)
  5. `PSVR2`: **2.5%** (10px)
  6. `OTHER`: **19.5%** (76px)
- **Bar Visual Styling (Jarvis Cyan)**:
  - Width: 32px (normal) -> 54px (maximized).
  - Background: Vertical gradient:
    `background: linear-gradient(180deg, #00f0ff 0%, rgba(0, 229, 255, 0.45) 85%, rgba(0, 229, 255, 0.15) 100%);`
  - Cap Highlight: 2px solid white top cap `#ffffff` with cyan glow `box-shadow: 0 0 10px #00f0ff;`
  - Corner Radius: `2px 2px 0 0` (clean tech aesthetic).
  - Entrance Animation:
    ```css
    @keyframes barRise {
      from { transform: scaleY(0); }
      to { transform: scaleY(1); }
    }
    .bar { transform-origin: bottom; animation: barRise 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
    ```
- **X-Axis Labels**:
  - `QUEST 2`, `QUEST 3`, `QUEST 3S`, `INDEX`, `PSVR2`, `OTHER`
  - Font: `font-family: 'JetBrains Mono', monospace; font-size: 9.5px; font-weight: 600; color: #a5f3fc; text-align: center;`
- **Card Footer / Source Citation**:
  - Separated by `border-top: 1px solid rgba(0, 229, 255, 0.2); margin-top: 10px; padding-top: 8px;`
  - Text:
    `Steam Hardware Survey, September 2024. 63.77% share of Quest PC users with VR headsets; selected models, not worldwide sales or standalone users.`
  - Font: `font-size: 10.5px; line-height: 1.45; color: rgba(226, 232, 240, 0.8);`

### Chart 5: Ecosystem MAU & Retention
- **Header**: `[CHART // ECOSYSTEM MAU & RETENTION]`
- **Bars**: 5 platform comparative metrics (Meta Quest Store: 82%, SteamVR: 68%, PlayStation VR: 44%, Pico: 22%, Viveport: 14%).
- **Color**: Alternating Cyan `#00e5ff` and Electric Blue `#38bdf8`.

### Chart 13: Revenue Tier Distribution
- **Header**: `[CHART // REVENUE TIER DISTRIBUTION]`
- **Bars**: 5 revenue brackets (`>$10M`, `$5M-$10M`, `$1M-$5M`, `$500K-$1M`, `<$500K`).
- **Footer**: `Ecosystem revenue spread across indie and AAA studios.`

---

## 5. Pillar 4: Stacked Notes & Analysis Cards
Cards 2, 11, and 12 provide formatted intelligence notes matching Huw Prosser's tactical layout.

### Block 11: Economics Long Tail Note Card
- **Header**: `[ECONOMICS // LONG TAIL MEETS LIVE SERVICE]`
- **Content**:
  > *Steam Hardware Survey, September 2024. Quest 2 retains top volume despite successor cycle; subscription models and hybrid flat-to-VR ports driving multiplayer engagement across legacy install base.*
- **Highlight Badges**: `[SUSTAINED VOLUME]`, `[HYBRID PORTS]`.

### Block 12: Enterprise Premier Note Card
- **Header**: `[ENTERPRISE // PREMIER TREND, NOT A UNIVERSAL APEX]`
- **Content**:
  > *Enterprise spatial computing headsets remain niche enterprise tools ($3,500+ bracket), while consumer gaming consolidates around $300-$500 standalone price point.*
- **Highlight Badges**: `[$3,500+ NICHE]`, `[$300-$500 CONSUMER CONSOLIDATION]`.

### Block 2: Market Trajectory Stacked Notes
- **Header**: `[NOTES // MARKET TRAJECTORY]`
- **Card Stacking Structure**: 3 stacked rows with 1px border cards:
  - Row 1: `2024 Q1` — `Hardware subsidies accelerate entry barrier reduction`
  - Row 2: `2024 Q2` — `Mixed Reality passthrough software exceeds 30% library share`
  - Row 3: `2024 Q4` — `SteamVR wireless streaming becomes default PCVR pathway`

---

## 6. Pillar 5: Maximize Card Zoom Motion Choreography
The zoom interaction is triggered either by voice (*"Can you maximize the headset share chart, please?"*) or by clicking the maximize icon `[🗖]` or card body.

### State Transition & Timing:
1. **Trigger Phase (0ms)**:
   - Voice trigger recognized or click event dispatched on Card 4.
2. **Backdrop Dimming (0ms - 350ms)**:
   - A full-screen backdrop overlay fades in:
     `background: rgba(4, 8, 16, 0.88); backdrop-filter: blur(8px);`
   - All other 12 cards dim down to `opacity: 0.12; pointer-events: none;`
3. **Card Expansion FLIP Animation (0ms - 420ms)**:
   - Initial Rect: `width: 380px; height: 240px;` at grid offset.
   - Target Rect: `width: 840px; height: 510px;` centered at `top: 48%; left: 50%; transform: translate(-50%, -50%);`
   - Timing Curve: `cubic-bezier(0.16, 1, 0.3, 1)` (snappy cybernetic ease-out, no bounce).
   - Card Z-Index: jumps to `999`.
4. **Enhanced Data Reveal (200ms - 420ms)**:
   - Chart bars expand proportionally; gap widens to 24px; bar width increases to 54px.
   - Detailed percentage callout bubbles fade in above each bar (e.g. `38.4%`, `21.6%`, `3.8%`, `14.2%`, `2.5%`, `19.5%`).
   - Y-Axis reference grid displays labeled ticks (`0%`, `10%, `20%`, `30%`, `40%`).
   - Card Header switches to: `[CHART // HEADSET MARKET SHARE 2024 H1, QUEST DOMINANCE - EXPANDED VIEW]`.
   - Control buttons update: `[ 🗗 RESTORE ] [ ✕ CLOSE ]`.
5. **Dismiss / Restore Phase (350ms)**:
   - Triggered by voice (*"You can go to sleep again"*, *"close"*, *"restore"*) or `Escape` key.
   - Card animates back to original grid position (`350ms cubic-bezier(0.16, 1, 0.3, 1)`).
   - Backdrop overlay dissolves to `opacity: 0`.
   - If user commands sleep, all 13 cards cascade fade out (`opacity: 0; transform: scale(0.96);`), and docked mini orb glides back to screen center.

---

## 7. Pillar 6: Exact Rose -> Jarvis Cyan 1:1 Design Tokens

| Token | Rose Reference | Jarvis Cyan Port | Usage |
|---|---|---|---|
| `--hud-bg` | `#08090d` | `#040810` / `rgba(6, 15, 25, 0.85)` | Main viewport background |
| `--card-bg` | `rgba(14, 16, 22, 0.88)` | `rgba(10, 20, 34, 0.82)` | 13-block card backgrounds |
| `--card-border` | `1px solid rgba(255, 42, 95, 0.28)` | `1px solid rgba(0, 229, 255, 0.28)` | Card borders |
| `--corner-bracket` | `#ff2a5f` | `#00e5ff` / `#00ffff` | 6px x 6px corner reticles `┌ ┐ └ ┘` |
| `--accent-primary` | `#ff2a5f` (Crimson) | `#00e5ff` (Electric Cyan) | Main titles, active buttons, glow |
| `--accent-secondary`| `#ff5c8a` (Pink) | `#38bdf8` (Sky Cyan) | Secondary bars, badges |
| `--accent-glow` | `rgba(255, 42, 95, 0.45)` | `rgba(0, 229, 255, 0.45)` | Box-shadow, orb halo |
| `--text-highlight` | `#ffffff` | `#ffffff` | Big numbers (`100+`, `63.77%`), headings |
| `--text-body` | `#cbd5e1` | `#e2e8f0` | Descriptive paragraph text |
| `--text-muted` | `#64748b` | `#94a3b8` / `#a5f3fc` | Labels, axis tags, footnotes |
| `--font-mono` | `'JetBrains Mono', monospace` | `'JetBrains Mono', monospace` | Headers, pills, numbers, telemetry |
| `--font-sans` | `'Inter', sans-serif` | `'Inter', sans-serif` | Long-form notes, body copy |

### Corner Bracket HUD CSS Snippet:
```css
.hud-card {
  position: relative;
  background: rgba(10, 20, 34, 0.82);
  border: 1px solid rgba(0, 229, 255, 0.25);
  backdrop-filter: blur(14px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6), inset 0 0 12px rgba(0, 229, 255, 0.05);
}
.hud-card::before, .hud-card::after {
  content: '';
  position: absolute;
  width: 6px;
  height: 6px;
  pointer-events: none;
}
.hud-card::before {
  top: -1px; left: -1px;
  border-top: 2px solid #00e5ff;
  border-left: 2px solid #00e5ff;
}
.hud-card::after {
  bottom: -1px; right: -1px;
  border-bottom: 2px solid #00e5ff;
  border-right: 2px solid #00e5ff;
}
```

---

## 8. Summary for Swarm Implementation
- **@hud-builder**: Ensure top pill `[REPORT: CARDS]` toggles the 13-block VR deck.
- **@orb-engineer**: Bind orb docking transition: when `REPORT: CARDS` activates, orb shrinks and glides to `bottom: 24px; right: 28px;`; when dismissed, orb glides back to screen center.
- **@cards-architect**: Implement the complete 13-block bento grid using the coordinates, data points (especially **63.77%**, Quest 2/3/3S breakdown), live bar charts, stacked notes, and the 420ms centered FLIP maximize zoom on Card 4.
- **@voice-vad-engineer**: Bind natural voice triggers:
  - *"bring up that VR report"* -> Show 13-block grid
  - *"how many headsets across Quest 2, Quest 3, Quest 3S"* -> Telemetry voice response (*"63.77% share on the board"*)
  - *"maximize the headset share chart"* -> Trigger Card 4 zoom modal
  - *"go to sleep again"* -> Close modal, fade cards, return orb to idle center.
