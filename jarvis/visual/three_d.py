"""
3D Data Visualization (Capability 134)
Generates 3D data geometry payloads, point clouds, vector fields, wireframe meshes,
isometric 3D SVG projections, and Three.js-ready JSON geometries.
CRITICAL DIRECTIVE: DOES NOT MODIFY viewer/index.html. Serves modular data and vector layers.
"""

import math
import json
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict


@dataclass
class Point3D:
    x: float
    y: float
    z: float
    r: float = 0.0
    g: float = 0.9
    b: float = 1.0
    size: float = 3.0
    label: str = ""


@dataclass
class Vector3D:
    origin_x: float
    origin_y: float
    origin_z: float
    dx: float
    dy: float
    dz: float
    magnitude: float = 1.0
    color: str = "#00e5ff"


class ThreeDDataVisualizer:
    """
    3D geometric mathematical generator and isometric SVG projection engine.
    """

    CYAN_NEON = "#00e5ff"
    DARK_BG = "#040d1a"

    def __init__(self):
        pass

    def generate_point_cloud(
        self,
        count: int = 200,
        shape: str = "sphere",  # 'sphere', 'galaxy_spiral', 'helix', 'cube', 'torus'
        radius: float = 120.0,
    ) -> List[Point3D]:
        """
        Generates 3D point cloud structures according to mathematical manifolds.
        """
        points = []

        if shape == "sphere":
            golden_ratio = (1 + math.sqrt(5)) / 2
            for i in range(count):
                theta = 2 * math.pi * i / golden_ratio
                phi = math.acos(1 - 2 * (i + 0.5) / count)
                px = radius * math.sin(phi) * math.cos(theta)
                py = radius * math.cos(phi)
                pz = radius * math.sin(phi) * math.sin(theta)
                # Cyan to sky blue color variation
                points.append(Point3D(x=px, y=py, z=pz, r=0.0, g=0.7 + (i % 3) * 0.1, b=1.0, size=2.5))

        elif shape == "galaxy_spiral":
            arms = 3
            for i in range(count):
                arm = i % arms
                arm_offset = (2 * math.pi * arm) / arms
                dist = (i / count) * radius
                angle = arm_offset + (dist / radius) * 4.0
                px = dist * math.cos(angle)
                pz = dist * math.sin(angle)
                py = (math.sin(dist * 0.1) * (radius * 0.15)) + (i % 5 - 2) * 4.0
                points.append(Point3D(x=px, y=py, z=pz, r=0.0, g=0.9, b=1.0, size=3.0))

        elif shape == "helix":
            for i in range(count):
                t = (i / count) * 4 * math.pi
                px = radius * 0.6 * math.cos(t)
                pz = radius * 0.6 * math.sin(t)
                py = (i / count) * (radius * 2.0) - radius
                points.append(Point3D(x=px, y=py, z=pz, r=0.2, g=0.8, b=1.0, size=2.5))

        elif shape == "torus":
            r_major = radius * 0.75
            r_minor = radius * 0.28
            for i in range(count):
                u = (i / count) * 2 * math.pi * 5
                v = (i / count) * 2 * math.pi
                px = (r_major + r_minor * math.cos(v)) * math.cos(u)
                pz = (r_major + r_minor * math.cos(v)) * math.sin(u)
                py = r_minor * math.sin(v)
                points.append(Point3D(x=px, y=py, z=pz, r=0.1, g=0.85, b=0.95, size=2.5))

        else:  # cube
            side = radius * 1.2
            for i in range(count):
                px = ((i % 6) / 5.0 - 0.5) * side
                py = (((i // 6) % 6) / 5.0 - 0.5) * side
                pz = (((i // 36) % 6) / 5.0 - 0.5) * side
                points.append(Point3D(x=px, y=py, z=pz, r=0.0, g=0.9, b=1.0, size=2.5))

        return points

    def generate_vector_field(
        self,
        grid_dim: int = 4,
        spacing: float = 40.0,
        pattern: str = "vortex",
    ) -> List[Vector3D]:
        """
        Generates a 3D vector field for physics and spatial telemetry visualization.
        """
        vectors = []
        half = (grid_dim - 1) * spacing / 2.0

        for ix in range(grid_dim):
            x = ix * spacing - half
            for iy in range(grid_dim):
                y = iy * spacing - half
                for iz in range(grid_dim):
                    z = iz * spacing - half

                    if pattern == "vortex":
                        # Tangential rotation in X-Z plane
                        r = math.sqrt(x * x + z * z) + 1e-4
                        dx = -z / r * 15.0
                        dz = x / r * 15.0
                        dy = -y * 0.1
                    elif pattern == "sink":
                        dx = -x * 0.3
                        dy = -y * 0.3
                        dz = -z * 0.3
                    else:  # uniform wave
                        dx = 12.0
                        dy = math.sin(x * 0.05) * 8.0
                        dz = math.cos(z * 0.05) * 8.0

                    mag = math.sqrt(dx * dx + dy * dy + dz * dz)
                    vectors.append(Vector3D(
                        origin_x=x, origin_y=y, origin_z=z,
                        dx=dx, dy=dy, dz=dz, magnitude=round(mag, 2),
                    ))

        return vectors

    def project_3d_to_2d(
        self,
        x: float,
        y: float,
        z: float,
        center_x: float,
        center_y: float,
        rot_x_deg: float = 25.0,
        rot_y_deg: float = -35.0,
        perspective_f: float = 600.0,
    ) -> Tuple[float, float, float]:
        """
        Rotates and projects a 3D point (x, y, z) into 2D camera coordinates with perspective depth.
        """
        rad_x = math.radians(rot_x_deg)
        rad_y = math.radians(rot_y_deg)

        # Rotate around Y axis
        x1 = x * math.cos(rad_y) + z * math.sin(rad_y)
        y1 = y
        z1 = -x * math.sin(rad_y) + z * math.cos(rad_y)

        # Rotate around X axis
        x2 = x1
        y2 = y1 * math.cos(rad_x) - z1 * math.sin(rad_x)
        z2 = y1 * math.sin(rad_x) + z1 * math.cos(rad_x)

        # Perspective projection
        factor = perspective_f / max(10.0, (perspective_f + z2))
        px = center_x + x2 * factor
        py = center_y - y2 * factor  # invert Y for screen coords

        return px, py, z2

    def render_isometric_svg(
        self,
        points: List[Point3D],
        lines: Optional[List[Tuple[int, int]]] = None,
        width: int = 600,
        height: int = 400,
        rot_x: float = 25.0,
        rot_y: float = -35.0,
        title: str = "3D POINT CLOUD",
    ) -> str:
        """
        Renders 3D points and optional connecting wireframe lines into an SVG vector diagram.
        """
        cx = width / 2.0
        cy = height / 2.0

        projected = []
        for p in points:
            px, py, pz = self.project_3d_to_2d(p.x, p.y, p.z, cx, cy, rot_x, rot_y)
            projected.append((px, py, pz, p))

        # Sort painter's algorithm: draw farthest (deepest z) first
        projected.sort(key=lambda item: item[2], reverse=True)

        # Lines SVG
        lines_svg = ""
        if lines:
            for idx_a, idx_b in lines:
                if 0 <= idx_a < len(points) and 0 <= idx_b < len(points):
                    pa = points[idx_a]
                    pb = points[idx_b]
                    pax, pay, _ = self.project_3d_to_2d(pa.x, pa.y, pa.z, cx, cy, rot_x, rot_y)
                    pbx, pby, _ = self.project_3d_to_2d(pb.x, pb.y, pb.z, cx, cy, rot_x, rot_y)
                    lines_svg += f'<line x1="{pax:.1f}" y1="{pay:.1f}" x2="{pbx:.1f}" y2="{pby:.1f}" stroke="#00e5ff" stroke-width="0.8" stroke-opacity="0.35"/>\n'

        # Points SVG
        points_svg = ""
        for px, py, pz, p in projected:
            color = f"rgb({int(p.r * 255)}, {int(p.g * 255)}, {int(p.b * 255)})"
            alpha = max(0.25, min(1.0, (pz + 200) / 400.0))
            points_svg += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{p.size:.1f}" fill="{color}" fill-opacity="{alpha:.2f}"/>\n'

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <rect width="{width}" height="{height}" rx="6" fill="#040d1a" stroke="#00e5ff" stroke-width="1" stroke-opacity="0.35"/>
    <text x="20" y="26" fill="#00e5ff" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="bold" letter-spacing="1.5">// 3D SPATIAL PROJECTION: {title.upper()} ({len(points)} VERTICES)</text>
    
    <!-- 3D Scene Viewport -->
    <g class="spatial-viewport">
        {lines_svg}
        {points_svg}
    </g>
</svg>"""
        return svg

    def render_exploded_orb_svg(
        self,
        width: int = 450,
        height: int = 350,
        label: str = "J.A.R.V.I.S.",
    ) -> str:
        """
        Renders the exploded kinetic gyroscope orb with concentric rings, radial ticks,
        central torus, and cyan bloom from the Rose UI / J.A.R.V.I.S. spec.
        """
        cx = width / 2.0
        cy = height / 2.0

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <defs>
        <filter id="orbBloom" x="-40%" y="-40%" width="180%" height="180%">
            <feGaussianBlur stdDeviation="6" result="blur1"/>
            <feGaussianBlur stdDeviation="2" result="blur2"/>
            <feMerge>
                <feMergeNode in="blur1"/>
                <feMergeNode in="blur2"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
        <linearGradient id="axisGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#00e5ff" stop-opacity="0.0"/>
            <stop offset="30%" stop-color="#00e5ff" stop-opacity="0.6"/>
            <stop offset="50%" stop-color="#ffffff" stop-opacity="0.9"/>
            <stop offset="70%" stop-color="#00e5ff" stop-opacity="0.6"/>
            <stop offset="100%" stop-color="#00e5ff" stop-opacity="0.0"/>
        </linearGradient>
    </defs>
    <!-- Background Frame -->
    <rect width="{width}" height="{height}" rx="6" fill="#040d1a" stroke="#00e5ff" stroke-width="1" stroke-opacity="0.35"/>
    <text x="20" y="26" fill="#00e5ff" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="bold" letter-spacing="1.5">// KINETIC ORB ARCHITECTURE</text>

    <!-- Central Projection Vector (Diagonal -35 deg) -->
    <line x1="{cx - 160}" y1="{cy + 100}" x2="{cx + 160}" y2="{cy - 100}" stroke="url(#axisGrad)" stroke-width="2"/>

    <!-- Exploded Rings along diagonal axis -->
    <!-- Layer 1: Left Detached Ring -->
    <ellipse cx="{cx - 65}" cy="{cy + 40}" rx="38" ry="75" transform="rotate(-30 {cx - 65} {cy + 40})"
             fill="none" stroke="#00e5ff" stroke-width="1.2" stroke-dasharray="14 6 4 6" stroke-opacity="0.6"/>

    <!-- Layer 2: Core Glowing Torus -->
    <ellipse cx="{cx}" cy="{cy}" rx="55" ry="110" transform="rotate(-30 {cx} {cy})"
             fill="none" stroke="#00e5ff" stroke-width="5" filter="url(#orbBloom)"/>
    
    <!-- Inner Concentric Reticle -->
    <ellipse cx="{cx}" cy="{cy}" rx="32" ry="64" transform="rotate(-30 {cx} {cy})"
             fill="rgba(0, 229, 255, 0.08)" stroke="#ffffff" stroke-width="1.5" stroke-opacity="0.8"/>

    <!-- Layer 3: Right Detached Ring -->
    <ellipse cx="{cx + 65}" cy="{cy - 40}" rx="38" ry="75" transform="rotate(-30 {cx + 65} {cy - 40})"
             fill="none" stroke="#38bdf8" stroke-width="1.2" stroke-dasharray="8 8" stroke-opacity="0.6"/>

    <!-- Center Monogram Label -->
    <text x="{cx}" y="{cy + 4}" fill="#ffffff" font-family="'JetBrains Mono', monospace" font-size="12" font-weight="bold" letter-spacing="2" text-anchor="middle">{label}</text>
    <text x="{cx}" y="{height - 20}" fill="#00e5ff" font-family="monospace" font-size="9" letter-spacing="1" text-anchor="middle">ISOMETRIC GYROSCOPE // DOCKED 3D KINETICS</text>
</svg>"""
        return svg

    def to_threejs_buffer_geometry_json(self, points: List[Point3D]) -> str:
        """
        Exports points to standard Three.js BufferGeometry JSON format.
        """
        positions = []
        colors = []
        for p in points:
            positions.extend([round(p.x, 2), round(p.y, 2), round(p.z, 2)])
            colors.extend([round(p.r, 2), round(p.g, 2), round(p.b, 2)])

        geom = {
            "metadata": {"version": 4.5, "type": "BufferGeometry", "generator": "JARVIS_Visual_Engine"},
            "data": {
                "attributes": {
                    "position": {
                        "itemSize": 3,
                        "type": "Float32Array",
                        "array": positions,
                    },
                    "color": {
                        "itemSize": 3,
                        "type": "Float32Array",
                        "array": colors,
                    },
                }
            },
        }
        return json.dumps(geom, indent=2)
