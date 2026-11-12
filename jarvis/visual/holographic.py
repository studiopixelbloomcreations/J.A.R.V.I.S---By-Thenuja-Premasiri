"""
Holographic-Style Data Panels (Capability 128)
Generates futuristic HUD, sci-fi cybernetic SVG widgets, and glassmorphic HTML components
with J.A.R.V.I.S. cyan neon glow (#00e5ff), corner brackets, scanlines, and telemetry readouts.
"""

import math
import time
from typing import List, Dict, Any, Optional, Tuple


class HolographicPanelGenerator:
    """
    Renders cybernetic HUD interfaces:
    - Circular arc reactor dials & telemetry gauges
    - Animated rotating radar reticles with target blips
    - Multi-channel telemetry status strips
    - Holographic cards with diagonal cut corners and corner brackets '//'
    - Glassmorphic diagnostic terminals
    """

    CYAN_PRIMARY = "#00e5ff"
    CYAN_SECONDARY = "#38bdf8"
    DARK_BG = "#040d1a"
    DARK_PANEL = "rgba(6, 19, 37, 0.85)"
    BORDER_GLOW = "rgba(0, 229, 255, 0.4)"

    def __init__(self, primary_color: str = CYAN_PRIMARY):
        self.primary_color = primary_color

    def render_circular_gauge_svg(
        self,
        value: float,
        min_val: float = 0.0,
        max_val: float = 100.0,
        label: str = "CORE TEMP",
        unit: str = "°C",
        radius: float = 70.0,
        center_x: float = 90.0,
        center_y: float = 90.0,
    ) -> str:
        """
        Renders a circular sci-fi arc reactor gauge with tick marks and glowing progress arc.
        """
        # Clamp value
        val_clamped = max(min_val, min(max_val, value))
        fraction = (val_clamped - min_val) / max(1e-5, (max_val - min_val))

        # Arc spans from 135 deg to 405 deg (270 degrees sweep)
        start_angle = 135.0
        sweep_angle = 270.0
        current_angle = start_angle + fraction * sweep_angle

        def polar_to_cart(cx, cy, r, angle_deg):
            rad = math.radians(angle_deg)
            return cx + r * math.cos(rad), cy + r * math.sin(rad)

        # Background track arc
        bg_start_x, bg_start_y = polar_to_cart(center_x, center_y, radius, start_angle)
        bg_end_x, bg_end_y = polar_to_cart(center_x, center_y, radius, start_angle + sweep_angle)

        # Value progress arc
        val_end_x, val_end_y = polar_to_cart(center_x, center_y, radius, current_angle)
        large_arc_flag = 1 if (fraction * sweep_angle) > 180 else 0

        # Radial tick marks
        ticks_svg = ""
        for i in range(13):
            t_angle = start_angle + (sweep_angle * i / 12)
            t_x1, t_y1 = polar_to_cart(center_x, center_y, radius - 8, t_angle)
            t_x2, t_y2 = polar_to_cart(center_x, center_y, radius - 2, t_angle)
            is_active = (t_angle <= current_angle)
            t_color = self.primary_color if is_active else "rgba(56, 189, 248, 0.25)"
            ticks_svg += f'<line x1="{t_x1:.1f}" y1="{t_y1:.1f}" x2="{t_x2:.1f}" y2="{t_y2:.1f}" stroke="{t_color}" stroke-width="1.5"/>\n'

        width = int(center_x * 2)
        height = int(center_y * 2)

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <defs>
        <filter id="gaugeGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="2.5" result="blur"/>
            <feComposite in="SourceGraphic" in2="blur" operator="over"/>
        </filter>
    </defs>
    <!-- Outer boundary ring -->
    <circle cx="{center_x}" cy="{center_y}" r="{radius + 12}" fill="none" stroke="rgba(0, 229, 255, 0.15)" stroke-width="1" stroke-dasharray="4 6"/>
    
    <!-- Background track -->
    <path d="M {bg_start_x:.1f} {bg_start_y:.1f} A {radius} {radius} 0 1 1 {bg_end_x:.1f} {bg_end_y:.1f}"
          fill="none" stroke="rgba(255, 255, 255, 0.1)" stroke-width="6" stroke-linecap="round"/>

    <!-- Ticks -->
    {ticks_svg}

    <!-- Active progress track -->
    <path d="M {bg_start_x:.1f} {bg_start_y:.1f} A {radius} {radius} 0 {large_arc_flag} 1 {val_end_x:.1f} {val_end_y:.1f}"
          fill="none" stroke="{self.primary_color}" stroke-width="6" stroke-linecap="round" filter="url(#gaugeGlow)"/>

    <!-- Digital Readout -->
    <text x="{center_x}" y="{center_y + 4}" fill="#ffffff" font-family="'JetBrains Mono', monospace" font-size="20" font-weight="bold" text-anchor="middle">{value:.1f}</text>
    <text x="{center_x}" y="{center_y + 18}" fill="{self.CYAN_SECONDARY}" font-family="'JetBrains Mono', monospace" font-size="9" text-anchor="middle">{unit}</text>
    <text x="{center_x}" y="{center_y + 36}" fill="{self.primary_color}" font-family="'JetBrains Mono', monospace" font-size="9" letter-spacing="1.2" text-anchor="middle">{label.upper()}</text>
</svg>"""
        return svg

    def render_radar_reticle_svg(
        self,
        targets: Optional[List[Dict[str, Any]]] = None,
        radius: float = 85.0,
        scan_angle_deg: float = 45.0,
        width: int = 210,
        height: int = 210,
    ) -> str:
        """
        Renders an authentic circular HUD radar reticle with azimuth degree marks and blips.
        """
        cx = width / 2
        cy = height / 2
        targets_list = targets or [
            {"distance": 0.45, "angle": 30, "label": "NODE_A"},
            {"distance": 0.75, "angle": 135, "label": "NODE_B"},
            {"distance": 0.30, "angle": 250, "label": "NODE_C"},
        ]

        # Scan line coordinates
        scan_rad = math.radians(scan_angle_deg)
        scan_x = cx + radius * math.cos(scan_rad)
        scan_y = cy + radius * math.sin(scan_rad)

        # Blips
        blips_svg = ""
        for t in targets_list:
            dist = float(t.get("distance", 0.5)) * radius
            ang_rad = math.radians(float(t.get("angle", 0)))
            bx = cx + dist * math.cos(ang_rad)
            by = cy + dist * math.sin(ang_rad)
            blabel = t.get("label", "")
            blips_svg += f"""
            <circle cx="{bx:.1f}" cy="{by:.1f}" r="3" fill="#ffffff" stroke="{self.primary_color}" stroke-width="1.5"/>
            <text x="{bx + 6:.1f}" y="{by + 3:.1f}" fill="{self.CYAN_SECONDARY}" font-family="monospace" font-size="8">{blabel}</text>
            """

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <defs>
        <radialGradient id="radarSweep" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="{self.primary_color}" stop-opacity="0.25"/>
            <stop offset="100%" stop-color="{self.primary_color}" stop-opacity="0.0"/>
        </radialGradient>
    </defs>
    <!-- Background Circle -->
    <circle cx="{cx}" cy="{cy}" r="{radius}" fill="#040d1a" stroke="{self.primary_color}" stroke-width="1.2" stroke-opacity="0.6"/>
    
    <!-- Concentric range rings -->
    <circle cx="{cx}" cy="{cy}" r="{radius * 0.33:.1f}" fill="none" stroke="{self.primary_color}" stroke-width="0.8" stroke-dasharray="3 4" stroke-opacity="0.4"/>
    <circle cx="{cx}" cy="{cy}" r="{radius * 0.66:.1f}" fill="none" stroke="{self.primary_color}" stroke-width="0.8" stroke-dasharray="3 4" stroke-opacity="0.4"/>

    <!-- Crosshairs -->
    <line x1="{cx - radius - 5}" y1="{cy}" x2="{cx + radius + 5}" y2="{cy}" stroke="{self.primary_color}" stroke-width="0.8" stroke-opacity="0.5"/>
    <line x1="{cx}" y1="{cy - radius - 5}" x2="{cx}" y2="{cy + radius + 5}" stroke="{self.primary_color}" stroke-width="0.8" stroke-opacity="0.5"/>

    <!-- Cardinal markers -->
    <text x="{cx}" y="{cy - radius + 11}" fill="{self.primary_color}" font-family="monospace" font-size="8" text-anchor="middle">N</text>
    <text x="{cx + radius - 9}" y="{cy + 3}" fill="{self.primary_color}" font-family="monospace" font-size="8" text-anchor="middle">E</text>
    <text x="{cx}" y="{cy + radius - 4}" fill="{self.primary_color}" font-family="monospace" font-size="8" text-anchor="middle">S</text>
    <text x="{cx - radius + 9}" y="{cy + 3}" fill="{self.primary_color}" font-family="monospace" font-size="8" text-anchor="middle">W</text>

    <!-- Scan Line -->
    <line x1="{cx}" y1="{cy}" x2="{scan_x:.1f}" y2="{scan_y:.1f}" stroke="{self.primary_color}" stroke-width="2"/>

    <!-- Targets -->
    {blips_svg}
    
    <text x="{cx}" y="{height - 6}" fill="{self.primary_color}" font-family="monospace" font-size="8" letter-spacing="1" text-anchor="middle">RADAR // SCANNER</text>
</svg>"""
        return svg

    def render_telemetry_bar_svg(
        self,
        metrics: List[Dict[str, Any]],
        width: int = 500,
        height: int = 70,
    ) -> str:
        """
        Renders a horizontal telemetry strip showing live operational indicators.
        """
        num_cells = max(1, len(metrics))
        cell_width = (width - 20) / num_cells

        cells_svg = ""
        for i, m in enumerate(metrics):
            x = 10 + i * cell_width
            label = str(m.get("label", "PARAM")).upper()
            val = str(m.get("value", "0"))
            unit = str(m.get("unit", ""))
            status = m.get("status", "NORMAL")
            status_color = "#34d399" if status == "OPTIMAL" else self.primary_color

            cells_svg += f"""
            <g transform="translate({x}, 10)">
                <rect width="{cell_width - 8}" height="{height - 20}" rx="4" fill="rgba(8, 28, 52, 0.6)" stroke="{self.primary_color}" stroke-width="1" stroke-opacity="0.3"/>
                <circle cx="12" cy="14" r="3" fill="{status_color}"/>
                <text x="22" y="17" fill="#7dd3fc" font-family="monospace" font-size="9" letter-spacing="1">{label}</text>
                <text x="12" y="38" fill="#ffffff" font-family="'JetBrains Mono', monospace" font-size="14" font-weight="bold">{val} <tspan font-size="9" fill="{self.primary_color}">{unit}</tspan></text>
            </g>
            """

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <rect width="{width}" height="{height}" rx="6" fill="#040d1a" stroke="{self.primary_color}" stroke-width="1" stroke-opacity="0.4"/>
    {cells_svg}
</svg>"""
        return svg

    def render_hud_card(
        self,
        title: str,
        content_html: str,
        status: str = "ONLINE",
        width: int = 400,
        height: int = 250,
        badge: str = "JARVIS // v2.0",
    ) -> str:
        """
        Renders a holographic card with corner brackets '//', cyan borders, and scanline overlay.
        """
        html = f"""
<div class="jarvis-hud-card" style="width: {width}px; min-height: {height}px;">
    <style>
        .jarvis-hud-card {{
            position: relative;
            background: rgba(6, 19, 37, 0.85);
            border: 1px solid rgba(0, 229, 255, 0.4);
            border-radius: 6px;
            box-shadow: 0 0 20px rgba(0, 229, 255, 0.12), inset 0 0 10px rgba(0, 229, 255, 0.05);
            backdrop-filter: blur(10px);
            padding: 16px;
            box-sizing: border-box;
            color: #e2e8f0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace;
            overflow: hidden;
        }}
        .jarvis-hud-card::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%);
            background-size: 100% 4px;
            pointer-events: none;
            opacity: 0.35;
        }}
        .hud-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(0, 229, 255, 0.2);
            padding-bottom: 8px;
            margin-bottom: 12px;
        }}
        .hud-card-title {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 1.5px;
            color: #00e5ff;
        }}
        .hud-card-badge {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 9px;
            color: #38bdf8;
            background: rgba(0, 229, 255, 0.1);
            padding: 2px 6px;
            border-radius: 3px;
            border: 1px solid rgba(0, 229, 255, 0.25);
        }}
        .hud-card-content {{
            font-size: 13px;
            line-height: 1.5;
            position: relative;
            z-index: 1;
        }}
        .hud-corner-tl {{
            position: absolute; top: 2px; left: 2px;
            width: 8px; height: 8px;
            border-top: 2px solid #00e5ff; border-left: 2px solid #00e5ff;
        }}
        .hud-corner-tr {{
            position: absolute; top: 2px; right: 2px;
            width: 8px; height: 8px;
            border-top: 2px solid #00e5ff; border-right: 2px solid #00e5ff;
        }}
        .hud-corner-bl {{
            position: absolute; bottom: 2px; left: 2px;
            width: 8px; height: 8px;
            border-bottom: 2px solid #00e5ff; border-left: 2px solid #00e5ff;
        }}
        .hud-corner-br {{
            position: absolute; bottom: 2px; right: 2px;
            width: 8px; height: 8px;
            border-bottom: 2px solid #00e5ff; border-right: 2px solid #00e5ff;
        }}
    </style>
    <div class="hud-corner-tl"></div>
    <div class="hud-corner-tr"></div>
    <div class="hud-corner-bl"></div>
    <div class="hud-corner-br"></div>
    <div class="hud-card-header">
        <span class="hud-card-title">{title}</span>
        <span class="hud-card-badge">{badge}</span>
    </div>
    <div class="hud-card-content">
        {content_html}
    </div>
</div>
"""
        return html

    def render_terminal_panel_html(
        self, logs: List[str], title: str = "SYSTEM DIAGNOSTICS // STREAM"
    ) -> str:
        """
        Renders a glowing dark glassmorphic terminal panel with timestamped log outputs.
        """
        log_lines_html = ""
        for line in logs:
            log_lines_html += f'<div class="term-line"><span class="term-prompt">&gt;</span> {line}</div>\n'

        html = f"""
<div class="jarvis-term-panel">
    <style>
        .jarvis-term-panel {{
            background: #030a14;
            border: 1px solid rgba(0, 229, 255, 0.4);
            border-radius: 6px;
            padding: 14px;
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            font-size: 11px;
            color: #38bdf8;
            max-height: 280px;
            overflow-y: auto;
            box-shadow: 0 0 20px rgba(0, 229, 255, 0.1);
        }}
        .term-header {{
            color: #00e5ff;
            font-weight: bold;
            letter-spacing: 1.2px;
            margin-bottom: 10px;
            border-bottom: 1px dashed rgba(0, 229, 255, 0.25);
            padding-bottom: 4px;
        }}
        .term-line {{
            margin-bottom: 4px;
            line-height: 1.4;
            word-break: break-all;
        }}
        .term-prompt {{
            color: #00e5ff;
            font-weight: bold;
            margin-right: 4px;
        }}
    </style>
    <div class="term-header">{title}</div>
    {log_lines_html}
</div>
"""
        return html
