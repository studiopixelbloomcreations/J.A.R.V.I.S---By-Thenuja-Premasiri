"""
Knowledge Deduplication Engine for J.A.R.V.I.S.
Capability 98: Knowledge Deduplication

Detects exact, normalized, and fuzzy duplicate notes and memories.
Computes similarity ratios, detects redundant knowledge fragments,
and provides automated conflict resolution and merge strategies.
"""

import re
import hashlib
import difflib
from typing import Dict, List, Set, Any, Optional, Tuple


class KnowledgeDeduplicator:
    """
    Multi-tiered knowledge deduplication engine for archival notes and memory stores.
    """

    def __init__(self, fuzzy_threshold: float = 0.75):
        self.fuzzy_threshold = fuzzy_threshold

    def compute_exact_hash(self, text: str) -> str:
        """Returns SHA-256 hash of raw text."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def normalize_text(self, text: str) -> str:
        """Strips markdown syntax, punctuation, extra whitespace, and lowercases."""
        # Strip code blocks
        clean = re.sub(r'```[\s\S]*?```', '', text)
        # Strip links
        clean = re.sub(r'\[\[([^\]]+)\]\]', r'\1', clean)
        clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean)
        # Strip markdown formatting
        clean = re.sub(r'[#*_~`>|-]', ' ', clean)
        # Strip non-alphanumeric
        clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', clean)
        # Collapse whitespace
        clean = re.sub(r'\s+', ' ', clean).strip().lower()
        return clean

    def compute_normalized_hash(self, text: str) -> str:
        """Returns SHA-256 hash of normalized text content."""
        return hashlib.sha256(self.normalize_text(text).encode("utf-8")).hexdigest()

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculates hybrid similarity: Jaccard token overlap blended with SequenceMatcher ratio.
        """
        norm1 = self.normalize_text(text1)
        norm2 = self.normalize_text(text2)

        if not norm1 and not norm2:
            return 1.0
        if not norm1 or not norm2:
            return 0.0
        if norm1 == norm2:
            return 1.0

        words1 = set(norm1.split())
        words2 = set(norm2.split())

        union = words1.union(words2)
        if not union:
            return 0.0

        jaccard = len(words1.intersection(words2)) / len(union)

        # Fast sequence similarity on snippet if texts are long
        sample1 = norm1[:1200]
        sample2 = norm2[:1200]
        seq_ratio = difflib.SequenceMatcher(None, sample1, sample2).ratio()

        # Weighted blend (60% Jaccard, 40% SequenceMatcher)
        similarity = round(0.6 * jaccard + 0.4 * seq_ratio, 3)
        return similarity

    def find_duplicates(self, notes: Dict[str, str]) -> Dict[str, Any]:
        """
        Scans a dictionary of {identifier/title: content} and detects duplicates.
        """
        exact_hash_map: Dict[str, List[str]] = {}
        norm_hash_map: Dict[str, List[str]] = {}

        for title, content in notes.items():
            e_hash = self.compute_exact_hash(content)
            n_hash = self.compute_normalized_hash(content)

            exact_hash_map.setdefault(e_hash, []).append(title)
            norm_hash_map.setdefault(n_hash, []).append(title)

        exact_dupes = [titles for titles in exact_hash_map.values() if len(titles) > 1]
        norm_dupes = [titles for titles in norm_hash_map.values() if len(titles) > 1 and titles not in exact_dupes]

        # Fuzzy duplicate detection among remaining items
        fuzzy_dupes: List[Dict[str, Any]] = []
        titles = list(notes.keys())

        # Avoid redundant pairs
        handled_pairs: Set[Tuple[str, str]] = set()
        for group in exact_dupes + norm_dupes:
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    handled_pairs.add((min(group[i], group[j]), max(group[i], group[j])))

        for i in range(len(titles)):
            for j in range(i + 1, len(titles)):
                t1, t2 = titles[i], titles[j]
                pair_key = (min(t1, t2), max(t1, t2))
                if pair_key in handled_pairs:
                    continue

                sim = self.calculate_similarity(notes[t1], notes[t2])
                if sim >= self.fuzzy_threshold:
                    fuzzy_dupes.append({
                        "item_a": t1,
                        "item_b": t2,
                        "similarity": sim,
                        "match_type": "high_semantic_overlap"
                    })

        total_issues = len(exact_dupes) + len(norm_dupes) + len(fuzzy_dupes)

        return {
            "total_items_checked": len(notes),
            "exact_duplicate_groups": exact_dupes,
            "normalized_duplicate_groups": norm_dupes,
            "fuzzy_duplicates": fuzzy_dupes,
            "total_duplicate_issues": total_issues,
            "clean_status": total_issues == 0
        }

    def merge_notes(self, primary_title: str, primary_text: str, secondary_title: str, secondary_text: str) -> Dict[str, Any]:
        """
        Merges two duplicate or overlapping notes into a single cohesive document,
        preserving distinct headings, bullet items, and wikilinks.
        """
        wikilinks_pattern = re.compile(r'\[\[([^\]]+)\]\]')
        all_links = set(wikilinks_pattern.findall(primary_text) + wikilinks_pattern.findall(secondary_text))

        # Extract lines from secondary that are not present in primary
        primary_norm_lines = set(self.normalize_text(l) for l in primary_text.splitlines() if l.strip())
        supplemental_lines = []

        for line in secondary_text.splitlines():
            s_norm = self.normalize_text(line)
            if s_norm and s_norm not in primary_norm_lines and not line.startswith('# '):
                supplemental_lines.append(line)

        merged_content = primary_text.rstrip()
        if supplemental_lines:
            merged_content += f"\n\n---\n### Merged Insights from [[{secondary_title}]]\n"
            merged_content += "\n".join(supplemental_lines) + "\n"

        return {
            "title": primary_title,
            "merged_content": merged_content,
            "preserved_wikilinks": sorted(list(all_links)),
            "appended_lines_count": len(supplemental_lines)
        }


# Module singleton
knowledge_deduplicator = KnowledgeDeduplicator()
