# J.A.R.V.I.S. SYSTEM ARCHITECTURE SPECIFICATION
**Version:** 2.0  
**Target Environment:** Windows 10/11 Desktop (with Web/Localhost fallback)

---

## 1. High-Level Architecture Diagram

```
+---------------------------------------------------------------------------------+
|                                WINDOWS DESKTOP                                  |
|                                                                                 |
|  +---------------------------------------------------------------------------+  |
|  |                 J.A.R.V.I.S. HUD OVERLAY (WebView2 / Browser)             |  |
|  |                                                                           |  |
|  |  +--------------------+  +---------------------------------------------+  |  |
|  |  |   HOLOGRAPHIC      |  |             EXPANDED HUD DECK               |  |  |
|  |  |   J.A.R.V.I.S.     |  |                                             |  |  |
|  |  |   CYAN ORB         |  |  [Conversation] [Screen Vision] [Galaxy]    |  |  |
|  |  |  - Rotating Rings  |  |  [Skills Manager] [Memory] [Diagnostics]    |  |  |
|  |  |  - Audio Waveform  |  |  [Task Progress & Approvals] [Settings]     |  |  |
|  |  |  - State Reactive  |  +---------------------------------------------+  |  |
|  |  +--------------------+                                                   |  |
|  +--------------------------------------^------------------------------------+  |
|                                         | Local REST / WebSocket / JSON-RPC     |
+-----------------------------------------|---------------------------------------+
                                          |
+-----------------------------------------v---------------------------------------+
|                    J.A.R.V.I.S. PYTHON CORE SERVICE (:4700)                     |
|                                                                                 |
|  +-------------------------+  +----------------------+  +--------------------+  |
|  |   Agent Orchestrator    |  |  Permission Broker   |  |   Task Engine      |  |
|  |   (Intent & Planning)   |  |  (4 Risk Tiers)      |  |   (Stop / Pause)   |  |
|  +------------+------------+  +----------+-----------+  +---------+----------+  |
|               |                          |                        |             |
|  +------------v--------------------------v------------------------v----------+  |
|  |                     150-SKILL REGISTRY & DISPATCHER                       |  |
|  |                                                                           |  |
|  |  [A. Voice & NLU]         [B. Screen Vision]       [C. Desktop Control]   |  |
|  |  [D. File Intelligence]   [E. Web & Research]      [F. Knowledge Galaxy]  |  |
|  |  [G. Productivity]        [H. Coding / Dev]        [I. System & HW]       |  |
|  |  [J. Creative & Media]                                                    |  |
|  +------------+--------------------------+------------------------+----------+  |
|               |                          |                        |             |
|  +------------v------------+  +----------v-----------+  +---------v----------+  |
|  |  Perception Subsystems  |  |   OS Automation      |  |  Model Gateway     |  |
|  |  - PIL / Win32 GDI      |  |  - Win32 user32/gdi  |  |  - Gemini 3.5/3.8   |  |
|  |  - Win32 Window Enum    |  |  - PowerShell UIA    |  |  - Fish Audio TTS   |  |
|  |  - OCR Engine           |  |  - psutil Monitor    |  |  - Local Voice VAD  |  |
|  +-------------------------+  +----------------------+  +--------------------+  |
+---------------------------------------------------------------------------------+
```

---

## 2. Core Subsystems

### 2.1 The Holographic HUD Orb
- **Visual Spec**: Multilayered vector SVG & Canvas rendering.
- **Rings**: Outer ring (smooth slow clockwise orbit), secondary ring (counter-clockwise with technical tick marks), data arc ring (segmented progress), core pulse orb (reactive to real microphone audio and TTS audio playback).
- **Nine Distinct States**:
  1. `IDLE` — Subdued cyan atmospheric rotation.
  2. `LISTENING` — Active cyan pulsing, real-time microphone waveform response.
  3. `THINKING` — Multilayer multi-speed planetary rotation with processing ring.
  4. `SPEAKING` — Amplitude-synchronized waveform glow synced with audio output.
  5. `EXECUTING` — Segmented amber/cyan execution ring with progress ticks.
  6. `WAITING_FOR_APPROVAL` — Golden/amber pulse with confirmation card on deck.
  7. `ERROR` — Crimson/orange pulse with error detail and recovery guidance.
  8. `PAUSED` — Static frozen rings with prominent pause glyph.
  9. `OFFLINE` — Desaturated gray rings with reconnect status.

### 2.2 Screen Vision Subsystem
- **Full Screen Capture**: `PIL.ImageGrab` / Win32 GDI bitblt for lightning-fast capture.
- **Active Window Capture**: Enumerates windows via `user32.GetForegroundWindow` and `GetWindowRect` to grab exact target window.
- **Region Capture**: User-selectable screen coordinate bounding box.
- **Visual Question Answering**: Sends authorized screenshot directly to Gemini multimodal vision model (`gemini-3.5-flash` or `gemini-2.5-flash`) with prompt context.
- **Non-Destructive Annotation Engine**: Visual overlay rendering highlights, direction arrows, step numbers, and labels without touching source image files.

### 2.3 OS Automation & Computer Control Subsystem
- **Mouse Engine**: `ctypes.windll.user32` calls:
  - `SetCursorPos(x, y)`
  - `mouse_event(MOUSEEVENTF_LEFTDOWN | MOUSEEVENTF_LEFTUP)`
  - `mouse_event(MOUSEEVENTF_RIGHTDOWN | MOUSEEVENTF_RIGHTUP)`
  - `mouse_event(MOUSEEVENTF_WHEEL, ..., delta)`
- **Keyboard Engine**: `ctypes.windll.user32.SendInput` / `keybd_event` for typing and shortcut dispatching.
- **Window Management**: `EnumWindows`, `ShowWindow`, `SetForegroundWindow`, `MoveWindow`.
- **Application Management**: Path resolution, verified process spawning, launch verification.

### 2.4 Modular 150-Skill Registry & Execution Engine
Every skill implements:
```python
class Skill:
    id: str               # e.g., "sys_get_system_info"
    category: str         # "system", "desktop", "vision", etc.
    name: str             # "System Diagnostics"
    description: str      # Documentation of what it does
    risk_level: str       # "read_only", "reversible", "consequential", "restricted"
    requires_approval: bool
    enabled: bool
    execute: Callable[[dict], dict]
```

### 2.5 Security & Permission Broker
- 4 Risk Tiers:
  - **Tier 1 (Read-only)**: Window inspection, reading notes, diagnostics $\rightarrow$ Auto-allowed.
  - **Tier 2 (Reversible)**: Opening apps, window arranging, draft note creation $\rightarrow$ Auto-allowed, logged.
  - **Tier 3 (Consequential)**: Bulk file moves/renames, emails, script runs, deletion $\rightarrow$ Explicit user approval card with Preview.
  - **Tier 4 (Restricted)**: OS partition modification, registry wipes, credential exposure $\rightarrow$ Blocked by design.
- **Global Emergency Stop (`/stop`)**: Immediately aborts all running tasks and revokes automation locks.

### 2.6 Personal Knowledge Galaxy & Memory
- Integrated `notes/` directory scanning.
- Main Hub Orbs for every sector + dynamic company/personal detection.
- Free 3D orbit, zoom, pan, and click exploration.
- Fast keyword + semantic scoring with source note citations `[ID]`.
