"""
Populates individual personal markdown notes from JARVIS-User-Context-Profile.md,
expanding them with semantic understanding, cross-references, and clear titles.
"""
import pathlib
import os
import re

NOTES_DIR = pathlib.Path("notes")
PERSONAL_DIR = NOTES_DIR / "personal"
PROFILE_PATH = pathlib.Path("JARVIS-User-Context-Profile.md")

SECTION_MAP = [
    {
        "num": "1",
        "filename": "Operating Protocols and Context Usage.md",
        "title": "Operating Protocols & Context Usage",
        "tags": ["protocol", "safety", "context", "jarvis"],
        "summary": "Rules for how J.A.R.V.I.S. processes personal context without exposing credentials or making assumptions."
    },
    {
        "num": "2",
        "filename": "General Preferences and Working Style.md",
        "title": "General Preferences & Working Style",
        "tags": ["preferences", "style", "personality", "hud"],
        "summary": "Preferences for cinematic Iron Man J.A.R.V.I.S. experience, direct actionable guidance, and high polish."
    },
    {
        "num": "3",
        "filename": "Education and Academic Background.md",
        "title": "Education & Academic Background",
        "tags": ["school", "education", "st-annes", "debating", "revision"],
        "summary": "Grade 10 academic context at St. Anne's College Kurunegala, English debating circle, and science revision."
    },
    {
        "num": "4",
        "filename": "Creative VFX and Short Film Goals.md",
        "title": "Creative VFX & Short Film Goals",
        "tags": ["creative", "vfx", "animation", "film", "davinci-resolve"],
        "summary": "Goal of becoming an AI VFX artist and director with CapCut, DaVinci Resolve, and cinematic 3D style."
    },
    {
        "num": "5.1",
        "filename": "Pixel Bloom Studios.md",
        "title": "Pixel Bloom Studios Creative Business",
        "tags": ["business", "pixel-bloom", "videography", "branding", "studio"],
        "summary": "Online creative venture 'Built by Pixels, Grown with Vision' covering video editing, photography, and design."
    },
    {
        "num": "5.2",
        "filename": "Creative Brands and Merchandise Concepts.md",
        "title": "Creative Brands & Merchandise Concepts",
        "tags": ["branding", "merch", "botani-code", "synth-bloom", "photography"],
        "summary": "Exploratory brand concepts including Botani Code, Synth Bloom, and event photography services."
    },
    {
        "num": "6",
        "filename": "Project JARVIS Architecture.md",
        "title": "Project JARVIS Assistant Architecture",
        "tags": ["jarvis", "architecture", "desktop-assistant", "orb", "vision"],
        "summary": "Core technical specification for J.A.R.V.I.S. desktop assistant: interactive orb, screen awareness, and 150 skills."
    },
    {
        "num": "7",
        "filename": "Aevra and Software Engineering Projects.md",
        "title": "Aevra & Software Engineering Projects",
        "tags": ["aevra", "stem-mind", "ai", "coding", "agents"],
        "summary": "Explorations with Aevra personal AI system, STEM-Mind-AI repository, and modern agentic coding workflows."
    },
    {
        "num": "8.1",
        "filename": "Main PC Hardware Specifications.md",
        "title": "Main PC Hardware Specifications (ThenujaPC)",
        "tags": ["hardware", "pc", "specs", "intel-i3", "windows-11"],
        "summary": "Hardware profile for ThenujaPC: Intel Core i3-3240, 6GB DDR3 RAM, H61 motherboard, 256GB NVMe SSD."
    },
    {
        "num": "8.2",
        "filename": "Secondary Device Fleet.md",
        "title": "Secondary Device Fleet",
        "tags": ["hardware", "laptops", "dell-inspiron", "hp-elitebook"],
        "summary": "Secondary computing devices: Dell Inspiron 15 3000 (Pentium 5405U) and HP EliteBook x360 1030 G2."
    },
    {
        "num": "8.3",
        "filename": "PC Maintenance and Storage Safety.md",
        "title": "PC Maintenance & Storage Safety Protocols",
        "tags": ["maintenance", "powershell", "safety", "storage", "diskpart"],
        "summary": "Strict safeguards against accidental disk formatting, PowerShell driver scripts, and system health checks."
    },
    {
        "num": "9",
        "filename": "Robotics Team Byte Raiders.md",
        "title": "Robotics Team Byte Raiders",
        "tags": ["robotics", "byte-raiders", "esp32", "cy-bots", "kandy"],
        "summary": "5-member school robotics team Byte Raiders competing in CY-BOTS Kick League soccer robot event at NIBM Kandy."
    },
    {
        "num": "10",
        "filename": "Active and Recurring Projects Directory.md",
        "title": "Active & Recurring Projects Directory",
        "tags": ["projects", "index", "portfolio", "creative", "engineering"],
        "summary": "Master index of Thenuja's recurring initiatives across AI development, media production, and robotics."
    },
    {
        "num": "11",
        "filename": "Software and Platform Ecosystem.md",
        "title": "Software & Development Toolchain",
        "tags": ["software", "tools", "blender", "capcut", "vscode", "github"],
        "summary": "Preferred software inventory: Windows 11, VS Code, Google Chrome, DaVinci Resolve, CapCut, Blender, GitHub."
    },
    {
        "num": "12",
        "filename": "Regional and Currency Context Sri Lanka.md",
        "title": "Regional & Currency Context (Sri Lanka)",
        "tags": ["location", "sri-lanka", "kurunegala", "kandy", "lkr"],
        "summary": "Regional grounding in Sri Lanka (Kurunegala/Kandy), pricing in LKR, and local educational/business environment."
    },
    {
        "num": "13",
        "filename": "Personalization Directives for Assistance.md",
        "title": "Personalization Directives for Assistance",
        "tags": ["persona", "tone", "personalization", "assistance", "butler"],
        "summary": "Guidelines for calibrating J.A.R.V.I.S. assistance across technical, creative, and academic inquiries."
    }
]


def extract_sections(text):
    """Extract raw section bodies from profile text."""
    sections = {}
    
    # 1. Main numbered sections
    sec_pattern = r'(?m)^#\s+(\d+)\.\s+(.+)$'
    matches = list(re.finditer(sec_pattern, text))
    
    for i, m in enumerate(matches):
        sec_num = m.group(1)
        start_pos = m.start()
        end_pos = matches[i+1].start() if i+1 < len(matches) else len(text)
        chunk = text[start_pos:end_pos].strip()
        sections[sec_num] = chunk
        
        # Subsections inside section 5
        if sec_num == "5":
            sub_51 = re.search(r'(?s)##\s+5\.1\s+Pixel Bloom Studios(.*?)(?=##\s+5\.2|\Z)', chunk)
            if sub_51:
                sections["5.1"] = f"# 5.1 Pixel Bloom Studios\n\n{sub_51.group(1).strip()}"
            sub_52 = re.search(r'(?s)##\s+5\.2\s+Other creative/business ideas(.*?)\Z', chunk)
            if sub_52:
                sections["5.2"] = f"# 5.2 Creative Brands and Merchandise\n\n{sub_52.group(1).strip()}"
                
        # Subsections inside section 8
        if sec_num == "8":
            sub_81 = re.search(r'(?s)##\s+8\.1\s+Main desktop.*?ThenujaPC(.*?)(?=##\s+8\.2|\Z)', chunk)
            if sub_81:
                sections["8.1"] = f"# 8.1 Main Desktop - ThenujaPC\n\n{sub_81.group(1).strip()}"
            sub_82 = re.search(r'(?s)##\s+8\.2\s+Other devices previously discussed(.*?)(?=##\s+8\.3|\Z)', chunk)
            if sub_82:
                sections["8.2"] = f"# 8.2 Secondary Device Fleet\n\n{sub_82.group(1).strip()}"
            sub_83 = re.search(r'(?s)##\s+8\.3\s+PC maintenance preferences(.*?)\Z', chunk)
            if sub_83:
                sections["8.3"] = f"# 8.3 PC Maintenance & Storage Safety\n\n{sub_83.group(1).strip()}"

    return sections


def main():
    if not PROFILE_PATH.exists():
        print(f"Error: {PROFILE_PATH} not found.")
        return

    PERSONAL_DIR.mkdir(parents=True, exist_ok=True)
    
    # Remove monolithic duplicate if exists
    monolithic = PERSONAL_DIR / "User Context Profile For.md"
    if monolithic.exists():
        monolithic.unlink()
        print(f"Removed monolithic note: {monolithic.name}")

    text = PROFILE_PATH.read_text(encoding="utf-8")
    sections = extract_sections(text)
    
    created_count = 0
    for meta in SECTION_MAP:
        key = meta["num"]
        content = sections.get(key)
        if not content:
            continue
            
        tags_str = ", ".join(meta["tags"])
        note_body = f"""# {meta['title']}
> **Category:** Personal / Knowledge Graph  
> **Tags:** [{tags_str}]  
> **Status:** Grounded Personal Context  

{content}

---

## 🧠 J.A.R.V.I.S. Neural Synthesis & Semantic Context
- **Core Semantic Understanding**: {meta['summary']}
- **Autonomous Operational Impact**: J.A.R.V.I.S. cross-references this context whenever executing desktop automation, answering questions, or rendering creative/technical guidance.
- **Knowledge Galaxy Cross-References**: Connected to [[Project JARVIS Architecture]], [[Pixel Bloom Studios]], [[Main PC Hardware Specifications]], and [[Personalization Directives]].
"""
        note_file = PERSONAL_DIR / meta["filename"]
        note_file.write_text(note_body.strip() + "\n", encoding="utf-8")
        created_count += 1
        print(f"  Created: {note_file.name} ({len(note_body)} chars)")

    print(f"\nSuccessfully generated {created_count} modular personal notes in {PERSONAL_DIR}")


if __name__ == "__main__":
    main()
