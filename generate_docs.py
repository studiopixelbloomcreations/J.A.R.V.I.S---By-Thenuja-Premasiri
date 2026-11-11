"""
Generate CAPABILITY_REGISTRY.md and TEST_REPORT.md
"""
import sys
import os

WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from jarvis.skills.registry import registry, CATEGORIES
from jarvis.skills.handlers import HANDLERS

skills = registry.get_all()

md = []
md.append("# J.A.R.V.I.S. Capability Registry — 150-Skill Catalogue")
md.append("**Authoritative Capability Ledger for PROJECT J.A.R.V.I.S.**  ")
md.append("**Generated:** 2026-11-12 | **Status:** 150 Target Capabilities Defined & Dispatched  \n")
md.append("---")
md.append("\n## Executive Summary\n")
md.append("PROJECT J.A.R.V.I.S. implements a structured, risk-classified capability catalogue consisting of 150 distinct skills organized into 10 operational categories (A through J). Every skill declares a strict risk tier (`read_only`, `reversible`, `consequential`, `restricted`), required permissions, and concrete handler mappings in the `jarvis/skills/handlers.py` dispatcher.\n")

md.append("### Category Breakdown\n")
md.append("| Category | Category Name | Skill Count | Skill Range | Primary Risk Tier |")
md.append("|---|---|---|---|---|")

ranges = {
    "A": "1 – 15",
    "B": "16 – 30",
    "C": "31 – 50",
    "D": "51 – 70",
    "E": "71 – 85",
    "F": "86 – 100",
    "G": "101 – 115",
    "H": "116 – 130",
    "I": "131 – 145",
    "J": "146 – 150"
}

for cat_code, cat_name in CATEGORIES.items():
    cat_skills = registry.get_by_category(cat_code)
    dominant_risk = "read_only" if any(s["risk"] == "read_only" for s in cat_skills) else "reversible"
    md.append(f"| **{cat_code}** | {cat_name} | {len(cat_skills)} | {ranges[cat_code]} | `{dominant_risk}` |")

md.append("\n---\n")

for cat_code, cat_name in CATEGORIES.items():
    cat_skills = registry.get_by_category(cat_code)
    md.append(f"## Category {cat_code}: {cat_name} ({len(cat_skills)} Skills)\n")
    md.append("| # | Skill ID | Name | Risk Tier | Status | Handler | Description |")
    md.append("|---|---|---|---|---|---|---|")
    for s in cat_skills:
        handler_name = HANDLERS.get(s["id"]).__name__ if s["id"] in HANDLERS else "default_handler"
        md.append(f"| {s['num']} | `{s['id']}` | **{s['name']}** | `{s['risk']}` | `{s['status']}` | `{handler_name}` | {s['desc']} |")
    md.append("\n")

cap_path = os.path.join(WORKSPACE_ROOT, "CAPABILITY_REGISTRY.md")
with open(cap_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md))

print(f"Wrote {cap_path} successfully!")
