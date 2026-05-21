#!/usr/bin/env python3
"""
Claude Code Usage Widget
Floating always-on-top overlay showing session (5h) and weekly (7d) utilization,
with pixel-art Clawd animations that react to your usage rate.
"""

import json
import random
import re
import sys
import threading
import time
from pathlib import Path

import httpx
import pystray
from PIL import Image, ImageDraw, ImageFont, ImageTk
import tkinter as tk

# ── Config ────────────────────────────────────────────────────────────────────

SCRIPT_DIR       = Path(__file__).parent
CREDENTIALS_PATH = Path.home() / ".claude" / ".credentials.json"
POSITION_FILE    = Path.home() / ".config" / "claude-widget" / "position.json"
ANIM_DIR         = SCRIPT_DIR.parent / "tools" / "claudepix_data"

API_URL     = "https://api.anthropic.com/v1/messages"
API_HEADERS = {
    "anthropic-version": "2023-06-01",
    "anthropic-beta":    "oauth-2025-04-20",
    "Content-Type":      "application/json",
    "User-Agent":        "claude-code/2.1.5",
}
API_BODY = {
    "model":      "claude-haiku-4-5-20251001",
    "max_tokens": 1,
    "messages":   [{"role": "user", "content": "hi"}],
}

POLL_INTERVAL  = 60    # seconds between API polls
ANIM_ROTATE_S  = 20    # seconds before auto-rotating to next animation in group

CELL = 4               # px per 20×20 grid cell → 80×80 px animation

# Mood groups mirror the firmware's splash grouping
MOOD_GROUPS = {
    "idle":  ["idle_blink", "idle_breathe", "idle_look_around"],
    "work":  ["work_coding", "work_think"],
    "dance": ["dance_bounce", "dance_sway", "dance_djmix",
              "dance_bounce_dj", "dance_sway_dj"],
}

# ── Palette ───────────────────────────────────────────────────────────────────

BG     = "#1a1a1a"
BORDER = "#2e2e2e"
TEXT   = "#e2e2e2"
DIM    = "#666666"
BAR_BG = "#2a2a2a"
GREEN  = "#4ade80"
AMBER  = "#fbbf24"
RED    = "#f87171"
ACCENT = "#d97757"

ANIM_BG = "#111111"   # slightly darker well for the animation panel

W, H = 258, 258

# ── Credential & API helpers ──────────────────────────────────────────────────

def _extract_token(blob: str) -> str | None:
    blob = blob.strip()
    if not blob:
        return None
    try:
        data = json.loads(blob)
    except json.JSONDecodeError:
        data = None
    if isinstance(data, dict):
        if isinstance(data.get("accessToken"), str):
            return data["accessToken"]
        for v in data.values():
            if isinstance(v, dict) and isinstance(v.get("accessToken"), str):
                return v["accessToken"]
    m = re.search(r'"accessToken"\s*:\s*"([^"]+)"', blob)
    return m.group(1) if m else None


def read_token() -> str | None:
    try:
        return _extract_token(CREDENTIALS_PATH.read_text())
    except OSError:
        return None


def fetch_usage() -> dict:
    token = read_token()
    if not token:
        return {"error": "Credenciais não encontradas.\nAbra o Claude Code para entrar."}

    headers = {**API_HEADERS, "Authorization": f"Bearer {token}"}
    try:
        with httpx.Client(timeout=20.0) as http:
            resp = http.post(API_URL, headers=headers, json=API_BODY)
    except httpx.HTTPError as exc:
        return {"error": f"Erro de rede:\n{exc}"}

    if resp.status_code >= 400:
        return {"error": f"API retornou {resp.status_code}"}

    now = time.time()

    def hdr(name, default="0"):
        return resp.headers.get(name, default)

    def reset_min(ts):
        try:
            r = float(ts)
        except ValueError:
            return 0
        m = (r - now) / 60.0
        return int(round(m)) if m > 0 else 0

    def pct(util):
        try:
            return min(100, int(round(float(util) * 100)))
        except ValueError:
            return 0

    return {
        "session_pct":   pct(hdr("anthropic-ratelimit-unified-5h-utilization")),
        "session_reset": reset_min(hdr("anthropic-ratelimit-unified-5h-reset")),
        "weekly_pct":    pct(hdr("anthropic-ratelimit-unified-7d-utilization")),
        "weekly_reset":  reset_min(hdr("anthropic-ratelimit-unified-7d-reset")),
        "status":        hdr("anthropic-ratelimit-unified-5h-status", "ok"),
    }


def bar_color(pct: int) -> str:
    if pct >= 90:
        return RED
    if pct >= 70:
        return AMBER
    return GREEN


def fmt_reset(minutes: int) -> str:
    if minutes <= 0:
        return "reiniciando…"
    if minutes < 60:
        return f"reinicia em {minutes}m"
    h, m = divmod(minutes, 60)
    if h < 24:
        return (f"reinicia em {h}h {m}m" if m else f"reinicia em {h}h")
    d, h = divmod(h, 24)
    return (f"reinicia em {d}d {h}h" if h else f"reinicia em {d}d")


def pct_to_mood(pct: int) -> str:
    if pct >= 70:
        return "dance"
    if pct >= 40:
        return "work"
    return "idle"


# ── Widget ────────────────────────────────────────────────────────────────────

class ClaudeWidget:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Consumo do Claudinho")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.93)
        self.root.configure(bg=BORDER)

        sx = self.root.winfo_screenwidth()
        sy = self.root.winfo_screenheight()
        pos = self._load_position()
        x = pos.get("x", sx - W - 20)
        y = pos.get("y", sy - H - 60)
        self.root.geometry(f"{W}x{H}+{x}+{y}")

        # Animation state
        self._anims: dict = {}
        self._current_anim: str = ""
        self._current_mood: str = "idle"
        self._anim_frame: int = 0
        self._anim_after: str | None = None
        self._rotate_after: str | None = None
        self._anim_photo = None   # keep reference to prevent GC

        self._tray: pystray.Icon | None = None

        self._load_animations()
        self._build_ui()
        self._apply_win11_corners()
        self._start_poller()
        self._build_tray()
        self._start_animation_for_mood("idle")

        self.root.protocol("WM_DELETE_WINDOW", self._hide_to_tray)

    # ── Position persistence ──────────────────────────────────────────────────

    def _load_position(self) -> dict:
        try:
            return json.loads(POSITION_FILE.read_text())
        except (OSError, json.JSONDecodeError):
            return {}

    def _save_position(self):
        POSITION_FILE.parent.mkdir(parents=True, exist_ok=True)
        POSITION_FILE.write_text(
            json.dumps({"x": self.root.winfo_x(), "y": self.root.winfo_y()})
        )

    # ── Windows 11 rounded corners ────────────────────────────────────────────

    def _apply_win11_corners(self):
        try:
            import ctypes
            hwnd = self.root.winfo_id()

            # Rounded corners
            pref = ctypes.c_int(2)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 33, ctypes.byref(pref), ctypes.sizeof(pref)
            )

            # Set window icon via WM_SETICON so it shows correctly in alt+tab
            ico = SCRIPT_DIR / "claudinho.ico"
            if ico.exists():
                hicon = ctypes.windll.user32.LoadImageW(
                    None, str(ico), 1, 0, 0, 0x10 | 0x40
                )   # IMAGE_ICON | LR_LOADFROMFILE | LR_DEFAULTSIZE
                if hicon:
                    WM_SETICON = 0x0080
                    ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 1, hicon)  # big
                    ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 0, hicon)  # small
        except Exception:
            pass

    # ── Animation loading & rendering ─────────────────────────────────────────

    def _load_animations(self):
        if not ANIM_DIR.exists():
            return
        for path in ANIM_DIR.glob("*.json"):
            try:
                self._anims[path.stem] = json.loads(path.read_text())
            except Exception:
                pass

    def _render_frame(self, anim_name: str, frame_idx: int) -> Image.Image:
        data   = self._anims[anim_name]
        palette = data["palette"]
        grid   = data["frames"][frame_idx]["grid"]
        size   = len(grid)
        dim    = size * CELL

        img = Image.new("RGB", (dim, dim), ANIM_BG)
        d   = ImageDraw.Draw(img)

        for y, row in enumerate(grid):
            for x, idx in enumerate(row):
                color = palette[idx]
                if color == "transparent":
                    continue
                d.rectangle(
                    [x * CELL, y * CELL, (x + 1) * CELL - 1, (y + 1) * CELL - 1],
                    fill=color,
                )
        return img

    def _tick_animation(self):
        if not self._current_anim or self._current_anim not in self._anims:
            return
        data   = self._anims[self._current_anim]
        frames = data["frames"]
        idx    = self._anim_frame % len(frames)

        img   = self._render_frame(self._current_anim, idx)
        photo = ImageTk.PhotoImage(img)
        self._anim_label.configure(image=photo)
        self._anim_photo = photo   # prevent GC

        hold = frames[idx].get("hold", 100)
        self._anim_frame += 1
        self._anim_after = self.root.after(hold, self._tick_animation)

    def _start_animation_for_mood(self, mood: str):
        # Cancel running animation and rotation timer
        if self._anim_after:
            self.root.after_cancel(self._anim_after)
            self._anim_after = None
        if self._rotate_after:
            self.root.after_cancel(self._rotate_after)
            self._rotate_after = None

        self._current_mood = mood
        candidates = [
            n for n in MOOD_GROUPS.get(mood, []) if n in self._anims
        ]
        if not candidates:
            # Fallback: any available animation
            candidates = list(self._anims.keys())
        if not candidates:
            return

        self._current_anim = random.choice(candidates)
        self._anim_frame   = 0
        self._tick_animation()

        # Auto-rotate to the next animation in the group after ANIM_ROTATE_S
        self._rotate_after = self.root.after(
            ANIM_ROTATE_S * 1000, self._rotate_animation
        )

    def _rotate_animation(self):
        self._start_animation_for_mood(self._current_mood)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        inner = tk.Frame(self.root, bg=BG)
        inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # ── Title bar ─────────────────────────────────────────────────────
        bar = tk.Frame(inner, bg=BG, height=30)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        dot = tk.Label(bar, text="●", bg=BG, fg=ACCENT, font=("Segoe UI", 9))
        dot.pack(side=tk.LEFT, padx=(10, 4))

        title = tk.Label(bar, text="Consumo do Claudinho", bg=BG, fg=TEXT,
                         font=("Segoe UI", 9, "bold"))
        title.pack(side=tk.LEFT)

        self._lbl_ts = tk.Label(bar, text="", bg=BG, fg=DIM, font=("Segoe UI", 7))
        self._lbl_ts.pack(side=tk.RIGHT, padx=(0, 6))

        # Hide button — bound AFTER drag loop so it keeps its binding
        btn_hide = tk.Label(bar, text="–", bg=BG, fg=DIM,
                            font=("Segoe UI", 12), cursor="hand2")
        btn_hide.pack(side=tk.RIGHT, padx=(0, 2))

        # Drag only on the bar background and non-interactive labels
        for w in (bar, dot, title):
            w.bind("<Button-1>",       self._drag_start)
            w.bind("<B1-Motion>",      self._drag_move)
            w.bind("<ButtonRelease-1>", lambda _: self._save_position())

        # Bind hide button after drag loop so it isn't overwritten
        btn_hide.bind("<Button-1>", lambda _: self._hide_to_tray())

        # ── Divider ───────────────────────────────────────────────────────
        tk.Frame(inner, bg=BORDER, height=1).pack(fill=tk.X)

        # ── Animation panel ───────────────────────────────────────────────
        anim_size = 20 * CELL   # 80 px
        anim_panel = tk.Frame(inner, bg=ANIM_BG,
                              height=anim_size + 16, width=W - 2)
        anim_panel.pack(fill=tk.X)
        anim_panel.pack_propagate(False)

        self._anim_label = tk.Label(anim_panel, bg=ANIM_BG, bd=0)
        self._anim_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # ── Divider ───────────────────────────────────────────────────────
        tk.Frame(inner, bg=BORDER, height=1).pack(fill=tk.X)

        # ── Metrics ───────────────────────────────────────────────────────
        content = tk.Frame(inner, bg=BG)
        content.pack(fill=tk.BOTH, expand=True, padx=14, pady=(10, 12))

        self._blk_session = self._metric_block(content, "SESSÃO · 5H")
        self._blk_session.pack(fill=tk.X, pady=(0, 9))

        self._blk_weekly = self._metric_block(content, "SEMANAL · 7D")
        self._blk_weekly.pack(fill=tk.X)

        self._lbl_err = tk.Label(inner, text="", bg=BG, fg=DIM,
                                 font=("Segoe UI", 8), wraplength=W - 28,
                                 justify=tk.LEFT)

        self._set_loading()

    def _metric_block(self, parent, label: str) -> tk.Frame:
        frame = tk.Frame(parent, bg=BG)

        header = tk.Frame(frame, bg=BG)
        header.pack(fill=tk.X)

        tk.Label(header, text=label, bg=BG, fg=DIM,
                 font=("Segoe UI", 7, "bold")).pack(side=tk.LEFT)

        lbl_pct = tk.Label(header, text="–", bg=BG, fg=TEXT,
                           font=("Segoe UI", 9, "bold"))
        lbl_pct.pack(side=tk.RIGHT)

        bar = tk.Canvas(frame, bg=BAR_BG, height=5,
                        highlightthickness=0, bd=0)
        bar.pack(fill=tk.X, pady=(3, 2))

        lbl_reset = tk.Label(frame, text="", bg=BG, fg=DIM, font=("Segoe UI", 7))
        lbl_reset.pack(anchor=tk.W)

        frame._lbl_pct   = lbl_pct
        frame._bar       = bar
        frame._lbl_reset = lbl_reset
        return frame

    def _update_block(self, block: tk.Frame, pct: int, reset_min: int):
        color = bar_color(pct)
        block._lbl_pct.configure(text=f"{pct}%", fg=color)
        block._lbl_reset.configure(text=fmt_reset(reset_min))

        def _draw_bar():
            self.root.update_idletasks()
            w = block._bar.winfo_width()
            h = block._bar.winfo_height()
            block._bar.delete("all")
            if w > 1:
                fill_w = max(0, min(w, w * pct // 100))
                if fill_w:
                    block._bar.create_rectangle(0, 0, fill_w, h,
                                                fill=color, outline="")

        self.root.after_idle(_draw_bar)

    def _set_loading(self):
        for blk in (self._blk_session, self._blk_weekly):
            blk._lbl_pct.configure(text="–", fg=DIM)
            blk._lbl_reset.configure(text="carregando…")

    def _apply_data(self, data: dict):
        if "error" in data:
            self._lbl_err.configure(text=data["error"])
            self._lbl_err.pack(side=tk.BOTTOM, pady=(0, 10), padx=14, anchor=tk.W)
            self._lbl_ts.configure(text="erro")
            return

        self._lbl_err.pack_forget()
        self._update_block(self._blk_session,
                           data["session_pct"], data["session_reset"])
        self._update_block(self._blk_weekly,
                           data["weekly_pct"],  data["weekly_reset"])
        self._lbl_ts.configure(text=time.strftime("%H:%M"))
        self._update_tray_icon(data["session_pct"])

        # Switch mood if it changed
        new_mood = pct_to_mood(data["session_pct"])
        if new_mood != self._current_mood:
            self._start_animation_for_mood(new_mood)

    # ── Background poller ─────────────────────────────────────────────────────

    def _start_poller(self):
        def _loop():
            while True:
                data = fetch_usage()
                self.root.after(0, self._apply_data, data)
                time.sleep(POLL_INTERVAL)

        threading.Thread(target=_loop, daemon=True).start()

    # ── Drag ─────────────────────────────────────────────────────────────────

    def _drag_start(self, e: tk.Event):
        self._ox = e.x_root - self.root.winfo_x()
        self._oy = e.y_root - self.root.winfo_y()

    def _drag_move(self, e: tk.Event):
        self.root.geometry(f"+{e.x_root - self._ox}+{e.y_root - self._oy}")

    # ── System tray ───────────────────────────────────────────────────────────

    def _tray_icon(self, pct: int) -> Image.Image:
        size = 64
        ico  = SCRIPT_DIR / "claudinho.ico"

        if ico.exists():
            base = Image.open(ico).resize((size, size), Image.NEAREST).convert("RGBA")
        else:
            base = Image.new("RGBA", (size, size), "#1a1a1a")

        d = ImageDraw.Draw(base)

        # Small coloured badge in the bottom-right corner
        b  = size // 4          # badge diameter
        bx = size - b - 1
        by = size - b - 1
        d.ellipse([bx, by, bx + b, by + b], fill=bar_color(pct))

        try:
            fnt = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", b - 2)
        except OSError:
            fnt = ImageFont.load_default()

        text = str(pct)
        bbox = d.textbbox((0, 0), text, font=fnt)
        tw   = bbox[2] - bbox[0]
        th   = bbox[3] - bbox[1]
        d.text((bx + (b - tw) / 2 - bbox[0],
                by + (b - th) / 2 - bbox[1]),
               text, font=fnt, fill="#0a0a0a")

        return base

    def _build_tray(self):
        img  = self._tray_icon(0)
        menu = pystray.Menu(
            pystray.MenuItem("Mostrar", self._show_from_tray, default=True),
            pystray.MenuItem("Sair", self._quit),
        )
        self._tray = pystray.Icon("Consumo do Claudinho", img, "Consumo do Claudinho", menu)
        threading.Thread(target=self._tray.run, daemon=True).start()

    def _update_tray_icon(self, pct: int):
        if self._tray:
            self._tray.icon = self._tray_icon(pct)

    def _hide_to_tray(self):
        self._save_position()
        self.root.withdraw()

    def _show_from_tray(self, *_):
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)

    def _quit(self, *_):
        self._save_position()
        if self._tray:
            self._tray.stop()
        self.root.destroy()
        sys.exit(0)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    ClaudeWidget().run()
