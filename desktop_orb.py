"""
J.A.R.V.I.S. Desktop Floating AssistiveTouch Orb Companion
Runs as an always-on-top, frameless, transparent floating widget anywhere on the Windows desktop.
Draggable anywhere across multiple monitors, just like iOS AssistiveTouch.
"""
import sys
import os
import math
import time
import json
import threading
import urllib.request
import tkinter as tk

SERVER_URL = "http://localhost:4700"


class DesktopAssistiveOrb:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("J.A.R.V.I.S. AssistiveTouch")
        self.root.geometry("200x240+100+100")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)

        # Transparent background color key
        self.trans_color = "#030712"
        self.root.configure(bg=self.trans_color)
        try:
            self.root.wm_attributes("-transparentcolor", self.trans_color)
        except Exception:
            pass

        self.canvas = tk.Canvas(
            self.root,
            width=200,
            height=200,
            bg=self.trans_color,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Status badge below orb
        self.status_label = tk.Label(
            self.root,
            text="✦ JARVIS ONLINE",
            font=("Consolas", 8, "bold"),
            fg="#00e5ff",
            bg=self.trans_color
        )
        self.status_label.pack(side=tk.BOTTOM, pady=2)

        # Drag state
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._has_moved = False

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.status_label.bind("<Button-1>", lambda e: self.toggle_brain())

        # Close on right click
        self.canvas.bind("<Button-3>", lambda e: self.show_context_menu(e))

        # Animation state
        self.angle = 0
        self.state = "idle"  # idle, listening, thinking, speaking
        self.current_brain = "gemini-3.5"
        self.running = True

        self.animate()

    def on_press(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self._has_moved = False

    def on_drag(self, event):
        dx = event.x - self._drag_start_x
        dy = event.y - self._drag_start_y
        if math.hypot(dx, dy) > 3:
            self._has_moved = True
            new_x = self.root.winfo_x() + dx
            new_y = self.root.winfo_y() + dy
            self.root.geometry(f"+{new_x}+{new_y}")

    def on_release(self, event):
        if not self._has_moved:
            # Clicked without dragging: toggle voice listening or open quick prompt
            self.quick_interact()

    def quick_interact(self):
        self.state = "listening"
        self.status_label.config(text="● LISTENING...", fg="#00ffff")
        # In a real environment, trigger voice transcription or quick chat
        threading.Thread(target=self._query_jarvis, daemon=True).start()

    def toggle_brain(self):
        if self.current_brain == "gemini-3.5":
            self.current_brain = "gemini-live"
            self.status_label.config(text="⚡ GEMINI LIVE", fg="#00ffff")
        else:
            self.current_brain = "gemini-3.5"
            self.status_label.config(text="✦ GEMINI 3.5", fg="#00e5ff")

    def _query_jarvis(self):
        time.sleep(1.5)
        self.state = "thinking"
        self.status_label.config(text="◌ REASONING...", fg="#38bdf8")
        try:
            req = urllib.request.Request(
                f"{SERVER_URL}/chat",
                data=json.dumps({"question": "Status report, sir.", "brain": self.current_brain}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                self.state = "speaking"
                ans = data.get("answer", "Systems operational.")
                self.status_label.config(text=f"✦ {ans[:24]}...", fg="#22d3ee")
                time.sleep(3.5)
        except Exception as e:
            self.state = "idle"
            self.status_label.config(text="✦ JARVIS ONLINE", fg="#00e5ff")

        self.state = "idle"
        self.status_label.config(text="✦ JARVIS ONLINE", fg="#00e5ff")

    def show_context_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0, bg="#080e1a", fg="#00e5ff")
        menu.add_command(label="Toggle Brain (Gemini 3.5 / Live)", command=self.toggle_brain)
        menu.add_command(label="Open Web Knowledge Galaxy", command=lambda: os.system("start http://localhost:4700"))
        menu.add_separator()
        menu.add_command(label="Close AssistiveTouch Orb", command=self.root.destroy)
        menu.tk_popup(event.x_root, event.y_root)

    def animate(self):
        if not self.running:
            return

        self.canvas.delete("all")
        cx, cy = 100, 100
        self.angle = (self.angle + 0.04) % (2 * math.pi)

        colors = {
            "idle": ("#00e5ff", "#00838f"),
            "listening": ("#00ffff", "#0288d1"),
            "thinking": ("#38bdf8", "#6366f1"),
            "speaking": ("#22d3ee", "#06b6d4")
        }.get(self.state, ("#00e5ff", "#00838f"))

        # Outer ring
        r_outer = 68
        self.canvas.create_oval(cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer, outline=colors[1], width=2)

        # Rotating dashed segments
        for i in range(12):
            seg_a = self.angle + i * (math.pi / 6)
            x1 = cx + (r_outer - 5) * math.cos(seg_a)
            y1 = cy + (r_outer - 5) * math.sin(seg_a)
            x2 = cx + (r_outer + 3) * math.cos(seg_a)
            y2 = cy + (r_outer + 3) * math.sin(seg_a)
            self.canvas.create_line(x1, y1, x2, y2, fill=colors[0], width=2)

        # Inner ring
        r_inner = 44
        self.canvas.create_oval(cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner, outline=colors[0], width=1)

        # Core glowing orb
        pulse = 22 + 4 * math.sin(self.angle * 2)
        self.canvas.create_oval(cx - pulse, cy - pulse, cx + pulse, cy + pulse, fill=colors[1], outline=colors[0], width=2)
        self.canvas.create_text(cx, cy, text="J.A.R.V.I.S.", font=("Consolas", 8, "bold"), fill="#ffffff")

        self.root.after(33, self.animate)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = DesktopAssistiveOrb()
    app.run()
