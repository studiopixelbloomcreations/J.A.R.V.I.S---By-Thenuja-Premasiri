"""
Interactive Research Boxes (Capability 126)
Generates structured findings payloads, interactive HTML cards, standalone SVG cards,
and multi-block report decks (including the 13-block holographic HUD layout).
"""

import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class ResearchCitation:
    id: str
    title: str
    url: str
    snippet: str = ""
    reliability: float = 0.95
    author: str = ""
    publish_date: str = ""


@dataclass
class ResearchMetric:
    label: str
    value: str
    unit: str = ""
    delta: str = ""
    trend: str = "neutral"  # up, down, neutral


@dataclass
class ResearchFinding:
    id: str
    title: str
    summary: str
    category: str = "general"
    confidence: float = 0.9
    evidence: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    impact: str = "medium"  # low, medium, high, critical


class ResearchBoxPayloadGenerator:
    """
    Structured findings payload generator for J.A.R.V.I.S.
    Produces machine-readable JSON payloads, SVG cards, and interactive HTML modules.
    """

    CYAN_ACCENT = "#00e5ff"
    DARK_BG = "#061325"
    BORDER_GLOW = "rgba(0, 229, 255, 0.4)"

    def __init__(self, theme: str = "cyan_holo"):
        self.theme = theme

    def create_payload(
        self,
        topic: str,
        query: str,
        summary: str,
        findings: Optional[List[Dict[str, Any]]] = None,
        citations: Optional[List[Dict[str, Any]]] = None,
        metrics: Optional[List[Dict[str, Any]]] = None,
        tags: Optional[List[str]] = None,
        status: str = "COMPLETED",
        confidence: float = 0.95,
        execution_time_ms: float = 420.0,
    ) -> Dict[str, Any]:
        """
        Creates a structured, schema-compliant research box payload.
        """
        findings_list = findings or []
        citations_list = citations or []
        metrics_list = metrics or []
        tags_list = tags or []

        payload = {
            "version": "2.0.0",
            "type": "interactive_research_box",
            "topic": topic,
            "query": query,
            "timestamp": time.time(),
            "status": status,
            "confidence": confidence,
            "execution_time_ms": execution_time_ms,
            "summary": summary,
            "metrics": metrics_list,
            "findings": findings_list,
            "citations": citations_list,
            "tags": tags_list,
            "meta": {
                "theme": self.theme,
                "accent_color": self.CYAN_ACCENT,
                "expandable": True,
                "allow_filtering": True,
            },
        }
        return payload

    def generate_13_block_report_deck(
        self,
        topic: str,
        overview_stat: str,
        overview_label: str,
        milestones: List[Dict[str, str]],
        bar_chart_data: List[Dict[str, Any]],
        spec_items: List[Dict[str, str]],
        sources: List[str],
    ) -> Dict[str, Any]:
        """
        Generates the 13-block asymmetrical holographic HUD report grid payload
        modeled after the J.A.R.V.I.S. VR Market Survey & Deep Intelligence specs.
        """
        blocks = [
            {
                "id": "block_1",
                "index": 1,
                "type": "stat_highlight",
                "title": "EXECUTIVE METRIC // 2026",
                "value": overview_stat,
                "subtitle": overview_label,
                "col": 1,
                "row": 1,
            },
            {
                "id": "block_2",
                "index": 2,
                "type": "stacked_notes",
                "title": "NOTES // TRAJECTORY LOG",
                "items": milestones,
                "col": 1,
                "row": 2,
            },
            {
                "id": "block_3",
                "index": 3,
                "type": "mini_telemetry",
                "title": "TELEMETRY // SIGNAL STRENGTH",
                "rate": "98.4%",
                "status": "OPTIMAL",
                "col": 1,
                "row": 3,
            },
            {
                "id": "block_4",
                "index": 4,
                "type": "live_bar_chart",
                "title": f"CHART // {topic.upper()} DISTRIBUTION",
                "data": bar_chart_data,
                "maximizable": True,
                "col": 2,
                "row": 1,
            },
            {
                "id": "block_5",
                "index": 5,
                "type": "reticle_scanner",
                "title": "SENSOR // RADAR TRACKER",
                "targets_count": len(bar_chart_data),
                "col": 3,
                "row": 1,
            },
            {
                "id": "block_6",
                "index": 6,
                "type": "hero_viewport",
                "title": "HERO VIEWPORT // SPATIAL MATRIX",
                "aspect_ratio": "16:9",
                "mode": "3d_wireframe",
                "col": 2,
                "row": 2,
                "colspan": 2,
            },
            {
                "id": "block_7",
                "index": 7,
                "type": "banner_callout",
                "title": "INTEL ALERT",
                "text": f"Strategic synthesis verified for {topic}",
                "col": 4,
                "row": 1,
            },
            {
                "id": "block_8",
                "index": 8,
                "type": "hardware_spec",
                "title": "SUBSYSTEM SPECS",
                "specs": spec_items,
                "col": 4,
                "row": 2,
            },
            {
                "id": "block_9",
                "index": 9,
                "type": "citation_strip",
                "title": "VERIFIED CITATIONS",
                "sources": sources,
                "col": 1,
                "row": 4,
                "colspan": 4,
            },
            {
                "id": "block_10",
                "index": 10,
                "type": "status_badge",
                "title": "J.A.R.V.I.S. RUNTIME",
                "status": "ACTIVE_SYNTHESIS",
                "col": 4,
                "row": 3,
            },
            {
                "id": "block_11",
                "index": 11,
                "type": "confidence_matrix",
                "title": "CONFIDENCE COVARIANCE",
                "score": 0.965,
                "col": 3,
                "row": 3,
            },
            {
                "id": "block_12",
                "index": 12,
                "type": "action_triggers",
                "title": "PROPOSED ACTIONS",
                "actions": ["Export to Markdown", "Refresh Galaxy Graph", "Generate Patch"],
                "col": 2,
                "row": 3,
            },
            {
                "id": "block_13",
                "index": 13,
                "type": "docked_orb_telemetry",
                "title": "ORB KINETICS",
                "state": "DOCKED_BOTTOM_RIGHT",
                "diameter_px": 72,
                "col": 4,
                "row": 4,
            },
        ]
        return {
            "type": "13_block_report_deck",
            "topic": topic,
            "blocks_count": len(blocks),
            "blocks": blocks,
            "timestamp": time.time(),
        }

    def render_svg_card(self, payload: Dict[str, Any], width: int = 600, height: int = 340) -> str:
        """
        Renders a standalone, high-res SVG research card with cyan holographic aesthetic.
        """
        topic = payload.get("topic", "Research Synthesis")
        query = payload.get("query", "")
        summary = payload.get("summary", "")
        confidence = payload.get("confidence", 0.95)
        metrics = payload.get("metrics", [])
        findings = payload.get("findings", [])
        tags = payload.get("tags", [])

        # Format metrics string
        metrics_svg = ""
        mx = 30
        for m in metrics[:3]:
            m_val = f"{m.get('value', '')} {m.get('unit', '')}".strip()
            m_lbl = m.get("label", "").upper()
            metrics_svg += f"""
            <g transform="translate({mx}, 180)">
                <rect width="160" height="48" rx="4" fill="rgba(6, 25, 45, 0.7)" stroke="#00e5ff" stroke-width="1" stroke-opacity="0.3"/>
                <text x="10" y="20" fill="#7dd3fc" font-family="monospace" font-size="10" letter-spacing="1">{m_lbl}</text>
                <text x="10" y="40" fill="#ffffff" font-family="sans-serif" font-weight="bold" font-size="16">{m_val}</text>
            </g>
            """
            mx += 175

        # Format tags
        tags_svg = ""
        tx = 30
        for t in tags[:4]:
            t_str = f"#{t.upper()}"
            t_width = len(t_str) * 7 + 16
            tags_svg += f"""
            <rect x="{tx}" y="300" width="{t_width}" height="20" rx="10" fill="rgba(0, 229, 255, 0.15)" stroke="#00e5ff" stroke-width="1"/>
            <text x="{tx + 8}" y="314" fill="#00e5ff" font-family="monospace" font-size="10">{t_str}</text>
            """
            tx += t_width + 8

        # Short summary slice
        summary_short = summary[:120] + ("..." if len(summary) > 120 else "")

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
    <defs>
        <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#040d1a" stop-opacity="0.95"/>
            <stop offset="100%" stop-color="#071b30" stop-opacity="0.95"/>
        </linearGradient>
        <filter id="cyanGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur"/>
            <feComposite in="SourceGraphic" in2="blur" operator="over"/>
        </filter>
    </defs>

    <!-- Main Card Body -->
    <rect x="10" y="10" width="{width - 20}" height="{height - 20}" rx="8" fill="url(#bgGrad)" stroke="#00e5ff" stroke-width="1.5" stroke-opacity="0.5"/>
    
    <!-- Corner HUD Brackets -->
    <path d="M 16 30 L 16 16 L 30 16" fill="none" stroke="#00e5ff" stroke-width="2.5" filter="url(#cyanGlow)"/>
    <path d="M {width - 30} 16 L {width - 16} 16 L {width - 16} 30" fill="none" stroke="#00e5ff" stroke-width="2.5" filter="url(#cyanGlow)"/>
    <path d="M 16 {height - 30} L 16 {height - 16} L 30 {height - 16}" fill="none" stroke="#00e5ff" stroke-width="2.5" filter="url(#cyanGlow)"/>
    <path d="M {width - 30} {height - 16} L {width - 16} {height - 16} L {width - 16} {height - 30}" fill="none" stroke="#00e5ff" stroke-width="2.5" filter="url(#cyanGlow)"/>

    <!-- Header Strip -->
    <text x="30" y="42" fill="#00e5ff" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="bold" letter-spacing="2">RESEARCH BOX // CONFIDENCE: {int(confidence * 100)}%</text>
    <line x1="30" y1="52" x2="{width - 30}" y2="52" stroke="#00e5ff" stroke-width="0.8" stroke-opacity="0.3"/>

    <!-- Title & Query -->
    <text x="30" y="82" fill="#ffffff" font-family="system-ui, sans-serif" font-size="20" font-weight="700">{topic}</text>
    <text x="30" y="104" fill="#38bdf8" font-family="'JetBrains Mono', monospace" font-size="11">Q: {query}</text>

    <!-- Summary -->
    <text x="30" y="134" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12">{summary_short}</text>

    <!-- Metrics -->
    {metrics_svg}

    <!-- Tags -->
    {tags_svg}

    <!-- Findings Count Badge -->
    <rect x="{width - 140}" y="296" width="110" height="26" rx="4" fill="rgba(0, 229, 255, 0.1)" stroke="#00e5ff" stroke-width="1"/>
    <text x="{width - 85}" y="313" fill="#00e5ff" font-family="monospace" font-size="11" font-weight="bold" text-anchor="middle">{len(findings)} FINDINGS</text>
</svg>"""
        return svg

    def render_html_card(self, payload: Dict[str, Any]) -> str:
        """
        Renders an interactive, responsive HTML component with glassmorphism and cyan glow.
        """
        topic = payload.get("topic", "Research Findings")
        query = payload.get("query", "")
        summary = payload.get("summary", "")
        confidence = payload.get("confidence", 0.95)
        findings = payload.get("findings", [])
        citations = payload.get("citations", [])
        metrics = payload.get("metrics", [])
        tags = payload.get("tags", [])

        findings_html = ""
        for f in findings:
            f_title = f.get("title", "")
            f_sum = f.get("summary", "")
            f_conf = int(f.get("confidence", 0.9) * 100)
            findings_html += f"""
            <div class="holo-finding-item">
                <div class="holo-finding-header">
                    <span class="finding-title">{f_title}</span>
                    <span class="finding-conf">{f_conf}% MATCH</span>
                </div>
                <div class="finding-body">{f_sum}</div>
            </div>
            """

        citations_html = ""
        for c in citations:
            c_title = c.get("title", "")
            c_url = c.get("url", "#")
            citations_html += f"""
            <a href="{c_url}" target="_blank" class="holo-citation-pill">
                <span class="cite-icon">🔗</span>
                <span class="cite-title">{c_title}</span>
            </a>
            """

        metrics_html = ""
        for m in metrics:
            m_lbl = m.get("label", "").upper()
            m_val = m.get("value", "")
            m_unit = m.get("unit", "")
            metrics_html += f"""
            <div class="holo-metric-cell">
                <div class="metric-label">{m_lbl}</div>
                <div class="metric-val">{m_val} <span class="metric-unit">{m_unit}</span></div>
            </div>
            """

        tags_html = "".join([f'<span class="holo-tag">#{t}</span>' for t in tags])

        html = f"""
<div class="jarvis-holo-research-box">
    <style>
        .jarvis-holo-research-box {{
            background: rgba(6, 19, 37, 0.85);
            border: 1px solid rgba(0, 229, 255, 0.4);
            border-radius: 8px;
            box-shadow: 0 0 25px rgba(0, 229, 255, 0.15), inset 0 0 15px rgba(0, 229, 255, 0.05);
            backdrop-filter: blur(12px);
            color: #e2e8f0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 20px;
            max-width: 800px;
            position: relative;
            overflow: hidden;
        }}
        .jarvis-holo-research-box::before {{
            content: "// J.A.R.V.I.S. INTERACTIVE RESEARCH MATRIX";
            display: block;
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            letter-spacing: 1.5px;
            color: #00e5ff;
            margin-bottom: 8px;
        }}
        .holo-title-row {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            border-bottom: 1px solid rgba(0, 229, 255, 0.2);
            padding-bottom: 10px;
            margin-bottom: 12px;
        }}
        .holo-title {{
            font-size: 20px;
            font-weight: 700;
            color: #ffffff;
            margin: 0;
        }}
        .holo-confidence-badge {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: #00e5ff;
            background: rgba(0, 229, 255, 0.1);
            padding: 3px 8px;
            border-radius: 4px;
            border: 1px solid rgba(0, 229, 255, 0.3);
        }}
        .holo-query-bar {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: #38bdf8;
            margin-bottom: 12px;
        }}
        .holo-summary {{
            font-size: 14px;
            line-height: 1.5;
            color: #94a3b8;
            margin-bottom: 16px;
        }}
        .holo-metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 10px;
            margin-bottom: 18px;
        }}
        .holo-metric-cell {{
            background: rgba(14, 42, 71, 0.6);
            border: 1px solid rgba(0, 229, 255, 0.25);
            border-radius: 6px;
            padding: 8px 12px;
        }}
        .metric-label {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            color: #7dd3fc;
            letter-spacing: 0.8px;
        }}
        .metric-val {{
            font-size: 18px;
            font-weight: bold;
            color: #ffffff;
        }}
        .metric-unit {{
            font-size: 12px;
            color: #00e5ff;
        }}
        .holo-findings-section {{
            margin-bottom: 16px;
        }}
        .holo-finding-item {{
            background: rgba(4, 15, 30, 0.5);
            border-left: 3px solid #00e5ff;
            padding: 8px 12px;
            margin-bottom: 8px;
            border-radius: 0 4px 4px 0;
        }}
        .holo-finding-header {{
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            font-weight: 600;
            color: #f1f5f9;
        }}
        .finding-conf {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            color: #00e5ff;
        }}
        .finding-body {{
            font-size: 12px;
            color: #cbd5e1;
            margin-top: 4px;
        }}
        .holo-citations-wrap {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 12px;
        }}
        .holo-citation-pill {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 3px 8px;
            background: rgba(0, 229, 255, 0.1);
            border: 1px solid rgba(0, 229, 255, 0.3);
            border-radius: 12px;
            color: #38bdf8;
            text-decoration: none;
            font-size: 11px;
            transition: all 0.2s ease;
        }}
        .holo-citation-pill:hover {{
            background: rgba(0, 229, 255, 0.25);
            color: #ffffff;
        }}
        .holo-tags-row {{
            display: flex;
            gap: 6px;
            margin-top: 8px;
        }}
        .holo-tag {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            color: #00e5ff;
            opacity: 0.8;
        }}
    </style>
    <div class="holo-title-row">
        <h3 class="holo-title">{topic}</h3>
        <span class="holo-confidence-badge">CONFIDENCE: {int(confidence * 100)}%</span>
    </div>
    <div class="holo-query-bar">QUERY // {query}</div>
    <div class="holo-summary">{summary}</div>
    {f'<div class="holo-metrics-grid">{metrics_html}</div>' if metrics_html else ''}
    {f'<div class="holo-findings-section">{findings_html}</div>' if findings_html else ''}
    {f'<div class="holo-citations-wrap">{citations_html}</div>' if citations_html else ''}
    {f'<div class="holo-tags-row">{tags_html}</div>' if tags_html else ''}
</div>
"""
        return html
