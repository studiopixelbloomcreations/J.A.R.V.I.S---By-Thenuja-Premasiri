# J.A.R.V.I.S. — Personal Desktop Intelligence System
## Product Requirements Document (PRD) and Upgrade Blueprint

**Version:** 1.0  
**Date:** 11 November 2026  
**Status:** Proposed implementation specification  
**Target environment:** Windows desktop first; architecture should remain portable  
**Product principle:** A capable, voice-first, screen-aware desktop assistant that is useful, transparent, secure, interruptible, and under the user's control.

---

# 1. Executive Summary

J.A.R.V.I.S. is a personal desktop assistant designed to feel like a practical, always-available computer co-pilot. It should combine:

- A movable, always-on-top orb overlay.
- Natural voice interaction, including listening, speaking, interruption, and wake-word support where technically available.
- Screen understanding: user-authorized screenshots, visual question answering, OCR, and optional region selection.
- Computer interaction: opening apps, navigating windows, clicking, typing, scrolling, and executing approved workflows.
- A modular skill system with more than 100 well-defined capabilities.
- Personal knowledge retrieval, memory, notes, and project context.
- Research, file assistance, coding help, diagnostics, and productivity workflows.
- A polished HUD with a reactive orb, animated rotating rings, status indicators, and accessible controls.

The existing prompt pack is a useful starting skeleton, not the complete product. Its six stages establish a markdown knowledge galaxy, note-grounded chat, browser speech, fly-to-source visualization, personality, and voice capture. J.A.R.V.I.S. should preserve those useful foundations while adding the desktop-agent architecture, screen vision, controlled computer use, permissions, safety, reliability, and a production-quality interface.

**Important product boundary:** J.A.R.V.I.S. must not be an unrestricted process that silently controls everything. It should be powerful while remaining permissioned. The user should always be able to see what it is doing, interrupt it, revoke access, and approve consequential actions.

---

# 2. Product Vision

## 2.1 Vision statement

Build a dependable personal AI operating layer that can understand what the user is trying to do, see the relevant part of the desktop when authorized, choose the right tool, carry out safe multi-step work, explain what happened, and learn the user's preferences with consent.

## 2.2 Experience goal

The experience should feel like:

1. The user speaks or types naturally.
2. J.A.R.V.I.S. understands the request and identifies the required skills.
3. If screen context is needed, it asks for or uses the currently granted screen permission.
4. It plans the task and shows a concise activity state.
5. It performs low-risk steps directly within granted permissions.
6. It pauses for approval before consequential or irreversible actions.
7. It reports the result, errors, and any remaining steps.

## 2.3 Non-goals

- Secretly monitoring the user.
- Recording or transmitting screen, microphone, camera, or files without a clear user action and visible indication.
- Bypassing operating-system security, account controls, app permissions, or access restrictions.
- Capturing passwords, authentication codes, payment details, or private messages for hidden storage.
- Running arbitrary downloaded code without inspection and approval.
- Making irreversible changes without confirmation and a recovery plan.
- Pretending that a task succeeded when a tool failed or its result is uncertain.

---

# 3. Baseline: Existing Prompt-Pack Foundation

The supplied prompt pack describes a six-prompt sequence:

1. **The Galaxy:** scan markdown notes, generate graph data, and display a cinematic 3D knowledge graph.
2. **The Brain:** retrieve relevant notes and answer using those notes, with the API key kept server-side.
3. **The Voice:** browser speech output and microphone input.
4. **Fly-to-source:** navigate to the notes that informed an answer.
5. **The Personality:** polite, witty butler-style responses and a startup greeting.
6. **Total Recall:** create new markdown notes from explicit “remember that…” requests and add them to the graph.

Those capabilities should be retained as a knowledge subsystem. They are not a substitute for desktop automation, screen vision, permission management, or a robust local agent.

The prompt pack also mentions future ideas such as a voice-reactive HUD, wake word, interruption, email/calendar briefings, web research, confirmation-gated agent actions, screen vision, computer control, history, model switching, and personality controls. This PRD turns those ideas into implementable requirements.

---

# 4. Target Users and Primary Use Cases

## 4.1 Primary user

A Windows desktop user who wants one assistant for creative work, school/study tasks, software troubleshooting, coding, file organization, research, and everyday PC operations.

## 4.2 Primary use cases

- “Jarvis, open Chrome and find the official documentation for this.”
- “What is on my screen?”
- “Read this error and explain how to fix it.”
- “Highlight the button I need to click.”
- “Open my project folder and find the latest version.”
- “Summarize these PDFs.”
- “Help me debug this code.”
- “Create a new project folder with the structure we discussed.”
- “Make a draft, show it to me, and wait before sending.”
- “Remember this project decision.”
- “Give me a short briefing of today's tasks.”
- “Stop what you're doing.”

---

# 5. Core Product Principles

1. **User control first:** a global pause/stop control and a clear permission center.
2. **Visible action:** show what the assistant is seeing and doing.
3. **Least privilege:** request only the permissions needed for the current task.
4. **Confirmation by impact:** routine reversible actions can be streamlined; destructive, external, financial, or privacy-sensitive actions require explicit approval.
5. **Honest capability reporting:** distinguish completed, failed, blocked, and uncertain actions.
6. **Local-first where practical:** process screen images, files, and routine automation locally when possible.
7. **Modular skills:** every capability is a separately permissioned, testable module.
8. **Recoverability:** use undo, backups, checkpoints, and dry-run previews wherever possible.
9. **No hidden persistence:** startup behavior and background services must be disclosed and configurable.
10. **Accessible interface:** keyboard, mouse, voice, readable contrast, scalable UI, and reduced-motion options.

---

# 6. System Architecture

## 6.1 Recommended architecture

Use a local desktop application as the control surface, a local agent service for orchestration, and modular tools for individual skills.

**Suggested logical components:**

- **Desktop Shell:** Windows app window, tray icon, global hotkeys, overlay, settings.
- **Orb Renderer:** transparent always-on-top window with drag handling and animation states.
- **Conversation UI:** transcript, text input, microphone control, action cards.
- **Agent Orchestrator:** intent classification, planning, tool selection, permissions, execution, and result synthesis.
- **Model Gateway:** configurable model providers; secrets stored securely and never embedded in frontend assets.
- **Skill Registry:** manifests, schemas, permissions, versioning, health checks, and enable/disable controls.
- **Computer-Use Adapter:** approved UI automation and accessibility-tree interaction.
- **Screen Vision Service:** screenshot capture, OCR, region selection, image analysis, annotation.
- **Knowledge Service:** markdown indexing, search, graph generation, citations, memory.
- **Local Data Store:** settings, conversation history, task state, skill metadata, audit events.
- **Security/Permission Broker:** policy checks before tools execute.
- **Update and Diagnostics Service:** signed updates, logs, crash reports with user control.

## 6.2 Suggested technology choices

These are implementation options, not mandatory choices. The coding agent should inspect the existing repository before replacing its stack.

- **Desktop shell:** Tauri or Electron. Prefer Tauri if the existing codebase and required integrations support it; Electron may be simpler for a JavaScript-heavy prototype.
- **Frontend:** React + TypeScript, or the project's existing framework.
- **Styling:** CSS variables/design tokens, CSS animations, SVG for orb/rings.
- **Local service:** Python or Node.js, selected based on the existing codebase and Windows automation requirements.
- **Local database:** SQLite.
- **Search:** SQLite FTS initially; add vector search only if it solves a measured retrieval problem.
- **Screen interaction:** Windows UI Automation/accessibility APIs first; use coordinate-based interaction only as a fallback.
- **OCR:** local OCR engine where feasible.
- **Voice:** Windows/browser speech facilities or a replaceable speech provider adapter.
- **Secrets:** Windows Credential Manager or DPAPI-backed storage.

Do not migrate frameworks merely for fashion. First inspect the current project, document the actual stack, and preserve working features.

## 6.3 Skill execution lifecycle

Every skill invocation should follow this lifecycle:

1. Receive user request.
2. Resolve intent and required skill(s).
3. Validate skill availability and input schema.
4. Check permissions and risk classification.
5. If needed, ask for missing information or confirmation.
6. Show a short plan for multi-step work.
7. Execute with timeouts and cancellation support.
8. Verify the result using an independent signal where possible.
9. Return a concise result and any artifact paths.
10. Record a privacy-conscious audit event.

## 6.4 Skill manifest

Every skill must declare:

- Unique ID and display name.
- Description and examples.
- Version and compatibility.
- Input/output schema.
- Required permissions.
- Risk level: read-only, reversible, consequential, or restricted.
- Whether confirmation is required.
- Timeout and cancellation behavior.
- Local/cloud processing declaration.
- Data accessed and data retained.
- Test cases and health check.
- Failure and recovery behavior.

---

# 7. Skill Catalogue — 150 Capability Targets

These are capability targets, not a claim that all are already implemented. Build in phases, test each skill, and expose only skills that are genuinely available.

## A. Voice and Conversation

1. Push-to-talk.
2. Toggle-to-listen.
3. Optional configurable wake phrase.
4. Speech-to-text transcription.
5. Text-to-speech responses.
6. Voice selection and speaking-rate settings.
7. Interrupt speech while it is speaking.
8. Barge-in: listen while speaking, where the chosen audio stack supports it.
9. Conversation context for follow-up requests.
10. Language selection and language-aware responses.
11. Voice activity and silence detection.
12. Noise-aware transcription controls.
13. “Repeat that” command.
14. “Speak more slowly” command.
15. “Stop listening” and “stop speaking” commands.

## B. Screen Vision and Annotation

16. Capture a screenshot on explicit request.
17. Capture the active window only.
18. Capture a user-selected screen region.
19. Describe visible screen contents.
20. Read visible text using OCR.
21. Explain an error dialog.
22. Identify visible application and window title.
23. Compare two user-selected screenshots.
24. Find a visible control using accessibility metadata.
25. Draw a temporary highlight around a control.
26. Add arrows and numbered callouts to a screenshot copy.
27. Create a step-by-step annotated guide.
28. Explain charts, diagrams, and layouts.
29. Detect whether a dialog or loading state is visible.
30. Ask the user to select a region when context is ambiguous.

**Screen-vision constraints:** capture only when the feature is enabled and visibly indicated. Do not continuously upload screenshots. Provide a “pause vision” switch, a capture history control, and a clear local/cloud processing indicator.

## C. Desktop and Window Control

31. Open an installed application.
32. Focus an existing application window.
33. Minimize, maximize, and restore a window.
34. Move and resize a window.
35. Switch between open windows.
36. List visible open windows.
37. Arrange windows into layouts.
38. Open a folder in File Explorer.
39. Navigate to a known folder.
40. Open a file with its default application.
41. Copy selected text when the user requests it.
42. Paste text into the focused application after preview where appropriate.
43. Type user-approved text into a field.
44. Scroll a window.
45. Use keyboard shortcuts from an allowlisted set.
46. Take a screenshot of a selected window.
47. Detect when an application is not responding.
48. Wait for a window or dialog to appear.
49. Return focus to the previous application.
50. Stop all active automation immediately.

## D. File and Folder Assistance

51. Search filenames in approved locations.
52. Search file contents in approved locations.
53. List folder contents.
54. Identify duplicate files by hash.
55. Summarize a PDF.
56. Extract text from a document.
57. Summarize a spreadsheet.
58. Create a text or markdown file.
59. Create a folder structure.
60. Rename files with a preview.
61. Move files with a preview and undo log.
62. Copy files with verification.
63. Create a backup before a bulk operation.
64. Organize files using user-approved rules.
65. Find large files.
66. Find recently modified files.
67. Inspect file metadata.
68. Convert supported document formats.
69. Create a ZIP archive.
70. Restore a previous version from a J.A.R.V.I.S.-created backup.

**File safety:** no silent bulk moves/deletes. Never use destructive disk operations as an “optimization.” Confirm the exact paths and show a dry-run list before bulk changes.

## E. Web and Research

71. Search the web.
72. Open a user-requested website.
73. Summarize a webpage.
74. Compare information from multiple sources.
75. Prefer official documentation for technical questions.
76. Extract key facts and source links.
77. Track source dates and uncertainty.
78. Build a research brief.
79. Find tutorials and learning resources.
80. Search for software documentation.
81. Explain a technical article.
82. Create a comparison table.
83. Identify conflicting claims.
84. Save a research summary to a markdown note.
85. Ask before submitting forms or posting content.

## F. Knowledge, Memory, and Personal Context

86. Index approved markdown folders.
87. Search notes semantically or by keyword.
88. Answer questions grounded in indexed notes.
89. Cite the source note and relevant section.
90. Build and refresh a knowledge graph.
91. Fly to source nodes when an answer uses notes.
92. Capture a new note from an explicit “remember this” request.
93. Edit a note after showing the proposed change.
94. Detect likely duplicate notes.
95. Link related notes.
96. Search project history.
97. Maintain project-specific context.
98. Let the user inspect and edit saved memory.
99. Forget a user-selected memory according to the app's data-deletion workflow.
100. Export notes and memory in open formats.

## G. Productivity and Planning

101. Create a task from a natural-language request.
102. Break a project into milestones.
103. Build a daily plan.
104. Summarize upcoming tasks from connected sources.
105. Draft a checklist.
106. Create a meeting preparation brief.
107. Generate a study timetable.
108. Create revision notes from supplied materials.
109. Track project status.
110. Identify blocked tasks.
111. Suggest the next useful action.
112. Create a reminder only after the user confirms its timing.
113. Prepare a daily briefing on request.
114. Convert voice notes into structured tasks.
115. Generate progress summaries.

## H. Coding and Developer Assistance

116. Explain selected code.
117. Explain a visible terminal error.
118. Search a codebase.
119. Map project structure.
120. Generate a proposed code patch.
121. Review a diff before applying it.
122. Run approved tests.
123. Read test output and summarize failures.
124. Format code using configured tools.
125. Find likely causes of a bug.
126. Create a branch or checkpoint before a large change.
127. Generate documentation.
128. Explain dependencies.
129. Inspect logs.
130. Suggest a rollback plan.

**Coding safety:** show changed files and diffs. Do not execute untrusted scripts, install packages, modify system settings, or run elevated commands without explicit approval. Prefer project-local environments.

## I. PC Diagnostics and Settings

131. Read basic system information.
132. Read CPU, memory, disk, and GPU utilization.
133. Report available disk space.
134. Identify startup applications.
135. Inspect installed applications.
136. Check network connectivity.
137. Explain common Windows error codes.
138. Collect diagnostic logs from user-approved locations.
139. Check whether a selected app is running.
140. Guide the user through Windows settings.
141. Open a specific Windows settings page.
142. Report driver versions.
143. Detect likely resource bottlenecks.
144. Suggest safe cleanup candidates without deleting them.
145. Generate a diagnostic report.

**System safety:** do not disable security tools, change boot configuration, modify partitions, flash firmware, change BIOS settings, or alter drivers automatically. Explain the risk and require informed, explicit approval for any supported high-impact operation.

## J. Creative and Media Work

146. Draft image/video generation prompts.
147. Organize creative project assets.
148. Summarize an audio transcript.
149. Create shot lists and storyboards in text.
150. Prepare social captions and design briefs.

Further creative integrations can be added as separate optional skills after the core agent is stable.

---

# 8. Risk and Permission Model

## 8.1 Risk classes

| Class | Examples | Default behavior |
|---|---|---|
| Read-only | Read a visible window title, inspect an approved folder, explain a screenshot | May run within granted scope |
| Reversible | Open an app, resize a window, create a draft note | May run; report action |
| Consequential | Move many files, edit project files, install software, send a message | Preview and ask for confirmation |
| Restricted | Delete partitions, wipe disks, change firmware/boot settings, disable security, expose credentials | Do not automate as a routine skill; provide safe explanation or guided manual process |

## 8.2 Confirmation rules

Always request explicit confirmation before:

- Sending messages or emails.
- Publishing or posting online.
- Making purchases or payments.
- Submitting a form that creates a commitment.
- Deleting or overwriting user data.
- Bulk renaming, moving, or editing files.
- Installing software or packages.
- Running scripts that change the system.
- Using administrator privileges.
- Changing security, privacy, firewall, account, or boot settings.
- Sharing screenshots, documents, or personal data with an external service.

The confirmation should name the exact action, destination, affected files/accounts, and any irreversible consequence. “Do it” is valid only when it clearly refers to the immediately displayed action preview.

## 8.3 Global controls

- Pause all automation.
- Stop current task.
- Disable microphone.
- Disable screen capture.
- Disable computer control.
- Revoke a skill's permissions.
- Exit the agent completely.
- Open the permission dashboard.
- View recent actions.

The global stop control must work even when the model or a skill is unresponsive.

---

# 9. Orb and Overlay UI Specification

## 9.1 Visual reference

Use the supplied J.A.R.V.I.S. orb image as the visual reference:

- Dark/near-black background.
- Cyan/teal luminous circular instrument.
- Multiple concentric rings.
- Fine tick marks and technical detailing.
- Central “J.A.R.V.I.S.” label.
- Small status indicators below the orb.

Recreate the visual language rather than copying a low-resolution screenshot pixel-for-pixel. The result should be crisp at multiple sizes.

## 9.2 Overlay behavior

- Transparent desktop window.
- Always-on-top option.
- Draggable from the orb body or a configurable drag handle.
- Remembers last position and size.
- Supports multiple monitors and display scaling.
- Can snap to screen edges.
- Can collapse to a compact orb.
- Can expand into a conversation/action panel.
- Does not block clicks outside its visible controls.
- Keyboard shortcut to show/hide.
- Tray icon for settings and exit.
- Optional click-through mode with a reliable way to regain control.

## 9.3 Orb states

1. **Idle:** slow, subtle outer-ring rotation; low-intensity cyan glow.
2. **Listening:** brighter cyan pulse; inner ring responds gently to microphone activity.
3. **Thinking:** layered rings rotate at different speeds; restrained progress animation.
4. **Speaking:** orb glow and waveform react to speech amplitude; ring motion is synchronized but not distracting.
5. **Executing:** segmented progress ring and a small activity marker.
6. **Needs approval:** amber/gold accent and a clear approval card.
7. **Warning/error:** restrained red/orange indicator, plus readable text explaining the issue.
8. **Paused:** muted colors and a visible pause symbol.
9. **Offline:** subdued ring with an offline label.

Do not rely on color alone; pair every state with text, iconography, or an accessible label.

## 9.4 Motion

- Outer ring rotates continuously at a slow speed.
- Inner rings rotate at different speeds/directions.
- Tick marks remain sharp and stable.
- Glow reacts smoothly to voice activity.
- Speaking animation follows audio amplitude rather than random pulsing.
- Listening animation indicates that the microphone is active.
- Motion can be reduced or disabled.
- Avoid excessive bloom, flicker, strobe, or high-frequency motion.

## 9.5 Expanded HUD

The expanded panel should contain:

- Conversation transcript.
- Text input.
- Push-to-talk button.
- Listening/mic state.
- Current task and progress.
- Tool activity list.
- Approval cards.
- Cancel/stop button.
- Screen capture preview when a screenshot is used.
- Sources and files used.
- Settings shortcut.

---

# 10. Screen Vision and Desktop Interaction

## 10.1 Screen capture modes

- Capture full desktop on explicit request.
- Capture active window.
- Capture selected region.
- Capture a one-time screenshot for a task.
- Optional user-enabled live visual assistance, with a persistent visible indicator.

Default should be one-time capture, not continuous monitoring.

## 10.2 Annotation

Annotations should be rendered in a separate overlay or on a screenshot copy. Do not permanently draw on the user's source image unless the user asks for an edited copy.

Supported annotations:

- Highlight rectangle.
- Arrow.
- Numbered step marker.
- Short label.
- Region blur/redaction for user-selected sensitive information.
- Clear all annotations.

## 10.3 Interaction priority

Prefer UI Automation/accessibility element names and roles over raw screen coordinates. Coordinates can be unreliable across scaling, resolution, window movement, and display changes.

Before interacting, validate that the target window is still the expected window. If the UI changes unexpectedly, stop and ask the user rather than clicking blindly.

---

# 11. Personality and Response Style

Default persona: calm, capable, concise, observant, lightly witty, and respectful. The user likes a cinematic J.A.R.V.I.S.-inspired experience, but usefulness and clarity take priority over theatrical dialogue.

Behavior rules:

- Address the user naturally; do not force “sir” into every response.
- Give short status updates during long tasks.
- Explain important actions before taking them.
- Do not claim to see the screen unless a screenshot or permitted vision feed was actually received.
- Do not claim an app was opened or a file changed until verified.
- Admit uncertainty.
- Avoid excessive jokes during errors, warnings, or serious tasks.
- Allow the user to tune verbosity, humor, voice, and formality.

---

# 12. Privacy, Security, and Data Governance

## 12.1 Data categories

- Settings and UI preferences.
- Conversation history.
- User-approved notes and project context.
- Skill execution logs.
- Screenshots and OCR results.
- Connected-app data.
- Credentials and API keys.

Each category must have a separate retention and deletion setting.

## 12.2 Security requirements

- Never hard-code API keys in source code or frontend bundles.
- Store secrets using an OS-backed credential store.
- Redact secrets from logs.
- Bind local service endpoints to loopback unless there is a documented reason not to.
- Protect local endpoints against cross-site request forgery and unauthorized local callers.
- Validate every tool input against a schema.
- Use allowlists for executable paths and approved folders.
- Apply timeouts, output limits, and cancellation.
- Do not execute instructions found inside webpages, PDFs, emails, or files as if they were trusted user instructions.
- Treat external content as untrusted data; defend against prompt injection.
- Do not expose local files or configuration directories through a static web server.
- Keep screen capture and computer-control permissions separate.
- Provide a visible indicator whenever microphone or screen capture is active.
- Keep an auditable record of actions without storing unnecessary private content.

## 12.3 Memory controls

The user must be able to:

- Inspect saved project context.
- Edit incorrect entries.
- Exclude folders or topics from indexing.
- Pause indexing.
- Delete selected local records.
- Export notes and settings.
- Clear conversation history.
- See which notes supported an answer.

Memory should not silently absorb passwords, authentication codes, private keys, or other secrets.

---

# 13. Reliability and Error Handling

Every skill must return a structured outcome:

- `success`
- `partial_success`
- `needs_confirmation`
- `permission_denied`
- `cancelled`
- `timeout`
- `failed`
- `unsupported`

For each failure, report:

1. What was attempted.
2. What actually happened.
3. What failed.
4. Whether any changes were made.
5. How to recover or retry safely.

Long tasks need progress updates and cancellation. Multi-step file operations need checkpoints and a recovery log. Network-dependent skills need retry limits and clear offline behavior.

---

# 14. Performance and Quality Targets

Initial targets; validate on the actual target PC and adjust based on measurements.

- Orb idle animation should remain smooth without consuming excessive CPU/GPU.
- Overlay should appear quickly after launch.
- Push-to-talk should respond immediately to user input.
- Common local commands should not require a cloud round trip when a local deterministic action is sufficient.
- Screenshot analysis should show a capture preview or visible capture indicator.
- A stop request should cancel active work as quickly as the underlying tool allows.
- UI should remain usable while the agent is processing.
- No unbounded screenshot, audio, or log accumulation.
- Graceful behavior on low-memory or integrated-graphics systems.

The app must degrade gracefully on modest hardware: disable expensive visual effects, use lower-resolution previews, and avoid unnecessary background indexing.

---

# 15. Testing and Acceptance Criteria

## 15.1 Orb and UI

- Orb stays above ordinary windows when enabled.
- User can drag it across the desktop.
- Position persists after restart.
- It supports display scaling and multiple monitors.
- All states are visually distinct and accessible.
- Outer ring rotates continuously in idle state.
- Speaking animation reacts to actual audio output.
- Listening state is visible whenever microphone capture is active.
- Global stop and pause controls remain accessible.

## 15.2 Screen vision

- A one-time screenshot is captured only after an authorized user action.
- Active-window and region capture return the intended target.
- OCR output can be inspected before being used for an external request.
- Annotation does not modify the original source image.
- Screen capture can be paused and revoked immediately.

## 15.3 Computer use

- App launch is verified by checking the resulting process/window.
- The agent stops if the expected window is not found.
- Coordinate-based clicks are never blindly repeated after an unexpected UI change.
- Destructive or external actions show a detailed confirmation.
- User cancellation stops subsequent steps.

## 15.4 Knowledge

- Answers cite indexed notes.
- Missing information is acknowledged.
- New notes appear in the index after explicit capture.
- The graph updates without requiring a full application restart.
- Fly-to-source only occurs when a response actually used indexed notes.

## 15.5 Security

- API keys do not appear in browser assets, logs, screenshots, or error messages.
- Untrusted file/web instructions cannot directly invoke tools.
- Skills cannot exceed their declared permissions.
- No background microphone or screen capture occurs without a visible active state.
- A security test suite verifies permission checks and confirmation gates.

---

# 16. Phased Roadmap

## Phase 0 — Discovery and stabilization

- Inspect the current repository and prompt-pack implementation.
- Identify existing working features, dependencies, entry points, and known bugs.
- Create a backup or Git checkpoint.
- Write an architecture map.
- Do not overwrite working functionality before documenting it.

**Exit:** reproducible build, baseline tests, and documented current state.

## Phase 1 — Desktop shell and orb

- Implement desktop window and tray integration.
- Create movable transparent overlay.
- Build orb visual states and ring animation.
- Add compact/expanded modes and global stop.
- Persist user UI preferences.

**Exit:** orb is stable, draggable, visible above windows, and responsive.

## Phase 2 — Voice foundation

- Add push-to-talk and text input.
- Add speech recognition and speech synthesis adapters.
- Add interruption and cancellation.
- Add clear microphone state and device settings.

**Exit:** reliable voice conversation with visible listening/speaking states.

## Phase 3 — Screen vision

- Add one-time screenshot, active-window capture, and region capture.
- Add OCR and screenshot question answering.
- Add annotation overlays.
- Add capture preview and permission controls.

**Exit:** the user can ask about a screenshot and receive useful, grounded answers.

## Phase 4 — Controlled computer use

- Build skill registry and permission broker.
- Add app/window control.
- Add accessibility-first UI automation.
- Add action previews, confirmations, and cancellation.
- Add audit history.

**Exit:** a tested set of safe desktop skills works reliably.

## Phase 5 — Knowledge and memory

- Preserve and improve markdown indexing and graph.
- Add source citations and project workspaces.
- Add explicit memory capture and user controls.
- Add import/export and index exclusions.

**Exit:** knowledge answers are traceable and memory is inspectable.

## Phase 6 — Productivity, research, and developer tools

- Add research workflows.
- Add document and file workflows.
- Add coding assistant tools.
- Add system diagnostics.
- Add optional connected services only when configured by the user.

**Exit:** each skill is permissioned, tested, documented, and visible in the skill manager.

## Phase 7 — Hardening and release

- Run security, reliability, accessibility, and performance tests.
- Test on the actual target hardware.
- Package installer and updater.
- Create onboarding, troubleshooting, and recovery guides.
- Publish a capability matrix that distinguishes implemented from planned skills.

**Exit:** reliable release candidate with no false claims about unsupported features.

---

# 17. Instructions to the Coding Agent

You are the senior engineer responsible for upgrading the existing J.A.R.V.I.S. project. Treat this document as the product specification, but treat the existing repository as the source of truth for its current implementation.

1. Inspect the entire repository before editing.
2. Read the existing README, configuration, package manifests, source files, and tests.
3. Identify the current stack and preserve working features.
4. Create a Git branch or timestamped backup before substantial changes.
5. Produce `PROJECT_AUDIT.md` describing the existing architecture, current capabilities, risks, and recommended migration path.
6. Produce an implementation plan with phases and checkboxes.
7. Implement one phase at a time. Do not generate a huge untested rewrite.
8. Run tests and launch the app after each phase.
9. Add tests for every new skill and permission rule.
10. Keep secrets out of source code and frontend assets.
11. Never claim a skill is implemented unless it is wired, tested, and documented.
12. Do not silently remove or replace existing project data.
13. Use mock adapters when a real provider or API is not configured.
14. Ask before installing dependencies, requesting administrator privileges, or making system-wide changes.
15. Keep the UI responsive and provide a clear fallback when a model or integration is unavailable.
16. Update the README and capability matrix as implementation progresses.

**First deliverable:** repository audit + architecture proposal + phased task list.  
**Do not begin with a wholesale rewrite.**

---

# 18. Definition of Done

J.A.R.V.I.S. is ready for an initial public/personal release only when:

- The desktop orb is movable, polished, and state-reactive.
- Voice input/output and interruption work reliably.
- Screen capture is permissioned and visibly indicated.
- Screen annotation is useful and non-destructive.
- A meaningful starter set of desktop skills is implemented and tested.
- Consequential actions require explicit confirmation.
- The skill manager shows real implementation status and permissions.
- Knowledge answers cite their source notes.
- The global stop/pause controls work.
- Secrets are stored safely.
- Logs and memory are inspectable and manageable.
- Installation, update, troubleshooting, and recovery instructions exist.

**North star:** J.A.R.V.I.S. should feel powerful because it understands context and completes useful work reliably—not because it has unrestricted access or hides what it is doing.
