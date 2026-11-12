"""
The 150-Skill Catalogue and Registry for J.A.R.V.I.S.
Implements the complete capability catalogue specified in PRD Section 7.
"""
from ..core.permissions import (
    broker,
    RISK_READ_ONLY,
    RISK_REVERSIBLE,
    RISK_CONSEQUENTIAL,
    RISK_RESTRICTED,
)

# Skill status constants
STATUS_TESTED = "implemented_tested"
STATUS_PENDING_CONFIG = "implemented_pending_config"
STATUS_PENDING_PERM = "implemented_pending_permission"
STATUS_UNAVAILABLE = "unavailable_dependency"

CATEGORIES = {
    "A": "Voice and Conversation",
    "B": "Screen Vision and Annotation",
    "C": "Desktop and Window Control",
    "D": "File and Folder Assistance",
    "E": "Web and Research",
    "F": "Knowledge, Memory, and Personal Context",
    "G": "Productivity and Planning",
    "H": "Coding and Developer Assistance",
    "I": "PC Diagnostics and Settings",
    "J": "Creative and Media Work",
}

# The 150-Skill Registry Definition
SKILL_DEFINITIONS = [
    # ── Category A: Voice and Conversation (1-15) ──
    {"num": 1, "id": "voice_ptt", "cat": "A", "name": "Push-to-Talk", "risk": RISK_READ_ONLY, "desc": "Activates microphone listening while key or button is held."},
    {"num": 2, "id": "voice_toggle_listen", "cat": "A", "name": "Toggle-to-Listen", "risk": RISK_READ_ONLY, "desc": "Toggles continuous voice listening on/off."},
    {"num": 3, "id": "voice_wake_phrase", "cat": "A", "name": "Wake Phrase Detection", "risk": RISK_READ_ONLY, "desc": "Configurable wake phrase detector ('Jarvis')."},
    {"num": 4, "id": "voice_transcription", "cat": "A", "name": "Speech-to-Text", "risk": RISK_READ_ONLY, "desc": "Transcribes incoming voice input into text."},
    {"num": 5, "id": "voice_tts", "cat": "A", "name": "Text-to-Speech Output", "risk": RISK_READ_ONLY, "desc": "Speaks responses aloud via Fish Audio / Browser Speech."},
    {"num": 6, "id": "voice_rate_settings", "cat": "A", "name": "Voice Rate Settings", "risk": RISK_REVERSIBLE, "desc": "Configures voice speaking pitch, volume, and rate."},
    {"num": 7, "id": "voice_interrupt", "cat": "A", "name": "Interrupt Speech", "risk": RISK_READ_ONLY, "desc": "Instantly cancels active audio playback upon user input."},
    {"num": 8, "id": "voice_barge_in", "cat": "A", "name": "Barge-In Listening", "risk": RISK_READ_ONLY, "desc": "Listens for user speech while speaking to allow smooth interruption."},
    {"num": 9, "id": "voice_context", "cat": "A", "name": "Conversation Context", "risk": RISK_READ_ONLY, "desc": "Maintains multi-turn context across follow-up queries."},
    {"num": 10, "id": "voice_language_select", "cat": "A", "name": "Language Selection", "risk": RISK_REVERSIBLE, "desc": "Configures input and response language preferences."},
    {"num": 11, "id": "voice_vad", "cat": "A", "name": "Voice Activity Detection", "risk": RISK_READ_ONLY, "desc": "Detects speech onset and trailing silence automatically."},
    {"num": 12, "id": "voice_noise_filter", "cat": "A", "name": "Noise-Aware Transcription", "risk": RISK_READ_ONLY, "desc": "Filters background audio noise to improve recognition."},
    {"num": 13, "id": "voice_repeat", "cat": "A", "name": "Repeat That Command", "risk": RISK_READ_ONLY, "desc": "Repeats the assistant's last spoken statement."},
    {"num": 14, "id": "voice_speak_slower", "cat": "A", "name": "Speak More Slowly", "risk": RISK_REVERSIBLE, "desc": "Reduces TTS speech playback rate by 20%."},
    {"num": 15, "id": "voice_stop_listening", "cat": "A", "name": "Stop Listening / Stop Speaking", "risk": RISK_READ_ONLY, "desc": "Silences TTS and turns off active microphone stream."},

    # ── Category B: Screen Vision and Annotation (16-30) ──
    {"num": 16, "id": "vis_capture_fullscreen", "cat": "B", "name": "Capture Fullscreen", "risk": RISK_READ_ONLY, "desc": "Captures a high-resolution screenshot of all desktop displays."},
    {"num": 17, "id": "vis_capture_active_window", "cat": "B", "name": "Capture Active Window", "risk": RISK_READ_ONLY, "desc": "Captures only the currently focused application window."},
    {"num": 18, "id": "vis_capture_region", "cat": "B", "name": "Capture Screen Region", "risk": RISK_READ_ONLY, "desc": "Captures a user-specified coordinate bounding box."},
    {"num": 19, "id": "vis_describe_screen", "cat": "B", "name": "Describe Screen Contents", "risk": RISK_READ_ONLY, "desc": "Analyzes screen visually via Gemini Multimodal Vision."},
    {"num": 20, "id": "vis_ocr_text", "cat": "B", "name": "Read Visible Text (OCR)", "risk": RISK_READ_ONLY, "desc": "Extracts readable text and labels from screen captures."},
    {"num": 21, "id": "vis_explain_error", "cat": "B", "name": "Explain Error Dialog", "risk": RISK_READ_ONLY, "desc": "Diagnoses visible crash reports, stack traces, and modal alerts."},
    {"num": 22, "id": "vis_identify_window", "cat": "B", "name": "Identify Visible Window", "risk": RISK_READ_ONLY, "desc": "Returns active window title, process name, and geometry."},
    {"num": 23, "id": "vis_compare_screenshots", "cat": "B", "name": "Compare Screenshots", "risk": RISK_READ_ONLY, "desc": "Compares two captures to detect UI changes or differences."},
    {"num": 24, "id": "vis_find_control", "cat": "B", "name": "Find Visible Control", "risk": RISK_READ_ONLY, "desc": "Locates buttons, inputs, or tabs on screen using visual metadata."},
    {"num": 25, "id": "vis_highlight_control", "cat": "B", "name": "Highlight Control", "risk": RISK_READ_ONLY, "desc": "Draws a luminous bounding box around a specific element."},
    {"num": 26, "id": "vis_annotate_arrows", "cat": "B", "name": "Add Arrows and Callouts", "risk": RISK_READ_ONLY, "desc": "Draws non-destructive arrows and numbered step badges."},
    {"num": 27, "id": "vis_create_guide", "cat": "B", "name": "Annotated Step-by-Step Guide", "risk": RISK_READ_ONLY, "desc": "Generates a composite visual walkthrough with numbered callouts."},
    {"num": 28, "id": "vis_explain_charts", "cat": "B", "name": "Explain Charts and Layouts", "risk": RISK_READ_ONLY, "desc": "Interprets visual data, charts, architecture diagrams, and wireframes."},
    {"num": 29, "id": "vis_detect_loading", "cat": "B", "name": "Detect Modal / Loading State", "risk": RISK_READ_ONLY, "desc": "Detects whether an app is actively loading or blocking input."},
    {"num": 30, "id": "vis_request_region", "cat": "B", "name": "Region Selection Prompt", "risk": RISK_READ_ONLY, "desc": "Prompts user to highlight ambiguous screen areas."},

    # ── Category C: Desktop and Window Control (31-50) ──
    {"num": 31, "id": "desk_open_app", "cat": "C", "name": "Open Application", "risk": RISK_REVERSIBLE, "desc": "Launches an installed Windows application or executable."},
    {"num": 32, "id": "desk_focus_window", "cat": "C", "name": "Focus Application Window", "risk": RISK_REVERSIBLE, "desc": "Brings the target application window to the foreground."},
    {"num": 33, "id": "desk_min_max_restore", "cat": "C", "name": "Minimize/Maximize/Restore", "risk": RISK_REVERSIBLE, "desc": "Controls window states using Win32 ShowWindow API."},
    {"num": 34, "id": "desk_move_resize", "cat": "C", "name": "Move and Resize Window", "risk": RISK_REVERSIBLE, "desc": "Sets window position coordinates and dimensions."},
    {"num": 35, "id": "desk_switch_window", "cat": "C", "name": "Switch Windows", "risk": RISK_REVERSIBLE, "desc": "Cycles or activates specific open desktop applications."},
    {"num": 36, "id": "desk_list_windows", "cat": "C", "name": "List Visible Windows", "risk": RISK_READ_ONLY, "desc": "Returns all active visible desktop windows and handles."},
    {"num": 37, "id": "desk_arrange_layout", "cat": "C", "name": "Arrange Windows Layout", "risk": RISK_REVERSIBLE, "desc": "Tiles windows side-by-side or into a split-screen layout."},
    {"num": 38, "id": "desk_open_explorer", "cat": "C", "name": "Open Folder in Explorer", "risk": RISK_REVERSIBLE, "desc": "Opens File Explorer at a target folder path."},
    {"num": 39, "id": "desk_nav_known_folder", "cat": "C", "name": "Navigate to Known Folder", "risk": RISK_REVERSIBLE, "desc": "Opens Downloads, Documents, Pictures, or Project folders."},
    {"num": 40, "id": "desk_open_file_default", "cat": "C", "name": "Open File with Default App", "risk": RISK_REVERSIBLE, "desc": "Opens a document or media file with its default Windows handler."},
    {"num": 41, "id": "desk_copy_selected", "cat": "C", "name": "Copy Selected Text", "risk": RISK_READ_ONLY, "desc": "Dispatches Ctrl+C to copy selected content to clipboard."},
    {"num": 42, "id": "desk_paste_content", "cat": "C", "name": "Paste Content", "risk": RISK_REVERSIBLE, "desc": "Pastes approved text into the active focused field."},
    {"num": 43, "id": "desk_type_text", "cat": "C", "name": "Type Text into Field", "risk": RISK_REVERSIBLE, "desc": "Types unicode characters smoothly into the active input."},
    {"num": 44, "id": "desk_scroll_window", "cat": "C", "name": "Scroll Window", "risk": RISK_REVERSIBLE, "desc": "Scrolls the active window content up or down."},
    {"num": 45, "id": "desk_keyboard_shortcut", "cat": "C", "name": "Allowlisted Hotkey Dispatch", "risk": RISK_REVERSIBLE, "desc": "Sends safe hotkeys (e.g. Ctrl+S, Alt+Tab, Win+D)."},
    {"num": 46, "id": "desk_capture_window", "cat": "C", "name": "Screenshot Target Window", "risk": RISK_READ_ONLY, "desc": "Captures a clean screenshot of a specified window handle."},
    {"num": 47, "id": "desk_detect_unresponsive", "cat": "C", "name": "Detect Not Responding App", "risk": RISK_READ_ONLY, "desc": "Checks if an application process has frozen or stopped responding."},
    {"num": 48, "id": "desk_wait_for_dialog", "cat": "C", "name": "Wait for Dialog / Window", "risk": RISK_READ_ONLY, "desc": "Waits with timeout for an expected window title to appear."},
    {"num": 49, "id": "desk_return_focus", "cat": "C", "name": "Return Previous Focus", "risk": RISK_REVERSIBLE, "desc": "Restores focus to the application active prior to JARVIS overlay."},
    {"num": 50, "id": "desk_stop_automation", "cat": "C", "name": "Global Stop All Automation", "risk": RISK_READ_ONLY, "desc": "Instantly halts all active mouse, keyboard, and script actions."},

    # ── Category D: File and Folder Assistance (51-70) ──
    {"num": 51, "id": "file_search_names", "cat": "D", "name": "Search Filenames", "risk": RISK_READ_ONLY, "desc": "Searches files by name matching patterns in approved folders."},
    {"num": 52, "id": "file_search_content", "cat": "D", "name": "Search File Contents", "risk": RISK_READ_ONLY, "desc": "Searches for text within documents, code, and notes."},
    {"num": 53, "id": "file_list_contents", "cat": "D", "name": "List Folder Contents", "risk": RISK_READ_ONLY, "desc": "Lists files, subfolders, sizes, and timestamps."},
    {"num": 54, "id": "file_find_duplicates", "cat": "D", "name": "Find Duplicate Files", "risk": RISK_READ_ONLY, "desc": "Detects identical files using SHA-256 hash comparison."},
    {"num": 55, "id": "file_summarize_pdf", "cat": "D", "name": "Summarize PDF Document", "risk": RISK_READ_ONLY, "desc": "Extracts and synthesizes core takeaways from PDF documents."},
    {"num": 56, "id": "file_extract_text", "cat": "D", "name": "Extract Document Text", "risk": RISK_READ_ONLY, "desc": "Reads plain text from Markdown, TXT, CSV, and code files."},
    {"num": 57, "id": "file_summarize_sheet", "cat": "D", "name": "Summarize Spreadsheet", "risk": RISK_READ_ONLY, "desc": "Analyzes columns, rows, and key statistical metrics in CSV."},
    {"num": 58, "id": "file_create_doc", "cat": "D", "name": "Create Markdown / Text File", "risk": RISK_REVERSIBLE, "desc": "Writes a clean markdown document or report to disk."},
    {"num": 59, "id": "file_create_folders", "cat": "D", "name": "Create Folder Structure", "risk": RISK_REVERSIBLE, "desc": "Creates organized directory hierarchies for projects."},
    {"num": 60, "id": "file_rename_preview", "cat": "D", "name": "Rename Files with Preview", "risk": RISK_CONSEQUENTIAL, "desc": "Shows dry-run rename plan before updating filenames."},
    {"num": 61, "id": "file_move_preview", "cat": "D", "name": "Move Files with Undo Log", "risk": RISK_CONSEQUENTIAL, "desc": "Transfers files between folders with an auditable undo log."},
    {"num": 62, "id": "file_copy_verify", "cat": "D", "name": "Copy Files with Verification", "risk": RISK_REVERSIBLE, "desc": "Copies files and verifies checksums to prevent corruption."},
    {"num": 63, "id": "file_backup_bulk", "cat": "D", "name": "Pre-Operation Backup", "risk": RISK_REVERSIBLE, "desc": "Creates a safety snapshot before any bulk modification."},
    {"num": 64, "id": "file_organize_rules", "cat": "D", "name": "Auto-Organize Archives", "risk": RISK_CONSEQUENTIAL, "desc": "Classifies and sorts loose documents into categorized folders."},
    {"num": 65, "id": "file_find_large", "cat": "D", "name": "Find Large Files", "risk": RISK_READ_ONLY, "desc": "Identifies space-consuming files exceeding a size threshold."},
    {"num": 66, "id": "file_find_recent", "cat": "D", "name": "Find Recently Modified", "risk": RISK_READ_ONLY, "desc": "Lists files created or modified within the last 24h/7 days."},
    {"num": 67, "id": "file_inspect_metadata", "cat": "D", "name": "Inspect File Metadata", "risk": RISK_READ_ONLY, "desc": "Reports creation time, permissions, file type, and exact size."},
    {"num": 68, "id": "file_convert_format", "cat": "D", "name": "Convert Document Formats", "risk": RISK_REVERSIBLE, "desc": "Converts plain text, markdown, and CSV structures."},
    {"num": 69, "id": "file_create_zip", "cat": "D", "name": "Create ZIP Archive", "risk": RISK_REVERSIBLE, "desc": "Compresses files and folders into a standard ZIP archive."},
    {"num": 70, "id": "file_restore_backup", "cat": "D", "name": "Restore from Safety Backup", "risk": RISK_CONSEQUENTIAL, "desc": "Restores files from a JARVIS-created backup snapshot."},

    # ── Category E: Web and Research (71-85) ──
    {"num": 71, "id": "web_search_queries", "cat": "E", "name": "Web Search Query", "risk": RISK_READ_ONLY, "desc": "Conducts web searches for factual data and documentation."},
    {"num": 72, "id": "web_open_url", "cat": "E", "name": "Open Website URL", "risk": RISK_REVERSIBLE, "desc": "Launches a specific verified website in the default browser."},
    {"num": 73, "id": "web_summarize_page", "cat": "E", "name": "Summarize Webpage", "risk": RISK_READ_ONLY, "desc": "Fetches and condenses article text into structured notes."},
    {"num": 74, "id": "web_compare_sources", "cat": "E", "name": "Compare Multiple Sources", "risk": RISK_READ_ONLY, "desc": "Cross-verifies claims across multiple search results."},
    {"num": 75, "id": "web_official_docs", "cat": "E", "name": "Prioritize Official Docs", "risk": RISK_READ_ONLY, "desc": "Prioritizes authoritative vendor documentation over blogs."},
    {"num": 76, "id": "web_extract_facts", "cat": "E", "name": "Extract Facts & Citations", "risk": RISK_READ_ONLY, "desc": "Extracts verified bullet points with supporting URLs."},
    {"num": 77, "id": "web_track_dates", "cat": "E", "name": "Track Dates & Freshness", "risk": RISK_READ_ONLY, "desc": "Verifies publication dates to avoid outdated technical info."},
    {"num": 78, "id": "web_research_brief", "cat": "E", "name": "Build Research Brief", "risk": RISK_REVERSIBLE, "desc": "Generates a structured research dossier with executive summary."},
    {"num": 79, "id": "web_find_tutorials", "cat": "E", "name": "Find Learning Resources", "risk": RISK_READ_ONLY, "desc": "Discovers tutorials, official guides, and reference material."},
    {"num": 80, "id": "web_software_docs", "cat": "E", "name": "Search Software APIs", "risk": RISK_READ_ONLY, "desc": "Finds technical documentation for APIs, libraries, and tools."},
    {"num": 81, "id": "web_explain_article", "cat": "E", "name": "Explain Technical Article", "risk": RISK_READ_ONLY, "desc": "Breaks complex technical papers into clear concepts."},
    {"num": 82, "id": "web_comparison_table", "cat": "E", "name": "Build Comparison Table", "risk": RISK_READ_ONLY, "desc": "Compares tools, specs, or pricing in markdown table format."},
    {"num": 83, "id": "web_identify_conflicts", "cat": "E", "name": "Identify Conflicting Claims", "risk": RISK_READ_ONLY, "desc": "Flags discrepancies between conflicting external sources."},
    {"num": 84, "id": "web_save_research_note", "cat": "E", "name": "Save Research to Galaxy", "risk": RISK_REVERSIBLE, "desc": "Saves structured web research into notes/ with metadata."},
    {"num": 85, "id": "web_confirm_submits", "cat": "E", "name": "External Action Confirmation", "risk": RISK_CONSEQUENTIAL, "desc": "Requires confirmation before submitting any web form or post."},

    # ── Category F: Knowledge, Memory, and Personal Context (86-100) ──
    {"num": 86, "id": "mem_index_notes", "cat": "F", "name": "Index Markdown Archives", "risk": RISK_READ_ONLY, "desc": "Scans all notes and maintains searchable text indices."},
    {"num": 87, "id": "mem_search_notes", "cat": "F", "name": "Search Knowledge Base", "risk": RISK_READ_ONLY, "desc": "Keyword and relevance search across archived notes."},
    {"num": 88, "id": "mem_grounded_answer", "cat": "F", "name": "Note-Grounded Q&A", "risk": RISK_READ_ONLY, "desc": "Answers queries strictly using facts from indexed notes."},
    {"num": 89, "id": "mem_cite_sources", "cat": "F", "name": "Cite Note ID Sources", "risk": RISK_READ_ONLY, "desc": "Embeds clickable source citations [ID] in responses."},
    {"num": 90, "id": "mem_refresh_galaxy", "cat": "F", "name": "Build & Refresh Galaxy Graph", "risk": RISK_REVERSIBLE, "desc": "Recomputes Main Hub Orbs, backbone, and spoke links."},
    {"num": 91, "id": "mem_fly_to_source", "cat": "F", "name": "Fly Camera to Source Note", "risk": RISK_READ_ONLY, "desc": "Navigates 3D camera to the specific note that informed answer."},
    {"num": 92, "id": "mem_remember_explicit", "cat": "F", "name": "Total Recall Note Capture", "risk": RISK_REVERSIBLE, "desc": "Captures user facts into full research documents."},
    {"num": 93, "id": "mem_edit_note", "cat": "F", "name": "Edit Note Content", "risk": RISK_CONSEQUENTIAL, "desc": "Updates note markdown after displaying proposed change."},
    {"num": 94, "id": "mem_detect_duplicates", "cat": "F", "name": "Detect Duplicate Notes", "risk": RISK_READ_ONLY, "desc": "Identifies overlapping or redundant notes in archives."},
    {"num": 95, "id": "mem_link_related", "cat": "F", "name": "Link Related Notes", "risk": RISK_REVERSIBLE, "desc": "Adds wikilinks [[Target]] between cross-referenced notes."},
    {"num": 96, "id": "mem_search_projects", "cat": "F", "name": "Search Project History", "risk": RISK_READ_ONLY, "desc": "Retrieves milestones from Pixel Bloom, Aevra, STEM-Mind."},
    {"num": 97, "id": "mem_user_context", "cat": "F", "name": "Grounding in User Profile", "risk": RISK_READ_ONLY, "desc": "Grounds assistance in user preferences and hardware limits."},
    {"num": 98, "id": "mem_inspect_memory", "cat": "F", "name": "Inspect & Review Memory", "risk": RISK_READ_ONLY, "desc": "Displays all stored personal context and remembered facts."},
    {"num": 99, "id": "mem_forget_entry", "cat": "F", "name": "Forget Specific Memory", "risk": RISK_CONSEQUENTIAL, "desc": "Deletes user-selected memory record from disk."},
    {"num": 100, "id": "mem_export_open_data", "cat": "F", "name": "Export Notes & Memory", "risk": RISK_READ_ONLY, "desc": "Exports knowledge base as a clean ZIP of Markdown files."},

    # ── Category G: Productivity and Planning (101-115) ──
    {"num": 101, "id": "prod_create_task", "cat": "G", "name": "Create Structured Task", "risk": RISK_REVERSIBLE, "desc": "Converts natural language input into a trackable task."},
    {"num": 102, "id": "prod_breakdown_milestones", "cat": "G", "name": "Breakdown into Milestones", "risk": RISK_READ_ONLY, "desc": "Splits a complex project goal into sequential phases."},
    {"num": 103, "id": "prod_daily_plan", "cat": "G", "name": "Build Daily Schedule", "risk": RISK_READ_ONLY, "desc": "Structures prioritized tasks for the day with time estimates."},
    {"num": 104, "id": "prod_summarize_tasks", "cat": "G", "name": "Summarize Upcoming Tasks", "risk": RISK_READ_ONLY, "desc": "Reports pending items and deadlines across active projects."},
    {"num": 105, "id": "prod_draft_checklist", "cat": "G", "name": "Draft Project Checklist", "risk": RISK_REVERSIBLE, "desc": "Creates a markdown checklist with actionable tick boxes."},
    {"num": 106, "id": "prod_meeting_brief", "cat": "G", "name": "Meeting Preparation Brief", "risk": RISK_READ_ONLY, "desc": "Drafts agendas, participant context, and key objectives."},
    {"num": 107, "id": "prod_study_timetable", "cat": "G", "name": "Generate Study Timetable", "risk": RISK_READ_ONLY, "desc": "Builds balanced revision schedules for Grade 10 lessons."},
    {"num": 108, "id": "prod_revision_notes", "cat": "G", "name": "Create Science Revision Notes", "risk": RISK_REVERSIBLE, "desc": "Synthesizes concise lesson notes aligned with textbook topics."},
    {"num": 109, "id": "prod_track_status", "cat": "G", "name": "Track Project Status", "risk": RISK_READ_ONLY, "desc": "Maintains current status (active/paused/completed)."},
    {"num": 110, "id": "prod_identify_blockers", "cat": "G", "name": "Identify Blocked Tasks", "risk": RISK_READ_ONLY, "desc": "Pinpoints bottlenecks and missing dependencies in plans."},
    {"num": 111, "id": "prod_suggest_next", "cat": "G", "name": "Suggest Next Action", "risk": RISK_READ_ONLY, "desc": "Recommends highest leverage next action based on context."},
    {"num": 112, "id": "prod_create_reminder", "cat": "G", "name": "Create Confirmed Reminder", "risk": RISK_REVERSIBLE, "desc": "Schedules a timed notification after user confirms."},
    {"num": 113, "id": "prod_daily_briefing", "cat": "G", "name": "Deliver Daily Briefing", "risk": RISK_READ_ONLY, "desc": "Spoken and written morning summary of tasks and archives."},
    {"num": 114, "id": "prod_voice_to_tasks", "cat": "G", "name": "Voice Note to Task Items", "risk": RISK_REVERSIBLE, "desc": "Parses recorded speech into distinct actionable tasks."},
    {"num": 115, "id": "prod_progress_summary", "cat": "G", "name": "Generate Progress Summary", "risk": RISK_READ_ONLY, "desc": "Synthesizes accomplishments and completed tasks."},

    # ── Category H: Coding and Developer Assistance (116-130) ──
    {"num": 116, "id": "dev_explain_code", "cat": "H", "name": "Explain Selected Code", "risk": RISK_READ_ONLY, "desc": "Provides concise, line-by-line code explanations."},
    {"num": 117, "id": "dev_explain_terminal_error", "cat": "H", "name": "Explain Terminal Error", "risk": RISK_READ_ONLY, "desc": "Interprets compiler, interpreter, and shell error outputs."},
    {"num": 118, "id": "dev_search_codebase", "cat": "H", "name": "Search Codebase Files", "risk": RISK_READ_ONLY, "desc": "Finds function definitions, classes, and variable usages."},
    {"num": 119, "id": "dev_map_structure", "cat": "H", "name": "Map Project Structure", "risk": RISK_READ_ONLY, "desc": "Visualizes repository folder tree and module layout."},
    {"num": 120, "id": "dev_generate_patch", "cat": "H", "name": "Generate Proposed Code Patch", "risk": RISK_READ_ONLY, "desc": "Produces targeted bug fixes and refactored code snippets."},
    {"num": 121, "id": "dev_review_diff", "cat": "H", "name": "Review Diff Before Apply", "risk": RISK_READ_ONLY, "desc": "Displays side-by-side diff preview before saving code."},
    {"num": 122, "id": "dev_run_tests", "cat": "H", "name": "Run Approved Unit Tests", "risk": RISK_REVERSIBLE, "desc": "Executes pytest / unittest suites and tracks results."},
    {"num": 123, "id": "dev_summarize_failures", "cat": "H", "name": "Summarize Test Failures", "risk": RISK_READ_ONLY, "desc": "Isolates failing test cases and root error causes."},
    {"num": 124, "id": "dev_format_code", "cat": "H", "name": "Format Code Syntax", "risk": RISK_REVERSIBLE, "desc": "Cleans indentation and formatting across code files."},
    {"num": 125, "id": "dev_investigate_bug", "cat": "H", "name": "Investigate Crash / Bug", "risk": RISK_READ_ONLY, "desc": "Traces stack execution to diagnose unexpected errors."},
    {"num": 126, "id": "dev_create_git_checkpoint", "cat": "H", "name": "Create Git Checkpoint", "risk": RISK_REVERSIBLE, "desc": "Commits a clean safety checkpoint to local git repository."},
    {"num": 127, "id": "dev_generate_docs", "cat": "H", "name": "Generate Technical Docs", "risk": RISK_REVERSIBLE, "desc": "Writes API documentation and usage guides."},
    {"num": 128, "id": "dev_explain_deps", "cat": "H", "name": "Explain Dependencies", "risk": RISK_READ_ONLY, "desc": "Explains role and version constraints of packages."},
    {"num": 129, "id": "dev_inspect_logs", "cat": "H", "name": "Inspect Application Logs", "risk": RISK_READ_ONLY, "desc": "Parses runtime error logs to isolate anomalies."},
    {"num": 130, "id": "dev_suggest_rollback", "cat": "H", "name": "Suggest Rollback Plan", "risk": RISK_READ_ONLY, "desc": "Provides exact commands to revert safely to prior state."},

    # ── Category I: PC Diagnostics and Settings (131-145) ──
    {"num": 131, "id": "sys_info", "cat": "I", "name": "Read System Information", "risk": RISK_READ_ONLY, "desc": "Reports OS version, machine name, CPU model, and architecture."},
    {"num": 132, "id": "sys_utilization", "cat": "I", "name": "Read CPU / RAM / Disk Usage", "risk": RISK_READ_ONLY, "desc": "Live hardware metrics via psutil (CPU %, RAM %, Disk %)."},
    {"num": 133, "id": "sys_disk_space", "cat": "I", "name": "Report Available Disk Space", "risk": RISK_READ_ONLY, "desc": "Reports free and total bytes across all storage drives."},
    {"num": 134, "id": "sys_startup_apps", "cat": "I", "name": "Identify Startup Applications", "risk": RISK_READ_ONLY, "desc": "Lists programs scheduled to launch on Windows login."},
    {"num": 135, "id": "sys_installed_apps", "cat": "I", "name": "Inspect Installed Applications", "risk": RISK_READ_ONLY, "desc": "Enumerates installed software and version information."},
    {"num": 136, "id": "sys_network_check", "cat": "I", "name": "Check Network Connectivity", "risk": RISK_READ_ONLY, "desc": "Tests local network adapters, IP routing, and DNS latency."},
    {"num": 137, "id": "sys_explain_win_errors", "cat": "I", "name": "Explain Windows Error Codes", "risk": RISK_READ_ONLY, "desc": "Translates NTSTATUS/Win32 error hex codes into clear steps."},
    {"num": 138, "id": "sys_collect_logs", "cat": "I", "name": "Collect Diagnostics Logs", "risk": RISK_READ_ONLY, "desc": "Gathers application logs from approved directories."},
    {"num": 139, "id": "sys_check_app_running", "cat": "I", "name": "Check if App is Running", "risk": RISK_READ_ONLY, "desc": "Verifies whether a specific process name or PID is active."},
    {"num": 140, "id": "sys_settings_guidance", "cat": "I", "name": "Windows Settings Guidance", "risk": RISK_READ_ONLY, "desc": "Provides step-by-step instructions for Windows 11 settings."},
    {"num": 141, "id": "sys_open_settings_page", "cat": "I", "name": "Open Windows Settings Page", "risk": RISK_REVERSIBLE, "desc": "Launches ms-settings: URI pages (display, sound, apps)."},
    {"num": 142, "id": "sys_driver_versions", "cat": "I", "name": "Report Driver Versions", "risk": RISK_READ_ONLY, "desc": "Reports driver metadata for display, network, and audio devices."},
    {"num": 143, "id": "sys_detect_bottlenecks", "cat": "I", "name": "Detect Resource Bottlenecks", "risk": RISK_READ_ONLY, "desc": "Analyzes RAM saturation and background CPU consumption."},
    {"num": 144, "id": "sys_suggest_cleanup", "cat": "I", "name": "Suggest Safe Cleanup Candidates", "risk": RISK_READ_ONLY, "desc": "Identifies temporary files without deleting them."},
    {"num": 145, "id": "sys_diagnostic_report", "cat": "I", "name": "Generate Diagnostic Report", "risk": RISK_READ_ONLY, "desc": "Compiles a complete health summary of the PC environment."},

    # ── Category J: Creative and Media Work (146-150) ──
    {"num": 146, "id": "cre_draft_prompts", "cat": "J", "name": "Draft Image & Video Prompts", "risk": RISK_READ_ONLY, "desc": "Formulates visual prompts with lighting, lens, and continuity."},
    {"num": 147, "id": "cre_organize_assets", "cat": "J", "name": "Organize Creative Assets", "risk": RISK_CONSEQUENTIAL, "desc": "Sorts video clips, logos, audio stems, and renders into folders."},
    {"num": 148, "id": "cre_summarize_transcript", "cat": "J", "name": "Summarize Audio Transcript", "risk": RISK_READ_ONLY, "desc": "Extracts timestamps, quotes, and core topics from transcripts."},
    {"num": 149, "id": "cre_shot_lists", "cat": "J", "name": "Create Shot Lists & Storyboards", "risk": RISK_READ_ONLY, "desc": "Builds scene-by-scene shot lists for video production."},
    {"num": 150, "id": "cre_social_copy", "cat": "J", "name": "Prepare Social Captions & Briefs", "risk": RISK_READ_ONLY, "desc": "Drafts brand-consistent marketing copy and design briefs."},
]

# ── Intelligence and Reasoning Capabilities (Capabilities 1-15) ──
INTELLIGENCE_CAPABILITY_DEFINITIONS = [
    {"num": 1, "id": "intel_deep_research", "cat": "INTEL", "name": "Deep Research Engine", "risk": RISK_READ_ONLY, "desc": "Capability 1: Multi-source research gathering, vector decomposition, and entity synthesis."},
    {"num": 2, "id": "intel_recursive_research", "cat": "INTEL", "name": "Recursive Research", "risk": RISK_READ_ONLY, "desc": "Capability 2: Iterative frontier tree expansion with redundancy pruning and convergence."},
    {"num": 3, "id": "intel_hypothesis_generation", "cat": "INTEL", "name": "Hypothesis Generation", "risk": RISK_READ_ONLY, "desc": "Capability 3: Formulates competing Null, Primary, Alternative, and Edge hypotheses."},
    {"num": 4, "id": "intel_evidence_verification", "cat": "INTEL", "name": "Evidence Verification", "risk": RISK_READ_ONLY, "desc": "Capability 4: Evaluates claims against source evidence, calculates credibility and hallucination risk."},
    {"num": 5, "id": "intel_contradiction_detection", "cat": "INTEL", "name": "Contradiction Detection", "risk": RISK_READ_ONLY, "desc": "Capability 5: Detects direct negation, quantitative mismatches, and temporal inconsistencies."},
    {"num": 6, "id": "intel_predictive_analysis", "cat": "INTEL", "name": "Predictive Analysis", "risk": RISK_READ_ONLY, "desc": "Capability 6: Time-series trend extrapolation and multi-scenario probability forecasting."},
    {"num": 7, "id": "intel_pattern_recognition", "cat": "INTEL", "name": "Pattern Recognition", "risk": RISK_READ_ONLY, "desc": "Capability 7: Numerical anomaly detection (z-score/IQR) and text motif extraction."},
    {"num": 8, "id": "intel_decision_support", "cat": "INTEL", "name": "Decision Support", "risk": RISK_READ_ONLY, "desc": "Capability 8: Multi-criteria decision analysis (MCDA) via weighted scoring and sensitivity analysis."},
    {"num": 9, "id": "intel_knowledge_synthesis", "cat": "INTEL", "name": "Knowledge Synthesis", "risk": RISK_READ_ONLY, "desc": "Capability 9: Triadic dialectic synthesis (Thesis, Antithesis, Synthesis) and conceptual bridging."},
    {"num": 10, "id": "intel_contextual_reasoning", "cat": "INTEL", "name": "Contextual Reasoning", "risk": RISK_READ_ONLY, "desc": "Capability 10: Pragmatic inference grounded in user profile, OS environment, and risk posture."},
    {"num": 11, "id": "intel_multi_agent_collab", "cat": "INTEL", "name": "Multi-Agent Collaboration", "risk": RISK_READ_ONLY, "desc": "Capability 11: Multi-role structured debate protocol with consensus scoring."},
    {"num": 12, "id": "intel_long_term_research", "cat": "INTEL", "name": "Long-Term Research", "risk": RISK_REVERSIBLE, "desc": "Capability 12: Persistent research agendas, Bayesian hypothesis updates, and snapshot journal."},
    {"num": 13, "id": "intel_uncertainty_estimation", "cat": "INTEL", "name": "Uncertainty Estimation", "risk": RISK_READ_ONLY, "desc": "Capability 13: Shannon entropy, epistemic vs aleatoric decomposition, and unknown-unknown risk."},
    {"num": 14, "id": "intel_literature_analysis", "cat": "INTEL", "name": "Scientific Literature Analysis", "risk": RISK_READ_ONLY, "desc": "Capability 14: Extracts study design, sample size (N), p-values/CIs, rigor scorecard, and bias risk."},
    {"num": 15, "id": "intel_autonomous_report", "cat": "INTEL", "name": "Autonomous Report Generation", "risk": RISK_REVERSIBLE, "desc": "Capability 15: Compiles publication-ready Markdown briefings and 13-block holographic HUD decks."},
]


class SkillRegistry:
    def __init__(self):
        self.skills = {}
        self.enabled_state = {}
        for s in SKILL_DEFINITIONS:
            sid = s["id"]
            self.skills[sid] = dict(s)
            self.skills[sid]["status"] = STATUS_TESTED
            self.skills[sid]["enabled"] = True
            self.enabled_state[sid] = True

        self.intelligence_skills = {}
        for s in INTELLIGENCE_CAPABILITY_DEFINITIONS:
            sid = s["id"]
            self.intelligence_skills[sid] = dict(s)
            self.intelligence_skills[sid]["status"] = STATUS_TESTED
            self.intelligence_skills[sid]["enabled"] = True
            self.enabled_state[sid] = True

    def get_all(self, include_intelligence=False):
        base = list(self.skills.values())
        if include_intelligence:
            return base + list(self.intelligence_skills.values())
        return base

    def get_intelligence_skills(self):
        return list(self.intelligence_skills.values())

    def get_skill(self, skill_id):
        if skill_id in self.skills:
            return self.skills[skill_id]
        if skill_id in self.intelligence_skills:
            return self.intelligence_skills[skill_id]
        alias_key = f"intel_{skill_id}"
        if alias_key in self.intelligence_skills:
            return self.intelligence_skills[alias_key]
        return None

    def set_enabled(self, skill_id, enabled):
        if skill_id in self.skills:
            self.skills[skill_id]["enabled"] = bool(enabled)
            self.enabled_state[skill_id] = bool(enabled)
            return True
        if skill_id in self.intelligence_skills:
            self.intelligence_skills[skill_id]["enabled"] = bool(enabled)
            self.enabled_state[skill_id] = bool(enabled)
            return True
        alias_key = f"intel_{skill_id}"
        if alias_key in self.intelligence_skills:
            self.intelligence_skills[alias_key]["enabled"] = bool(enabled)
            self.enabled_state[alias_key] = bool(enabled)
            return True
        return False

    def get_by_category(self, cat_code):
        if cat_code == "INTEL":
            return list(self.intelligence_skills.values())
        return [s for s in self.skills.values() if s["cat"] == cat_code]

    def search(self, query):
        q = query.lower().strip()
        all_skills = list(self.skills.values()) + list(self.intelligence_skills.values())
        return [
            s for s in all_skills
            if q in s["name"].lower() or q in s["desc"].lower() or q in s["id"].lower()
        ]


# Global Skill Registry instance
registry = SkillRegistry()
