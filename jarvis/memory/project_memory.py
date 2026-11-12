"""
Project Memory Management Engine for J.A.R.V.I.S.
Capability 92: Project Memory

Tracks project contexts, architecture decisions, milestones, tech stacks,
dependencies, and active operational blockers across all initiatives.
"""

import json
import uuid
import pathlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from ..config import DATA_DIR

PROJECT_MEMORY_FILE = DATA_DIR / "project_memory.json"


class ProjectMemoryManager:
    """
    Manages longitudinal memory for all active and archived projects,
    recording architecture decisions, milestones, blockers, and tech specs.
    """

    def __init__(self, storage_path: Optional[pathlib.Path] = None):
        self.storage_path = storage_path or PROJECT_MEMORY_FILE
        self.projects: Dict[str, Dict[str, Any]] = {}
        self.load()
        if not self.projects:
            self._seed_default_projects()

    def register_project(
        self,
        project_id: str,
        name: str,
        description: str,
        category: str = "engineering",
        tech_stack: Optional[List[str]] = None,
        status: str = "active"
    ) -> Dict[str, Any]:
        """Registers a new project or updates an existing one."""
        p_id = project_id.lower().strip().replace(" ", "_")
        proj = {
            "project_id": p_id,
            "name": name,
            "description": description,
            "category": category,
            "tech_stack": tech_stack or [],
            "status": status,
            "milestones": [],
            "decisions": [],
            "blockers": [],
            "created_at": self.projects.get(p_id, {}).get("created_at", datetime.now().isoformat()),
            "last_updated": datetime.now().isoformat()
        }
        self.projects[p_id] = proj
        self.save()
        return proj

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves project memory by project ID."""
        p_id = project_id.lower().strip().replace(" ", "_")
        return self.projects.get(p_id)

    def list_projects(self, category: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists projects matching optional category and status filters."""
        results = []
        for p in self.projects.values():
            if category and p.get("category", "").lower() != category.lower():
                continue
            if status and p.get("status", "").lower() != status.lower():
                continue
            results.append(p)
        return results

    def add_milestone(
        self,
        project_id: str,
        name: str,
        target_date: str = "",
        status: str = "pending"
    ) -> Optional[Dict[str, Any]]:
        """Adds a milestone to a project."""
        p = self.get_project(project_id)
        if not p:
            return None

        milestone = {
            "id": f"ms_{len(p['milestones']) + 1}",
            "name": name,
            "target_date": target_date,
            "status": status,
            "created_at": datetime.now().isoformat()
        }
        p["milestones"].append(milestone)
        p["last_updated"] = datetime.now().isoformat()
        self.save()
        return milestone

    def update_milestone_status(self, project_id: str, milestone_id: str, status: str) -> bool:
        """Updates the status of a specific milestone."""
        p = self.get_project(project_id)
        if not p:
            return False

        for ms in p["milestones"]:
            if ms["id"] == milestone_id or ms["name"].lower() == milestone_id.lower():
                ms["status"] = status
                p["last_updated"] = datetime.now().isoformat()
                self.save()
                return True
        return False

    def record_decision(
        self,
        project_id: str,
        title: str,
        rationale: str,
        alternatives: Optional[List[str]] = None,
        author: str = "Thenuja Premasiri"
    ) -> Optional[Dict[str, Any]]:
        """Records an Architectural Decision Record (ADR)."""
        p = self.get_project(project_id)
        if not p:
            return None

        decision = {
            "id": f"adr_{len(p['decisions']) + 1}",
            "title": title,
            "rationale": rationale,
            "alternatives_considered": alternatives or [],
            "author": author,
            "timestamp": datetime.now().isoformat()
        }
        p["decisions"].append(decision)
        p["last_updated"] = datetime.now().isoformat()
        self.save()
        return decision

    def add_blocker(self, project_id: str, description: str, severity: str = "medium") -> Optional[Dict[str, Any]]:
        """Logs an operational or technical blocker."""
        p = self.get_project(project_id)
        if not p:
            return None

        blocker = {
            "id": f"blk_{uuid.uuid4().hex[:6]}",
            "description": description,
            "severity": severity,
            "resolved": False,
            "created_at": datetime.now().isoformat()
        }
        p["blockers"].append(blocker)
        p["last_updated"] = datetime.now().isoformat()
        self.save()
        return blocker

    def resolve_blocker(self, project_id: str, blocker_id: str) -> bool:
        """Marks a blocker as resolved."""
        p = self.get_project(project_id)
        if not p:
            return False

        for blk in p["blockers"]:
            if blk["id"] == blocker_id:
                blk["resolved"] = True
                blk["resolved_at"] = datetime.now().isoformat()
                p["last_updated"] = datetime.now().isoformat()
                self.save()
                return True
        return False

    def get_all_active_blockers(self) -> List[Dict[str, Any]]:
        """Returns all unresolved blockers across every registered project."""
        unresolved = []
        for p in self.projects.values():
            for blk in p.get("blockers", []):
                if not blk.get("resolved"):
                    unresolved.append({
                        "project_id": p["project_id"],
                        "project_name": p["name"],
                        **blk
                    })
        return unresolved

    def _seed_default_projects(self):
        """Pre-seeds standard projects from user context."""
        jarvis = self.register_project(
            "jarvis",
            "Project J.A.R.V.I.S.",
            "Autonomous multi-agent desktop intelligence system with cybernetic HUD and 24/7 voice interaction.",
            "engineering",
            ["Python", "FastAPI", "Gemini 3.5", "Web Audio API", "Fish Audio", "Three.js"],
            "active"
        )
        self.add_milestone("jarvis", "150-Skill Comprehensive Architecture", "2026-11-15", "completed")
        self.add_milestone("jarvis", "Native Swarm Autonomous Multi-Agent", "2026-11-20", "in_progress")
        self.record_decision(
            "jarvis",
            "Local Fallback Determinism",
            "All core skills and tests execute deterministically without external cloud dependency blockers."
        )

        self.register_project(
            "pixel_bloom",
            "Pixel Bloom Studios",
            "Creative VFX, cinematic animation, and AI-assisted short film production studio.",
            "creative",
            ["DaVinci Resolve", "Blender 3D", "CapCut", "Stable Diffusion", "Midjourney"],
            "active"
        )
        self.add_milestone("pixel_bloom", "Character Consistency & Continuity Bible", "2026-12-01", "in_progress")

        self.register_project(
            "stem_mind",
            "STEM-Mind",
            "Curriculum-aligned science and STEM revision portal for Grade 10 students.",
            "education",
            ["Markdown", "Anki", "Quizlet API", "Python"],
            "active"
        )

        self.register_project(
            "aevra",
            "Project Aevra",
            "Next-generation autonomous agent ecosystem and workflow automation suite.",
            "engineering",
            ["Python", "TypeScript", "Docker"],
            "planning"
        )

        self.save()

    def load(self):
        """Loads projects from disk."""
        if self.storage_path and self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text(encoding="utf-8"))
                self.projects = data.get("projects", {})
            except Exception:
                self.projects = {}

    def save(self):
        """Saves projects to disk."""
        if self.storage_path:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "project_count": len(self.projects),
                "projects": self.projects
            }
            self.storage_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


# Module singleton
project_memory = ProjectMemoryManager()
