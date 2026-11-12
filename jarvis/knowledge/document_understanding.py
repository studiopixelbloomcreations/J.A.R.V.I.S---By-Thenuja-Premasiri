"""
Document Understanding Engine for J.A.R.V.I.S.
Capability 94: Document Understanding

Provides deep structural and semantic parsing of documents, markdown archives,
notes, and raw text. Extracts section hierarchies, action items, wikilinks,
tables, code blocks, metrics, lexical complexity, and executive summaries.
"""

import re
import math
from typing import Dict, List, Any, Optional


class DocumentUnderstandingEngine:
    """
    Advanced document analysis engine for parsing, extracting structure,
    computing complexity metrics, and generating semantic summaries.
    """

    WIKILINK_PATTERN = re.compile(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')
    URL_PATTERN = re.compile(r'\[([^\]]+)\]\((https?://[^\s)]+)\)')
    TASK_PATTERN = re.compile(r'^\s*[-*]\s*\[([ xX])\]\s*(.+)$', re.MULTILINE)
    CODE_BLOCK_PATTERN = re.compile(r'```([a-zA-Z0-9_\-\+]*)\n([\s\S]*?)```')
    HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    TABLE_PATTERN = re.compile(r'((?:\|[^\n]+\|\r?\n){2,})')

    SECTOR_KEYWORDS = {
        "finance": ["revenue", "profit", "cash", "invoice", "payment", "bank", "cost", "budget", "pricing", "dollar", "lkr", "usd"],
        "marketing": ["brand", "campaign", "social media", "audience", "ad", "ctr", "engagement", "reach", "conversion", "youtube", "tiktok"],
        "operations": ["logistics", "workflow", "process", "inventory", "shipping", "supplier", "schedule", "dispatch", "warehouse"],
        "products": ["feature", "release", "roadmap", "mvp", "spec", "ui", "ux", "prototype", "vfx", "render", "animation"],
        "tech": ["python", "api", "code", "database", "server", "git", "gpu", "cuda", "model", "webrtc", "docker", "pipeline"],
        "creative": ["vfx", "blender", "davinci", "color grading", "cinematic", "storyboard", "shot", "soundtrack", "audio", "capcut"],
        "personal": ["study", "school", "grade 10", "health", "exam", "debating", "kurunegala", "st. anne", "routine", "habit"]
    }

    def __init__(self, wpm_reading_speed: int = 200):
        self.wpm_reading_speed = max(50, wpm_reading_speed)

    def parse_document(self, text: str, title: Optional[str] = None) -> Dict[str, Any]:
        """
        Performs comprehensive structural and semantic parsing of a document.
        """
        clean_text = text or ""
        word_list = re.findall(r'\b[a-zA-Z0-9_\'-]+\b', clean_text)
        word_count = len(word_list)
        char_count = len(clean_text)

        headings = self.extract_headings(clean_text)
        tasks = self.extract_tasks(clean_text)
        wikilinks = self.extract_wikilinks(clean_text)
        urls = self.extract_urls(clean_text)
        code_blocks = self.extract_code_blocks(clean_text)
        tables = self.extract_tables(clean_text)
        entities = self.extract_key_entities(clean_text)
        metrics = self.calculate_metrics(clean_text, word_list)
        topic_classification = self.classify_topic(clean_text, title or "")
        summary = self.generate_summary(clean_text, title, headings, tasks)

        return {
            "title": title or (headings[0]["text"] if headings else "Untitled Document"),
            "word_count": word_count,
            "char_count": char_count,
            "estimated_reading_minutes": round(word_count / self.wpm_reading_speed, 2),
            "headings": headings,
            "tasks": tasks,
            "wikilinks": wikilinks,
            "external_links": urls,
            "code_blocks": code_blocks,
            "tables": tables,
            "key_entities": entities,
            "metrics": metrics,
            "primary_topic": topic_classification["primary_topic"],
            "topic_scores": topic_classification["scores"],
            "executive_summary": summary
        }

    def extract_headings(self, text: str) -> List[Dict[str, Any]]:
        """Extracts markdown heading hierarchy."""
        results = []
        for match in self.HEADING_PATTERN.finditer(text):
            level = len(match.group(1))
            heading_text = match.group(2).strip()
            results.append({
                "level": level,
                "text": heading_text,
                "anchor": re.sub(r'[^a-zA-Z0-9_\-]', '', heading_text.lower().replace(' ', '-'))
            })
        return results

    def extract_tasks(self, text: str) -> List[Dict[str, Any]]:
        """Extracts actionable checkbox tasks."""
        tasks = []
        for match in self.TASK_PATTERN.finditer(text):
            completed = match.group(1).lower() == 'x'
            item_text = match.group(2).strip()
            tasks.append({
                "text": item_text,
                "completed": completed
            })
        return tasks

    def extract_wikilinks(self, text: str) -> List[Dict[str, str]]:
        """Extracts internal [[wikilinks]]."""
        links = []
        seen = set()
        for match in self.WIKILINK_PATTERN.finditer(text):
            target = match.group(1).strip()
            alias = match.group(2).strip() if match.group(2) else target
            if target not in seen:
                seen.add(target)
                links.append({"target": target, "alias": alias})
        return links

    def extract_urls(self, text: str) -> List[Dict[str, str]]:
        """Extracts markdown hyperlinks [label](url)."""
        urls = []
        for match in self.URL_PATTERN.finditer(text):
            urls.append({
                "label": match.group(1).strip(),
                "url": match.group(2).strip()
            })
        return urls

    def extract_code_blocks(self, text: str) -> List[Dict[str, Any]]:
        """Extracts fenced code snippets."""
        blocks = []
        for match in self.CODE_BLOCK_PATTERN.finditer(text):
            lang = match.group(1).strip() or "text"
            code = match.group(2)
            blocks.append({
                "language": lang,
                "code": code,
                "line_count": len(code.splitlines())
            })
        return blocks

    def extract_tables(self, text: str) -> List[Dict[str, Any]]:
        """Extracts and parses markdown tables."""
        tables = []
        for match in self.TABLE_PATTERN.finditer(text):
            raw_table = match.group(1).strip()
            lines = [l.strip() for l in raw_table.splitlines() if l.strip()]
            if len(lines) >= 2:
                headers = [col.strip() for col in lines[0].split('|')[1:-1]]
                start_row_idx = 1
                if len(lines) > 1 and re.match(r'^[\|\s\-:]+$', lines[1]):
                    start_row_idx = 2
                rows = []
                for row_line in lines[start_row_idx:]:
                    row_cols = [col.strip() for col in row_line.split('|')[1:-1]]
                    if row_cols:
                        rows.append(row_cols)
                if headers and rows:
                    tables.append({
                        "headers": headers,
                        "rows": rows,
                        "row_count": len(rows),
                        "col_count": len(headers)
                    })
        return tables

    def extract_key_entities(self, text: str) -> List[str]:
        """Extracts named entities, acronyms, and capitalized terminology."""
        clean = re.sub(r'```[\s\S]*?```', '', text)
        clean = re.sub(r'\[\[([^\]]+)\]\]', r'\1', clean)
        matches = re.findall(r'\b[A-Z][a-zA-Z0-9_\'-]+(?:\s+[A-Z][a-zA-Z0-9_\'-]+)*\b', clean)
        freq: Dict[str, int] = {}
        stop_words = {"The", "This", "That", "There", "Here", "And", "Or", "In", "On", "At", "To", "For", "With", "If", "When", "Then"}
        for m in matches:
            m_strip = m.strip()
            if m_strip not in stop_words and len(m_strip) > 2:
                freq[m_strip] = freq.get(m_strip, 0) + 1
        sorted_entities = sorted(freq.keys(), key=lambda k: freq[k], reverse=True)
        return sorted_entities[:15]

    def calculate_metrics(self, text: str, words: List[str]) -> Dict[str, Any]:
        """Calculates readability, lexical richness, and structural statistics."""
        if not words:
            return {
                "lexical_density": 0.0,
                "avg_word_length": 0.0,
                "sentence_count": 0,
                "readability_score": 100.0,
                "complexity_rating": "Elementary"
            }

        unique_words = set(w.lower() for w in words)
        lexical_density = round(len(unique_words) / len(words), 3)
        avg_word_len = round(sum(len(w) for w in words) / len(words), 2)

        sentences = re.split(r'[.!?]+(?:\s+|$)', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = max(1, len(sentences))

        words_per_sentence = len(words) / sentence_count

        # Approximate Flesch Reading Ease
        # 206.835 - 1.015 * (words/sentence) - 84.6 * (syllables/word)
        syllables_count = sum(self._count_syllables(w) for w in words)
        syllables_per_word = syllables_count / len(words)
        reading_ease = 206.835 - (1.015 * words_per_sentence) - (84.6 * syllables_per_word)
        reading_ease = max(0.0, min(100.0, round(reading_ease, 1)))

        if reading_ease >= 80:
            rating = "Accessible"
        elif reading_ease >= 60:
            rating = "Standard"
        elif reading_ease >= 40:
            rating = "Technical"
        else:
            rating = "Advanced / Academic"

        return {
            "lexical_density": lexical_density,
            "avg_word_length": avg_word_len,
            "sentence_count": sentence_count,
            "readability_score": reading_ease,
            "complexity_rating": rating
        }

    def _count_syllables(self, word: str) -> int:
        """Heuristic syllable counter."""
        w = word.lower()
        if len(w) <= 3:
            return 1
        w = re.sub(r'(?:[^laeiouy]|ed|es|e)$', '', w)
        w = re.sub(r'^y', '', w)
        matches = re.findall(r'[aeiouy]{1,2}', w)
        return max(1, len(matches))

    def classify_topic(self, text: str, title: str) -> Dict[str, Any]:
        """Classifies document into knowledge sectors based on keyword densities."""
        combined = (title + " " + text).lower()
        scores: Dict[str, int] = {}
        for sector, kws in self.SECTOR_KEYWORDS.items():
            score = 0
            for kw in kws:
                score += combined.count(kw)
            scores[sector] = score

        best_sector = "general"
        highest_score = 0
        for s, score in scores.items():
            if score > highest_score:
                highest_score = score
                best_sector = s

        return {
            "primary_topic": best_sector,
            "scores": scores
        }

    def generate_summary(self, text: str, title: Optional[str], headings: List[Dict[str, Any]], tasks: List[Dict[str, Any]]) -> str:
        """Synthesizes a structured executive summary."""
        lines = [line.strip() for line in text.splitlines() if line.strip() and not line.startswith('#')]
        first_paragraph = lines[0] if lines else "Document contains structured archival notes."
        if len(first_paragraph) > 280:
            first_paragraph = first_paragraph[:280] + "…"

        summary_parts = [
            f"**Overview**: {first_paragraph}"
        ]

        if headings:
            main_sections = [h["text"] for h in headings if h["level"] <= 2][:4]
            if main_sections:
                summary_parts.append(f"**Key Sections**: {', '.join(main_sections)}")

        if tasks:
            pending = [t["text"] for t in tasks if not t["completed"]][:3]
            if pending:
                summary_parts.append(f"**Pending Actions**: {'; '.join(pending)}")

        return "\n".join(summary_parts)


# Module singleton
document_understanding = DocumentUnderstandingEngine()
