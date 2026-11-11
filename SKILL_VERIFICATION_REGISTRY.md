# J.A.R.V.I.S. Skill Verification Registry
**Individual Capability Audit & Execution Verification Ledger**  
**Execution Timestamp:** 2026-11-12 | **Total Capabilities Audited:** 150  
**Audit Result:** 150 / 150 Verified Operational (100% Pass Rate)

---

## Audit Methodology

Each of the 150 skills was individually executed through `dispatch_skill()` with realistic operational inputs, checking:
1. **Permission Gating:** Verified that `read_only` and `reversible` actions execute seamlessly, while `consequential` actions properly generate approval tokens.
2. **Handler Execution:** Executed native Win32 controls, screen capture, file operations, web research, Gemini API reasoning, and diagnostic telemetry.
3. **Output Schema Validation:** Confirmed that every handler returns structured dictionaries with explicit status flags and data payloads.


### Category A: Voice and Conversation (15 Skills)

| # | Skill ID | Name | Risk | Handler | Status | Execution Test & Verification |
|---|---|---|---|---|:---:|---|
| 1 | `voice_ptt` | **Push-to-Talk** | `read_only` | `h_voice_ptt` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 2 | `voice_toggle_listen` | **Toggle-to-Listen** | `read_only` | `h_voice_toggle_listen` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 3 | `voice_wake_phrase` | **Wake Phrase Detection** | `read_only` | `h_voice_wake_phrase` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 4 | `voice_transcription` | **Speech-to-Text** | `read_only` | `h_voice_transcription` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 5 | `voice_tts` | **Text-to-Speech Output** | `read_only` | `h_voice_tts` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 6 | `voice_rate_settings` | **Voice Rate Settings** | `reversible` | `h_voice_rate_settings` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 7 | `voice_interrupt` | **Interrupt Speech** | `read_only` | `h_voice_interrupt` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 8 | `voice_barge_in` | **Barge-In Listening** | `read_only` | `h_voice_barge_in` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 9 | `voice_context` | **Conversation Context** | `read_only` | `h_voice_context` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 10 | `voice_language_select` | **Language Selection** | `reversible` | `h_voice_language_select` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 11 | `voice_vad` | **Voice Activity Detection** | `read_only` | `h_voice_vad` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 12 | `voice_noise_filter` | **Noise-Aware Transcription** | `read_only` | `h_voice_noise_filter` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 13 | `voice_repeat` | **Repeat That Command** | `read_only` | `h_voice_repeat` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 14 | `voice_speak_slower` | **Speak More Slowly** | `reversible` | `h_voice_speak_slower` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 15 | `voice_stop_listening` | **Stop Listening / Stop Speaking** | `read_only` | `h_voice_stop_listening` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |

### Category B: Screen Vision and Annotation (15 Skills)

| # | Skill ID | Name | Risk | Handler | Status | Execution Test & Verification |
|---|---|---|---|---|:---:|---|
| 16 | `vis_capture_fullscreen` | **Capture Fullscreen** | `read_only` | `h_vis_capture_fullscreen` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 17 | `vis_capture_active_window` | **Capture Active Window** | `read_only` | `h_vis_capture_active_window` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 18 | `vis_capture_region` | **Capture Screen Region** | `read_only` | `h_vis_capture_region` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 19 | `vis_describe_screen` | **Describe Screen Contents** | `read_only` | `h_vis_describe_screen` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 20 | `vis_ocr_text` | **Read Visible Text (OCR)** | `read_only` | `h_vis_ocr_text` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 21 | `vis_explain_error` | **Explain Error Dialog** | `read_only` | `h_vis_explain_error` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 22 | `vis_identify_window` | **Identify Visible Window** | `read_only` | `h_vis_identify_window` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 23 | `vis_compare_screenshots` | **Compare Screenshots** | `read_only` | `h_vis_compare_screenshots` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 24 | `vis_find_control` | **Find Visible Control** | `read_only` | `h_vis_find_control` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 25 | `vis_highlight_control` | **Highlight Control** | `read_only` | `h_vis_highlight_control` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 26 | `vis_annotate_arrows` | **Add Arrows and Callouts** | `read_only` | `h_vis_annotate_arrows` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 27 | `vis_create_guide` | **Annotated Step-by-Step Guide** | `read_only` | `h_vis_create_guide` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 28 | `vis_explain_charts` | **Explain Charts and Layouts** | `read_only` | `h_vis_explain_charts` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 29 | `vis_detect_loading` | **Detect Modal / Loading State** | `read_only` | `h_vis_detect_loading` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 30 | `vis_request_region` | **Region Selection Prompt** | `read_only` | `h_vis_request_region` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |

### Category C: Desktop and Window Control (20 Skills)

| # | Skill ID | Name | Risk | Handler | Status | Execution Test & Verification |
|---|---|---|---|---|:---:|---|
| 31 | `desk_open_app` | **Open Application** | `reversible` | `h_desk_open_app` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 32 | `desk_focus_window` | **Focus Application Window** | `reversible` | `h_desk_focus_window` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 33 | `desk_min_max_restore` | **Minimize/Maximize/Restore** | `reversible` | `h_desk_min_max` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 34 | `desk_move_resize` | **Move and Resize Window** | `reversible` | `h_desk_move_resize` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 35 | `desk_switch_window` | **Switch Windows** | `reversible` | `h_desk_switch_window` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 36 | `desk_list_windows` | **List Visible Windows** | `read_only` | `h_desk_list_windows` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 37 | `desk_arrange_layout` | **Arrange Windows Layout** | `reversible` | `h_desk_arrange_layout` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 38 | `desk_open_explorer` | **Open Folder in Explorer** | `reversible` | `h_desk_open_explorer` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 39 | `desk_nav_known_folder` | **Navigate to Known Folder** | `reversible` | `h_desk_nav_known_folder` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 40 | `desk_open_file_default` | **Open File with Default App** | `reversible` | `h_desk_open_file_default` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 41 | `desk_copy_selected` | **Copy Selected Text** | `read_only` | `h_desk_copy_selected` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 42 | `desk_paste_content` | **Paste Content** | `reversible` | `h_desk_paste_content` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 43 | `desk_type_text` | **Type Text into Field** | `reversible` | `h_desk_type_text` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 44 | `desk_scroll_window` | **Scroll Window** | `reversible` | `h_desk_scroll` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 45 | `desk_keyboard_shortcut` | **Allowlisted Hotkey Dispatch** | `reversible` | `h_desk_shortcut` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 46 | `desk_capture_window` | **Screenshot Target Window** | `read_only` | `h_desk_capture_window` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 47 | `desk_detect_unresponsive` | **Detect Not Responding App** | `read_only` | `h_desk_detect_unresponsive` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 48 | `desk_wait_for_dialog` | **Wait for Dialog / Window** | `read_only` | `h_desk_wait_for_dialog` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 49 | `desk_return_focus` | **Return Previous Focus** | `reversible` | `h_desk_return_focus` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 50 | `desk_stop_automation` | **Global Stop All Automation** | `read_only` | `h_desk_stop` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |

### Category D: File and Folder Assistance (20 Skills)

| # | Skill ID | Name | Risk | Handler | Status | Execution Test & Verification |
|---|---|---|---|---|:---:|---|
| 51 | `file_search_names` | **Search Filenames** | `read_only` | `h_file_search_names` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 52 | `file_search_content` | **Search File Contents** | `read_only` | `h_file_search_content` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 53 | `file_list_contents` | **List Folder Contents** | `read_only` | `h_file_list_contents` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 54 | `file_find_duplicates` | **Find Duplicate Files** | `read_only` | `h_file_find_duplicates` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 55 | `file_summarize_pdf` | **Summarize PDF Document** | `read_only` | `h_file_summarize_pdf` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 56 | `file_extract_text` | **Extract Document Text** | `read_only` | `h_file_extract_text` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 57 | `file_summarize_sheet` | **Summarize Spreadsheet** | `read_only` | `h_file_summarize_sheet` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 58 | `file_create_doc` | **Create Markdown / Text File** | `reversible` | `h_file_create_doc` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 59 | `file_create_folders` | **Create Folder Structure** | `reversible` | `h_file_create_folders` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 60 | `file_rename_preview` | **Rename Files with Preview** | `consequential` | `h_file_rename_preview` | `PASS` | Gated with confirmation token 047f60ff; approved and verified |
| 61 | `file_move_preview` | **Move Files with Undo Log** | `consequential` | `h_file_move_preview` | `PASS` | Gated with confirmation token 45f92e28; approved and verified |
| 62 | `file_copy_verify` | **Copy Files with Verification** | `reversible` | `h_file_copy_verify` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 63 | `file_backup_bulk` | **Pre-Operation Backup** | `reversible` | `h_file_backup_before_bulk` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 64 | `file_organize_rules` | **Auto-Organize Archives** | `consequential` | `h_file_organize_rules` | `PASS` | Gated with confirmation token 18df1a8d; approved and verified |
| 65 | `file_find_large` | **Find Large Files** | `read_only` | `h_file_find_large` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 66 | `file_find_recent` | **Find Recently Modified** | `read_only` | `h_file_find_recent` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 67 | `file_inspect_metadata` | **Inspect File Metadata** | `read_only` | `h_file_metadata` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 68 | `file_convert_format` | **Convert Document Formats** | `reversible` | `h_file_convert_format` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 69 | `file_create_zip` | **Create ZIP Archive** | `reversible` | `h_file_create_zip` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 70 | `file_restore_backup` | **Restore from Safety Backup** | `consequential` | `h_file_restore_backup` | `PASS` | Gated with confirmation token aed17526; approved and verified |

### Category E: Web and Research (15 Skills)

| # | Skill ID | Name | Risk | Handler | Status | Execution Test & Verification |
|---|---|---|---|---|:---:|---|
| 71 | `web_search_queries` | **Web Search Query** | `read_only` | `h_web_search` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 72 | `web_open_url` | **Open Website URL** | `reversible` | `h_web_open_url` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 73 | `web_summarize_page` | **Summarize Webpage** | `read_only` | `h_web_summarize_page` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 74 | `web_compare_sources` | **Compare Multiple Sources** | `read_only` | `h_web_compare_sources` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 75 | `web_official_docs` | **Prioritize Official Docs** | `read_only` | `h_web_official_docs` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 76 | `web_extract_facts` | **Extract Facts & Citations** | `read_only` | `h_web_extract_facts` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 77 | `web_track_dates` | **Track Dates & Freshness** | `read_only` | `h_web_track_dates` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 78 | `web_research_brief` | **Build Research Brief** | `reversible` | `h_web_build_brief` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 79 | `web_find_tutorials` | **Find Learning Resources** | `read_only` | `h_web_find_tutorials` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 80 | `web_software_docs` | **Search Software APIs** | `read_only` | `h_web_search_devdocs` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 81 | `web_explain_article` | **Explain Technical Article** | `read_only` | `h_web_explain_article` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 82 | `web_comparison_table` | **Build Comparison Table** | `read_only` | `h_web_create_comparison_table` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 83 | `web_identify_conflicts` | **Identify Conflicting Claims** | `read_only` | `h_web_identify_conflicts` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 84 | `web_save_research_note` | **Save Research to Galaxy** | `reversible` | `h_web_save_research_note` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 85 | `web_confirm_submits` | **External Action Confirmation** | `consequential` | `h_web_prompt_before_form` | `PASS` | Gated with confirmation token 7ce310e9; approved and verified |

### Category F: Knowledge, Memory, and Personal Context (15 Skills)

| # | Skill ID | Name | Risk | Handler | Status | Execution Test & Verification |
|---|---|---|---|---|:---:|---|
| 86 | `mem_index_notes` | **Index Markdown Archives** | `read_only` | `h_mem_index_notes` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 87 | `mem_search_notes` | **Search Knowledge Base** | `read_only` | `h_mem_search_notes` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 88 | `mem_grounded_answer` | **Note-Grounded Q&A** | `read_only` | `h_mem_grounded_qa` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 89 | `mem_cite_sources` | **Cite Note ID Sources** | `read_only` | `h_mem_cite_sources` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 90 | `mem_refresh_galaxy` | **Build & Refresh Galaxy Graph** | `reversible` | `h_mem_refresh_galaxy` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 91 | `mem_fly_to_source` | **Fly Camera to Source Note** | `read_only` | `h_mem_fly_to_node` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 92 | `mem_remember_explicit` | **Total Recall Note Capture** | `reversible` | `h_mem_remember_this` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 93 | `mem_edit_note` | **Edit Note Content** | `consequential` | `h_mem_edit_note` | `PASS` | Gated with confirmation token 4fbf9428; approved and verified |
| 94 | `mem_detect_duplicates` | **Detect Duplicate Notes** | `read_only` | `h_mem_detect_duplicates` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 95 | `mem_link_related` | **Link Related Notes** | `reversible` | `h_mem_link_notes` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 96 | `mem_search_projects` | **Search Project History** | `read_only` | `h_mem_search_history` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 97 | `mem_user_context` | **Grounding in User Profile** | `read_only` | `h_mem_user_context` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 98 | `mem_inspect_memory` | **Inspect & Review Memory** | `read_only` | `h_mem_inspect_memory` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 99 | `mem_forget_entry` | **Forget Specific Memory** | `consequential` | `h_mem_forget_item` | `PASS` | Gated with confirmation token bfe56364; approved and verified |
| 100 | `mem_export_open_data` | **Export Notes & Memory** | `read_only` | `h_mem_export_knowledge` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |

### Category G: Productivity and Planning (15 Skills)

| # | Skill ID | Name | Risk | Handler | Status | Execution Test & Verification |
|---|---|---|---|---|:---:|---|
| 101 | `prod_create_task` | **Create Structured Task** | `reversible` | `h_prod_create_task` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 102 | `prod_breakdown_milestones` | **Breakdown into Milestones** | `read_only` | `h_prod_break_milestones` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 103 | `prod_daily_plan` | **Build Daily Schedule** | `read_only` | `h_prod_daily_plan` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 104 | `prod_summarize_tasks` | **Summarize Upcoming Tasks** | `read_only` | `h_prod_summarize_tasks` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 105 | `prod_draft_checklist` | **Draft Project Checklist** | `reversible` | `h_prod_draft_checklist` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 106 | `prod_meeting_brief` | **Meeting Preparation Brief** | `read_only` | `h_prod_meeting_brief` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 107 | `prod_study_timetable` | **Generate Study Timetable** | `read_only` | `h_prod_study_timetable` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 108 | `prod_revision_notes` | **Create Science Revision Notes** | `reversible` | `h_prod_revision_notes` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 109 | `prod_track_status` | **Track Project Status** | `read_only` | `h_prod_track_status` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 110 | `prod_identify_blockers` | **Identify Blocked Tasks** | `read_only` | `h_prod_find_blocked` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 111 | `prod_suggest_next` | **Suggest Next Action** | `read_only` | `h_prod_next_action` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 112 | `prod_create_reminder` | **Create Confirmed Reminder** | `reversible` | `h_prod_set_reminder` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 113 | `prod_daily_briefing` | **Deliver Daily Briefing** | `read_only` | `h_prod_daily_briefing` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 114 | `prod_voice_to_tasks` | **Voice Note to Task Items** | `reversible` | `h_prod_voice_to_tasks` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 115 | `prod_progress_summary` | **Generate Progress Summary** | `read_only` | `h_prod_progress_summary` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |

### Category H: Coding and Developer Assistance (15 Skills)

| # | Skill ID | Name | Risk | Handler | Status | Execution Test & Verification |
|---|---|---|---|---|:---:|---|
| 116 | `dev_explain_code` | **Explain Selected Code** | `read_only` | `h_dev_explain_code` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 117 | `dev_explain_terminal_error` | **Explain Terminal Error** | `read_only` | `h_dev_explain_terminal_error` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 118 | `dev_search_codebase` | **Search Codebase Files** | `read_only` | `h_dev_search_codebase` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 119 | `dev_map_structure` | **Map Project Structure** | `read_only` | `h_dev_map_project` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 120 | `dev_generate_patch` | **Generate Proposed Code Patch** | `read_only` | `h_dev_propose_patch` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 121 | `dev_review_diff` | **Review Diff Before Apply** | `read_only` | `h_dev_review_diff` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 122 | `dev_run_tests` | **Run Approved Unit Tests** | `reversible` | `h_dev_run_tests` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 123 | `dev_summarize_failures` | **Summarize Test Failures** | `read_only` | `h_dev_summarize_failures` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 124 | `dev_format_code` | **Format Code Syntax** | `reversible` | `h_dev_format_code` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 125 | `dev_investigate_bug` | **Investigate Crash / Bug** | `read_only` | `h_dev_find_bug_causes` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 126 | `dev_create_git_checkpoint` | **Create Git Checkpoint** | `reversible` | `h_dev_git_checkpoint` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 127 | `dev_generate_docs` | **Generate Technical Docs** | `reversible` | `h_dev_generate_docs` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 128 | `dev_explain_deps` | **Explain Dependencies** | `read_only` | `h_dev_explain_dependencies` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 129 | `dev_inspect_logs` | **Inspect Application Logs** | `read_only` | `h_dev_inspect_logs` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 130 | `dev_suggest_rollback` | **Suggest Rollback Plan** | `read_only` | `h_dev_suggest_rollback` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |

### Category I: PC Diagnostics and Settings (15 Skills)

| # | Skill ID | Name | Risk | Handler | Status | Execution Test & Verification |
|---|---|---|---|---|:---:|---|
| 131 | `sys_info` | **Read System Information** | `read_only` | `h_sys_info` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 132 | `sys_utilization` | **Read CPU / RAM / Disk Usage** | `read_only` | `h_sys_utilization` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 133 | `sys_disk_space` | **Report Available Disk Space** | `read_only` | `h_sys_disk_space` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 134 | `sys_startup_apps` | **Identify Startup Applications** | `read_only` | `h_sys_startup_apps` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 135 | `sys_installed_apps` | **Inspect Installed Applications** | `read_only` | `h_sys_installed_apps` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 136 | `sys_network_check` | **Check Network Connectivity** | `read_only` | `h_sys_network_check` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 137 | `sys_explain_win_errors` | **Explain Windows Error Codes** | `read_only` | `h_sys_explain_win_errors` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 138 | `sys_collect_logs` | **Collect Diagnostics Logs** | `read_only` | `h_sys_collect_logs` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 139 | `sys_check_app_running` | **Check if App is Running** | `read_only` | `h_sys_check_app` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 140 | `sys_settings_guidance` | **Windows Settings Guidance** | `read_only` | `h_sys_settings_guidance` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 141 | `sys_open_settings_page` | **Open Windows Settings Page** | `reversible` | `h_sys_open_settings` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 142 | `sys_driver_versions` | **Report Driver Versions** | `read_only` | `h_sys_driver_versions` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 143 | `sys_detect_bottlenecks` | **Detect Resource Bottlenecks** | `read_only` | `h_sys_detect_bottlenecks` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 144 | `sys_suggest_cleanup` | **Suggest Safe Cleanup Candidates** | `read_only` | `h_sys_suggest_cleanup` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 145 | `sys_diagnostic_report` | **Generate Diagnostic Report** | `read_only` | `h_sys_diagnostic_report` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |

### Category J: Creative and Media Work (5 Skills)

| # | Skill ID | Name | Risk | Handler | Status | Execution Test & Verification |
|---|---|---|---|---|:---:|---|
| 146 | `cre_draft_prompts` | **Draft Image & Video Prompts** | `read_only` | `h_cre_draft_prompts` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 147 | `cre_organize_assets` | **Organize Creative Assets** | `consequential` | `h_cre_organize_assets` | `PASS` | Gated with confirmation token 478de664; approved and verified |
| 148 | `cre_summarize_transcript` | **Summarize Audio Transcript** | `read_only` | `h_cre_summarize_transcript` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 149 | `cre_shot_lists` | **Create Shot Lists & Storyboards** | `read_only` | `h_cre_shot_lists` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |
| 150 | `cre_social_copy` | **Prepare Social Captions & Briefs** | `read_only` | `h_cre_social_copy` | `PASS` | Executed with HTTP-equivalent 200 payload and validated schema |