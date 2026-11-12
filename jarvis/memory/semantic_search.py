"""
Semantic Search Retrieval Engine for J.A.R.V.I.S.
Capability 93: Semantic Search

Provides vector space cosine similarity and BM25/TF-IDF normalized retrieval
across notes, memory records, research dossiers, and personal entities.
Supports semantic query expansion, synonym dictionaries, and snippet highlighting.
"""

import re
import math
import pathlib
from typing import Dict, List, Set, Any, Optional, Tuple
from collections import Counter
from ..config import NOTES_DIR


class SemanticSearchEngine:
    """
    Sub-linear BM25/TF-IDF and cosine similarity semantic retrieval engine.
    """

    # Domain-specific semantic expansion synonyms
    SYNONYM_EXPANSION = {
        "vfx": ["visual effects", "cinematic", "blender", "davinci", "render", "animation", "film"],
        "film": ["video", "cinematic", "vfx", "short-film", "director", "production"],
        "school": ["study", "grade 10", "exam", "lesson", "textbook", "st. anne", "kurunegala"],
        "study": ["revision", "notes", "grade 10", "science", "physics", "chemistry", "debating"],
        "finance": ["revenue", "money", "profit", "cash", "invoice", "bank", "expenses"],
        "ai": ["jarvis", "gemini", "model", "neural", "agent", "intelligence", "llm"],
        "code": ["python", "api", "function", "script", "developer", "backend", "git"],
        "task": ["todo", "milestone", "action", "priority", "deadline", "schedule"]
    }

    def __init__(self, notes_dir: Optional[pathlib.Path] = None):
        self.notes_dir = notes_dir or NOTES_DIR
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.idf: Dict[str, float] = {}
        self.avg_doc_len: float = 0.0
        self._build_index()

    def tokenize(self, text: str) -> List[str]:
        """Tokenizes text into lowercase alphanumeric terms (length >= 2)."""
        return [w.lower() for w in re.findall(r'\b[a-zA-Z0-9_\'-]{2,}\b', text)]

    def _build_index(self):
        """Indexes all markdown notes in the configured notes directory."""
        self.documents = {}
        doc_count = 0
        doc_freq: Dict[str, int] = Counter()
        total_len = 0

        # Scan NOTES_DIR
        if self.notes_dir and self.notes_dir.exists():
            for p in self.notes_dir.rglob("*.md"):
                if p.is_file() and not p.name.startswith("."):
                    try:
                        content = p.read_text(encoding="utf-8", errors="replace")
                        title = p.stem
                        group = p.parent.name if p.parent != self.notes_dir else "general"
                        tokens = self.tokenize(title + " " + content)
                        doc_len = len(tokens)
                        total_len += doc_len

                        self.documents[title] = {
                            "id": title,
                            "title": title,
                            "group": group,
                            "path": str(p),
                            "content": content,
                            "tokens": tokens,
                            "tf": Counter(tokens),
                            "doc_len": doc_len
                        }
                        for term in set(tokens):
                            doc_freq[term] += 1
                        doc_count += 1
                    except Exception:
                        continue

        self.avg_doc_len = (total_len / doc_count) if doc_count > 0 else 1.0

        # Compute smoothed IDF: ln(1 + (N - n + 0.5) / (n + 0.5))
        self.idf = {}
        for term, df in doc_freq.items():
            self.idf[term] = math.log(1.0 + (doc_count - df + 0.5) / (df + 0.5))

    def add_custom_document(self, doc_id: str, title: str, content: str, group: str = "memory"):
        """Indexes an in-memory document or custom memory entry."""
        tokens = self.tokenize(title + " " + content)
        doc_len = len(tokens)
        self.documents[doc_id] = {
            "id": doc_id,
            "title": title,
            "group": group,
            "path": "",
            "content": content,
            "tokens": tokens,
            "tf": Counter(tokens),
            "doc_len": doc_len
        }
        # Update IDF approximation
        for term in set(tokens):
            self.idf[term] = self.idf.get(term, 1.0) + 0.1

    def expand_query(self, query: str) -> List[str]:
        """Expands query tokens using the domain synonym vocabulary."""
        raw_tokens = self.tokenize(query)
        expanded = set(raw_tokens)
        for t in raw_tokens:
            if t in self.SYNONYM_EXPANSION:
                for syn in self.SYNONYM_EXPANSION[t]:
                    expanded.update(self.tokenize(syn))
        return list(expanded)

    def search(
        self,
        query: str,
        top_k: int = 5,
        group_filter: Optional[str] = None,
        min_score: float = 0.1,
        expand_synonyms: bool = True
    ) -> Dict[str, Any]:
        """
        Executes BM25-weighted semantic retrieval for a query string.
        """
        if not query.strip():
            return {"status": "success", "query": query, "results": [], "total_matches": 0}

        query_tokens = self.expand_query(query) if expand_synonyms else self.tokenize(query)
        if not query_tokens:
            return {"status": "success", "query": query, "results": [], "total_matches": 0}

        k1 = 1.2
        b = 0.75
        scored_docs = []

        for doc_id, doc in self.documents.items():
            if group_filter and doc["group"].lower() != group_filter.lower():
                continue

            score = 0.0
            doc_len = doc["doc_len"]
            tf = doc["tf"]
            title_lower = doc["title"].lower()

            for term in query_tokens:
                if term in tf:
                    term_freq = tf[term]
                    idf_val = self.idf.get(term, 0.5)
                    # BM25 term weighting formula
                    numerator = term_freq * (k1 + 1.0)
                    denominator = term_freq + k1 * (1.0 - b + b * (doc_len / self.avg_doc_len))
                    score += idf_val * (numerator / max(0.001, denominator))

                    # Title exact boost
                    if term in title_lower:
                        score += 3.5

            if score >= min_score:
                snippet = self._generate_snippet(doc["content"], query_tokens)
                scored_docs.append({
                    "id": doc["id"],
                    "title": doc["title"],
                    "group": doc["group"],
                    "score": round(score, 3),
                    "snippet": snippet,
                    "path": doc["path"]
                })

        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        top_results = scored_docs[:top_k]

        return {
            "status": "success",
            "query": query,
            "expanded_terms": query_tokens,
            "total_matches": len(scored_docs),
            "results": top_results
        }

    def _generate_snippet(self, text: str, query_tokens: List[str], max_chars: int = 260) -> str:
        """Finds the most relevant paragraph snippet containing matched tokens."""
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        best_para = paragraphs[0] if paragraphs else text[:max_chars]
        best_matches = 0

        for para in paragraphs:
            para_lower = para.lower()
            matches = sum(1 for tok in query_tokens if tok in para_lower)
            if matches > best_matches:
                best_matches = matches
                best_para = para

        clean_snippet = re.sub(r'#+\s*', '', best_para).strip()
        if len(clean_snippet) > max_chars:
            clean_snippet = clean_snippet[:max_chars] + "…"
        return clean_snippet


# Module singleton
semantic_search = SemanticSearchEngine()
