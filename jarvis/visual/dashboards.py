"""
Statistical Dashboards (Capability 130)
Generates pure SVG analytics charts, KPI telemetry cards, mini sparklines,
donut distribution charts, and composite cybernetic Bento dashboards without external JS dependencies.
"""

import math
from typing import List, Dict, Any, Optional, Tuple


class StatisticalDashboardGenerator:
    """
    High-performance pure SVG and HTML dashboard generator.
    Produces crisp vector bar charts, line graphs, donut charts, sparklines, and Bento grids.
    """

    CYAN_PRIMARY = "#00e5ff"
    CYAN_MUTED = "rgba(0, 229, 255, 0.4)"
    DARK_BG = "#040d1a"
    DARK_CARD = "rgba(6, 25, 45, 0.85)"

    SERIES_COLORS = ["#00e5ff", "#38bdf8", "#34d399", "#f472b6", "#a78bfa", "#fbbf24"]

    def __init__(self, title: str = "JARVIS Analytics"):
        self.title = title

    def render_sparkline_svg(
        self,
        values: List[float],
        width: int = 140,
        height: int = 36,
        color: str = CYAN_PRIMARY,
        show_fill: bool = True,
    ) -> str:
        """
        Renders an ultra-compact SVG sparkline for KPI cards.
        """
        if not values or len(values) < 2:
            return f'<svg width="{width}" height="{height}"><line x1="0" y1="{height/2}" x2="{width}" y2="{height/2}" stroke="{color}"/></svg>'

        min_v = min(values)
        max_v = max(values)
        span_v = max(1e-5, max_v - min_v)

        points = []
        step_x = width / (len(values) - 1)
        for i, val in enumerate(values):
            x = i * step_x
            y = height - ((val - min_v) / span_v) * (height - 8) - 4
            points.append((x, y))

        polyline_pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)

        fill_svg = ""
        if show_fill:
            poly_fill = f"0,{height} {polyline_pts} {width},{height}"
            fill_svg = f'<polygon points="{poly_fill}" fill="{color}" fill-opacity="0.15"/>'

        last_x, last_y = points[-1]

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    {fill_svg}
    <polyline points="{polyline_pts}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="{last_x:.1f}" cy="{last_y:.1f}" r="3" fill="#ffffff" stroke="{color}" stroke-width="1.5"/>
</svg>"""
        return svg

    def render_bar_chart_svg(
        self,
        data: List[Dict[str, Any]],
        width: int = 500,
        height: int = 280,
        title: str = "DISTRIBUTION",
    ) -> str:
        """
        Renders a clean SVG vertical bar chart with axis ticks, labels, and cyan value bars.
        `data`: [{'label': 'Quest 2', 'value': 42.5}, ...]
        """
        if not data:
            return f'<svg width="{width}" height="{height}"><text x="20" y="30" fill="#fff">No data</text></svg>'

        max_v = max(float(d.get("value", 0)) for d in data)
        max_v = max(1.0, max_v * 1.15)  # Add headroom

        pad_left = 60
        pad_bottom = 45
        pad_top = 45
        pad_right = 25

        plot_w = width - pad_left - pad_right
        plot_h = height - pad_top - pad_bottom

        num_bars = len(data)
        bar_slot = plot_w / num_bars
        bar_w = min(40.0, bar_slot * 0.65)

        bars_svg = ""
        for i, item in enumerate(data):
            v = float(item.get("value", 0))
            lbl = str(item.get("label", ""))
            bh = (v / max_v) * plot_h
            bx = pad_left + i * bar_slot + (bar_slot - bar_w) / 2
            by = pad_top + plot_h - bh

            color = item.get("color") or self.SERIES_COLORS[i % len(self.SERIES_COLORS)]

            bars_svg += f"""
            <!-- Bar -->
            <rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w:.1f}" height="{bh:.1f}" rx="3" fill="{color}" fill-opacity="0.85" stroke="{color}" stroke-width="1"/>
            
            <!-- Value text -->
            <text x="{bx + bar_w/2:.1f}" y="{by - 6:.1f}" fill="#ffffff" font-family="'JetBrains Mono', monospace" font-size="10" font-weight="bold" text-anchor="middle">{v:.1f}</text>
            
            <!-- Category label -->
            <text x="{bx + bar_w/2:.1f}" y="{pad_top + plot_h + 18:.1f}" fill="#94a3b8" font-family="sans-serif" font-size="10" text-anchor="middle">{lbl[:8]}</text>
            """

        # Grid lines (4 intervals)
        grid_svg = ""
        for k in range(5):
            gy = pad_top + plot_h * (1.0 - k / 4)
            val_label = f"{(max_v * k / 4):.0f}"
            grid_svg += f"""
            <line x1="{pad_left}" y1="{gy:.1f}" x2="{width - pad_right}" y2="{gy:.1f}" stroke="rgba(0, 229, 255, 0.12)" stroke-width="1" stroke-dasharray="2 3"/>
            <text x="{pad_left - 8}" y="{gy + 4:.1f}" fill="#7dd3fc" font-family="monospace" font-size="9" text-anchor="end">{val_label}</text>
            """

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <rect width="{width}" height="{height}" rx="6" fill="#040d1a" stroke="#00e5ff" stroke-width="1" stroke-opacity="0.35"/>
    <text x="20" y="26" fill="#00e5ff" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="bold" letter-spacing="1.5">// CHART: {title.upper()}</text>
    
    <!-- Grid -->
    {grid_svg}

    <!-- Axis lines -->
    <line x1="{pad_left}" y1="{pad_top + plot_h}" x2="{width - pad_right}" y2="{pad_top + plot_h}" stroke="#00e5ff" stroke-width="1.2"/>
    <line x1="{pad_left}" y1="{pad_top}" x2="{pad_left}" y2="{pad_top + plot_h}" stroke="#00e5ff" stroke-width="1.2"/>

    <!-- Bars -->
    {bars_svg}
</svg>"""
        return svg

    def render_donut_chart_svg(
        self,
        data: List[Dict[str, Any]],
        width: int = 400,
        height: int = 250,
        title: str = "ALLOCATION",
        inner_radius_ratio: float = 0.58,
    ) -> str:
        """
        Renders a multi-segment SVG donut chart with legend.
        `data`: [{'label': 'A', 'value': 40}, {'label': 'B', 'value': 60}]
        """
        if not data:
            return f'<svg width="{width}" height="{height}"><text x="20" y="30" fill="#fff">No data</text></svg>'

        total = sum(float(d.get("value", 0)) for d in data)
        if total <= 0:
            total = 1.0

        cx = 120.0
        cy = height / 2.0 + 8
        outer_r = min(cx - 25, (height - 60) / 2.0)
        inner_r = outer_r * inner_radius_ratio

        segments_svg = ""
        legend_svg = ""
        current_angle = -math.pi / 2.0

        for i, item in enumerate(data):
            val = float(item.get("value", 0))
            pct = (val / total) * 100.0
            angle_span = (val / total) * 2 * math.pi
            color = item.get("color") or self.SERIES_COLORS[i % len(self.SERIES_COLORS)]

            end_angle = current_angle + angle_span

            # Arc coordinates
            x1_out = cx + outer_r * math.cos(current_angle)
            y1_out = cy + outer_r * math.sin(current_angle)
            x2_out = cx + outer_r * math.cos(end_angle)
            y2_out = cy + outer_r * math.sin(end_angle)

            x1_in = cx + inner_r * math.cos(end_angle)
            y1_in = cy + inner_r * math.sin(end_angle)
            x2_in = cx + inner_r * math.cos(current_angle)
            y2_in = cy + inner_r * math.sin(current_angle)

            large_arc = 1 if angle_span > math.pi else 0

            d_path = f"M {x1_out:.1f} {y1_out:.1f} A {outer_r} {outer_r} 0 {large_arc} 1 {x2_out:.1f} {y2_out:.1f} L {x1_in:.1f} {y1_in:.1f} A {inner_r} {inner_r} 0 {large_arc} 0 {x2_in:.1f} {y2_in:.1f} Z"

            segments_svg += f'<path d="{d_path}" fill="{color}" stroke="#040d1a" stroke-width="2"/>\n'

            # Legend entry
            leg_y = 50 + i * 26
            lbl = item.get("label", "")
            legend_svg += f"""
            <rect x="235" y="{leg_y}" width="10" height="10" rx="2" fill="{color}"/>
            <text x="252" y="{leg_y + 9}" fill="#ffffff" font-family="sans-serif" font-size="11">{lbl}</text>
            <text x="360" y="{leg_y + 9}" fill="{color}" font-family="'JetBrains Mono', monospace" font-size="10" font-weight="bold" text-anchor="end">{pct:.1f}%</text>
            """

            current_angle = end_angle

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <rect width="{width}" height="{height}" rx="6" fill="#040d1a" stroke="#00e5ff" stroke-width="1" stroke-opacity="0.35"/>
    <text x="20" y="24" fill="#00e5ff" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="bold" letter-spacing="1.5">// DONUT: {title.upper()}</text>
    
    <g class="donut-group">
        {segments_svg}
    </g>

    <g class="legend-group">
        {legend_svg}
    </g>
</svg>"""
        return svg

    def render_bento_dashboard_html(
        self,
        cards: List[Dict[str, Any]],
        title: Optional[str] = None,
    ) -> str:
        """
        Renders a responsive multi-panel Bento grid dashboard (combining KPI metrics, sparklines, and charts).
        """
        t_title = title or self.title

        cards_html = ""
        for c in cards:
            c_type = c.get("type", "kpi")
            c_title = c.get("title", "METRIC")
            col_span = c.get("colspan", 1)

            if c_type == "kpi":
                val = c.get("value", "0")
                unit = c.get("unit", "")
                delta = c.get("delta", "")
                trend = c.get("trend", "up")
                delta_color = "#34d399" if trend == "up" else ("#f87171" if trend == "down" else "#38bdf8")
                spark_vals = c.get("sparkline", [])
                spark_svg = self.render_sparkline_svg(spark_vals, width=120, height=32) if spark_vals else ""

                cards_html += f"""
                <div class="bento-card" style="grid-column: span {col_span};">
                    <div class="bento-card-header">
                        <span class="bento-card-title">{c_title}</span>
                        <span class="bento-delta" style="color: {delta_color};">{delta}</span>
                    </div>
                    <div class="bento-kpi-row">
                        <div class="bento-value">{val} <span class="bento-unit">{unit}</span></div>
                        <div class="bento-sparkline">{spark_svg}</div>
                    </div>
                </div>
                """
            elif c_type == "chart_bar":
                bar_svg = self.render_bar_chart_svg(c.get("data", []), width=380, height=220, title=c_title)
                cards_html += f"""
                <div class="bento-card bento-card-chart" style="grid-column: span {col_span};">
                    {bar_svg}
                </div>
                """
            elif c_type == "chart_donut":
                donut_svg = self.render_donut_chart_svg(c.get("data", []), width=360, height=220, title=c_title)
                cards_html += f"""
                <div class="bento-card bento-card-chart" style="grid-column: span {col_span};">
                    {donut_svg}
                </div>
                """

        html = f"""
<div class="jarvis-bento-dashboard">
    <style>
        .jarvis-bento-dashboard {{
            background: #020710;
            border: 1px solid rgba(0, 229, 255, 0.4);
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 0 30px rgba(0, 229, 255, 0.12);
            color: #f8fafc;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        .bento-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(0, 229, 255, 0.25);
            padding-bottom: 10px;
            margin-bottom: 16px;
        }}
        .bento-header-title {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            font-weight: bold;
            color: #00e5ff;
            letter-spacing: 2px;
        }}
        .bento-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 14px;
        }}
        .bento-card {{
            background: rgba(6, 25, 45, 0.7);
            border: 1px solid rgba(0, 229, 255, 0.25);
            border-radius: 6px;
            padding: 14px;
            box-sizing: border-box;
        }}
        .bento-card-chart {{
            padding: 0;
            overflow: hidden;
            display: flex;
            justify-content: center;
            background: transparent;
            border: none;
        }}
        .bento-card-header {{
            display: flex;
            justify-content: space-between;
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            margin-bottom: 8px;
        }}
        .bento-card-title {{
            color: #7dd3fc;
            letter-spacing: 1px;
        }}
        .bento-kpi-row {{
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }}
        .bento-value {{
            font-size: 24px;
            font-weight: bold;
            color: #ffffff;
        }}
        .bento-unit {{
            font-size: 12px;
            color: #00e5ff;
            font-weight: normal;
        }}
    </style>
    <div class="bento-header">
        <span class="bento-header-title">// DASHBOARD: {t_title.upper()}</span>
        <span style="font-family: monospace; font-size: 10px; color: #38bdf8;">LIVE TELEMETRY</span>
    </div>
    <div class="bento-grid">
        {cards_html}
    </div>
</div>
"""
        return html
