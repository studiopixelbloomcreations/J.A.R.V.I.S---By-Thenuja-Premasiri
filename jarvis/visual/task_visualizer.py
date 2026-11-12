"""
Live Task Visualization (Capability 131)
Visualizes live executing tasks, multi-agent swarm activity, DAG workflows,
and cybernetic segmented progress bars (including the 20-block Rose UI progress tracker).
"""

import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class TaskNode:
    task_id: str
    name: str
    agent_name: str = "orchestrator"
    status: str = "pending"  # pending, running, completed, failed, blocked
    progress: float = 0.0  # 0 to 100
    dependencies: List[str] = field(default_factory=list)
    start_time: float = 0.0
    duration_s: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class LiveTaskVisualizer:
    """
    Renders live DAG workflows, multi-agent swarm telemetry, and progress indicators.
    """

    STATUS_COLORS = {
        "completed": "#34d399",
        "running": "#00e5ff",
        "pending": "#64748b",
        "failed": "#f87171",
        "blocked": "#fbbf24",
    }

    def __init__(self, workflow_name: str = "Autonomous Execution"):
        self.workflow_name = workflow_name
        self.tasks: Dict[str, TaskNode] = {}

    def add_task(self, task: TaskNode) -> None:
        self.tasks[task.task_id] = task

    def update_task_progress(self, task_id: str, progress: float, status: Optional[str] = None) -> bool:
        if task_id in self.tasks:
            t = self.tasks[task_id]
            t.progress = max(0.0, min(100.0, progress))
            if status:
                t.status = status
            return True
        return False

    def to_live_state_payload(self) -> Dict[str, Any]:
        """
        Generates full JSON state payload of active workflow.
        """
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t.status == "completed")
        running = sum(1 for t in self.tasks.values() if t.status == "running")
        failed = sum(1 for t in self.tasks.values() if t.status == "failed")
        overall_progress = sum(t.progress for t in self.tasks.values()) / max(1, total)

        return {
            "type": "live_task_state",
            "workflow_name": self.workflow_name,
            "timestamp": time.time(),
            "total_tasks": total,
            "completed_tasks": completed,
            "running_tasks": running,
            "failed_tasks": failed,
            "overall_progress_pct": round(overall_progress, 1),
            "tasks": [asdict(t) for t in self.tasks.values()],
        }

    def render_segmented_progress_bar_svg(
        self,
        progress_pct: float,
        total_blocks: int = 20,
        width: int = 400,
        height: int = 28,
        label: str = "SYNTHESIS IN PROGRESS",
    ) -> str:
        """
        Renders the exact 20-block segmented cyan progress bar from the J.A.R.V.I.S. / Rose UI specs.
        """
        pct_clamped = max(0.0, min(100.0, progress_pct))
        filled_count = int(round((pct_clamped / 100.0) * total_blocks))

        pad_x = 10
        pad_y = 6
        bar_w = width - 2 * pad_x
        bar_h = height - 2 * pad_y
        block_gap = 3
        single_w = (bar_w - (total_blocks - 1) * block_gap) / total_blocks

        blocks_svg = ""
        for i in range(total_blocks):
            bx = pad_x + i * (single_w + block_gap)
            is_filled = (i < filled_count)
            fill_color = "#00e5ff" if is_filled else "rgba(0, 229, 255, 0.12)"
            stroke_color = "#00e5ff" if is_filled else "rgba(0, 229, 255, 0.25)"
            glow_attr = 'filter="url(#segGlow)"' if is_filled else ''

            blocks_svg += f"""
            <rect x="{bx:.1f}" y="{pad_y}" width="{single_w:.1f}" height="{bar_h}" rx="2" fill="{fill_color}" stroke="{stroke_color}" stroke-width="0.8" {glow_attr}/>
            """

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <defs>
        <filter id="segGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="1.5" result="blur"/>
            <feComposite in="SourceGraphic" in2="blur" operator="over"/>
        </filter>
    </defs>
    <!-- Background Frame -->
    <rect width="{width}" height="{height}" rx="4" fill="#040d1a" stroke="rgba(0, 229, 255, 0.3)" stroke-width="1"/>
    
    <!-- Blocks -->
    {blocks_svg}
</svg>"""
        return svg

    def render_dag_svg(self, width: int = 850, height: int = 420) -> str:
        """
        Renders a directional DAG workflow graph with connecting arrows and glowing status badges.
        """
        task_list = list(self.tasks.values())
        if not task_list:
            return f'<svg width="{width}" height="{height}"><text x="20" y="30" fill="#fff">No tasks defined</text></svg>'

        # Determine topological stages / levels based on dependencies
        levels: Dict[str, int] = {}

        def get_level(tid: str, visited=None) -> int:
            if visited is None:
                visited = set()
            if tid in visited:
                return 0
            visited.add(tid)
            t = self.tasks.get(tid)
            if not t or not t.dependencies:
                return 0
            return 1 + max(get_level(d, visited) for d in t.dependencies)

        for tid in self.tasks:
            levels[tid] = get_level(tid)

        max_lvl = max(levels.values()) if levels else 0
        cols: Dict[int, List[TaskNode]] = {}
        for tid, lvl in levels.items():
            cols.setdefault(lvl, []).append(self.tasks[tid])

        # Calculate coordinates
        pad_x = 80
        pad_y = 60
        col_w = (width - 2 * pad_x) / max(1, max_lvl) if max_lvl > 0 else 0

        coords: Dict[str, Tuple[float, float]] = {}
        for lvl, col_tasks in cols.items():
            cx = pad_x + lvl * col_w
            row_h = (height - 2 * pad_y) / max(1, len(col_tasks))
            for r, task in enumerate(col_tasks):
                cy = pad_y + r * row_h + row_h / 2
                coords[task.task_id] = (cx, cy)

        # Render connecting dependency lines
        lines_svg = ""
        for task in task_list:
            tx, ty = coords[task.task_id]
            for dep_id in task.dependencies:
                if dep_id in coords:
                    sx, sy = coords[dep_id]
                    lines_svg += f"""
                    <path d="M {sx + 70} {sy} C {(sx + tx)/2} {sy}, {(sx + tx)/2} {ty}, {tx - 70} {ty}"
                          fill="none" stroke="#00e5ff" stroke-width="1.5" stroke-opacity="0.4" marker-end="url(#arrow)"/>
                    """

        # Render task cards
        nodes_svg = ""
        for task in task_list:
            cx, cy = coords[task.task_id]
            color = self.STATUS_COLORS.get(task.status, "#64748b")
            card_w = 140
            card_h = 46

            nodes_svg += f"""
            <g transform="translate({cx - card_w/2}, {cy - card_h/2})">
                <rect width="{card_w}" height="{card_h}" rx="5" fill="rgba(6, 25, 45, 0.9)" stroke="{color}" stroke-width="1.5"/>
                <circle cx="12" cy="14" r="3.5" fill="{color}"/>
                <text x="22" y="17" fill="#ffffff" font-family="sans-serif" font-size="10" font-weight="bold">{task.name[:16]}</text>
                <text x="12" y="36" fill="#7dd3fc" font-family="'JetBrains Mono', monospace" font-size="9">@{task.agent_name} // {int(task.progress)}%</text>
            </g>
            """

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 8 5 L 0 9 z" fill="#00e5ff" fill-opacity="0.6"/>
        </marker>
    </defs>
    <rect width="{width}" height="{height}" rx="6" fill="#040d1a" stroke="#00e5ff" stroke-width="1" stroke-opacity="0.35"/>
    <text x="20" y="28" fill="#00e5ff" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="bold" letter-spacing="1.5">// WORKFLOW DAG: {self.workflow_name.upper()} ({len(self.tasks)} NODES)</text>
    
    {lines_svg}
    {nodes_svg}
</svg>"""
        return svg

    def render_swarm_monitor_svg(
        self,
        agents_data: List[Dict[str, Any]],
        width: int = 700,
        height: int = 340,
    ) -> str:
        """
        Visualizes the 10-Agent Swarm execution matrix (Agents 1 through 10) with status, role, and throughput.
        """
        pad_x = 20
        pad_y = 50
        cols = 2
        card_w = (width - 2 * pad_x - 16) / cols
        card_h = 48

        cards_svg = ""
        for i, a in enumerate(agents_data[:10]):
            col = i % cols
            row = i // cols
            x = pad_x + col * (card_w + 16)
            y = pad_y + row * (card_h + 10)

            name = a.get("name", f"agent-{i+1}")
            role = a.get("role", "Specialist")
            status = a.get("status", "working")
            color = "#34d399" if status in ("done", "completed") else ("#00e5ff" if status == "working" else "#94a3b8")

            cards_svg += f"""
            <g transform="translate({x}, {y})">
                <rect width="{card_w}" height="{card_h}" rx="4" fill="rgba(6, 25, 45, 0.75)" stroke="{color}" stroke-width="1" stroke-opacity="0.4"/>
                <circle cx="14" cy="16" r="3.5" fill="{color}"/>
                <text x="25" y="19" fill="#ffffff" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="bold">@{name.upper()}</text>
                <text x="{card_w - 12}" y="19" fill="{color}" font-family="monospace" font-size="9" text-anchor="end">{status.upper()}</text>
                <text x="25" y="36" fill="#7dd3fc" font-family="sans-serif" font-size="10">{role[:28]}</text>
            </g>
            """

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <rect width="{width}" height="{height}" rx="6" fill="#040d1a" stroke="#00e5ff" stroke-width="1" stroke-opacity="0.35"/>
    <text x="20" y="28" fill="#00e5ff" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="bold" letter-spacing="1.5">// SWARM AGENT ROSTER // LIVE TELEMETRY</text>
    {cards_svg}
</svg>"""
        return svg
