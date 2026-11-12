"""
Capability 119: Camera Integration
Provides OpenCV / UVC webcam capture, RTSP video stream adapter,
real-time frame differencing motion detection, and synthetic frame fallback.
"""

import base64
import os
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Callable

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None


@dataclass
class CameraFrame:
    width: int
    height: int
    timestamp: float
    is_synthetic: bool = False
    jpeg_bytes: Optional[bytes] = None
    base64_jpeg: Optional[str] = None
    motion_score: float = 0.0
    motion_boxes: List[Tuple[int, int, int, int]] = field(default_factory=list)


class CameraManager:
    """Manages local webcam capture, RTSP IP camera streams, and motion tracking."""

    def __init__(
        self,
        device_index: int = 0,
        stream_url: Optional[str] = None,
        width: int = 640,
        height: int = 480,
        fps_target: int = 30,
        motion_threshold: float = 0.03
    ):
        self.device_index = device_index
        self.stream_url = stream_url
        self.target_width = width
        self.target_height = height
        self.fps_target = fps_target
        self.motion_threshold = motion_threshold

        self._cap = None
        self._is_opened = False
        self._last_frame_gray = None
        self._frame_count = 0
        self._last_fps_time = time.time()
        self._current_fps = 0.0
        self._motion_callbacks: List[Callable[[CameraFrame], None]] = []

    def open_stream(self) -> bool:
        """Initializes OpenCV capture device or RTSP URL stream."""
        if not cv2:
            self._is_opened = False
            return False

        try:
            source = self.stream_url if self.stream_url else self.device_index
            self._cap = cv2.VideoCapture(source)
            if self._cap and self._cap.isOpened():
                self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_width)
                self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_height)
                self._is_opened = True
                return True
        except Exception:
            pass

        self._is_opened = False
        return False

    def close_stream(self):
        """Releases OpenCV video capture handle."""
        if self._cap:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None
        self._is_opened = False
        self._last_frame_gray = None

    def is_stream_active(self) -> bool:
        return self._is_opened and (self._cap is not None) and self._cap.isOpened()

    def add_motion_callback(self, callback: Callable[[CameraFrame], None]):
        """Registers a callback invoked when motion exceeding threshold is detected."""
        self._motion_callbacks.append(callback)

    def _generate_synthetic_frame(self, motion_sim: bool = False) -> Tuple[Any, bytes]:
        """
        Generates high-resolution synthetic test HUD frame when physical webcam
        or RTSP source is unavailable.
        """
        w, h = self.target_width, self.target_height
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")

        if np is not None and cv2 is not None:
            # Create dark obsidian backdrop (#02060c)
            img = np.zeros((h, w, 3), dtype=np.uint8)
            img[:] = (12, 6, 2)  # BGR

            # Draw cyan CAD grid lines
            grid_step = 40
            for x in range(0, w, grid_step):
                cv2.line(img, (x, 0), (x, h), (40, 30, 10), 1)
            for y in range(0, h, grid_step):
                cv2.line(img, (0, y), (w, y), (40, 30, 10), 1)

            # Central reticle / crosshair
            cx, cy = w // 2, h // 2
            cv2.circle(img, (cx, cy), 35, (255, 240, 0), 1)  # Cyan circle
            cv2.line(img, (cx - 50, cy), (cx + 50, cy), (255, 240, 0), 1)
            cv2.line(img, (cx, cy - 50), (cx, cy + 50), (255, 240, 0), 1)

            # Simulated moving object for motion verification
            if motion_sim:
                offset = int(math_sin := (time.time() * 3) % w)
                cv2.rectangle(img, (offset % (w - 60), cy - 25), (offset % (w - 60) + 50, cy + 25), (0, 255, 128), -1)

            # HUD text overlay
            cv2.putText(img, "J.A.R.V.I.S. OPTICAL FEED", (18, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 240, 0), 1)
            cv2.putText(img, f"STREAM: {'RTSP' if self.stream_url else 'UVC-0'}", (18, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)
            cv2.putText(img, f"TIME: {now_str}", (18, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 220, 255), 1)
            cv2.putText(img, f"{w}x{h} @ {self.fps_target}FPS", (w - 160, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)

            _, buf = cv2.imencode(".jpg", img)
            jpeg_bytes = buf.tobytes()
            return img, jpeg_bytes

        # Fallback minimal mock JPEG header
        mock_bytes = b"EXIF_SYNTHETIC_FRAME_J_A_R_V_I_S_" + now_str.encode("utf-8")
        return None, mock_bytes

    def capture_frame(self, simulate_motion: bool = False) -> CameraFrame:
        """
        Captures a single frame, executes motion analysis, and produces
        base64 JPEG payload.
        """
        timestamp = time.time()
        self._frame_count += 1

        # Track FPS
        dt = timestamp - self._last_fps_time
        if dt >= 1.0:
            self._current_fps = round(self._frame_count / dt, 1)
            self._frame_count = 0
            self._last_fps_time = timestamp

        raw_frame = None
        is_synthetic = False

        if self.is_stream_active():
            ret, frame = self._cap.read()
            if ret and frame is not None:
                raw_frame = frame
            else:
                raw_frame, jpeg_bytes = self._generate_synthetic_frame(motion_sim=simulate_motion)
                is_synthetic = True
        else:
            raw_frame, jpeg_bytes = self._generate_synthetic_frame(motion_sim=simulate_motion)
            is_synthetic = True

        motion_score = 0.0
        motion_boxes = []

        # Motion detection via frame differencing
        if cv2 is not None and np is not None and raw_frame is not None:
            gray = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            if self._last_frame_gray is not None:
                frame_delta = cv2.absdiff(self._last_frame_gray, gray)
                thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)

                non_zero = cv2.countNonZero(thresh)
                total_pixels = self.target_width * self.target_height
                motion_score = round(non_zero / float(total_pixels), 4)

                contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for c in contours:
                    if cv2.contourArea(c) > 400:
                        (x, y, bw, bh) = cv2.boundingRect(c)
                        motion_boxes.append((int(x), int(y), int(bw), int(bh)))

            self._last_frame_gray = gray

            _, buf = cv2.imencode(".jpg", raw_frame)
            jpeg_bytes = buf.tobytes()

        b64_str = base64.b64encode(jpeg_bytes).decode("ascii") if jpeg_bytes else ""

        frame_obj = CameraFrame(
            width=self.target_width,
            height=self.target_height,
            timestamp=timestamp,
            is_synthetic=is_synthetic,
            jpeg_bytes=jpeg_bytes,
            base64_jpeg=b64_str,
            motion_score=motion_score,
            motion_boxes=motion_boxes
        )

        if motion_score >= self.motion_threshold:
            for cb in self._motion_callbacks:
                try:
                    cb(frame_obj)
                except Exception:
                    pass

        return frame_obj

    def save_snapshot(self, output_path: str) -> bool:
        """Captures a snapshot and writes it to disk."""
        frame = self.capture_frame()
        if not frame.jpeg_bytes:
            return False

        try:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(frame.jpeg_bytes)
            return True
        except Exception:
            return False

    def get_status(self) -> Dict[str, Any]:
        """Returns camera health, stream settings, and runtime FPS."""
        return {
            "source": self.stream_url if self.stream_url else f"device_{self.device_index}",
            "is_open": self._is_opened,
            "resolution": f"{self.target_width}x{self.target_height}",
            "target_fps": self.fps_target,
            "current_fps": self._current_fps,
            "motion_threshold": self.motion_threshold,
            "opencv_available": cv2 is not None,
        }
