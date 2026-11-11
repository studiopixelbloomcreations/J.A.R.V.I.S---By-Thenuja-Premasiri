# J.A.R.V.I.S. Vercel Deployment & Architecture Guide

**Target Platform:** [Vercel](https://vercel.com/)  
**Application Architecture:** Hybrid Cloud Web Frontend & Serverless AI Gateway + Local Windows Desktop Companion  
**Repository:** `https://github.com/studiopixelbloomcreations/J.A.R.V.I.S---By-Thenuja-Premasiri.git`  

---

## 1. Architectural Separation

PROJECT J.A.R.V.I.S. utilizes an intentional hybrid architecture to provide global access while strictly respecting operating system boundaries and security isolation.

```
┌────────────────────────────────────────────────────────┐
│                   VERCEL CLOUD EDGE                    │
│                                                        │
│  ┌──────────────────────┐    ┌──────────────────────┐  │
│  │ 3D Knowledge Galaxy  │    │ Serverless Gateway   │  │
│  │ Web Frontend (WebGL) │    │ (/api/chat, /skills) │  │
│  └──────────────────────┘    └──────────────────────┘  │
└───────────────────────────┬────────────────────────────┘
                            │
               Encrypted WebSocket / REST Bridge
                            │
┌───────────────────────────▼────────────────────────────┐
│              LOCAL WINDOWS PC COMPANION                │
│                                                        │
│  ┌──────────────────────┐    ┌──────────────────────┐  │
│  │ Native Win32 Desktop │    │ GDI Screen Capture   │  │
│  │ Automation (user32)  │    │ & Local Audio Engine │  │
│  └──────────────────────┘    └──────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

### A. Cloud-Compatible Components (Deploys to Vercel)
- **WebGL 3D Knowledge Galaxy:** Interactive Three.js force graph, holographic HUD vector orb, category filters, and node inspector.
- **Serverless AI Gateway (`api/index.py`):** Multi-model Gemini reasoning (`gemini-3.5-flash-lite`, `gemini-3.5-flash`, `gemini-2.5-flash`).
- **Capability Manifest (`/api/skills`):** Dynamic 150-skill catalogue discovery, search, and capability inspection.
- **Knowledge Base Retrieval:** Markdown note indexing, entity relationship links, and contextual profile grounding.
- **Companion Bridge (`/api/bridge`):** Connects cloud web clients to local desktop automation instances.

### B. Local Desktop-Only Components (Runs on Host Windows PC)
- **Native Automation:** Win32 `user32.dll` cursor positioning, clicks, Unicode typing, and allowlisted hotkeys.
- **Screen Perception:** GDI `BitBlt` and display buffer capture.
- **Window Management:** Enumeration of active desktop windows, minimize/maximize/restore, and application launcher.
- **Security Confirmation Broker:** In-memory approval modal preventing unconfirmed consequential disk actions.

---

## 2. Step-by-Step Vercel Deployment Instructions

### Step 1: Connect GitHub Repository
1. Log in to [Vercel](https://vercel.com/).
2. Click **"Add New..."** -> **"Project"**.
3. Select your GitHub repository:
   `studiopixelbloomcreations/J.A.R.V.I.S---By-Thenuja-Premasiri`
4. Click **"Import"**.

### Step 2: Configure Build Settings
Vercel automatically detects `vercel.json` and `package.json`. Confirm the following settings:
- **Framework Preset:** `Other`
- **Build Command:** `python build.py` (or `npm run build`)
- **Output Directory:** `viewer`
- **Install Command:** Leave default (or `pip install -r requirements.txt` if needed)

### Step 3: Configure Environment Variables
In the Vercel Project Settings under **Environment Variables**, add:

| Variable Name | Required | Description | Example Value |
|---|:---:|---|---|
| `GEMINI_API_KEY` | **Yes** | Google Gemini API Key | `AIzaSy...` |
| `DEFAULT_MODEL` | No | Primary reasoning model | `gemini-3.5-flash-lite` |
| `FISH_AUDIO_API_KEY` | No | Fish Audio Voice Gateway | `sk-fish-...` |
| `FISH_AUDIO_VOICE_REF` | No | Voice Reference Voice ID | `05b36da8574341d0803391491850db20` |
| `JARVIS_COMPANION_URL` | No | Local companion bridge | `http://localhost:4700` |

### Step 4: Deploy
Click **"Deploy"**. Vercel will:
1. Clone the repository.
2. Execute `python build.py` to scan notes and generate `viewer/graph-data.js`.
3. Deploy static assets from `viewer/` to the global edge network.
4. Deploy `api/index.py` as a Serverless Function on edge regions.

---

## 3. Connecting Local Windows Desktop Companion
When you access your deployed Vercel URL from your Windows computer:
1. Ensure the local JARVIS companion service is running on your machine:
   ```powershell
   python server.py
   ```
2. The web frontend automatically discovers the companion on `http://localhost:4700`.
3. When connected, screen perception, window management, and native computer control capabilities become active directly from the cloud UI!

---

## 4. Production Build Verification

To verify the production build locally before pushing:
```powershell
# Run graph builder
python build.py

# Run comprehensive test suite
python -m unittest tests/test_jarvis.py
```
Both commands must complete with exit code `0`.
