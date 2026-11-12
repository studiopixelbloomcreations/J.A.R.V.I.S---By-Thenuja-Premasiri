"""
Capability 101: Goal Decomposition
Decomposes complex high-level goals into structured hierarchical sub-goals,
identifies prerequisites, inputs/outputs, risk classifications, and acceptance criteria.
"""
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

from ..core.permissions import RISK_READ_ONLY, RISK_REVERSIBLE, RISK_CONSEQUENTIAL, RISK_RESTRICTED


@dataclass
class SubGoal:
    """Represents a discrete, executable sub-goal resulting from goal decomposition."""
    id: str
    title: str
    description: str
    phase: int
    dependencies: List[str] = field(default_factory=list)
    estimated_complexity: str = "medium"  # low, medium, high
    estimated_seconds: int = 60
    risk_level: str = RISK_READ_ONLY
    inputs: List[str] = field(default_factory=list)
    expected_outputs: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SubGoal:
        return cls(**data)


@dataclass
class DecomposedGoal:
    """Structured representation of a decomposed high-level objective."""
    goal_id: str
    original_goal: str
    objective_summary: str
    constraints: List[str] = field(default_factory=list)
    preconditions: List[str] = field(default_factory=list)
    sub_goals: List[SubGoal] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "original_goal": self.original_goal,
            "objective_summary": self.objective_summary,
            "constraints": self.constraints,
            "preconditions": self.preconditions,
            "sub_goals": [sg.to_dict() for sg in self.sub_goals],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DecomposedGoal:
        sub_goals_data = data.get("sub_goals", [])
        sub_goals = [SubGoal.from_dict(sg) for sg in sub_goals_data]
        return cls(
            goal_id=data["goal_id"],
            original_goal=data["original_goal"],
            objective_summary=data["objective_summary"],
            constraints=data.get("constraints", []),
            preconditions=data.get("preconditions", []),
            sub_goals=sub_goals,
            metadata=data.get("metadata", {}),
        )

    def to_markdown_plan(self) -> str:
        """Renders the decomposed plan into a readable Markdown document."""
        lines = [
            f"# Execution Plan: {self.objective_summary}",
            f"**Goal ID:** `{self.goal_id}`",
            f"**Original Goal:** {self.original_goal}",
            "",
            "## Constraints & Preconditions",
        ]
        if self.constraints:
            lines.append("### Constraints")
            for c in self.constraints:
                lines.append(f"- {c}")
        if self.preconditions:
            lines.append("### Preconditions")
            for p in self.preconditions:
                lines.append(f"- {p}")
        lines.append("")
        lines.append("## Decomposed Sub-Goals")
        for sg in sorted(self.sub_goals, key=lambda x: (x.phase, x.id)):
            deps = ", ".join(sg.dependencies) if sg.dependencies else "None"
            lines.extend([
                f"### Phase {sg.phase}: {sg.title} (`{sg.id}`)",
                f"- **Description:** {sg.description}",
                f"- **Dependencies:** {deps}",
                f"- **Complexity:** {sg.estimated_complexity} (~{sg.estimated_seconds}s)",
                f"- **Risk Level:** `{sg.risk_level}`",
                f"- **Inputs:** {', '.join(sg.inputs) if sg.inputs else 'None'}",
                f"- **Expected Outputs:** {', '.join(sg.expected_outputs) if sg.expected_outputs else 'None'}",
                "- **Acceptance Criteria:**",
            ])
            for ac in sg.acceptance_criteria:
                lines.append(f"  - [ ] {ac}")
            lines.append("")
        return "\n".join(lines)


class GoalDecomposer:
    """
    Capability 101: Goal Decomposition Engine.
    Analyzes high-level objectives, detects domain patterns, and partitions goals
    into modular phases and discrete dependency-linked sub-goals.
    """

    def __init__(self):
        # Domain keyword indicators to tailor decomposition templates
        self._domain_indicators = {
            "research": ["research", "investigate", "study", "analyze", "literature", "paper", "survey"],
            "software": ["code", "build", "develop", "refactor", "test", "api", "bug", "implement", "feature"],
            "security": ["audit", "vulnerability", "cve", "firewall", "security", "scan", "penetration"],
            "data": ["dataset", "csv", "clean", "extract", "etl", "database", "query", "metrics"],
            "document": ["document", "report", "manual", "guide", "summary", "writeup", "slides"]
        }

    def detect_domain(self, text: str) -> str:
        """Determines primary domain of the objective."""
        t_lower = text.lower()
        counts = {dom: 0 for dom in self._domain_indicators}
        for dom, keywords in self._domain_indicators.items():
            for kw in keywords:
                if re.search(rf"\b{re.escape(kw)}\b", t_lower):
                    counts[dom] += 1
        sorted_doms = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_doms[0][0] if sorted_doms[0][1] > 0 else "general"

    def decompose(self, goal: str, context: Optional[Dict[str, Any]] = None) -> DecomposedGoal:
        """
        Decomposes a goal string into a comprehensive DecomposedGoal DAG specification.
        """
        context = context or {}
        goal_id = f"goal_{uuid.uuid4().hex[:8]}"
        clean_goal = goal.strip()
        domain = self.detect_domain(clean_goal)

        # Detect constraints
        constraints = []
        if "without" in clean_goal.lower():
            match = re.search(r'without\s+([^,.;]+)', clean_goal, re.IGNORECASE)
            if match:
                constraints.append(f"Avoid: {match.group(1).strip()}")
        if "must" in clean_goal.lower():
            match = re.search(r'must\s+([^,.;]+)', clean_goal, re.IGNORECASE)
            if match:
                constraints.append(f"Mandatory: {match.group(1).strip()}")
        if not constraints:
            constraints.append("Execution must adhere to safe permission boundaries and avoid data loss.")

        preconditions = [
            "Workspace and storage directories accessible",
            "Required runtime dependencies verified"
        ]

        # Generate sub-goals based on domain patterns
        sub_goals: List[SubGoal] = []
        if domain == "software":
            sub_goals = self._decompose_software(clean_goal)
        elif domain == "research":
            sub_goals = self._decompose_research(clean_goal)
        elif domain == "security":
            sub_goals = self._decompose_security(clean_goal)
        else:
            sub_goals = self._decompose_generic(clean_goal)

        return DecomposedGoal(
            goal_id=goal_id,
            original_goal=clean_goal,
            objective_summary=clean_goal[:120],
            constraints=constraints,
            preconditions=preconditions,
            sub_goals=sub_goals,
            metadata={"domain": domain, "context": context}
        )

    def _decompose_software(self, goal: str) -> List[SubGoal]:
        sg1_id = "sg_arch"
        sg2_id = "sg_impl"
        sg3_id = "sg_test"
        sg4_id = "sg_docs"

        return [
            SubGoal(
                id=sg1_id,
                title="Architecture & Interface Design",
                description=f"Define component specifications, class interfaces, and modular layout for: {goal}",
                phase=1,
                dependencies=[],
                estimated_complexity="medium",
                estimated_seconds=45,
                risk_level=RISK_READ_ONLY,
                inputs=["user_specification", "existing_codebase"],
                expected_outputs=["interface_specs", "module_layout"],
                acceptance_criteria=["Module architecture is non-cyclic and modular.", "Interfaces are typed."]
            ),
            SubGoal(
                id=sg2_id,
                title="Core Implementation",
                description=f"Implement functions, handlers, and business logic for: {goal}",
                phase=2,
                dependencies=[sg1_id],
                estimated_complexity="high",
                estimated_seconds=120,
                risk_level=RISK_REVERSIBLE,
                inputs=["interface_specs"],
                expected_outputs=["source_code"],
                acceptance_criteria=["Code compiles and passes ast.parse without syntax errors.", "Adheres to standards."]
            ),
            SubGoal(
                id=sg3_id,
                title="Verification & Unit Testing",
                description="Write and execute automated unit tests covering edge cases, assertions, and contracts.",
                phase=3,
                dependencies=[sg2_id],
                estimated_complexity="medium",
                estimated_seconds=60,
                risk_level=RISK_READ_ONLY,
                inputs=["source_code"],
                expected_outputs=["test_results", "test_report"],
                acceptance_criteria=["All test assertions pass cleanly with 0 errors.", "Edge cases covered."]
            ),
            SubGoal(
                id=sg4_id,
                title="Documentation & Integration",
                description="Generate technical docstrings, API reference, and usage documentation.",
                phase=4,
                dependencies=[sg3_id],
                estimated_complexity="low",
                estimated_seconds=30,
                risk_level=RISK_REVERSIBLE,
                inputs=["source_code", "test_results"],
                expected_outputs=["markdown_docs", "changelog_entry"],
                acceptance_criteria=["Documentation includes complete usage examples and parameter definitions."]
            )
        ]

    def _decompose_research(self, goal: str) -> List[SubGoal]:
        sg1_id = "sg_gather"
        sg2_id = "sg_synthesize"
        sg3_id = "sg_verify"
        sg4_id = "sg_report"

        return [
            SubGoal(
                id=sg1_id,
                title="Information Gathering & Source Collection",
                description=f"Query local notes, documents, and external sources for: {goal}",
                phase=1,
                dependencies=[],
                estimated_complexity="medium",
                estimated_seconds=40,
                risk_level=RISK_READ_ONLY,
                inputs=["query_terms"],
                expected_outputs=["raw_sources", "citations"],
                acceptance_criteria=["At least 3 authoritative sources or notes identified."]
            ),
            SubGoal(
                id=sg2_id,
                title="Evidence Synthesis & Analysis",
                description="Extract key findings, detect contradictions, and synthesize thematic insights.",
                phase=2,
                dependencies=[sg1_id],
                estimated_complexity="medium",
                estimated_seconds=50,
                risk_level=RISK_READ_ONLY,
                inputs=["raw_sources"],
                expected_outputs=["synthesized_findings", "comparison_matrix"],
                acceptance_criteria=["Core claims mapped to source references with uncertainty scores."]
            ),
            SubGoal(
                id=sg3_id,
                title="Fact Verification & Cross-Checking",
                description="Cross-verify numerical data, dates, and conclusions against primary references.",
                phase=3,
                dependencies=[sg2_id],
                estimated_complexity="low",
                estimated_seconds=30,
                risk_level=RISK_READ_ONLY,
                inputs=["synthesized_findings"],
                expected_outputs=["verification_log"],
                acceptance_criteria=["Conflicting claims are explicitly flagged and resolved."]
            ),
            SubGoal(
                id=sg4_id,
                title="Research Report Generation",
                description="Compile complete structured research brief with executive summary and actionable takeaways.",
                phase=4,
                dependencies=[sg3_id],
                estimated_complexity="low",
                estimated_seconds=30,
                risk_level=RISK_REVERSIBLE,
                inputs=["synthesized_findings", "verification_log"],
                expected_outputs=["research_dossier_markdown"],
                acceptance_criteria=["Report adheres to standard academic/intelligence dossier format."]
            )
        ]

    def _decompose_security(self, goal: str) -> List[SubGoal]:
        sg1_id = "sg_sec_inventory"
        sg2_id = "sg_sec_scan"
        sg3_id = "sg_sec_remediate"
        sg4_id = "sg_sec_audit_doc"

        return [
            SubGoal(
                id=sg1_id,
                title="Asset & Attack Surface Discovery",
                description=f"Map target scopes, configurations, interfaces, and permissions for: {goal}",
                phase=1,
                dependencies=[],
                estimated_complexity="medium",
                estimated_seconds=40,
                risk_level=RISK_READ_ONLY,
                inputs=["target_scope"],
                expected_outputs=["asset_inventory"],
                acceptance_criteria=["Target boundaries and authorization boundaries defined."]
            ),
            SubGoal(
                id=sg2_id,
                title="Vulnerability & Policy Scanning",
                description="Execute non-destructive security checks, dependency audits, and baseline comparisons.",
                phase=2,
                dependencies=[sg1_id],
                estimated_complexity="high",
                estimated_seconds=75,
                risk_level=RISK_READ_ONLY,
                inputs=["asset_inventory"],
                expected_outputs=["vulnerability_findings"],
                acceptance_criteria=["Findings categorized by CVSS severity and false-positive checks performed."]
            ),
            SubGoal(
                id=sg3_id,
                title="Remediation Plan Formulation",
                description="Synthesize precise patches, configuration adjustments, and hardening directives.",
                phase=3,
                dependencies=[sg2_id],
                estimated_complexity="medium",
                estimated_seconds=45,
                risk_level=RISK_REVERSIBLE,
                inputs=["vulnerability_findings"],
                expected_outputs=["hardening_plan"],
                acceptance_criteria=["Rollback instructions provided for every configuration modification."]
            ),
            SubGoal(
                id=sg4_id,
                title="Security Posture Report",
                description="Draft executive posture summary, compliance status, and security audit log.",
                phase=4,
                dependencies=[sg3_id],
                estimated_complexity="low",
                estimated_seconds=25,
                risk_level=RISK_REVERSIBLE,
                inputs=["vulnerability_findings", "hardening_plan"],
                expected_outputs=["security_audit_report"],
                acceptance_criteria=["Includes clear risk metrics and signed verification timestamps."]
            )
        ]

    def _decompose_generic(self, goal: str) -> List[SubGoal]:
        sg1_id = "sg_assess"
        sg2_id = "sg_execute"
        sg3_id = "sg_validate"

        return [
            SubGoal(
                id=sg1_id,
                title="Preparation & Scope Assessment",
                description=f"Analyze inputs, verify dependencies, and outline steps for: {goal}",
                phase=1,
                dependencies=[],
                estimated_complexity="low",
                estimated_seconds=30,
                risk_level=RISK_READ_ONLY,
                inputs=["initial_prompt"],
                expected_outputs=["prepared_context"],
                acceptance_criteria=["Scope is bounded and unambiguous."]
            ),
            SubGoal(
                id=sg2_id,
                title="Primary Execution",
                description=f"Perform the core transformation or task actions for: {goal}",
                phase=2,
                dependencies=[sg1_id],
                estimated_complexity="medium",
                estimated_seconds=60,
                risk_level=RISK_REVERSIBLE,
                inputs=["prepared_context"],
                expected_outputs=["execution_artifacts"],
                acceptance_criteria=["Artifacts produced match requested specifications."]
            ),
            SubGoal(
                id=sg3_id,
                title="Quality Verification & Sign-off",
                description="Validate outputs against acceptance standards and finalize output delivery.",
                phase=3,
                dependencies=[sg2_id],
                estimated_complexity="low",
                estimated_seconds=25,
                risk_level=RISK_READ_ONLY,
                inputs=["execution_artifacts"],
                expected_outputs=["final_deliverable"],
                acceptance_criteria=["All success metrics satisfied."]
            )
        ]
