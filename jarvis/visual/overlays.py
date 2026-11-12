"""
Contextual Visual Overlays (Capability 135)
Generates floating HUD widgets, top-navigation pill bars, anchored cybernetic tooltips,
status badges, and modular screen HUD layers for desktop and web interfaces.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict


@dataclass
class HUDPill:
    label: str
    active: bool = False
    icon: str = ""
    action_id: str = ""


@dataclass
class FloatingTooltip:
    target_x: int
    target_y: int
    title: str
    description: str
    severity: str = "info"  # info, warning, success, alert
    actions: List[str] = field(default_factory=list)


class ContextualOverlayEngine:
    """
    Renders modular contextual visual overlays, HUD pills, and floating pointer callouts.
    """

    CYAN_PRIMARY = "#00e5ff"
    DARK_PANEL = "rgba(6, 19, 37, 0.9)"

    SEVERITY_COLORS = {
        "info": "#00e5ff",
        "warning": "#fbbf24",
        "success": "#34d399",
        "alert": "#f87171",
    }

    def __init__(self):
        self.pills: List[HUDPill] = []
        self.tooltips: List[FloatingTooltip] = []

    def add_pill(self, label: str, active: bool = False, icon: str = "", action_id: str = "") -> "ContextualOverlayEngine":
        self.pills.append(HUDPill(label=label, active=active, icon=icon, action_id=action_id))
        return self

    def add_tooltip(
        self,
        target_x: int,
        target_y: int,
        title: str,
        description: str,
        severity: str = "info",
        actions: Optional[List[str]] = None,
    ) -> "ContextualOverlayEngine":
        self.tooltips.append(FloatingTooltip(
            target_x=target_x,
            target_y=target_y,
            title=title,
            description=description,
            severity=severity,
            actions=actions or [],
        ))
        return self

    def render_hud_pills_svg(self, width: int = 600, height: int = 40) -> str:
        """
        Renders the top navigation pill bar in crisp SVG.
        """
        pills_svg = ""
        current_x = 10
        for p in self.pills:
            label_text = f"[{p.label.upper()}]"
            pill_w = len(label_text) * 7.5 + 20
            color = self.CYAN_PRIMARY if p.active else "rgba(56, 189, 248, 0.7)"
            bg_fill = "rgba(0, 229, 255, 0.22)" if p.active else "rgba(6, 19, 37, 0.75)"
            border_stroke = self.CYAN_PRIMARY if p.active else "rgba(0, 229, 255, 0.3)"

            pills_svg += f"""
            <rect x="{current_x}" y="8" width="{pill_w}" height="24" rx="12" fill="{bg_fill}" stroke="{border_stroke}" stroke-width="1"/>
            <text x="{current_x + pill_w/2}" y="24" fill="{color}" font-family="'JetBrains Mono', monospace" font-size="10" font-weight="bold" letter-spacing="1" text-anchor="middle">{label_text}</text>
            """
            current_x += pill_w + 10

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <g class="hud-pill-group">
        {pills_svg}
    </g>
</svg>"""
        return svg

    def render_overlay_svg(self, screen_width: int = 1920, screen_height: int = 1080) -> str:
        """
        Assembles a full-screen contextual HUD overlay SVG:
        - Corner bracket indicators
        - Floating anchor tooltips with cyan pointer lines
        - Top navigation HUD pill row
        """
        tooltips_svg = ""
        for tt in self.tooltips:
            tx = tt.target_x
            ty = tt.target_y
            color = self.SEVERITY_COLORS.get(tt.severity, self.CYAN_PRIMARY)

            # Tooltip box offset
            box_x = tx + 35
            box_y = ty - 45
            box_w = 210
            box_h = 70

            # Pointer line from box to target
            tooltips_svg += f"""
            <!-- Pointer Anchor -->
            <circle cx="{tx}" cy="{ty}" r="4" fill="{color}"/>
            <circle cx="{tx}" cy="{ty}" r="9" fill="none" stroke="{color}" stroke-width="1.2" stroke-dasharray="3 3"/>
            <polyline points="{tx},{ty} {tx + 20},{ty - 25} {box_x},{ty - 25}" fill="none" stroke="{color}" stroke-width="1.5"/>

            <!-- Tooltip Card -->
            <g transform="translate({box_x}, {box_y})">
                <rect width="{box_w}" height="{box_h}" rx="5" fill="rgba(6, 19, 37, 0.92)" stroke="{color}" stroke-width="1.2"/>
                <text x="10" y="18" fill="{color}" font-family="'JetBrains Mono', monospace" font-size="10" font-weight="bold">// {tt.title.upper()}</text>
                <text x="10" y="36" fill="#e2e8f0" font-family="sans-serif" font-size="11">{tt.description[:28]}</text>
                <text x="10" y="56" fill="#7dd3fc" font-family="monospace" font-size="9">{tt.actions[0] if tt.actions else 'PROCEED'}</text>
            </g>
            """

        pills_markup = self.render_hud_pills_svg(width=800, height=40)

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{screen_width}" height="{screen_height}" viewBox="0 0 {screen_width} {screen_height}">
    <defs>
        <filter id="hudGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="2.5" result="blur"/>
            <feComposite in="SourceGraphic" in2="blur" operator="over"/>
        </filter>
    </defs>
    <!-- Screen Corner Reticles -->
    <path d="M 24 50 L 24 24 L 50 24" fill="none" stroke="#00e5ff" stroke-width="2.5" filter="url(#hudGlow)"/>
    <path d="M {screen_width - 50} 24 L {screen_width - 24} 24 L {screen_width - 24} 50" fill="none" stroke="#00e5ff" stroke-width="2.5" filter="url(#hudGlow)"/>
    <path d="M 24 {screen_height - 50} L 24 {screen_height - 24} L 50 {screen_height - 24}" fill="none" stroke="#00e5ff" stroke-width="2.5" filter="url(#hudGlow)"/>
    <path d="M {screen_width - 50} {screen_height - 24} L {screen_width - 24} {screen_height - 24} L {screen_width - 24} {screen_height - 50}" fill="none" stroke="#00e5ff" stroke-width="2.5" filter="url(#hudGlow)"/>

    <!-- Watermark / HUD Sub-label -->
    <text x="32" y="{screen_height - 32}" fill="#00e5ff" font-family="'JetBrains Mono', monospace" font-size="10" letter-spacing="2">J.A.R.V.I.S. // CONTEXTUAL OVERLAY ACTIVE</text>

    <!-- Top Pills -->
    <g transform="translate(60, 20)">
        {pills_markup}
    </g>

    <!-- Anchored Tooltips -->
    {tooltips_svg}
</svg>"""
        return svg

    def render_overlay_html(self) -> str:
        """
        Renders an HTML/CSS floating overlay layer with responsive cybernetic styling.
        """
        pills_html = ""
        for p in self.pills:
            cls = "hud-pill active" if p.active else "hud-pill"
            pills_html += f'<div class="{cls}">[{p.label.upper()}]</div>\n'

        html = f"""
<div class="jarvis-contextual-overlay-layer">
    <style>
        .jarvis-contextual-overlay-layer {{
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            pointer-events: none;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        .hud-pills-bar {{
            position: absolute;
            top: 18px;
            right: 28px;
            display: flex;
            gap: 10px;
            pointer-events: auto;
        }}
        .hud-pill {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 1.2px;
            padding: 3px 10px;
            border-radius: 12px;
            border: 1px solid rgba(0, 229, 255, 0.4);
            color: #38bdf8;
            background: rgba(6, 19, 37, 0.7);
            backdrop-filter: blur(8px);
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .hud-pill.active {{
            background: rgba(0, 229, 255, 0.22);
            color: #00e5ff;
            border-color: #00e5ff;
            box-shadow: 0 0 10px rgba(0, 229, 255, 0.4);
        }}
    </style>
    <div class="hud-pills-bar">
        {pills_html}
    </div>
</div>
"""
        return html
