"""
Timeline Visualization (Capability 129)
Generates interactive chronological timelines, milestone roadmaps, horizontal SVG sequences,
and Gantt-style execution charts for project milestones and research streams.
"""

import time
import math
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class TimelineEvent:
    id: str
    title: str
    timestamp: float
    description: str = ""
    category: str = "general"
    status: str = "completed"  # completed, in_progress, pending, failed
    duration_mins: float = 0.0
    tags: List[str] = field(default_factory=list)
    link_ids: List[str] = field(default_factory=list)


@dataclass
class TimelineMilestone:
    id: str
    title: str
    target_date: str
    status: str = "pending"  # completed, in_progress, pending
    deliverable: str = ""
    progress_pct: int = 0


class TimelineVisualizer:
    """
    Renders timeline data structures into SVG visualizations and interactive web views.
    """

    CYAN_ACCENT = "#00e5ff"
    STATUS_COLORS = {
        "completed": "#34d399",
        "in_progress": "#00e5ff",
        "pending": "#94a3b8",
        "failed": "#f87171",
        "blocked": "#fbbf24",
    }

    def __init__(self, title: str = "Operations Timeline"):
        self.title = title
        self.events: List[TimelineEvent] = []
        self.milestones: List[TimelineMilestone] = []

    def add_event(self, event: TimelineEvent) -> None:
        self.events.append(event)
        self.events.sort(key=lambda e: e.timestamp)

    def add_milestone(self, milestone: TimelineMilestone) -> None:
        self.milestones.append(milestone)

    def to_timeline_payload(self) -> Dict[str, Any]:
        """
        Exports structured JSON timeline payload.
        """
        return {
            "type": "timeline_visualization",
            "title": self.title,
            "events_count": len(self.events),
            "milestones_count": len(self.milestones),
            "events": [asdict(e) for e in self.events],
            "milestones": [asdict(m) for m in self.milestones],
            "time_range": {
                "start": self.events[0].timestamp if self.events else time.time(),
                "end": self.events[-1].timestamp if self.events else time.time(),
            },
        }

    def render_horizontal_svg(self, width: int = 900, height: int = 280) -> str:
        """
        Renders a clean, high-tech horizontal timeline SVG with glowing nodes and date ticks.
        """
        if not self.events:
            return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><text x="20" y="30" fill="#fff">No timeline events</text></svg>'

        n = len(self.events)
        padding_x = 70
        timeline_y = 130
        step_x = (width - 2 * padding_x) / max(1, n - 1) if n > 1 else 0

        # Backbone line
        line_start = padding_x
        line_end = width - padding_x

        nodes_svg = ""
        for i, ev in enumerate(self.events):
            cx = line_start + i * step_x
            color = self.STATUS_COLORS.get(ev.status, self.CYAN_ACCENT)
            time_str = time.strftime("%H:%M", time.localtime(ev.timestamp)) if ev.timestamp > 100000 else f"T+{int(ev.timestamp)}"

            # Alternate labels top / bottom to avoid collision
            is_top = (i % 2 == 0)
            card_y = timeline_y - 65 if is_top else timeline_y + 35
            stem_y = timeline_y - 12 if is_top else timeline_y + 12

            nodes_svg += f"""
            <!-- Stem line -->
            <line x1="{cx}" y1="{timeline_y}" x2="{cx}" y2="{stem_y}" stroke="{color}" stroke-width="1.5" stroke-dasharray="2 2"/>

            <!-- Node Circle -->
            <circle cx="{cx}" cy="{timeline_y}" r="9" fill="#040d1a" stroke="{color}" stroke-width="2"/>
            <circle cx="{cx}" cy="{timeline_y}" r="4" fill="{color}"/>

            <!-- Event Card -->
            <g transform="translate({cx - 70}, {card_y})">
                <rect width="140" height="48" rx="4" fill="rgba(6, 25, 45, 0.85)" stroke="{color}" stroke-width="1" stroke-opacity="0.4"/>
                <text x="8" y="16" fill="{color}" font-family="monospace" font-size="9" font-weight="bold">{time_str} // {ev.status.upper()}</text>
                <text x="8" y="32" fill="#ffffff" font-family="sans-serif" font-size="11" font-weight="bold">{ev.title[:28]}</text>
                <text x="8" y="44" fill="#94a3b8" font-family="sans-serif" font-size="9">{ev.category.upper()}</text>
            </g>
            """

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <defs>
        <linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#00e5ff" stop-opacity="0.2"/>
            <stop offset="50%" stop-color="#00e5ff" stop-opacity="0.9"/>
            <stop offset="100%" stop-color="#00e5ff" stop-opacity="0.2"/>
        </linearGradient>
    </defs>
    <!-- Background Frame -->
    <rect width="{width}" height="{height}" rx="6" fill="#040d1a" stroke="#00e5ff" stroke-width="1" stroke-opacity="0.35"/>
    <text x="24" y="30" fill="#00e5ff" font-family="'JetBrains Mono', monospace" font-size="12" font-weight="bold" letter-spacing="1.5">// TIMELINE: {self.title.upper()} ({len(self.events)} EVENTS)</text>
    
    <!-- Central Backbone Line -->
    <line x1="{line_start - 20}" y1="{timeline_y}" x2="{line_end + 20}" y2="{timeline_y}" stroke="url(#lineGrad)" stroke-width="3"/>

    {nodes_svg}
</svg>"""
        return svg

    def render_vertical_gantt_svg(self, width: int = 800, height: int = 360) -> str:
        """
        Renders a Gantt-style schedule / milestone execution chart in SVG.
        """
        items = self.events or [
            TimelineEvent(id="1", title="Planning Phase", timestamp=0, duration_mins=60, status="completed"),
            TimelineEvent(id="2", title="Code Implementation", timestamp=60, duration_mins=120, status="in_progress"),
            TimelineEvent(id="3", title="Verification & Tests", timestamp=180, duration_mins=60, status="pending"),
        ]

        total_span = max(1.0, max(e.timestamp + e.duration_mins for e in items) - min(e.timestamp for e in items))
        min_time = min(e.timestamp for e in items)

        chart_x = 200
        chart_width = width - chart_x - 30
        row_height = 36
        start_y = 60

        rows_svg = ""
        for i, it in enumerate(items[:8]):
            y = start_y + i * row_height
            color = self.STATUS_COLORS.get(it.status, self.CYAN_ACCENT)

            # Compute bar position
            offset_fraction = (it.timestamp - min_time) / total_span
            dur_fraction = max(0.04, it.duration_mins / total_span)
            bar_x = chart_x + offset_fraction * chart_width
            bar_w = dur_fraction * chart_width

            rows_svg += f"""
            <!-- Row Track -->
            <rect x="20" y="{y}" width="{width - 40}" height="30" rx="3" fill="rgba(6, 25, 45, 0.4)" stroke="rgba(0, 229, 255, 0.1)"/>
            <text x="30" y="{y + 19}" fill="#ffffff" font-family="sans-serif" font-size="11" font-weight="bold">{it.title[:24]}</text>
            <text x="160" y="{y + 19}" fill="{color}" font-family="monospace" font-size="9">{it.status.upper()}</text>

            <!-- Duration Bar -->
            <rect x="{bar_x:.1f}" y="{y + 5}" width="{bar_w:.1f}" height="20" rx="4" fill="{color}" fill-opacity="0.75" stroke="{color}" stroke-width="1"/>
            """

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <rect width="{width}" height="{height}" rx="6" fill="#040d1a" stroke="#00e5ff" stroke-width="1" stroke-opacity="0.35"/>
    <text x="24" y="32" fill="#00e5ff" font-family="'JetBrains Mono', monospace" font-size="12" font-weight="bold" letter-spacing="1.5">// GANTT EXECUTION SCHEDULE // {self.title.upper()}</text>
    <line x1="20" y1="46" x2="{width - 20}" y2="46" stroke="rgba(0, 229, 255, 0.2)"/>

    {rows_svg}
</svg>"""
        return svg

    def render_interactive_html(self, title: Optional[str] = None) -> str:
        """
        Renders an interactive HTML timeline view with cybernetic styling.
        """
        t_title = title or self.title
        events_html = ""
        for ev in self.events:
            color = self.STATUS_COLORS.get(ev.status, self.CYAN_ACCENT)
            t_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(ev.timestamp)) if ev.timestamp > 100000 else f"T+{int(ev.timestamp)}"
            events_html += f"""
            <div class="timeline-step">
                <div class="step-marker" style="border-color: {color}; box-shadow: 0 0 8px {color};"></div>
                <div class="step-content">
                    <div class="step-header">
                        <span class="step-time">{t_str}</span>
                        <span class="step-badge" style="color: {color}; border-color: {color};">{ev.status.upper()}</span>
                    </div>
                    <div class="step-title">{ev.title}</div>
                    <div class="step-desc">{ev.description}</div>
                </div>
            </div>
            """

        html = f"""
<div class="jarvis-timeline-container">
    <style>
        .jarvis-timeline-container {{
            background: rgba(4, 13, 26, 0.9);
            border: 1px solid rgba(0, 229, 255, 0.4);
            border-radius: 8px;
            padding: 20px;
            color: #f1f5f9;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            box-shadow: 0 0 25px rgba(0, 229, 255, 0.12);
        }}
        .timeline-title {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            color: #00e5ff;
            letter-spacing: 1.5px;
            margin-bottom: 20px;
            border-bottom: 1px solid rgba(0, 229, 255, 0.2);
            padding-bottom: 8px;
        }}
        .timeline-flow {{
            position: relative;
            padding-left: 24px;
            border-left: 2px solid rgba(0, 229, 255, 0.3);
        }}
        .timeline-step {{
            position: relative;
            margin-bottom: 20px;
        }}
        .step-marker {{
            position: absolute;
            left: -31px;
            top: 2px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #040d1a;
            border: 2px solid #00e5ff;
        }}
        .step-content {{
            background: rgba(6, 25, 45, 0.6);
            border: 1px solid rgba(0, 229, 255, 0.2);
            border-radius: 6px;
            padding: 10px 14px;
        }}
        .step-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 4px;
        }}
        .step-time {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            color: #7dd3fc;
        }}
        .step-badge {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 9px;
            padding: 1px 6px;
            border-radius: 3px;
            border: 1px solid #00e5ff;
        }}
        .step-title {{
            font-size: 14px;
            font-weight: bold;
            color: #ffffff;
        }}
        .step-desc {{
            font-size: 12px;
            color: #94a3b8;
            margin-top: 4px;
        }}
    </style>
    <div class="timeline-title">// CHRONOLOGICAL PIPELINE: {t_title.upper()}</div>
    <div class="timeline-flow">
        {events_html}
    </div>
</div>
"""
        return html
