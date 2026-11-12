"""
CAD Assistance Engine (Capability 65)
Provides AutoCAD DXF R12 generator, ASCII & Binary 3D STL mesh generators,
and Technical SVG Orthographic Wireframe generators with engineering dimensions and title blocks.
"""

import math
import struct
from typing import Dict, List, Optional, Tuple, Union
import numpy as np


class DXFGenerator:
    """Generates standard AutoCAD ASCII DXF (Release 12) CAD files."""

    def __init__(self, filename: str = "drawing.dxf"):
        self.filename = filename
        self.entities: List[str] = []
        self.layers: Dict[str, int] = {"0": 7}  # name -> AutoCAD color index (7 = white/black)

    def add_layer(self, name: str, color_index: int = 7) -> None:
        self.layers[name] = color_index

    def add_line(self, x1: float, y1: float, x2: float, y2: float, z1: float = 0.0, z2: float = 0.0, layer: str = "0") -> None:
        """Adds a 3D/2D line entity."""
        block = [
            "0\nLINE",
            f"8\n{layer}",
            f"10\n{x1:.4f}",
            f"20\n{y1:.4f}",
            f"30\n{z1:.4f}",
            f"11\n{x2:.4f}",
            f"21\n{y2:.4f}",
            f"31\n{z2:.4f}",
        ]
        self.entities.append("\n".join(block))

    def add_circle(self, cx: float, cy: float, radius: float, cz: float = 0.0, layer: str = "0") -> None:
        """Adds a circle entity."""
        block = [
            "0\nCIRCLE",
            f"8\n{layer}",
            f"10\n{cx:.4f}",
            f"20\n{cy:.4f}",
            f"30\n{cz:.4f}",
            f"40\n{radius:.4f}",
        ]
        self.entities.append("\n".join(block))

    def add_arc(self, cx: float, cy: float, radius: float, start_deg: float, end_deg: float, layer: str = "0") -> None:
        """Adds an arc entity."""
        block = [
            "0\nARC",
            f"8\n{layer}",
            f"10\n{cx:.4f}",
            f"20\n{cy:.4f}",
            f"30\n0.0",
            f"40\n{radius:.4f}",
            f"50\n{start_deg:.4f}",
            f"51\n{end_deg:.4f}",
        ]
        self.entities.append("\n".join(block))

    def add_text(self, text: str, x: float, y: float, height: float = 2.5, layer: str = "0") -> None:
        """Adds single-line text entity."""
        block = [
            "0\nTEXT",
            f"8\n{layer}",
            f"10\n{x:.4f}",
            f"20\n{y:.4f}",
            f"30\n0.0",
            f"40\n{height:.4f}",
            f"1\n{text}",
        ]
        self.entities.append("\n".join(block))

    def generate_dxf_string(self) -> str:
        """Builds complete DXF string with HEADER, TABLES, and ENTITIES sections."""
        lines = [
            "0\nSECTION",
            "2\nHEADER",
            "0\nENDSEC",
            "0\nSECTION",
            "2\nTABLES",
            "0\nTABLE",
            "2\nLAYER",
            f"70\n{len(self.layers)}",
        ]
        for name, col in self.layers.items():
            lines.extend([
                "0\nLAYER",
                f"2\n{name}",
                "70\n0",
                f"62\n{col}",
                "6\nCONTINUOUS",
            ])
        lines.extend([
            "0\nENDTAB",
            "0\nENDSEC",
            "0\nSECTION",
            "2\nENTITIES",
        ])
        lines.extend(self.entities)
        lines.extend([
            "0\nENDSEC",
            "0\nEOF",
            "",
        ])
        return "\n".join(lines)

    def save(self, filepath: str) -> None:
        content = self.generate_dxf_string()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)


class STLGenerator:
    """Generates standard ASCII and Binary 3D STL mesh files."""

    @staticmethod
    def _compute_normal(v1: Tuple[float, float, float], v2: Tuple[float, float, float], v3: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Calculates normalized outward unit normal vector for triangle (v1, v2, v3)."""
        ax, ay, az = v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2]
        bx, by, bz = v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2]
        nx = ay * bz - az * by
        ny = az * bx - ax * bz
        nz = ax * by - ay * bx
        norm = math.sqrt(nx * nx + ny * ny + nz * nz)
        if norm > 1e-12:
            return (nx / norm, ny / norm, nz / norm)
        return (0.0, 0.0, 1.0)

    @staticmethod
    def create_box_facets(width: float, height: float, depth: float) -> List[Tuple[Tuple[float, float, float], Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]]]:
        """
        Creates 12 triangular facets for an axis-aligned box centered at origin.
        Returns list of (normal, (v1, v2, v3)).
        """
        hx, hy, hz = width / 2.0, height / 2.0, depth / 2.0

        # 8 corners
        v = [
            (-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
            (-hx, -hy, hz),  (hx, -hy, hz),  (hx, hy, hz),  (-hx, hy, hz),
        ]

        # 6 faces * 2 triangles = 12 facets
        face_indices = [
            # Front (+z)
            (4, 5, 6), (4, 6, 7),
            # Back (-z)
            (1, 0, 3), (1, 3, 2),
            # Top (+y)
            (3, 6, 2), (3, 7, 6),
            # Bottom (-y)
            (0, 1, 5), (0, 5, 4),
            # Right (+x)
            (1, 2, 6), (1, 6, 5),
            # Left (-x)
            (0, 4, 7), (0, 7, 3),
        ]

        facets = []
        for i1, i2, i3 in face_indices:
            p1, p2, p3 = v[i1], v[i2], v[i3]
            norm = STLGenerator._compute_normal(p1, p2, p3)
            facets.append((norm, (p1, p2, p3)))

        return facets

    @staticmethod
    def create_cylinder_facets(radius: float, height: float, segments: int = 16) -> List[Tuple[Tuple[float, float, float], Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]]]:
        """Creates cylinder facets with top/bottom disc and side walls."""
        facets = []
        hz = height / 2.0
        angle_step = (2.0 * math.pi) / segments

        # Side walls & caps
        for i in range(segments):
            a1 = i * angle_step
            a2 = (i + 1) * angle_step

            x1, y1 = radius * math.cos(a1), radius * math.sin(a1)
            x2, y2 = radius * math.cos(a2), radius * math.sin(a2)

            # Top cap triangle (0, 0, hz), (x1, y1, hz), (x2, y2, hz)
            top_center = (0.0, 0.0, hz)
            p1_top = (x1, y1, hz)
            p2_top = (x2, y2, hz)
            facets.append((STLGenerator._compute_normal(top_center, p1_top, p2_top), (top_center, p1_top, p2_top)))

            # Bottom cap triangle (0, 0, -hz), (x2, y2, -hz), (x1, y1, -hz)
            bot_center = (0.0, 0.0, -hz)
            p1_bot = (x1, y1, -hz)
            p2_bot = (x2, y2, -hz)
            facets.append((STLGenerator._compute_normal(bot_center, p2_bot, p1_bot), (bot_center, p2_bot, p1_bot)))

            # Side quad split into 2 triangles
            t1 = ((x1, y1, -hz), (x2, y2, -hz), (x2, y2, hz))
            t2 = ((x1, y1, -hz), (x2, y2, hz), (x1, y1, hz))
            facets.append((STLGenerator._compute_normal(t1[0], t1[1], t1[2]), t1))
            facets.append((STLGenerator._compute_normal(t2[0], t2[1], t2[2]), t2))

        return facets

    @staticmethod
    def to_ascii_stl(solid_name: str, facets: List[Tuple[Tuple[float, float, float], Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]]]) -> str:
        """Converts facets into standard ASCII STL formatted text."""
        lines = [f"solid {solid_name}"]
        for norm, (v1, v2, v3) in facets:
            lines.append(f"  facet normal {norm[0]:.6e} {norm[1]:.6e} {norm[2]:.6e}")
            lines.append("    outer loop")
            lines.append(f"      vertex {v1[0]:.6e} {v1[1]:.6e} {v1[2]:.6e}")
            lines.append(f"      vertex {v2[0]:.6e} {v2[1]:.6e} {v2[2]:.6e}")
            lines.append(f"      vertex {v3[0]:.6e} {v3[1]:.6e} {v3[2]:.6e}")
            lines.append("    endloop")
            lines.append("  endfacet")
        lines.append(f"endsolid {solid_name}\n")
        return "\n".join(lines)

    @staticmethod
    def to_binary_stl(facets: List[Tuple[Tuple[float, float, float], Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]]]) -> bytes:
        """Converts facets into standard 80-byte header Binary STL bytes."""
        header = b"J.A.R.V.I.S. CAD Engine Binary STL Generator" + b"\x00" * (80 - 44)
        buf = bytearray(header)
        buf.extend(struct.pack("<I", len(facets)))
        for norm, (v1, v2, v3) in facets:
            # 50 bytes: normal (3 float32), 3 vertices (9 float32), 1 uint16 attribute
            buf.extend(struct.pack("<3f", *norm))
            buf.extend(struct.pack("<3f", *v1))
            buf.extend(struct.pack("<3f", *v2))
            buf.extend(struct.pack("<3f", *v3))
            buf.extend(struct.pack("<H", 0))
        return bytes(buf)


class SVGTechnicalDrawer:
    """Generates technical blueprint SVGs with orthographic views and dimension callouts."""

    def __init__(self, width: int = 800, height: int = 600, title: str = "PART 01 - TECHNICAL BLUEPRINT"):
        self.width = width
        self.height = height
        self.title = title
        self.elements: List[str] = []

    def add_rect(self, x: float, y: float, w: float, h: float, stroke: str = "#00e5ff", fill: str = "none", stroke_width: float = 1.5) -> None:
        self.elements.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" stroke="{stroke}" fill="{fill}" stroke-width="{stroke_width}"/>'
        )

    def add_line(self, x1: float, y1: float, x2: float, y2: float, stroke: str = "#00e5ff", stroke_width: float = 1.5, dashed: bool = False) -> None:
        dash_attr = ' stroke-dasharray="4,4"' if dashed else ""
        self.elements.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{stroke_width}"{dash_attr}/>'
        )

    def add_circle(self, cx: float, cy: float, r: float, stroke: str = "#00e5ff", fill: str = "none", stroke_width: float = 1.5) -> None:
        self.elements.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke="{stroke}" fill="{fill}" stroke-width="{stroke_width}"/>'
        )

    def add_dimension_h(self, x1: float, x2: float, y: float, label: str, offset: float = 15.0) -> None:
        """Adds horizontal dimension line with extension lines, arrows, and measurement text."""
        dim_y = y - offset
        # Extension lines
        self.add_line(x1, y - 2, x1, dim_y - 4, stroke="rgba(0,229,255,0.5)", stroke_width=1.0)
        self.add_line(x2, y - 2, x2, dim_y - 4, stroke="rgba(0,229,255,0.5)", stroke_width=1.0)
        # Main dimension line
        self.add_line(x1, dim_y, x2, dim_y, stroke="#00e5ff", stroke_width=1.2)
        # Dimension text
        mid_x = (x1 + x2) / 2.0
        self.elements.append(
            f'<text x="{mid_x}" y="{dim_y - 4}" fill="#00e5ff" font-family="monospace" font-size="11" text-anchor="middle">{label}</text>'
        )

    def add_text(self, text: str, x: float, y: float, font_size: int = 12, color: str = "#00e5ff") -> None:
        self.elements.append(
            f'<text x="{x}" y="{y}" fill="{color}" font-family="monospace" font-size="{font_size}">{text}</text>'
        )

    def render(self) -> str:
        """Renders complete SVG document with grid background and blueprint frame."""
        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" width="{self.width}" height="{self.height}">',
            '  <defs>',
            '    <pattern id="cadGrid" width="20" height="20" patternUnits="userSpaceOnUse">',
            '      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(0,229,255,0.08)" stroke-width="0.8"/>',
            '    </pattern>',
            '  </defs>',
            '  <!-- Background -->',
            f'  <rect width="{self.width}" height="{self.height}" fill="#050b14"/>',
            f'  <rect width="{self.width}" height="{self.height}" fill="url(#cadGrid)"/>',
            '  <!-- Border Frame -->',
            f'  <rect x="20" y="20" width="{self.width - 40}" height="{self.height - 40}" fill="none" stroke="rgba(0,229,255,0.4)" stroke-width="1.5"/>',
            '  <!-- Title Block -->',
            f'  <rect x="{self.width - 240}" y="{self.height - 70}" width="220" height="50" fill="rgba(6,16,30,0.85)" stroke="#00e5ff" stroke-width="1.2"/>',
            f'  <text x="{self.width - 230}" y="{self.height - 50}" fill="#00e5ff" font-family="monospace" font-size="10" font-weight="bold">{self.title}</text>',
            f'  <text x="{self.width - 230}" y="{self.height - 32}" fill="rgba(0,229,255,0.7)" font-family="monospace" font-size="9">SCALE: 1:1 | SYSTEM: J.A.R.V.I.S. CAD</text>',
            '  <!-- Entities -->',
        ]
        svg.extend(["  " + el for el in self.elements])
        svg.append("</svg>")
        return "\n".join(svg)
