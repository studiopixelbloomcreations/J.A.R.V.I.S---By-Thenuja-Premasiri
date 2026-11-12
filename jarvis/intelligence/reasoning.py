"""
Capabilities 3, 4, 5, 10, 13: Reasoning & Verification Engines for J.A.R.V.I.S.
3. Hypothesis Generation
4. Evidence Verification
5. Contradiction Detection
10. Contextual Reasoning
13. Uncertainty Estimation
"""
import os
import re
import math
import time
from typing import Dict, List, Any, Optional, Tuple

from ..config import load_user_profile


class HypothesisGenerator:
    """
    Capability 3: Hypothesis Generation.
    Formulates structured competing hypotheses (Null, Primary, Alternative, Edge)
    with prior probabilities, testable predictions, and falsification criteria.
    """
    def generate_hypotheses(
        self,
        observation: str,
        domain: str = "general",
        priors: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """Generates competing hypotheses for a given phenomenon or problem."""
        obs_clean = observation.strip()
        tokens = re.findall(r'\b[a-zA-Z0-9_-]{3,}\b', obs_clean.lower())

        hypotheses = [
            {
                "id": "H0_NULL",
                "type": "Null Hypothesis",
                "statement": f"The observed phenomenon '{obs_clean}' is due to baseline random variation, measurement artifact, or transient noise with no persistent systemic cause.",
                "prior": 0.20,
                "predictions": ["Re-measurement will show regression to baseline mean without intervention."],
                "falsification_criteria": "Observation persists reproducibly across multiple independent measurement cycles.",
                "required_evidence": ["Historical baseline variance metrics", "Repeated test runs"]
            },
            {
                "id": "H1_PRIMARY",
                "type": "Primary Mechanism",
                "statement": f"The phenomenon '{obs_clean}' is directly driven by primary operational inputs or core structural changes in the system.",
                "prior": 0.45,
                "predictions": ["Direct modulation of primary input will yield proportional changes in the observed outcome."],
                "falsification_criteria": "Modulating primary input yields zero measurable delta in the observed metric.",
                "required_evidence": ["Correlation telemetry", "Input perturbation test results"]
            },
            {
                "id": "H2_ALTERNATIVE",
                "type": "Alternative / Confounding",
                "statement": f"The phenomenon is governed by an unmodeled secondary confounder, resource saturation, or external dependency interaction.",
                "prior": 0.25,
                "predictions": ["System behavior will diverge when external dependencies or background load changes."],
                "falsification_criteria": "Isolating external dependencies does not eliminate the phenomenon.",
                "required_evidence": ["Resource saturation logs", "Dependency latency traces"]
            },
            {
                "id": "H3_EDGE",
                "type": "Contrarian / Structural",
                "statement": f"The phenomenon reflects a foundational architectural boundary, undocumented protocol edge-case, or inverse feedback loop.",
                "prior": 0.10,
                "predictions": ["Boundary conditions or peak load will trigger non-linear failure modes."],
                "falsification_criteria": "Linear scaling behavior maintained across extreme operational boundaries.",
                "required_evidence": ["Boundary stress tests", "Protocol specification audits"]
            }
        ]

        # Normalize priors if provided
        if priors and len(priors) == len(hypotheses):
            total_p = sum(priors)
            for i, p in enumerate(priors):
                hypotheses[i]["prior"] = round(p / max(1e-6, total_p), 3)

        return {
            "status": "success",
            "observation": observation,
            "domain": domain,
            "hypotheses_count": len(hypotheses),
            "hypotheses": hypotheses,
            "recommended_next_step": f"Execute test for {hypotheses[1]['id']} falsification criteria."
        }


class EvidenceVerifier:
    """
    Capability 4: Evidence Verification.
    Verifies factual claims against source evidence, computing confidence scores,
    evaluating source credibility, and detecting hallucinated assertions.
    """
    CREDIBILITY_WEIGHTS = {
        "peer_reviewed": 0.95,
        "official_documentation": 0.90,
        "telemetry_log": 0.88,
        "system_spec": 0.85,
        "indexed_note": 0.80,
        "secondary_report": 0.65,
        "unverified_source": 0.40
    }

    def verify_claim(
        self,
        claim: str,
        evidence_sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluates whether a claim is supported, refuted, or unverified by sources.
        evidence_sources: list of dicts with 'text', 'source', and optional 'source_type'.
        """
        claim_clean = claim.lower().strip()
        claim_tokens = set(re.findall(r'\b[a-zA-Z0-9.%_-]{2,}\b', claim_clean))

        # Check for numeric claims
        claim_numbers = set(re.findall(r'\b\d+(?:\.\d+)?%?\b', claim_clean))

        supporting_spans = []
        contradicting_spans = []
        source_weights = []

        for src in evidence_sources:
            src_text = src.get("text", "")
            src_name = src.get("source", "Unknown Source")
            src_type = src.get("source_type", "indexed_note")
            weight = self.CREDIBILITY_WEIGHTS.get(src_type, 0.70)
            source_weights.append(weight)

            # Split on sentence boundaries without breaking decimals like 63.77
            sentences = [s.strip() for s in re.split(r'(?<!\d)\.(?!\d)|[!?\n]+', src_text) if len(s.strip()) > 10]
            if not sentences and src_text.strip():
                sentences = [src_text.strip()]

            for s in sentences:
                s_lower = s.lower()
                s_tokens = set(re.findall(r'\b[a-zA-Z0-9.%_-]{2,}\b', s_lower))
                token_overlap = len(claim_tokens & s_tokens) / max(1, len(claim_tokens))

                # Check negation markers
                has_negation = bool(re.search(r'\b(not|never|no|neither|cannot|fails|false|unsupported)\b', s_lower))

                if token_overlap >= 0.40:
                    if has_negation:
                        contradicting_spans.append({"source": src_name, "text": s, "overlap": round(token_overlap, 2)})
                    else:
                        supporting_spans.append({"source": src_name, "text": s, "overlap": round(token_overlap, 2)})

        # Compute verification score
        avg_credibility = sum(source_weights) / max(1, len(source_weights)) if source_weights else 0.50
        max_support_overlap = max([s["overlap"] for s in supporting_spans], default=0.0)
        max_contra_overlap = max([s["overlap"] for s in contradicting_spans], default=0.0)

        # Check for ungrounded / hallucinated numbers
        all_evidence_text = " ".join([src.get("text", "") for src in evidence_sources])
        evidence_numbers = set(re.findall(r'\b\d+(?:\.\d+)?%?\b', all_evidence_text))
        unsupported_numbers = [num for num in claim_numbers if num not in all_evidence_text]

        # Detect quantitative conflict or polarity flip
        has_numeric_conflict = bool(claim_numbers and evidence_numbers and not (claim_numbers & evidence_numbers))
        claim_has_negation = bool(re.search(r'\b(not|never|no|neither|cannot|fails|false|unsupported|zero|0%)\b', claim_clean))

        # Status determination
        if has_numeric_conflict or (claim_has_negation and max_support_overlap >= 0.40):
            verdict = "REFUTED"
            confidence = round(0.85 * avg_credibility, 3)
        elif max_contra_overlap >= 0.50 and max_contra_overlap > max_support_overlap:
            verdict = "REFUTED"
            confidence = round(max_contra_overlap * avg_credibility, 3)
        elif max_support_overlap >= 0.50:
            verdict = "SUPPORTED"
            confidence = round(max_support_overlap * avg_credibility, 3)
        elif max_support_overlap >= 0.25:
            verdict = "PARTIALLY_SUPPORTED"
            confidence = round(max_support_overlap * avg_credibility, 3)
        else:
            verdict = "INSUFFICIENT_EVIDENCE"
            confidence = 0.15

        return {
            "status": "success",
            "claim": claim,
            "verdict": verdict,
            "confidence_score": confidence,
            "sources_evaluated": len(evidence_sources),
            "supporting_evidence": supporting_spans[:3],
            "contradicting_evidence": contradicting_spans[:3],
            "unsupported_numerical_claims": unsupported_numbers,
            "hallucination_risk": "High" if unsupported_numbers and verdict != "SUPPORTED" else "Low"
        }


class ContradictionDetector:
    """
    Capability 5: Contradiction Detection.
    Evaluates pairs or sets of statements for logical negation, quantitative mismatches,
    temporal inconsistencies, and computes severity metrics.
    """
    def compare_statements(self, statement_a: str, statement_b: str) -> Dict[str, Any]:
        """Detects contradictions between two distinct statements."""
        sa_lower = statement_a.lower().strip()
        sb_lower = statement_b.lower().strip()

        tokens_a = set(re.findall(r'\b[a-zA-Z0-9]{3,}\b', sa_lower))
        tokens_b = set(re.findall(r'\b[a-zA-Z0-9]{3,}\b', sb_lower))

        shared_tokens = tokens_a & tokens_b
        jaccard = len(shared_tokens) / max(1, len(tokens_a | tokens_b))

        # Check if statements are addressing the same topic
        if jaccard < 0.20:
            return {
                "status": "success",
                "is_contradiction": False,
                "contradiction_type": "None",
                "severity": "None",
                "topic_overlap": round(jaccard, 3),
                "reconciliation": "Statements address disjoint subject matters."
            }

        # 1. Direct Polarity Inversion (not / no / enabled vs disabled / active vs inactive)
        polarity_pairs = [
            ("enabled", "disabled"), ("active", "inactive"), ("online", "offline"),
            ("success", "failure"), ("true", "false"), ("supported", "unsupported"),
            ("increase", "decrease"), ("higher", "lower"), ("pass", "fail")
        ]
        has_polarity_inversion = False
        inversion_terms = ()
        for t1, t2 in polarity_pairs:
            if (t1 in sa_lower and t2 in sb_lower) or (t2 in sa_lower and t1 in sb_lower):
                has_polarity_inversion = True
                inversion_terms = (t1, t2)
                break

        # Check negation words
        neg_a = bool(re.search(r'\b(not|never|no|none|neither|cannot)\b', sa_lower))
        neg_b = bool(re.search(r'\b(not|never|no|none|neither|cannot)\b', sb_lower))
        negation_flip = (neg_a != neg_b) and (jaccard > 0.40)

        # 2. Quantitative Mismatch
        nums_a = re.findall(r'\b\d+(?:\.\d+)?\b', sa_lower)
        nums_b = re.findall(r'\b\d+(?:\.\d+)?\b', sb_lower)
        quant_mismatch = False
        mismatched_values = []
        if nums_a and nums_b and nums_a != nums_b and jaccard > 0.35:
            quant_mismatch = True
            mismatched_values = [nums_a, nums_b]

        # 3. Temporal Inconsistency
        years_a = re.findall(r'\b(19\d\d|20\d\d)\b', sa_lower)
        years_b = re.findall(r'\b(19\d\d|20\d\d)\b', sb_lower)
        temporal_mismatch = bool(years_a and years_b and set(years_a) != set(years_b) and jaccard > 0.35)

        is_contradiction = has_polarity_inversion or negation_flip or quant_mismatch or temporal_mismatch

        if is_contradiction:
            if has_polarity_inversion or negation_flip:
                c_type = "Direct Polarity Inversion"
                severity = "FATAL"
            elif quant_mismatch:
                c_type = "Quantitative Discrepancy"
                severity = "MAJOR"
            elif temporal_mismatch:
                c_type = "Temporal Inconsistency"
                severity = "MAJOR"
            else:
                c_type = "Definitional Divergence"
                severity = "MINOR"

            reconciliation = (
                f"Contradiction identified ({c_type}, severity: {severity}). "
                f"Check whether measurement timeframes, operational modes, or environment boundaries differ."
            )
        else:
            c_type = "None"
            severity = "None"
            reconciliation = "Statements are logically consistent or complementary."

        return {
            "status": "success",
            "is_contradiction": is_contradiction,
            "contradiction_type": c_type,
            "severity": severity,
            "topic_overlap": round(jaccard, 3),
            "statement_a": statement_a,
            "statement_b": statement_b,
            "reconciliation": reconciliation
        }

    def detect_in_corpus(self, statements: List[str]) -> List[Dict[str, Any]]:
        """Scans an entire list of statements for all pairwise contradictions."""
        contradictions = []
        for i in range(len(statements)):
            for j in range(i + 1, len(statements)):
                res = self.compare_statements(statements[i], statements[j])
                if res["is_contradiction"]:
                    contradictions.append(res)
        return contradictions


class ContextualReasoner:
    """
    Capability 10: Contextual Reasoning.
    Grounds high-level human directives into rigorously constrained reasoning trees,
    taking into account user preferences, hardware state, and operational safety boundaries.
    """
    def __init__(self, user_profile: Optional[str] = None):
        self._user_profile = user_profile

    def get_profile(self) -> str:
        if self._user_profile is not None:
            return self._user_profile
        try:
            return load_user_profile()
        except Exception:
            return "User: Thenuja | OS: Windows 11 | Model: Gemini"

    def contextualize_directive(
        self,
        directive: str,
        active_constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Translates high-level directive into context-grounded parameters."""
        profile = self.get_profile()
        constraints = active_constraints or {}

        # Default system context
        ctx = {
            "os": "Windows 11",
            "user": "Thenuja",
            "risk_profile": "Standard Operator",
            "network_mode": "Online",
            "active_window": constraints.get("active_window", "Desktop"),
            "memory_usage_mb": constraints.get("memory_usage_mb", 512),
            "safety_level": constraints.get("safety_level", "Standard")
        }
        ctx.update(constraints)

        d_lower = directive.lower().strip()

        # Infer intent category & scope
        if any(kw in d_lower for kw in ["speed up", "faster", "optimize", "accelerate"]):
            intent = "PERFORMANCE_OPTIMIZATION"
            actionable_steps = [
                "Profile background resource consumers via psutil",
                "Isolate throttled worker processes",
                "Apply batch pipeline optimizations"
            ]
            risk = "REVERSIBLE"
        elif any(kw in d_lower for kw in ["clean", "cleanup", "organize", "tidy", "purge"]):
            intent = "STORAGE_ORGANIZATION"
            actionable_steps = [
                "Generate dry-run preview of candidate files",
                "Verify file hashes to prevent data loss",
                "Require explicit confirmation before relocation"
            ]
            risk = "CONSEQUENTIAL"
        elif any(kw in d_lower for kw in ["research", "investigate", "study", "explore"]):
            intent = "DEEP_INVESTIGATION"
            actionable_steps = [
                "Decompose inquiry into multi-angle vectors",
                "Cross-reference indexed notes and official documentation",
                "Synthesize findings with source attribution"
            ]
            risk = "READ_ONLY"
        else:
            intent = "GENERAL_EXECUTION"
            actionable_steps = [
                "Validate user prompt semantics",
                "Dispatch approved operational skill"
            ]
            risk = "READ_ONLY"

        return {
            "status": "success",
            "directive": directive,
            "inferred_intent": intent,
            "risk_classification": risk,
            "operating_context": ctx,
            "grounded_execution_plan": actionable_steps,
            "reasoning_rationale": (
                f"Directive '{directive}' contextualized for user {ctx['user']} on {ctx['os']}. "
                f"Inferred intent is {intent} with {risk} risk posture."
            )
        }


class UncertaintyEstimator:
    """
    Capability 13: Uncertainty Estimation.
    Quantifies epistemic (knowledge deficit) vs aleatoric (random stochasticity) uncertainty,
    computes Shannon entropy across distributions, and flags known/unknown unknowns.
    """
    def estimate_uncertainty(
        self,
        probabilities: List[float],
        sample_count: int = 1,
        source_count: int = 1
    ) -> Dict[str, Any]:
        """
        Calculates Shannon entropy, variance, epistemic vs aleatoric split,
        and calibration confidence for probability distributions.
        """
        if not probabilities:
            probabilities = [1.0]

        # Normalize probabilities
        total = sum(probabilities)
        norm_probs = [p / max(1e-9, total) for p in probabilities]

        # Shannon Entropy H(P) = - sum(p * log2(p))
        entropy = 0.0
        for p in norm_probs:
            if p > 1e-9:
                entropy -= p * math.log2(p)

        max_entropy = math.log2(len(norm_probs)) if len(norm_probs) > 1 else 1.0
        normalized_entropy = round(entropy / max(1e-9, max_entropy), 3)

        # Epistemic Uncertainty (inversely related to evidence samples and source count)
        epistemic = round(max(0.05, 1.0 / (math.sqrt(sample_count) * math.sqrt(source_count))), 3)
        epistemic = min(0.95, epistemic)

        # Aleatoric Uncertainty (inherent dispersion / entropy in outcomes)
        aleatoric = round(min(0.95, max(0.05, normalized_entropy)), 3)

        # Overall composite uncertainty score
        composite = round(min(0.99, max(0.05, (epistemic * 0.50) + (aleatoric * 0.50))), 3)
        confidence = round(1.0 - composite, 3)

        # Risk classification
        if composite > 0.65:
            classification = "HIGH_UNCERTAINTY"
        elif composite > 0.35:
            classification = "MODERATE_UNCERTAINTY"
        else:
            classification = "LOW_UNCERTAINTY_ROBUST"

        return {
            "status": "success",
            "normalized_probabilities": [round(p, 3) for p in norm_probs],
            "shannon_entropy_bits": round(entropy, 3),
            "normalized_entropy": normalized_entropy,
            "epistemic_uncertainty": epistemic,
            "aleatoric_uncertainty": aleatoric,
            "composite_uncertainty": composite,
            "confidence_score": confidence,
            "uncertainty_classification": classification,
            "known_unknowns": [
                f"Sample size is {sample_count} observations",
                f"Corpus drawn from {source_count} distinct sources"
            ],
            "unknown_unknowns_risk": "Elevated" if source_count <= 1 else "Nominal"
        }
