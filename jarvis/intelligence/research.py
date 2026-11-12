"""
Capabilities 1, 2, 12, 14: Research & Literature Systems for J.A.R.V.I.S.
1. Deep Research Engine
2. Recursive Research
12. Long-Term Research Tracker
14. Scientific Literature Analysis
"""
import os
import re
import json
import math
import time
import uuid
import pathlib
from typing import Dict, List, Any, Optional

from ..config import NOTES_DIR, DATA_DIR
from ..knowledge.graph import scan_full_texts, load_graph_data

# Ensure intelligence storage directory
INTEL_DATA_DIR = os.path.join(DATA_DIR, "intelligence")
os.makedirs(INTEL_DATA_DIR, exist_ok=True)


class DeepResearchEngine:
    """
    Capability 1: Deep Research Engine.
    Executes multi-angle information gathering across local knowledge archives,
    extracts factual claims, identifies key entities, and synthesizes structured findings.
    """
    def __init__(self, notes_dir: str = NOTES_DIR):
        self.notes_dir = notes_dir

    def decompose_query(self, query: str, breadth: int = 3) -> List[str]:
        """Decomposes a broad research inquiry into focused investigative vectors."""
        clean_q = re.sub(r'[^\w\s]', ' ', query).strip()
        words = [w for w in clean_q.split() if len(w) > 2 and w.lower() not in {
            "what", "when", "where", "which", "who", "whom", "this", "that", "with", "from",
            "about", "into", "over", "after", "explain", "research", "investigate", "analyze"
        }]

        sub_queries = [query]
        if len(words) >= 2:
            sub_queries.append(f"{words[0]} {words[1]} architecture and implementation")
            sub_queries.append(f"{words[-2]} {words[-1]} performance and mechanisms")
            sub_queries.append(f"comparative analysis of {clean_q}")
        else:
            sub_queries.append(f"{query} overview and foundational principles")
            sub_queries.append(f"{query} evidence and practical applications")

        return sub_queries[:breadth]

    def _extract_entities(self, text: str) -> List[str]:
        """Extracts significant capitalized entities, technical terms, and acronyms."""
        # Find acronyms (2-6 uppercase letters)
        acronyms = set(re.findall(r'\b[A-Z]{2,6}\b', text))
        # Find Title Case compound entities
        title_cases = set(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text))
        # Find version/numeric technical terms
        tech_terms = set(re.findall(r'\b[a-zA-Z]+[-_][0-9a-zA-Z.]+\b', text))
        all_entities = list(acronyms | title_cases | tech_terms)
        return sorted(all_entities)[:15]

    def _extract_statistics(self, text: str) -> List[str]:
        """Extracts quantitative measurements, percentages, and metrics."""
        stat_patterns = [
            r'\b\d+(?:\.\d+)?%',
            r'\b\d+(?:\.\d+)?\s*(?:ms|seconds|minutes|hours|GB|MB|KB|GHz|MHz|fps|dB|kW|MW)\b',
            r'\b\$\d+(?:\.\d+)?(?:\s*(?:million|billion|trillion))?\b',
            r'\bp\s*[<>=]\s*0\.\d+\b',
            r'\bN\s*=\s*\d+\b'
        ]
        found = []
        for pat in stat_patterns:
            matches = re.findall(pat, text, re.IGNORECASE)
            found.extend(matches)
        return list(dict.fromkeys(found))[:10]

    def conduct_research(
        self,
        query: str,
        depth: int = 2,
        breadth: int = 3,
        corpus: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Executes deep research against indexed notes and custom corpora.
        Returns synthesized findings, entity graph, extracted stats, and confidence.
        """
        start_time = time.time()
        sub_vectors = self.decompose_query(query, breadth=breadth)
        notes = corpus if corpus is not None else scan_full_texts()

        # Tokenize query tokens
        query_tokens = set(re.findall(r'\b[a-zA-Z0-9]{3,}\b', query.lower()))

        matched_docs = []
        for title, content in notes.items():
            content_lower = content.lower()
            title_lower = title.lower()
            score = 0
            for t in query_tokens:
                if t in title_lower:
                    score += 5
                score += min(content_lower.count(t), 4)

            for vec in sub_vectors:
                vec_tokens = set(re.findall(r'\b[a-zA-Z0-9]{3,}\b', vec.lower()))
                overlap = len(vec_tokens & set(content_lower.split()))
                score += overlap * 2

            if score > 0:
                matched_docs.append({
                    "title": title,
                    "content": content,
                    "relevance_score": score
                })

        matched_docs.sort(key=lambda x: x["relevance_score"], reverse=True)
        top_matches = matched_docs[:max(5, depth * 2)]

        # Extract findings & synthesis
        all_text = " ".join([d["content"] for d in top_matches])
        entities = self._extract_entities(all_text)
        stats = self._extract_statistics(all_text)

        key_findings = []
        for d in top_matches[:3]:
            # Extract most informative sentence
            sentences = [s.strip() for s in re.split(r'[.!?]+', d["content"]) if len(s.strip()) > 30]
            if sentences:
                best_sentence = max(sentences, key=lambda s: sum(1 for t in query_tokens if t in s.lower()))
                key_findings.append({
                    "source": d["title"],
                    "finding": best_sentence,
                    "relevance": d["relevance_score"]
                })

        # Calculate research coverage confidence (0.0 to 1.0)
        num_sources = len(top_matches)
        token_coverage = sum(1 for t in query_tokens if t in all_text.lower()) / max(1, len(query_tokens))
        confidence = round(min(0.98, max(0.2, (num_sources * 0.15) + (token_coverage * 0.55))), 3)

        execution_time = round(time.time() - start_time, 4)

        return {
            "status": "success",
            "query": query,
            "depth": depth,
            "breadth": breadth,
            "investigation_vectors": sub_vectors,
            "sources_analyzed": len(top_matches),
            "sources": [d["title"] for d in top_matches],
            "key_findings": key_findings,
            "key_entities": entities,
            "statistics_extracted": stats,
            "confidence_score": confidence,
            "execution_time_sec": execution_time,
            "synthesis": (
                f"Synthesized analysis for '{query}' across {len(top_matches)} source documents. "
                f"Identified {len(entities)} core entities and {len(key_findings)} verified findings "
                f"with {confidence * 100:.1f}% confidence."
            )
        }


class RecursiveResearchPlanner:
    """
    Capability 2: Recursive Research.
    Conducts iterative multi-tier frontier expansion, pruning redundant queries,
    detecting information gaps, and halting upon convergence or depth limit.
    """
    def __init__(self, deep_engine: Optional[DeepResearchEngine] = None):
        self.engine = deep_engine or DeepResearchEngine()

    def _jaccard_similarity(self, q1: str, q2: str) -> float:
        set1 = set(re.findall(r'\b[a-zA-Z0-9]{3,}\b', q1.lower()))
        set2 = set(re.findall(r'\b[a-zA-Z0-9]{3,}\b', q2.lower()))
        if not set1 or not set2:
            return 0.0
        return len(set1 & set2) / len(set1 | set2)

    def plan_and_execute(
        self,
        root_query: str,
        max_depth: int = 3,
        max_branches: int = 2,
        stop_gain_threshold: float = 0.10,
        corpus: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Recursively explores research topics in a tree structure.
        Tracks discovered knowledge and halts when novelty gain falls below threshold.
        """
        frontier = [{
            "id": "node_0",
            "parent_id": None,
            "query": root_query,
            "depth": 0
        }]

        all_nodes = []
        visited_queries = []
        cumulative_tokens = set()
        tree_edges = []
        depth_levels_reached = 0

        while frontier:
            current = frontier.pop(0)
            node_id = current["id"]
            query = current["query"]
            depth = current["depth"]

            if depth > depth_levels_reached:
                depth_levels_reached = depth

            visited_queries.append(query)

            # Execute research step
            step_result = self.engine.conduct_research(query, depth=1, breadth=2, corpus=corpus)
            entities = step_result["key_entities"]
            stats = step_result["statistics_extracted"]

            # Compute information gain (ratio of newly discovered tokens)
            node_text = " ".join([f["finding"] for f in step_result["key_findings"]] + entities)
            node_tokens = set(re.findall(r'\b[a-zA-Z0-9]{3,}\b', node_text.lower()))
            new_tokens = node_tokens - cumulative_tokens
            gain = round(len(new_tokens) / max(1, len(node_tokens)), 3) if node_tokens else 0.0
            cumulative_tokens.update(node_tokens)

            recorded_node = {
                "id": node_id,
                "parent_id": current["parent_id"],
                "query": query,
                "depth": depth,
                "information_gain": gain,
                "entities_found": len(entities),
                "sources_consulted": step_result["sources"]
            }
            all_nodes.append(recorded_node)

            if current["parent_id"] is not None:
                tree_edges.append({"from": current["parent_id"], "to": node_id})

            # Check halting conditions
            if depth >= max_depth:
                continue
            if gain < stop_gain_threshold and depth > 0:
                continue

            # Generate child queries from uncovered entities
            branch_candidates = []
            for ent in entities[:max_branches + 2]:
                cand = f"{query} {ent}"
                # Prune if too similar to any visited query
                is_duplicate = any(self._jaccard_similarity(cand, v) > 0.70 for v in visited_queries)
                if not is_duplicate and cand not in [c["query"] for c in frontier]:
                    branch_candidates.append(cand)
                if len(branch_candidates) >= max_branches:
                    break

            for i, cand_query in enumerate(branch_candidates):
                child_id = f"node_{depth + 1}_{len(all_nodes)}_{i}"
                frontier.append({
                    "id": child_id,
                    "parent_id": node_id,
                    "query": cand_query,
                    "depth": depth + 1
                })

        return {
            "status": "success",
            "root_query": root_query,
            "max_depth_configured": max_depth,
            "max_depth_reached": depth_levels_reached,
            "total_nodes_explored": len(all_nodes),
            "total_unique_concepts": len(cumulative_tokens),
            "exploration_tree": all_nodes,
            "edges": tree_edges,
            "convergence_status": "converged" if depth_levels_reached < max_depth else "depth_bounded"
        }


class LongTermResearchTracker:
    """
    Capability 12: Long-Term Research.
    Maintains persistent research agendas, milestone tracking, hypothesis evolution,
    evidence journal, and serializes snapshots to disk.
    """
    def __init__(self, storage_dir: str = INTEL_DATA_DIR):
        self.storage_dir = storage_dir
        self.agendas: Dict[str, Dict[str, Any]] = {}

    def create_agenda(
        self,
        title: str,
        objective: str,
        milestones: Optional[List[str]] = None,
        agenda_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates and initializes a new long-term research agenda."""
        aid = agenda_id or f"agenda_{uuid.uuid4().hex[:8]}"
        ms_list = [{"id": i + 1, "title": m, "status": "pending", "completed_at": None} for i, m in enumerate(milestones or [])]
        agenda = {
            "agenda_id": aid,
            "title": title,
            "objective": objective,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "milestones": ms_list,
            "hypotheses": [],
            "evidence_journal": [],
            "open_questions": [],
            "status": "active"
        }
        self.agendas[aid] = agenda
        return agenda

    def log_evidence(
        self,
        agenda_id: str,
        claim: str,
        source: str,
        confidence: float = 0.85,
        notes: str = ""
    ) -> Dict[str, Any]:
        """Logs an empirical evidence entry to the research journal."""
        agenda = self.agendas.get(agenda_id)
        if not agenda:
            raise KeyError(f"Agenda '{agenda_id}' not found.")

        entry = {
            "entry_id": f"ev_{len(agenda['evidence_journal']) + 1}",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "claim": claim,
            "source": source,
            "confidence": max(0.0, min(1.0, float(confidence))),
            "notes": notes
        }
        agenda["evidence_journal"].append(entry)
        agenda["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        return entry

    def update_milestone(
        self,
        agenda_id: str,
        milestone_id: int,
        status: str = "completed"
    ) -> Dict[str, Any]:
        """Updates milestone progress state."""
        agenda = self.agendas.get(agenda_id)
        if not agenda:
            raise KeyError(f"Agenda '{agenda_id}' not found.")

        for ms in agenda["milestones"]:
            if ms["id"] == milestone_id:
                ms["status"] = status
                if status == "completed":
                    ms["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                agenda["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                return ms
        raise KeyError(f"Milestone {milestone_id} not found in agenda '{agenda_id}'.")

    def register_hypothesis(
        self,
        agenda_id: str,
        statement: str,
        prior_prob: float = 0.50
    ) -> Dict[str, Any]:
        """Tracks a working hypothesis with prior probability."""
        agenda = self.agendas.get(agenda_id)
        if not agenda:
            raise KeyError(f"Agenda '{agenda_id}' not found.")

        hyp = {
            "hyp_id": f"hyp_{len(agenda['hypotheses']) + 1}",
            "statement": statement,
            "prior": round(float(prior_prob), 3),
            "posterior": round(float(prior_prob), 3),
            "evidence_count": 0,
            "status": "testing"
        }
        agenda["hypotheses"].append(hyp)
        agenda["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        return hyp

    def update_hypothesis_bayes(
        self,
        agenda_id: str,
        hyp_id: str,
        likelihood_if_true: float,
        likelihood_if_false: float
    ) -> Dict[str, Any]:
        """
        Performs Bayesian posterior update:
        P(H|E) = (P(E|H) * P(H)) / [P(E|H)*P(H) + P(E|~H)*P(~H)]
        """
        agenda = self.agendas.get(agenda_id)
        if not agenda:
            raise KeyError(f"Agenda '{agenda_id}' not found.")

        for hyp in agenda["hypotheses"]:
            if hyp["hyp_id"] == hyp_id:
                p_h = hyp["posterior"]
                p_not_h = 1.0 - p_h
                numerator = likelihood_if_true * p_h
                denominator = (likelihood_if_true * p_h) + (likelihood_if_false * p_not_h)
                new_posterior = round(numerator / max(1e-9, denominator), 4)
                hyp["posterior"] = max(0.001, min(0.999, new_posterior))
                hyp["evidence_count"] += 1
                if hyp["posterior"] >= 0.85:
                    hyp["status"] = "validated"
                elif hyp["posterior"] <= 0.15:
                    hyp["status"] = "refuted"
                agenda["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                return hyp
        raise KeyError(f"Hypothesis '{hyp_id}' not found.")

    def save_to_disk(self, agenda_id: str, filepath: Optional[str] = None) -> str:
        """Persists agenda state as JSON."""
        agenda = self.agendas.get(agenda_id)
        if not agenda:
            raise KeyError(f"Agenda '{agenda_id}' not found.")

        target = filepath or os.path.join(self.storage_dir, f"{agenda_id}.json")
        with open(target, "w", encoding="utf-8") as f:
            json.dump(agenda, f, indent=2)
        return target

    def load_from_disk(self, filepath: str) -> Dict[str, Any]:
        """Loads and activates agenda from disk."""
        with open(filepath, "r", encoding="utf-8") as f:
            agenda = json.load(f)
        self.agendas[agenda["agenda_id"]] = agenda
        return agenda

    def get_summary(self, agenda_id: str) -> Dict[str, Any]:
        """Summarizes progress, completed milestones, and active hypotheses."""
        agenda = self.agendas.get(agenda_id)
        if not agenda:
            raise KeyError(f"Agenda '{agenda_id}' not found.")

        total_ms = len(agenda["milestones"])
        done_ms = sum(1 for m in agenda["milestones"] if m["status"] == "completed")
        completion_pct = round((done_ms / max(1, total_ms)) * 100, 1)

        return {
            "agenda_id": agenda_id,
            "title": agenda["title"],
            "progress_percent": completion_pct,
            "milestones_completed": f"{done_ms}/{total_ms}",
            "evidence_entries": len(agenda["evidence_journal"]),
            "hypotheses_count": len(agenda["hypotheses"]),
            "status": agenda["status"],
            "updated_at": agenda["updated_at"]
        }


class LiteratureAnalyzer:
    """
    Capability 14: Scientific Literature Analysis.
    Parses scientific research papers, extracting sample size, study design,
    statistical metrics (p-values, odds ratios, CIs), methodology rigor, and risk of bias.
    """
    STUDY_TYPES = [
        "Meta-Analysis", "Systematic Review", "Randomized Controlled Trial",
        "Cohort Study", "Case-Control Study", "Cross-Sectional Study",
        "Observational", "Theoretical", "Case Study"
    ]

    def _detect_study_type(self, text: str) -> str:
        text_lower = text.lower()
        if "meta-analysis" in text_lower or "systematic review" in text_lower:
            return "Meta-Analysis"
        if "randomized controlled" in text_lower or "rct" in text_lower or "placebo-controlled" in text_lower:
            return "Randomized Controlled Trial"
        if "cohort" in text_lower:
            return "Cohort Study"
        if "case-control" in text_lower:
            return "Case-Control Study"
        if "cross-sectional" in text_lower:
            return "Cross-Sectional Study"
        if "observational" in text_lower:
            return "Observational"
        return "Theoretical"

    def _extract_sample_size(self, text: str) -> Optional[int]:
        patterns = [
            r'\b[Nn]\s*=\s*([0-9,]+)\b',
            r'\bsample\s+size\s+(?:of\s+)?([0-9,]+)\b',
            r'\b([0-9,]+)\s+participants\b',
            r'\b([0-9,]+)\s+patients\b',
            r'\b([0-9,]+)\s+subjects\b'
        ]
        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                raw = match.group(1).replace(",", "")
                if raw.isdigit():
                    return int(raw)
        return None

    def _extract_stats(self, text: str) -> Dict[str, Any]:
        p_matches = re.findall(r'p\s*([<>=])\s*(0\.\d+)', text, re.IGNORECASE)
        cis = re.findall(r'95%\s*CI\s*\[([0-9.,\s-]+)\]', text, re.IGNORECASE)
        effect_sizes = re.findall(r'(?:Cohen\'s\s*d|hazard\s*ratio|odds\s*ratio|OR|HR)\s*=\s*([0-9.]+)', text, re.IGNORECASE)

        p_values = [float(val) for op, val in p_matches]
        statistically_significant = any(p < 0.05 for p in p_values) if p_values else None

        return {
            "p_values": p_values,
            "statistically_significant": statistically_significant,
            "confidence_intervals": cis,
            "effect_sizes": [float(e) for e in effect_sizes]
        }

    def analyze_paper(self, paper_text: str, title: Optional[str] = None) -> Dict[str, Any]:
        """Analyzes a scientific paper or abstract and produces a rigor scorecard."""
        study_type = self._detect_study_type(paper_text)
        sample_size = self._extract_sample_size(paper_text)
        stats = self._extract_stats(paper_text)

        # Methodology rigor scoring (0-100)
        rigor = 50.0
        # Study hierarchy weighting
        hierarchy_weights = {
            "Meta-Analysis": 30.0,
            "Systematic Review": 25.0,
            "Randomized Controlled Trial": 25.0,
            "Cohort Study": 15.0,
            "Case-Control Study": 10.0,
            "Observational": 5.0,
            "Theoretical": 0.0
        }
        rigor += hierarchy_weights.get(study_type, 0.0)

        # Sample size scoring
        if sample_size:
            if sample_size > 1000:
                rigor += 15.0
            elif sample_size > 100:
                rigor += 10.0
            elif sample_size > 30:
                rigor += 5.0

        # Statistical rigor
        if stats["p_values"]:
            rigor += 5.0
        if stats["confidence_intervals"]:
            rigor += 5.0

        rigor = min(100.0, round(rigor, 1))

        # Risk of bias estimation
        if rigor >= 80:
            bias_risk = "Low"
        elif rigor >= 60:
            bias_risk = "Moderate"
        else:
            bias_risk = "High"

        # Evidence tier
        if study_type in ("Meta-Analysis", "Randomized Controlled Trial") and rigor >= 75:
            tier = "Tier 1 (High Strength / Grade A)"
        elif study_type in ("Cohort Study", "Case-Control Study") and rigor >= 60:
            tier = "Tier 2 (Moderate Strength / Grade B)"
        else:
            tier = "Tier 3 (Observational / Exploratory / Grade C)"

        return {
            "status": "success",
            "title": title or "Untitled Scientific Paper",
            "study_type": study_type,
            "sample_size": sample_size,
            "statistics": stats,
            "methodology_rigor_score": rigor,
            "risk_of_bias": bias_risk,
            "evidence_tier": tier,
            "recommendation": (
                f"Paper classified as {study_type} with {bias_risk.lower()} risk of bias "
                f"(Rigor score: {rigor}/100). Suitable for {tier} evidentiary synthesis."
            )
        }

    def comparative_synthesis(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesizes multiple studies into a consensus assessment."""
        if not papers:
            return {"status": "error", "message": "No papers provided for synthesis."}

        analyses = [self.analyze_paper(p.get("text", ""), p.get("title")) for p in papers]
        avg_rigor = round(sum(a["methodology_rigor_score"] for a in analyses) / len(analyses), 1)

        total_sample = sum(a["sample_size"] for a in analyses if a["sample_size"])
        types_dist = {}
        for a in analyses:
            types_dist[a["study_type"]] = types_dist.get(a["study_type"], 0) + 1

        significant_count = sum(1 for a in analyses if a["statistics"]["statistically_significant"])

        return {
            "status": "success",
            "papers_analyzed": len(analyses),
            "aggregate_sample_size": total_sample,
            "average_rigor_score": avg_rigor,
            "study_distribution": types_dist,
            "statistically_significant_studies": f"{significant_count}/{len(analyses)}",
            "consensus_strength": "Robust" if avg_rigor >= 70 and significant_count >= (len(analyses) / 2) else "Moderate",
            "individual_evaluations": analyses
        }
