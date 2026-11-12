"""
3D Scene Understanding Engine (Capability 71)
Provides 3D triangle mesh representation, 4x4 homogeneous transformations,
AABB bounding boxes, surface area, volume integration, and Möller-Trumbore ray tracing.
"""

import math
from typing import Dict, List, Optional, Tuple, Union
import numpy as np


class Mesh3D:
    """Represents a 3D surface mesh composed of vertices and triangular faces."""

    def __init__(self, vertices: List[Tuple[float, float, float]], faces: List[Tuple[int, int, int]]):
        self.vertices = [tuple(float(c) for c in v) for v in vertices]
        self.faces = [tuple(int(idx) for idx in f) for f in faces]

    def num_vertices(self) -> int:
        return len(self.vertices)

    def num_faces(self) -> int:
        return len(self.faces)

    def compute_face_normals(self) -> List[Tuple[float, float, float]]:
        """Calculates normalized unit normal vector for each triangular face."""
        normals = []
        for i1, i2, i3 in self.faces:
            v1 = np.array(self.vertices[i1])
            v2 = np.array(self.vertices[i2])
            v3 = np.array(self.vertices[i3])
            edge1 = v2 - v1
            edge2 = v3 - v1
            n = np.cross(edge1, edge2)
            norm = np.linalg.norm(n)
            if norm > 1e-12:
                n = n / norm
            else:
                n = np.array([0.0, 0.0, 1.0])
            normals.append((float(n[0]), float(n[1]), float(n[2])))
        return normals

    def compute_aabb(self) -> Dict[str, Tuple[float, float, float]]:
        """Calculates Axis-Aligned Bounding Box (AABB) minimum, maximum, dimensions, and center."""
        if not self.vertices:
            return {"min": (0.0, 0.0, 0.0), "max": (0.0, 0.0, 0.0), "dimensions": (0.0, 0.0, 0.0), "center": (0.0, 0.0, 0.0)}

        arr = np.array(self.vertices)
        min_pt = np.min(arr, axis=0)
        max_pt = np.max(arr, axis=0)
        dims = max_pt - min_pt
        center = (min_pt + max_pt) / 2.0

        return {
            "min": (float(min_pt[0]), float(min_pt[1]), float(min_pt[2])),
            "max": (float(max_pt[0]), float(max_pt[1]), float(max_pt[2])),
            "dimensions": (float(dims[0]), float(dims[1]), float(dims[2])),
            "center": (float(center[0]), float(center[1]), float(center[2])),
        }

    def compute_surface_area(self) -> float:
        """Calculates total surface area of mesh by summing triangle areas."""
        total_area = 0.0
        for i1, i2, i3 in self.faces:
            v1 = np.array(self.vertices[i1])
            v2 = np.array(self.vertices[i2])
            v3 = np.array(self.vertices[i3])
            edge1 = v2 - v1
            edge2 = v3 - v1
            cross_prod = np.cross(edge1, edge2)
            tri_area = 0.5 * float(np.linalg.norm(cross_prod))
            total_area += tri_area
        return total_area

    def compute_enclosed_volume(self) -> float:
        """
        Calculates enclosed volume of a watertight 3D mesh using divergence theorem:
        V = 1/6 * sum(v1 . (v2 x v3))
        """
        vol = 0.0
        for i1, i2, i3 in self.faces:
            v1 = np.array(self.vertices[i1])
            v2 = np.array(self.vertices[i2])
            v3 = np.array(self.vertices[i3])
            vol += float(np.dot(v1, np.cross(v2, v3)))
        return abs(vol) / 6.0

    def apply_transform(self, matrix4x4: np.ndarray) -> "Mesh3D":
        """Transforms vertices by 4x4 affine matrix and returns new Mesh3D instance."""
        transformed = []
        for v in self.vertices:
            vec4 = np.array([v[0], v[1], v[2], 1.0])
            res = matrix4x4 @ vec4
            transformed.append((float(res[0]), float(res[1]), float(res[2])))
        return Mesh3D(transformed, self.faces)


class Transform3D:
    """4x4 Transformation Matrix Builder for 3D Geometry."""

    @staticmethod
    def identity() -> np.ndarray:
        return np.eye(4, dtype=float)

    @staticmethod
    def translation(dx: float, dy: float, dz: float) -> np.ndarray:
        m = np.eye(4, dtype=float)
        m[0, 3] = dx
        m[1, 3] = dy
        m[2, 3] = dz
        return m

    @staticmethod
    def scale(sx: float, sy: float, sz: float) -> np.ndarray:
        m = np.eye(4, dtype=float)
        m[0, 0] = sx
        m[1, 1] = sy
        m[2, 2] = sz
        return m

    @staticmethod
    def rotation_euler(roll_x_deg: float, pitch_y_deg: float, yaw_z_deg: float) -> np.ndarray:
        """Euler rotation matrix Z * Y * X in degrees."""
        rx = math.radians(roll_x_deg)
        ry = math.radians(pitch_y_deg)
        rz = math.radians(yaw_z_deg)

        mx = np.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, math.cos(rx), -math.sin(rx), 0.0],
            [0.0, math.sin(rx), math.cos(rx), 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])

        my = np.array([
            [math.cos(ry), 0.0, math.sin(ry), 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [-math.sin(ry), 0.0, math.cos(ry), 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])

        mz = np.array([
            [math.cos(rz), -math.sin(rz), 0.0, 0.0],
            [math.sin(rz), math.cos(rz), 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])

        return mz @ my @ mx


class RayTracer3D:
    """Möller-Trumbore ray-triangle intersection testing."""

    @staticmethod
    def ray_triangle_intersect(
        ray_origin: Tuple[float, float, float],
        ray_dir: Tuple[float, float, float],
        v0: Tuple[float, float, float],
        v1: Tuple[float, float, float],
        v2: Tuple[float, float, float],
    ) -> Optional[Dict[str, Any]]:
        """
        Fast Möller-Trumbore ray-triangle intersection test.
        Returns distance t, barycentric coordinates (u, v), and intersection point (x, y, z).
        """
        eps = 1e-7
        o = np.array(ray_origin, dtype=float)
        d = np.array(ray_dir, dtype=float)
        p0 = np.array(v0, dtype=float)
        p1 = np.array(v1, dtype=float)
        p2 = np.array(v2, dtype=float)

        edge1 = p1 - p0
        edge2 = p2 - p0
        h = np.cross(d, edge2)
        a = float(np.dot(edge1, h))

        if -eps < a < eps:
            return None  # Ray parallel to triangle

        f = 1.0 / a
        s = o - p0
        u = f * float(np.dot(s, h))
        if u < 0.0 or u > 1.0:
            return None

        q = np.cross(s, edge1)
        v = f * float(np.dot(d, q))
        if v < 0.0 or (u + v) > 1.0:
            return None

        t = f * float(np.dot(edge2, q))
        if t > eps:
            hit_pt = o + t * d
            return {
                "distance": float(t),
                "u": float(u),
                "v": float(v),
                "hit_point": (float(hit_pt[0]), float(hit_pt[1]), float(hit_pt[2])),
            }
        return None

    @staticmethod
    def ray_mesh_intersect(
        ray_origin: Tuple[float, float, float],
        ray_dir: Tuple[float, float, float],
        mesh: Mesh3D,
    ) -> Optional[Dict[str, Any]]:
        """Tests ray intersection across all mesh faces and returns closest hit."""
        closest_hit = None
        closest_dist = float("inf")

        for face_idx, (i0, i1, i2) in enumerate(mesh.faces):
            hit = RayTracer3D.ray_triangle_intersect(
                ray_origin,
                ray_dir,
                mesh.vertices[i0],
                mesh.vertices[i1],
                mesh.vertices[i2],
            )
            if hit and hit["distance"] < closest_dist:
                closest_dist = hit["distance"]
                closest_hit = dict(hit)
                closest_hit["face_index"] = face_idx

        return closest_hit
