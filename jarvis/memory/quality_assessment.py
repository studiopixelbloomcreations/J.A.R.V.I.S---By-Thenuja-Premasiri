"""
Memory Quality Assessment Engine for J.A.R.V.I.S.
Capability 100: Memory Quality Assessment

Evaluates memory freshness, completeness, consistency, and connectivity.
Detects stale memories, orphan nodes, conflicting facts, and generates
actionable health indices and remediation recommendations.
"""

import math
import time
from datetime import datetime
from typing import Dict, List, Set, Any, Optional


class MemoryQualityAssessor:
    """
    Quality control and diagnostic auditor for knowledge notes,
    personal memories, and research records.
    """

    def __init__(self, freshness_half_life_days: float = 90.0):
        self.freshness_half_life_days = freshness_half_life_days

    def assess_note(
        self,
        title: str,
        content: str,
        last_modified_epoch: Optional[float] = None,
        wikilinks: Optional[List[str]] = None,
        available_titles: Optional[Set[str]] = None
    ) -> Dict[str, Any]:
        """
        Assesses quality metrics for a single note or memory document.
        """
        issues: List[str] = []
        recommendations: List[str] = []

        # 1. Freshness Evaluation
        now_epoch = time.time()
        mod_epoch = last_modified_epoch or now_epoch
        days_old = max(0.0, (now_epoch - mod_epoch) / 86400.0)
        # Exponential decay: e^(-lambda * t)
        decay_lambda = math.log(2) / self.freshness_half_life_days
        freshness_score = round(100.0 * math.exp(-decay_lambda * days_old), 1)

        if days_old > 120:
            issues.append(f"Memory is aging ({int(days_old)} days old)")
            recommendations.append("Conduct review to refresh facts and references")

        # 2. Completeness Evaluation
        words = content.split()
        word_count = len(words)
        has_headings = "#" in content
        has_bullets = "-" in content or "*" in content

        completeness_points = 0
        if word_count >= 50:
            completeness_points += 40
        elif word_count >= 20:
            completeness_points += 25
        else:
            completeness_points += 10
            issues.append("Sparse content (< 20 words)")
            recommendations.append("Expand note with deeper contextual details")

        if has_headings:
            completeness_points += 30
        else:
            recommendations.append("Add structured markdown headings (e.g. ## Overview)")

        if has_bullets:
            completeness_points += 30

        completeness_score = min(100.0, completeness_points)

        # 3. Connectivity Evaluation
        links = wikilinks or []
        broken_links = []
        if available_titles:
            for l in links:
                if l not in available_titles:
                    broken_links.append(l)

        if broken_links:
            issues.append(f"Contains {len(broken_links)} unresolvable wikilinks: {', '.join(broken_links[:3])}")
            recommendations.append(f"Create missing target notes or update links")

        if not links:
            connectivity_score = 40.0
            issues.append("Orphan note (no outbound wikilinks)")
            recommendations.append("Link to relevant project or concept using [[Target]]")
        else:
            connectivity_score = min(100.0, 50.0 + len(links) * 15.0)

        # 4. Consistency & Contradiction Heuristics
        consistency_score = 100.0
        content_lower = content.lower()
        if "todo" in content_lower and "done" in content_lower and "completed" in content_lower:
            # Ambiguous completion state
            consistency_score -= 15.0

        # Weighted Overall Health Index
        # Freshness 25%, Completeness 35%, Connectivity 25%, Consistency 15%
        overall_health = round(
            0.25 * freshness_score +
            0.35 * completeness_score +
            0.25 * connectivity_score +
            0.15 * consistency_score,
            1
        )

        return {
            "title": title,
            "overall_health_score": overall_health,
            "freshness_score": freshness_score,
            "completeness_score": completeness_score,
            "connectivity_score": connectivity_score,
            "consistency_score": consistency_score,
            "days_since_update": round(days_old, 1),
            "word_count": word_count,
            "outbound_links_count": len(links),
            "broken_links": broken_links,
            "issues": issues,
            "recommendations": recommendations,
            "grade": self._score_to_grade(overall_health)
        }

    def assess_knowledge_base(self, notes_dict: Dict[str, str], metadata: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Assesses health metrics across the entire collection of notes and memories.
        """
        meta = metadata or {}
        available_titles = set(notes_dict.keys())
        assessments: List[Dict[str, Any]] = []

        import re
        wikilink_re = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')

        for title, content in notes_dict.items():
            links = wikilink_re.findall(content)
            m = meta.get(title, {})
            last_mod = m.get("last_modified")

            note_eval = self.assess_note(
                title=title,
                content=content,
                last_modified_epoch=last_mod,
                wikilinks=links,
                available_titles=available_titles
            )
            assessments.append(note_eval)

        if not assessments:
            return {"status": "empty", "overall_health": 100.0, "total_notes": 0}

        avg_health = round(sum(a["overall_health_score"] for a in assessments) / len(assessments), 1)
        avg_freshness = round(sum(a["freshness_score"] for a in assessments) / len(assessments), 1)
        avg_completeness = round(sum(a["completeness_score"] for a in assessments) / len(assessments), 1)
        avg_connectivity = round(sum(a["connectivity_score"] for a in assessments) / len(assessments), 1)

        orphan_notes = [a["title"] for a in assessments if a["outbound_links_count"] == 0]
        critical_issues = [a for a in assessments if a["overall_health_score"] < 60.0]

        return {
            "status": "success",
            "total_notes_assessed": len(assessments),
            "average_health_score": avg_health,
            "grade": self._score_to_grade(avg_health),
            "telemetry": {
                "avg_freshness": avg_freshness,
                "avg_completeness": avg_completeness,
                "avg_connectivity": avg_connectivity
            },
            "orphan_notes_count": len(orphan_notes),
            "orphan_notes": orphan_notes[:10],
            "attention_required_count": len(critical_issues),
            "attention_required": critical_issues[:5]
        }

    def _score_to_grade(self, score: float) -> str:
        """Converts numeric score to health grade."""
        if score >= 90.0:
            return "A+ (Optimal)"
        elif score >= 80.0:
            return "A (Healthy)"
        elif score >= 70.0:
            return "B (Good)"
        elif score >= 60.0:
            return "C (Fair)"
        else:
            return "D (Needs Attention)"


# Module singleton
memory_quality_assessor = MemoryQualityAssessor()
