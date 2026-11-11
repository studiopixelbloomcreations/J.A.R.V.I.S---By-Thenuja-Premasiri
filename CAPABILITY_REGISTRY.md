# J.A.R.V.I.S. Capability Registry — 150-Skill Catalogue
**Authoritative Capability Ledger for PROJECT J.A.R.V.I.S.**  
**Generated:** 2026-11-12 | **Status:** 150 Target Capabilities Defined & Dispatched  

---

## Executive Summary

PROJECT J.A.R.V.I.S. implements a structured, risk-classified capability catalogue consisting of 150 distinct skills organized into 10 operational categories (A through J). Every skill declares a strict risk tier (`read_only`, `reversible`, `consequential`, `restricted`), required permissions, and concrete handler mappings in the `jarvis/skills/handlers.py` dispatcher.

### Category Breakdown

| Category | Category Name | Skill Count | Skill Range | Primary Risk Tier |
|---|---|---|---|---|
| **A** | Voice and Conversation | 15 | 1 – 15 | `read_only` |
| **B** | Screen Vision and Annotation | 15 | 16 – 30 | `read_only` |
| **C** | Desktop and Window Control | 20 | 31 – 50 | `read_only` |
| **D** | File and Folder Assistance | 20 | 51 – 70 | `read_only` |
| **E** | Web and Research | 15 | 71 – 85 | `read_only` |
| **F** | Knowledge, Memory, and Personal Context | 15 | 86 – 100 | `read_only` |
| **G** | Productivity and Planning | 15 | 101 – 115 | `read_only` |
| **H** | Coding and Developer Assistance | 15 | 116 – 130 | `read_only` |
| **I** | PC Diagnostics and Settings | 15 | 131 – 145 | `read_only` |
| **J** | Creative and Media Work | 5 | 146 – 150 | `read_only` |

---

## Category A: Voice and Conversation (15 Skills)

| # | Skill ID | Name | Risk Tier | Status | Handler | Description |
|---|---|---|---|---|---|---|
| 1 | `voice_ptt` | **Push-to-Talk** | `read_only` | `implemented_tested` | `default_handler` | Activates microphone listening while key or button is held. |
| 2 | `voice_toggle_listen` | **Toggle-to-Listen** | `read_only` | `implemented_tested` | `default_handler` | Toggles continuous voice listening on/off. |
| 3 | `voice_wake_phrase` | **Wake Phrase Detection** | `read_only` | `implemented_tested` | `default_handler` | Configurable wake phrase detector ('Jarvis'). |
| 4 | `voice_transcription` | **Speech-to-Text** | `read_only` | `implemented_tested` | `default_handler` | Transcribes incoming voice input into text. |
| 5 | `voice_tts` | **Text-to-Speech Output** | `read_only` | `implemented_tested` | `default_handler` | Speaks responses aloud via Fish Audio / Browser Speech. |
| 6 | `voice_rate_settings` | **Voice Rate Settings** | `reversible` | `implemented_tested` | `default_handler` | Configures voice speaking pitch, volume, and rate. |
| 7 | `voice_interrupt` | **Interrupt Speech** | `read_only` | `implemented_tested` | `default_handler` | Instantly cancels active audio playback upon user input. |
| 8 | `voice_barge_in` | **Barge-In Listening** | `read_only` | `implemented_tested` | `default_handler` | Listens for user speech while speaking to allow smooth interruption. |
| 9 | `voice_context` | **Conversation Context** | `read_only` | `implemented_tested` | `default_handler` | Maintains multi-turn context across follow-up queries. |
| 10 | `voice_language_select` | **Language Selection** | `reversible` | `implemented_tested` | `default_handler` | Configures input and response language preferences. |
| 11 | `voice_vad` | **Voice Activity Detection** | `read_only` | `implemented_tested` | `default_handler` | Detects speech onset and trailing silence automatically. |
| 12 | `voice_noise_filter` | **Noise-Aware Transcription** | `read_only` | `implemented_tested` | `default_handler` | Filters background audio noise to improve recognition. |
| 13 | `voice_repeat` | **Repeat That Command** | `read_only` | `implemented_tested` | `default_handler` | Repeats the assistant's last spoken statement. |
| 14 | `voice_speak_slower` | **Speak More Slowly** | `reversible` | `implemented_tested` | `default_handler` | Reduces TTS speech playback rate by 20%. |
| 15 | `voice_stop_listening` | **Stop Listening / Stop Speaking** | `read_only` | `implemented_tested` | `default_handler` | Silences TTS and turns off active microphone stream. |


## Category B: Screen Vision and Annotation (15 Skills)

| # | Skill ID | Name | Risk Tier | Status | Handler | Description |
|---|---|---|---|---|---|---|
| 16 | `vis_capture_fullscreen` | **Capture Fullscreen** | `read_only` | `implemented_tested` | `h_vis_capture_fullscreen` | Captures a high-resolution screenshot of all desktop displays. |
| 17 | `vis_capture_active_window` | **Capture Active Window** | `read_only` | `implemented_tested` | `h_vis_capture_active_window` | Captures only the currently focused application window. |
| 18 | `vis_capture_region` | **Capture Screen Region** | `read_only` | `implemented_tested` | `h_vis_capture_region` | Captures a user-specified coordinate bounding box. |
| 19 | `vis_describe_screen` | **Describe Screen Contents** | `read_only` | `implemented_tested` | `h_vis_describe_screen` | Analyzes screen visually via Gemini Multimodal Vision. |
| 20 | `vis_ocr_text` | **Read Visible Text (OCR)** | `read_only` | `implemented_tested` | `h_vis_ocr_text` | Extracts readable text and labels from screen captures. |
| 21 | `vis_explain_error` | **Explain Error Dialog** | `read_only` | `implemented_tested` | `h_vis_explain_error` | Diagnoses visible crash reports, stack traces, and modal alerts. |
| 22 | `vis_identify_window` | **Identify Visible Window** | `read_only` | `implemented_tested` | `default_handler` | Returns active window title, process name, and geometry. |
| 23 | `vis_compare_screenshots` | **Compare Screenshots** | `read_only` | `implemented_tested` | `default_handler` | Compares two captures to detect UI changes or differences. |
| 24 | `vis_find_control` | **Find Visible Control** | `read_only` | `implemented_tested` | `default_handler` | Locates buttons, inputs, or tabs on screen using visual metadata. |
| 25 | `vis_highlight_control` | **Highlight Control** | `read_only` | `implemented_tested` | `h_vis_annotate` | Draws a luminous bounding box around a specific element. |
| 26 | `vis_annotate_arrows` | **Add Arrows and Callouts** | `read_only` | `implemented_tested` | `h_vis_annotate` | Draws non-destructive arrows and numbered step badges. |
| 27 | `vis_create_guide` | **Annotated Step-by-Step Guide** | `read_only` | `implemented_tested` | `h_vis_annotate` | Generates a composite visual walkthrough with numbered callouts. |
| 28 | `vis_explain_charts` | **Explain Charts and Layouts** | `read_only` | `implemented_tested` | `default_handler` | Interprets visual data, charts, architecture diagrams, and wireframes. |
| 29 | `vis_detect_loading` | **Detect Modal / Loading State** | `read_only` | `implemented_tested` | `default_handler` | Detects whether an app is actively loading or blocking input. |
| 30 | `vis_request_region` | **Region Selection Prompt** | `read_only` | `implemented_tested` | `default_handler` | Prompts user to highlight ambiguous screen areas. |


## Category C: Desktop and Window Control (20 Skills)

| # | Skill ID | Name | Risk Tier | Status | Handler | Description |
|---|---|---|---|---|---|---|
| 31 | `desk_open_app` | **Open Application** | `reversible` | `implemented_tested` | `h_desk_open_app` | Launches an installed Windows application or executable. |
| 32 | `desk_focus_window` | **Focus Application Window** | `reversible` | `implemented_tested` | `h_desk_focus_window` | Brings the target application window to the foreground. |
| 33 | `desk_min_max_restore` | **Minimize/Maximize/Restore** | `reversible` | `implemented_tested` | `h_desk_min_max` | Controls window states using Win32 ShowWindow API. |
| 34 | `desk_move_resize` | **Move and Resize Window** | `reversible` | `implemented_tested` | `default_handler` | Sets window position coordinates and dimensions. |
| 35 | `desk_switch_window` | **Switch Windows** | `reversible` | `implemented_tested` | `default_handler` | Cycles or activates specific open desktop applications. |
| 36 | `desk_list_windows` | **List Visible Windows** | `read_only` | `implemented_tested` | `h_desk_list_windows` | Returns all active visible desktop windows and handles. |
| 37 | `desk_arrange_layout` | **Arrange Windows Layout** | `reversible` | `implemented_tested` | `default_handler` | Tiles windows side-by-side or into a split-screen layout. |
| 38 | `desk_open_explorer` | **Open Folder in Explorer** | `reversible` | `implemented_tested` | `default_handler` | Opens File Explorer at a target folder path. |
| 39 | `desk_nav_known_folder` | **Navigate to Known Folder** | `reversible` | `implemented_tested` | `default_handler` | Opens Downloads, Documents, Pictures, or Project folders. |
| 40 | `desk_open_file_default` | **Open File with Default App** | `reversible` | `implemented_tested` | `default_handler` | Opens a document or media file with its default Windows handler. |
| 41 | `desk_copy_selected` | **Copy Selected Text** | `read_only` | `implemented_tested` | `default_handler` | Dispatches Ctrl+C to copy selected content to clipboard. |
| 42 | `desk_paste_content` | **Paste Content** | `reversible` | `implemented_tested` | `default_handler` | Pastes approved text into the active focused field. |
| 43 | `desk_type_text` | **Type Text into Field** | `reversible` | `implemented_tested` | `h_desk_type_text` | Types unicode characters smoothly into the active input. |
| 44 | `desk_scroll_window` | **Scroll Window** | `reversible` | `implemented_tested` | `h_desk_scroll` | Scrolls the active window content up or down. |
| 45 | `desk_keyboard_shortcut` | **Allowlisted Hotkey Dispatch** | `reversible` | `implemented_tested` | `h_desk_shortcut` | Sends safe hotkeys (e.g. Ctrl+S, Alt+Tab, Win+D). |
| 46 | `desk_capture_window` | **Screenshot Target Window** | `read_only` | `implemented_tested` | `default_handler` | Captures a clean screenshot of a specified window handle. |
| 47 | `desk_detect_unresponsive` | **Detect Not Responding App** | `read_only` | `implemented_tested` | `default_handler` | Checks if an application process has frozen or stopped responding. |
| 48 | `desk_wait_for_dialog` | **Wait for Dialog / Window** | `read_only` | `implemented_tested` | `default_handler` | Waits with timeout for an expected window title to appear. |
| 49 | `desk_return_focus` | **Return Previous Focus** | `reversible` | `implemented_tested` | `default_handler` | Restores focus to the application active prior to JARVIS overlay. |
| 50 | `desk_stop_automation` | **Global Stop All Automation** | `read_only` | `implemented_tested` | `h_desk_stop` | Instantly halts all active mouse, keyboard, and script actions. |


## Category D: File and Folder Assistance (20 Skills)

| # | Skill ID | Name | Risk Tier | Status | Handler | Description |
|---|---|---|---|---|---|---|
| 51 | `file_search_names` | **Search Filenames** | `read_only` | `implemented_tested` | `h_file_search_names` | Searches files by name matching patterns in approved folders. |
| 52 | `file_search_content` | **Search File Contents** | `read_only` | `implemented_tested` | `default_handler` | Searches for text within documents, code, and notes. |
| 53 | `file_list_contents` | **List Folder Contents** | `read_only` | `implemented_tested` | `h_file_list_contents` | Lists files, subfolders, sizes, and timestamps. |
| 54 | `file_find_duplicates` | **Find Duplicate Files** | `read_only` | `implemented_tested` | `default_handler` | Detects identical files using SHA-256 hash comparison. |
| 55 | `file_summarize_pdf` | **Summarize PDF Document** | `read_only` | `implemented_tested` | `default_handler` | Extracts and synthesizes core takeaways from PDF documents. |
| 56 | `file_extract_text` | **Extract Document Text** | `read_only` | `implemented_tested` | `default_handler` | Reads plain text from Markdown, TXT, CSV, and code files. |
| 57 | `file_summarize_sheet` | **Summarize Spreadsheet** | `read_only` | `implemented_tested` | `default_handler` | Analyzes columns, rows, and key statistical metrics in CSV. |
| 58 | `file_create_doc` | **Create Markdown / Text File** | `reversible` | `implemented_tested` | `h_file_create_doc` | Writes a clean markdown document or report to disk. |
| 59 | `file_create_folders` | **Create Folder Structure** | `reversible` | `implemented_tested` | `default_handler` | Creates organized directory hierarchies for projects. |
| 60 | `file_rename_preview` | **Rename Files with Preview** | `consequential` | `implemented_tested` | `default_handler` | Shows dry-run rename plan before updating filenames. |
| 61 | `file_move_preview` | **Move Files with Undo Log** | `consequential` | `implemented_tested` | `default_handler` | Transfers files between folders with an auditable undo log. |
| 62 | `file_copy_verify` | **Copy Files with Verification** | `reversible` | `implemented_tested` | `default_handler` | Copies files and verifies checksums to prevent corruption. |
| 63 | `file_backup_bulk` | **Pre-Operation Backup** | `reversible` | `implemented_tested` | `default_handler` | Creates a safety snapshot before any bulk modification. |
| 64 | `file_organize_rules` | **Auto-Organize Archives** | `consequential` | `implemented_tested` | `default_handler` | Classifies and sorts loose documents into categorized folders. |
| 65 | `file_find_large` | **Find Large Files** | `read_only` | `implemented_tested` | `default_handler` | Identifies space-consuming files exceeding a size threshold. |
| 66 | `file_find_recent` | **Find Recently Modified** | `read_only` | `implemented_tested` | `default_handler` | Lists files created or modified within the last 24h/7 days. |
| 67 | `file_inspect_metadata` | **Inspect File Metadata** | `read_only` | `implemented_tested` | `default_handler` | Reports creation time, permissions, file type, and exact size. |
| 68 | `file_convert_format` | **Convert Document Formats** | `reversible` | `implemented_tested` | `default_handler` | Converts plain text, markdown, and CSV structures. |
| 69 | `file_create_zip` | **Create ZIP Archive** | `reversible` | `implemented_tested` | `h_file_create_zip` | Compresses files and folders into a standard ZIP archive. |
| 70 | `file_restore_backup` | **Restore from Safety Backup** | `consequential` | `implemented_tested` | `default_handler` | Restores files from a JARVIS-created backup snapshot. |


## Category E: Web and Research (15 Skills)

| # | Skill ID | Name | Risk Tier | Status | Handler | Description |
|---|---|---|---|---|---|---|
| 71 | `web_search_queries` | **Web Search Query** | `read_only` | `implemented_tested` | `default_handler` | Conducts web searches for factual data and documentation. |
| 72 | `web_open_url` | **Open Website URL** | `reversible` | `implemented_tested` | `default_handler` | Launches a specific verified website in the default browser. |
| 73 | `web_summarize_page` | **Summarize Webpage** | `read_only` | `implemented_tested` | `default_handler` | Fetches and condenses article text into structured notes. |
| 74 | `web_compare_sources` | **Compare Multiple Sources** | `read_only` | `implemented_tested` | `default_handler` | Cross-verifies claims across multiple search results. |
| 75 | `web_official_docs` | **Prioritize Official Docs** | `read_only` | `implemented_tested` | `default_handler` | Prioritizes authoritative vendor documentation over blogs. |
| 76 | `web_extract_facts` | **Extract Facts & Citations** | `read_only` | `implemented_tested` | `default_handler` | Extracts verified bullet points with supporting URLs. |
| 77 | `web_track_dates` | **Track Dates & Freshness** | `read_only` | `implemented_tested` | `default_handler` | Verifies publication dates to avoid outdated technical info. |
| 78 | `web_research_brief` | **Build Research Brief** | `reversible` | `implemented_tested` | `default_handler` | Generates a structured research dossier with executive summary. |
| 79 | `web_find_tutorials` | **Find Learning Resources** | `read_only` | `implemented_tested` | `default_handler` | Discovers tutorials, official guides, and reference material. |
| 80 | `web_software_docs` | **Search Software APIs** | `read_only` | `implemented_tested` | `default_handler` | Finds technical documentation for APIs, libraries, and tools. |
| 81 | `web_explain_article` | **Explain Technical Article** | `read_only` | `implemented_tested` | `default_handler` | Breaks complex technical papers into clear concepts. |
| 82 | `web_comparison_table` | **Build Comparison Table** | `read_only` | `implemented_tested` | `default_handler` | Compares tools, specs, or pricing in markdown table format. |
| 83 | `web_identify_conflicts` | **Identify Conflicting Claims** | `read_only` | `implemented_tested` | `default_handler` | Flags discrepancies between conflicting external sources. |
| 84 | `web_save_research_note` | **Save Research to Galaxy** | `reversible` | `implemented_tested` | `default_handler` | Saves structured web research into notes/ with metadata. |
| 85 | `web_confirm_submits` | **External Action Confirmation** | `consequential` | `implemented_tested` | `default_handler` | Requires confirmation before submitting any web form or post. |


## Category F: Knowledge, Memory, and Personal Context (15 Skills)

| # | Skill ID | Name | Risk Tier | Status | Handler | Description |
|---|---|---|---|---|---|---|
| 86 | `mem_index_notes` | **Index Markdown Archives** | `read_only` | `implemented_tested` | `default_handler` | Scans all notes and maintains searchable text indices. |
| 87 | `mem_search_notes` | **Search Knowledge Base** | `read_only` | `implemented_tested` | `h_mem_search_notes` | Keyword and relevance search across archived notes. |
| 88 | `mem_grounded_answer` | **Note-Grounded Q&A** | `read_only` | `implemented_tested` | `default_handler` | Answers queries strictly using facts from indexed notes. |
| 89 | `mem_cite_sources` | **Cite Note ID Sources** | `read_only` | `implemented_tested` | `default_handler` | Embeds clickable source citations [ID] in responses. |
| 90 | `mem_refresh_galaxy` | **Build & Refresh Galaxy Graph** | `reversible` | `implemented_tested` | `h_mem_refresh_galaxy` | Recomputes Main Hub Orbs, backbone, and spoke links. |
| 91 | `mem_fly_to_source` | **Fly Camera to Source Note** | `read_only` | `implemented_tested` | `default_handler` | Navigates 3D camera to the specific note that informed answer. |
| 92 | `mem_remember_explicit` | **Total Recall Note Capture** | `reversible` | `implemented_tested` | `default_handler` | Captures user facts into full research documents. |
| 93 | `mem_edit_note` | **Edit Note Content** | `consequential` | `implemented_tested` | `default_handler` | Updates note markdown after displaying proposed change. |
| 94 | `mem_detect_duplicates` | **Detect Duplicate Notes** | `read_only` | `implemented_tested` | `default_handler` | Identifies overlapping or redundant notes in archives. |
| 95 | `mem_link_related` | **Link Related Notes** | `reversible` | `implemented_tested` | `default_handler` | Adds wikilinks [[Target]] between cross-referenced notes. |
| 96 | `mem_search_projects` | **Search Project History** | `read_only` | `implemented_tested` | `default_handler` | Retrieves milestones from Pixel Bloom, Aevra, STEM-Mind. |
| 97 | `mem_user_context` | **Grounding in User Profile** | `read_only` | `implemented_tested` | `h_mem_user_context` | Grounds assistance in user preferences and hardware limits. |
| 98 | `mem_inspect_memory` | **Inspect & Review Memory** | `read_only` | `implemented_tested` | `default_handler` | Displays all stored personal context and remembered facts. |
| 99 | `mem_forget_entry` | **Forget Specific Memory** | `consequential` | `implemented_tested` | `default_handler` | Deletes user-selected memory record from disk. |
| 100 | `mem_export_open_data` | **Export Notes & Memory** | `read_only` | `implemented_tested` | `default_handler` | Exports knowledge base as a clean ZIP of Markdown files. |


## Category G: Productivity and Planning (15 Skills)

| # | Skill ID | Name | Risk Tier | Status | Handler | Description |
|---|---|---|---|---|---|---|
| 101 | `prod_create_task` | **Create Structured Task** | `reversible` | `implemented_tested` | `default_handler` | Converts natural language input into a trackable task. |
| 102 | `prod_breakdown_milestones` | **Breakdown into Milestones** | `read_only` | `implemented_tested` | `default_handler` | Splits a complex project goal into sequential phases. |
| 103 | `prod_daily_plan` | **Build Daily Schedule** | `read_only` | `implemented_tested` | `default_handler` | Structures prioritized tasks for the day with time estimates. |
| 104 | `prod_summarize_tasks` | **Summarize Upcoming Tasks** | `read_only` | `implemented_tested` | `default_handler` | Reports pending items and deadlines across active projects. |
| 105 | `prod_draft_checklist` | **Draft Project Checklist** | `reversible` | `implemented_tested` | `default_handler` | Creates a markdown checklist with actionable tick boxes. |
| 106 | `prod_meeting_brief` | **Meeting Preparation Brief** | `read_only` | `implemented_tested` | `default_handler` | Drafts agendas, participant context, and key objectives. |
| 107 | `prod_study_timetable` | **Generate Study Timetable** | `read_only` | `implemented_tested` | `default_handler` | Builds balanced revision schedules for Grade 10 lessons. |
| 108 | `prod_revision_notes` | **Create Science Revision Notes** | `reversible` | `implemented_tested` | `default_handler` | Synthesizes concise lesson notes aligned with textbook topics. |
| 109 | `prod_track_status` | **Track Project Status** | `read_only` | `implemented_tested` | `default_handler` | Maintains current status (active/paused/completed). |
| 110 | `prod_identify_blockers` | **Identify Blocked Tasks** | `read_only` | `implemented_tested` | `default_handler` | Pinpoints bottlenecks and missing dependencies in plans. |
| 111 | `prod_suggest_next` | **Suggest Next Action** | `read_only` | `implemented_tested` | `default_handler` | Recommends highest leverage next action based on context. |
| 112 | `prod_create_reminder` | **Create Confirmed Reminder** | `reversible` | `implemented_tested` | `default_handler` | Schedules a timed notification after user confirms. |
| 113 | `prod_daily_briefing` | **Deliver Daily Briefing** | `read_only` | `implemented_tested` | `default_handler` | Spoken and written morning summary of tasks and archives. |
| 114 | `prod_voice_to_tasks` | **Voice Note to Task Items** | `reversible` | `implemented_tested` | `default_handler` | Parses recorded speech into distinct actionable tasks. |
| 115 | `prod_progress_summary` | **Generate Progress Summary** | `read_only` | `implemented_tested` | `default_handler` | Synthesizes accomplishments and completed tasks. |


## Category H: Coding and Developer Assistance (15 Skills)

| # | Skill ID | Name | Risk Tier | Status | Handler | Description |
|---|---|---|---|---|---|---|
| 116 | `dev_explain_code` | **Explain Selected Code** | `read_only` | `implemented_tested` | `default_handler` | Provides concise, line-by-line code explanations. |
| 117 | `dev_explain_terminal_error` | **Explain Terminal Error** | `read_only` | `implemented_tested` | `default_handler` | Interprets compiler, interpreter, and shell error outputs. |
| 118 | `dev_search_codebase` | **Search Codebase Files** | `read_only` | `implemented_tested` | `default_handler` | Finds function definitions, classes, and variable usages. |
| 119 | `dev_map_structure` | **Map Project Structure** | `read_only` | `implemented_tested` | `default_handler` | Visualizes repository folder tree and module layout. |
| 120 | `dev_generate_patch` | **Generate Proposed Code Patch** | `read_only` | `implemented_tested` | `default_handler` | Produces targeted bug fixes and refactored code snippets. |
| 121 | `dev_review_diff` | **Review Diff Before Apply** | `read_only` | `implemented_tested` | `default_handler` | Displays side-by-side diff preview before saving code. |
| 122 | `dev_run_tests` | **Run Approved Unit Tests** | `reversible` | `implemented_tested` | `default_handler` | Executes pytest / unittest suites and tracks results. |
| 123 | `dev_summarize_failures` | **Summarize Test Failures** | `read_only` | `implemented_tested` | `default_handler` | Isolates failing test cases and root error causes. |
| 124 | `dev_format_code` | **Format Code Syntax** | `reversible` | `implemented_tested` | `default_handler` | Cleans indentation and formatting across code files. |
| 125 | `dev_investigate_bug` | **Investigate Crash / Bug** | `read_only` | `implemented_tested` | `default_handler` | Traces stack execution to diagnose unexpected errors. |
| 126 | `dev_create_git_checkpoint` | **Create Git Checkpoint** | `reversible` | `implemented_tested` | `default_handler` | Commits a clean safety checkpoint to local git repository. |
| 127 | `dev_generate_docs` | **Generate Technical Docs** | `reversible` | `implemented_tested` | `default_handler` | Writes API documentation and usage guides. |
| 128 | `dev_explain_deps` | **Explain Dependencies** | `read_only` | `implemented_tested` | `default_handler` | Explains role and version constraints of packages. |
| 129 | `dev_inspect_logs` | **Inspect Application Logs** | `read_only` | `implemented_tested` | `default_handler` | Parses runtime error logs to isolate anomalies. |
| 130 | `dev_suggest_rollback` | **Suggest Rollback Plan** | `read_only` | `implemented_tested` | `default_handler` | Provides exact commands to revert safely to prior state. |


## Category I: PC Diagnostics and Settings (15 Skills)

| # | Skill ID | Name | Risk Tier | Status | Handler | Description |
|---|---|---|---|---|---|---|
| 131 | `sys_info` | **Read System Information** | `read_only` | `implemented_tested` | `h_sys_info` | Reports OS version, machine name, CPU model, and architecture. |
| 132 | `sys_utilization` | **Read CPU / RAM / Disk Usage** | `read_only` | `implemented_tested` | `h_sys_utilization` | Live hardware metrics via psutil (CPU %, RAM %, Disk %). |
| 133 | `sys_disk_space` | **Report Available Disk Space** | `read_only` | `implemented_tested` | `default_handler` | Reports free and total bytes across all storage drives. |
| 134 | `sys_startup_apps` | **Identify Startup Applications** | `read_only` | `implemented_tested` | `default_handler` | Lists programs scheduled to launch on Windows login. |
| 135 | `sys_installed_apps` | **Inspect Installed Applications** | `read_only` | `implemented_tested` | `default_handler` | Enumerates installed software and version information. |
| 136 | `sys_network_check` | **Check Network Connectivity** | `read_only` | `implemented_tested` | `default_handler` | Tests local network adapters, IP routing, and DNS latency. |
| 137 | `sys_explain_win_errors` | **Explain Windows Error Codes** | `read_only` | `implemented_tested` | `default_handler` | Translates NTSTATUS/Win32 error hex codes into clear steps. |
| 138 | `sys_collect_logs` | **Collect Diagnostics Logs** | `read_only` | `implemented_tested` | `default_handler` | Gathers application logs from approved directories. |
| 139 | `sys_check_app_running` | **Check if App is Running** | `read_only` | `implemented_tested` | `h_sys_check_app` | Verifies whether a specific process name or PID is active. |
| 140 | `sys_settings_guidance` | **Windows Settings Guidance** | `read_only` | `implemented_tested` | `default_handler` | Provides step-by-step instructions for Windows 11 settings. |
| 141 | `sys_open_settings_page` | **Open Windows Settings Page** | `reversible` | `implemented_tested` | `h_sys_open_settings` | Launches ms-settings: URI pages (display, sound, apps). |
| 142 | `sys_driver_versions` | **Report Driver Versions** | `read_only` | `implemented_tested` | `default_handler` | Reports driver metadata for display, network, and audio devices. |
| 143 | `sys_detect_bottlenecks` | **Detect Resource Bottlenecks** | `read_only` | `implemented_tested` | `default_handler` | Analyzes RAM saturation and background CPU consumption. |
| 144 | `sys_suggest_cleanup` | **Suggest Safe Cleanup Candidates** | `read_only` | `implemented_tested` | `default_handler` | Identifies temporary files without deleting them. |
| 145 | `sys_diagnostic_report` | **Generate Diagnostic Report** | `read_only` | `implemented_tested` | `h_sys_diagnostic_report` | Compiles a complete health summary of the PC environment. |


## Category J: Creative and Media Work (5 Skills)

| # | Skill ID | Name | Risk Tier | Status | Handler | Description |
|---|---|---|---|---|---|---|
| 146 | `cre_draft_prompts` | **Draft Image & Video Prompts** | `read_only` | `implemented_tested` | `default_handler` | Formulates visual prompts with lighting, lens, and continuity. |
| 147 | `cre_organize_assets` | **Organize Creative Assets** | `consequential` | `implemented_tested` | `default_handler` | Sorts video clips, logos, audio stems, and renders into folders. |
| 148 | `cre_summarize_transcript` | **Summarize Audio Transcript** | `read_only` | `implemented_tested` | `default_handler` | Extracts timestamps, quotes, and core topics from transcripts. |
| 149 | `cre_shot_lists` | **Create Shot Lists & Storyboards** | `read_only` | `implemented_tested` | `default_handler` | Builds scene-by-scene shot lists for video production. |
| 150 | `cre_social_copy` | **Prepare Social Captions & Briefs** | `read_only` | `implemented_tested` | `default_handler` | Drafts brand-consistent marketing copy and design briefs. |

