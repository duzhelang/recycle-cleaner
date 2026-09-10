# -*- coding: utf-8 -*-
from __future__ import annotations

import ctypes
if hasattr(ctypes, 'windll'):
    _hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if _hwnd:
        ctypes.windll.user32.ShowWindow(_hwnd, 0)

import re
import csv
import json
import logging
import os
import platform
import subprocess
import sys
import tempfile
import threading
import traceback
import webbrowser
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import tkinter as tk
from urllib.request import urlopen, Request

from strings import STRINGS

APP_NAME = "回收站清理工具"
APP_VERSION = "2.0.0"
APP_ID = "recycle-cleaner"
GITHUB_REPO = "https://api.github.com/repos/user/recycle-cleaner/releases/latest"
APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent
CONFIG_DIR = APP_DIR / "data"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_DIR = CONFIG_DIR / "logs"

# ── Design Tokens ──────────────────────────────────────────────────────────────

C = {
    "bg":         "#f0f2f5",
    "card":       "#ffffff",
    "card_alt":   "#f8f9fb",
    "surface":    "#f5f6f8",
    "border":     "#e1e4e8",
    "border_lt":  "#eef0f2",
    "accent":     "#2563eb",
    "accent_h":   "#1d4ed8",
    "accent_p":   "#1e40af",
    "accent_lt":  "#eff6ff",
    "text":       "#111827",
    "text2":      "#6b7280",
    "text3":      "#9ca3af",
    "white":      "#ffffff",
    "success":    "#059669",
    "warning":    "#d97706",
    "danger":     "#dc2626",
    "log_bg":     "#0f1117",
    "log_fg":     "#c9d1d9",
    "log_dim":    "#484f58",
    "log_accent": "#58a6ff",
    "row_alt":    "#f6f8fa",
}

F = {
    "title": ("Segoe UI", 18, "bold"),
    "heading": ("Segoe UI", 11, "bold"),
    "body": ("Segoe UI", 10),
    "body_b": ("Segoe UI", 10, "bold"),
    "small": ("Segoe UI", 9),
    "small_b": ("Segoe UI", 9, "bold"),
    "tiny": ("Segoe UI", 8),
    "mono": ("Cascadia Code", 9),
    "btn": ("Segoe UI", 12, "bold"),
}

PAD = {"xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 20, "xxl": 28}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _ensure_dirs():
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def _load_config() -> dict:
    try:
        if CONFIG_FILE.exists():
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _save_config(cfg: dict):
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def _setup_logging() -> Path:
    _ensure_dirs()
    log_file = LOG_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(str(log_file), encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    logging.info("APP_NAME=%s APP_VERSION=%s", APP_NAME, APP_VERSION)
    logging.info("Python=%s OS=%s", sys.version, platform.platform())
    logging.info("Executable=%s", sys.executable)
    return log_file


def _resolve_packaged_resource(relative_path: str) -> Path | None:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    candidate = base / relative_path
    return candidate if candidate.exists() else None


def _self_check() -> list[str]:
    issues = []
    try:
        import tkinter as _tk
        _root = _tk.Tk()
        _root.withdraw()
        _root.destroy()
    except Exception as e:
        issues.append(f"tkinter: {e}")
    try:
        tmp = tempfile.gettempdir()
        test_f = os.path.join(tmp, f"_rc_test_{os.getpid()}.tmp")
        with open(test_f, "w") as f:
            f.write("test")
        os.remove(test_f)
    except Exception as e:
        issues.append(f"tempdir: {e}")
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "echo ok"],
            capture_output=True, timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if r.returncode != 0:
            issues.append("PowerShell: unavailable")
    except Exception as e:
        issues.append(f"PowerShell: {e}")
    return issues


def _run_self_check_ui(lang: str):
    s = STRINGS[lang]
    issues = _self_check()
    if issues:
        detail = "\n".join(f"- {i}" for i in issues)
        return messagebox.askyesno(
            s["selfcheck_title"],
            s["selfcheck_detail"].format(detail=detail),
        )
    return True


def format_size(size_bytes):
    if size_bytes >= 1024 ** 3:
        return f"{size_bytes / 1024 ** 3:.2f} GB"
    elif size_bytes >= 1024 ** 2:
        return f"{size_bytes / 1024 ** 2:.2f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes} B"


def parse_size_str(s):
    s = s.strip().lower()
    if not s:
        return 0
    m = re.match(r'^([\d.]+)\s*(bytes?|kb|mb|gb)?$', s)
    if not m:
        return 0
    val = float(m.group(1))
    unit = m.group(2) or 'bytes'
    if unit.startswith('k'):
        return int(val * 1024)
    elif unit.startswith('m'):
        return int(val * 1024 * 1024)
    elif unit.startswith('g'):
        return int(val * 1024 * 1024 * 1024)
    else:
        return int(val)


def parse_date_str(s):
    s = s.strip().replace('\u200e', '').replace('\u200f', '')
    if not s:
        return None
    for fmt in ['%Y/%m/%d %H:%M', '%Y/%m/%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d']:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    try:
        if '.' in s:
            d, t = s.split(' ', 1)
            parts = d.split('/')
            if len(parts) == 3:
                y, mon, day = int(parts[0]), int(parts[1]), int(parts[2])
                tparts = t.split(':')
                h, mi = int(tparts[0]), int(tparts[1])
                s_val = int(tparts[2]) if len(tparts) > 2 else 0
                return datetime(y, mon, day, h, mi, s_val)
    except Exception:
        pass
    return None


def _check_update_async(lang: str, callback):
    s = STRINGS[lang]
    try:
        req = Request(GITHUB_REPO, headers={"Accept": "application/vnd.github.v3+json", "User-Agent": APP_ID})
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        tag = data.get("tag_name", "").lstrip("v")
        if tag and tag != APP_VERSION:
            callback(tag)
    except Exception:
        logging.debug("Update check failed", exc_info=True)


# ── Application ────────────────────────────────────────────────────────────────

class RecycleCleaner:
    MODE_KEYS = ["by_ext", "by_path", "by_folder", "by_date", "by_size"]

    def __init__(self):
        self.cfg = _load_config()
        self.lang = self.cfg.get("lang", "zh")
        self.log_file_path = _setup_logging()
        self.scanned_items: list[tuple] = []
        self._last_targets: list[tuple] = []
        self._active_mode = 0
        self._busy = False
        self._log_queue: list[str] = []
        self._log_flush_scheduled = False
        self._seg_widgets: list[tuple[tk.Frame, tk.Label, tk.Frame]] = []
        self._content_frames: list[ttk.Frame] = []

        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("760x780")
        self.root.resizable(False, False)
        self.root.configure(bg=C["bg"])

        icon_path = _resolve_packaged_resource("assets/logo.ico")
        if icon_path is not None:
            self.root.iconbitmap(icon_path)

        self._center_window(760, 780)
        self._apply_style()
        self._build_ui()
        self._rebuild_texts()

        if not self.cfg.get("guide_shown"):
            self.root.after(300, self._show_guide)

        self.root.after(500, self._async_update_check)

    # ── Helpers ────────────────────────────────────────────────────────────

    def _t(self, key: str, **kwargs) -> str:
        val = STRINGS.get(self.lang, STRINGS["zh"]).get(key, key)
        if kwargs:
            val = val.format(**kwargs)
        return val

    def _center_window(self, w, h):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # ── Styles ─────────────────────────────────────────────────────────────

    def _apply_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(".", background=C["bg"], foreground=C["text"], font=F["body"])
        style.configure("Card.TFrame", background=C["card"])
        style.configure("Surface.TFrame", background=C["surface"])

        style.configure("Accent.TButton",
                         background=C["accent"], foreground=C["white"],
                         font=F["btn"], borderwidth=0, padding=[32, 14])
        style.map("Accent.TButton",
                   background=[("active", C["accent_h"]), ("pressed", C["accent_p"]),
                               ("disabled", "#94a3b8")],
                   foreground=[("disabled", "#e2e8f0")])

        style.configure("Tool.TButton",
                         background=C["card"], foreground=C["text2"],
                         font=F["small"], borderwidth=1, relief="solid",
                         bordercolor=C["border"], padding=[12, 6])
        style.map("Tool.TButton",
                   background=[("active", C["surface"]), ("pressed", C["border_lt"])],
                   bordercolor=[("active", C["border"])])

        style.configure("Small.TButton",
                         background=C["bg"], foreground=C["text2"],
                         font=F["tiny"], borderwidth=0, padding=[8, 4])
        style.map("Small.TButton",
                   background=[("active", C["surface"])])

        style.configure("TEntry", fieldbackground=C["card"], borderwidth=1,
                         relief="solid", bordercolor=C["border"], padding=8,
                         font=F["body"])
        style.map("TEntry",
                   bordercolor=[("focus", C["accent"])],
                   fieldbackground=[("disabled", C["surface"])])

        style.configure("TCombobox", fieldbackground=C["card"], borderwidth=1,
                         relief="solid", bordercolor=C["border"], padding=6,
                         font=F["body"])
        style.map("TCombobox",
                   bordercolor=[("focus", C["accent"])])

        style.configure("TCheckbutton", background=C["card"], foreground=C["text"],
                         font=F["body"])
        style.configure("TLabel", background=C["bg"], foreground=C["text"],
                         font=F["body"])

    # ── Segmented Control ──────────────────────────────────────────────────

    def _create_segmented_control(self, parent):
        seg_outer = tk.Frame(parent, bg=C["surface"], padx=2, pady=2)
        seg_outer.pack(fill=tk.X, pady=(0, 16))

        self._seg_widgets = []
        for idx in range(5):
            frame = tk.Frame(seg_outer, bg=C["surface"], cursor="hand2",
                             padx=2, pady=2)
            frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)

            indicator = tk.Frame(frame, bg=C["surface"], height=3)
            indicator.pack(fill=tk.X, pady=(0, 2))

            label = tk.Label(frame, font=F["small"], bg=C["surface"],
                             fg=C["text2"], cursor="hand2", pady=6)
            label.pack(fill=tk.X)

            self._seg_widgets.append((frame, label, indicator))

            for widget in (frame, label):
                widget.bind("<Button-1>", lambda e, i=idx: self._switch_mode(i))
                widget.bind("<Enter>", lambda e, i=idx: self._seg_hover(i, True))
                widget.bind("<Leave>", lambda e, i=idx: self._seg_hover(i, False))

        self._set_active_segment(0)

    def _seg_hover(self, idx, entering):
        if idx == self._active_mode:
            return
        frame, label, indicator = self._seg_widgets[idx]
        bg = C["border_lt"] if entering else C["surface"]
        for w in (frame, label, indicator):
            w.configure(bg=bg)

    def _set_active_segment(self, idx):
        for i, (frame, label, indicator) in enumerate(self._seg_widgets):
            if i == idx:
                for w in (frame, label, indicator):
                    w.configure(bg=C["card"])
                indicator.configure(bg=C["accent"], height=3)
                label.configure(fg=C["accent"], font=F["small_b"])
            else:
                for w in (frame, label, indicator):
                    w.configure(bg=C["surface"])
                indicator.configure(bg=C["surface"], height=3)
                label.configure(fg=C["text2"], font=F["small"])

    def _switch_mode(self, idx):
        if idx == self._active_mode:
            return
        self._active_mode = idx
        self._set_active_segment(idx)
        for i, frame in enumerate(self._content_frames):
            if i == idx:
                frame.pack(fill=tk.X, pady=0)
            else:
                frame.pack_forget()

    # ── Build UI ───────────────────────────────────────────────────────────

    def _build_ui(self):
        main = ttk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True)

        # ── Header Bar ─────────────────────────────────────────────────────
        header = tk.Frame(main, bg=C["accent"], padx=24, pady=18)
        header.pack(fill=tk.X)
        header_inner = tk.Frame(header, bg=C["accent"])
        header_inner.pack(fill=tk.X)

        self.title_label = tk.Label(header_inner, font=F["title"],
                                     fg=C["white"], bg=C["accent"])
        self.title_label.pack(side=tk.LEFT, anchor=tk.CENTER)

        self.lang_btn = tk.Label(header_inner, font=F["small_b"],
                                  fg="#bfdbfe", bg=C["accent"],
                                  cursor="hand2", padx=10, pady=4)
        self.lang_btn.pack(side=tk.RIGHT)
        self.lang_btn.bind("<Button-1>", lambda e: self._toggle_lang())
        self.lang_btn.bind("<Enter>",
                           lambda e: self.lang_btn.configure(fg=C["white"]))
        self.lang_btn.bind("<Leave>",
                           lambda e: self.lang_btn.configure(fg="#bfdbfe"))

        # ── Body ───────────────────────────────────────────────────────────
        body = ttk.Frame(main, padding=(24, 20, 24, 0))
        body.pack(fill=tk.BOTH, expand=True)

        # Segment control
        self._create_segmented_control(body)

        # ── Content Cards ──────────────────────────────────────────────────
        self._content_frames = []

        # Card: By Extension
        f_ext = ttk.Frame(body)
        self._content_frames.append(f_ext)
        card_ext = tk.Frame(f_ext, bg=C["card"], highlightbackground=C["border"],
                            highlightthickness=1, padx=20, pady=18)
        card_ext.pack(fill=tk.X)
        self.tab_ext_label = tk.Label(card_ext, font=F["heading"],
                                       fg=C["text"], bg=C["card"], anchor="w")
        self.tab_ext_label.pack(fill=tk.X)
        self.ext_entry = ttk.Entry(card_ext)
        self.ext_entry.pack(fill=tk.X, pady=(8, 6))
        self.ext_hint = tk.Label(card_ext, font=F["tiny"],
                                  fg=C["text3"], bg=C["card"], anchor="w")
        self.ext_hint.pack(fill=tk.X)

        # Card: By Path
        f_path = ttk.Frame(body)
        self._content_frames.append(f_path)
        card_path = tk.Frame(f_path, bg=C["card"], highlightbackground=C["border"],
                             highlightthickness=1, padx=20, pady=18)
        card_path.pack(fill=tk.X)
        self.tab_path_label = tk.Label(card_path, font=F["heading"],
                                        fg=C["text"], bg=C["card"], anchor="w")
        self.tab_path_label.pack(fill=tk.X)
        path_row = tk.Frame(card_path, bg=C["card"])
        path_row.pack(fill=tk.X, pady=(8, 6))
        self.path_entry = ttk.Entry(path_row)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.browse_btn = ttk.Button(path_row, command=self._browse,
                                      style="Tool.TButton")
        self.browse_btn.pack(side=tk.LEFT, padx=(10, 0))
        self.path_hint = tk.Label(card_path, font=F["tiny"],
                                   fg=C["text3"], bg=C["card"], anchor="w")
        self.path_hint.pack(fill=tk.X)

        # Card: By Folder
        f_folder = ttk.Frame(body)
        self._content_frames.append(f_folder)
        card_folder = tk.Frame(f_folder, bg=C["card"],
                               highlightbackground=C["border"],
                               highlightthickness=1, padx=20, pady=18)
        card_folder.pack(fill=tk.X)
        self.tab_folder_label = tk.Label(card_folder, font=F["heading"],
                                          fg=C["text"], bg=C["card"], anchor="w")
        self.tab_folder_label.pack(fill=tk.X)
        self.folder_entry = ttk.Entry(card_folder)
        self.folder_entry.pack(fill=tk.X, pady=(8, 6))
        self.folder_hint = tk.Label(card_folder, font=F["tiny"],
                                     fg=C["text3"], bg=C["card"], anchor="w")
        self.folder_hint.pack(fill=tk.X)

        # Card: By Date
        f_date = ttk.Frame(body)
        self._content_frames.append(f_date)
        card_date = tk.Frame(f_date, bg=C["card"], highlightbackground=C["border"],
                             highlightthickness=1, padx=20, pady=18)
        card_date.pack(fill=tk.X)
        self.tab_date_label = tk.Label(card_date, font=F["heading"],
                                        fg=C["text"], bg=C["card"], anchor="w")
        self.tab_date_label.pack(fill=tk.X)

        date_row1 = tk.Frame(card_date, bg=C["card"])
        date_row1.pack(fill=tk.X, pady=(10, 6))
        self.date_from_lbl = tk.Label(date_row1, font=F["body"],
                                       fg=C["text2"], bg=C["card"], width=6, anchor="w")
        self.date_from_lbl.pack(side=tk.LEFT)
        self.date_from_entry = ttk.Entry(date_row1, width=22)
        self.date_from_entry.pack(side=tk.LEFT, padx=(6, 20))

        self.date_to_lbl = tk.Label(date_row1, font=F["body"],
                                     fg=C["text2"], bg=C["card"], width=4, anchor="w")
        self.date_to_lbl.pack(side=tk.LEFT)
        self.date_to_entry = ttk.Entry(date_row1, width=22)
        self.date_to_entry.pack(side=tk.LEFT, padx=(6, 0))

        self.date_hint = tk.Label(card_date, font=F["tiny"],
                                   fg=C["text3"], bg=C["card"], anchor="w")
        self.date_hint.pack(fill=tk.X, pady=(4, 0))

        # Card: By Size
        f_size = ttk.Frame(body)
        self._content_frames.append(f_size)
        card_size = tk.Frame(f_size, bg=C["card"], highlightbackground=C["border"],
                             highlightthickness=1, padx=20, pady=18)
        card_size.pack(fill=tk.X)
        self.tab_size_label = tk.Label(card_size, font=F["heading"],
                                        fg=C["text"], bg=C["card"], anchor="w")
        self.tab_size_label.pack(fill=tk.X)
        self.size_units = ["KB", "MB", "GB", "TB"]

        size_row1 = tk.Frame(card_size, bg=C["card"])
        size_row1.pack(fill=tk.X, pady=(10, 6))
        self.size_from_lbl = tk.Label(size_row1, font=F["body"],
                                       fg=C["text2"], bg=C["card"], width=6, anchor="w")
        self.size_from_lbl.pack(side=tk.LEFT)
        self.size_from_entry = ttk.Entry(size_row1, width=10)
        self.size_from_entry.pack(side=tk.LEFT, padx=(6, 6))
        self.size_from_unit = ttk.Combobox(size_row1, values=self.size_units,
                                            width=6, state="readonly")
        self.size_from_unit.set("MB")
        self.size_from_unit.pack(side=tk.LEFT)

        size_row2 = tk.Frame(card_size, bg=C["card"])
        size_row2.pack(fill=tk.X, pady=(0, 6))
        self.size_to_lbl = tk.Label(size_row2, font=F["body"],
                                     fg=C["text2"], bg=C["card"], width=6, anchor="w")
        self.size_to_lbl.pack(side=tk.LEFT)
        self.size_to_entry = ttk.Entry(size_row2, width=10)
        self.size_to_entry.pack(side=tk.LEFT, padx=(6, 6))
        self.size_to_unit = ttk.Combobox(size_row2, values=self.size_units,
                                          width=6, state="readonly")
        self.size_to_unit.set("MB")
        self.size_to_unit.pack(side=tk.LEFT)

        self.size_hint = tk.Label(card_size, font=F["tiny"],
                                   fg=C["text3"], bg=C["card"], anchor="w")
        self.size_hint.pack(fill=tk.X, pady=(4, 0))

        # Show first mode
        self._content_frames[0].pack(fill=tk.X, pady=0)

        # ── Action Button ──────────────────────────────────────────────────
        self.run_btn = ttk.Button(body, style="Accent.TButton",
                                   command=self._run)
        self.run_btn.pack(fill=tk.X, pady=(16, 16))

        # ── Log Panel ──────────────────────────────────────────────────────
        log_card = tk.Frame(body, bg=C["log_bg"],
                            highlightbackground=C["border"],
                            highlightthickness=1)
        log_card.pack(fill=tk.BOTH, expand=True)

        log_header = tk.Frame(log_card, bg="#161b22", padx=16, pady=10)
        log_header.pack(fill=tk.X)
        self.log_frame_label = tk.Label(log_header, font=F["small_b"],
                                         fg=C["text3"], bg="#161b22")
        self.log_frame_label.pack(side=tk.LEFT)

        log_body = tk.Frame(log_card, bg=C["log_bg"])
        log_body.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(
            log_body, height=10, state=tk.DISABLED,
            font=F["mono"], wrap=tk.WORD,
            bg=C["log_bg"], fg=C["log_fg"],
            selectbackground="#264f78", relief=tk.FLAT,
            borderwidth=0, padx=16, pady=12,
            insertbackground=C["accent"], highlightthickness=0,
            spacing1=1, spacing3=1
        )
        scrollbar = tk.Scrollbar(log_body, command=self.log_text.yview,
                                  bg=C["log_bg"], troughcolor=C["log_bg"],
                                  activebackground=C["log_dim"],
                                  width=8, borderwidth=0, relief=tk.FLAT)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # ── Footer ─────────────────────────────────────────────────────────
        footer = tk.Frame(body, bg=C["bg"], pady=10)
        footer.pack(fill=tk.X)
        self.log_path_label = tk.Label(footer, font=F["tiny"],
                                        fg=C["text3"], bg=C["bg"])
        self.log_path_label.pack(side=tk.LEFT, anchor=tk.CENTER)
        self.export_btn = ttk.Button(footer, command=self._export_csv,
                                      style="Small.TButton")
        self.export_btn.pack(side=tk.RIGHT, padx=(4, 0))
        self.open_log_btn = ttk.Button(footer, command=self._open_log_dir,
                                        style="Small.TButton")
        self.open_log_btn.pack(side=tk.RIGHT)

        # ── Status Bar ─────────────────────────────────────────────────────
        self.status_var = tk.StringVar(value="")
        status_bar = tk.Frame(main, bg=C["card"], padx=24, pady=10,
                               highlightbackground=C["border"],
                               highlightthickness=1)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_dot = tk.Frame(status_bar, bg=C["success"],
                                    width=8, height=8)
        self.status_dot.pack(side=tk.LEFT, padx=(0, 8), anchor=tk.CENTER)
        self.status_label = tk.Label(status_bar, textvariable=self.status_var,
                                      font=F["small"], fg=C["text2"], bg=C["card"])
        self.status_label.pack(side=tk.LEFT, anchor=tk.CENTER)

    # ── Rebuild Texts ──────────────────────────────────────────────────────

    def _rebuild_texts(self):
        s = STRINGS[self.lang]
        self.root.title(f"{s['app_title']} v{APP_VERSION}")
        self.title_label.config(text=s["app_title"])
        self.lang_btn.config(text=s["lang_switch"])

        for idx in range(5):
            _, label, _ = self._seg_widgets[idx]
            label.config(text=s[self.MODE_KEYS[idx]].strip())

        self.tab_ext_label.config(text=s["ext_label"])
        self.ext_hint.config(text=s["ext_hint"])
        self.tab_path_label.config(text=s["path_label"])
        self.browse_btn.config(text=s["browse"])
        self.path_hint.config(text=s["path_hint"])
        self.tab_folder_label.config(text=s["folder_label"])
        self.folder_hint.config(text=s["folder_hint"])
        self.tab_date_label.config(text=s["date_label"])
        self.date_from_lbl.config(text=s["from"])
        self.date_to_lbl.config(text=s["to"])
        self.date_hint.config(text=s["date_hint"])
        self.tab_size_label.config(text=s["size_label"])
        self.size_from_lbl.config(text=s["size_from"])
        self.size_to_lbl.config(text=s["size_to"])
        self.size_hint.config(text=s["size_hint"])
        self.run_btn.config(text=s["start_clean"])
        self.log_frame_label.config(text=s["exec_log"])
        self.log_path_label.config(text=f"{s['log_path']}{self.log_file_path}")
        self.export_btn.config(text=s["export_csv"])
        self.open_log_btn.config(text=s["open_log_dir"])
        self.status_var.set(s["ready"])

    def _toggle_lang(self):
        self.lang = "en" if self.lang == "zh" else "zh"
        self.cfg["lang"] = self.lang
        _save_config(self.cfg)
        self._rebuild_texts()

    def _browse(self):
        d = filedialog.askdirectory(title="选择路径" if self.lang == "zh" else "Select path")
        if d:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, d)

    # ── Log ────────────────────────────────────────────────────────────────

    def _log(self, msg):
        logging.info(msg)
        if threading.current_thread() is threading.main_thread():
            self._log_gui(msg)
            return
        self._log_queue.append(msg)
        if self._log_flush_scheduled:
            return
        self._log_flush_scheduled = True
        try:
            self.root.after(150, self._flush_log_queue)
        except tk.TclError:
            self._log_flush_scheduled = False

    def _log_gui(self, msg):
        try:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, msg + "\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        except tk.TclError:
            pass

    def _flush_log_queue(self):
        self._log_flush_scheduled = False
        batch = self._log_queue
        self._log_queue = []
        try:
            self.log_text.config(state=tk.NORMAL)
            for msg in batch:
                self.log_text.insert(tk.END, msg + "\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        except tk.TclError:
            pass

    def _clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

    # ── Guide Dialog ───────────────────────────────────────────────────────

    def _show_guide(self):
        s = STRINGS[self.lang]
        dlg = tk.Toplevel(self.root)
        dlg.title(s["guide_title"])
        dlg.geometry("500x420")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.configure(bg=C["bg"])
        self._center_child(dlg, 500, 420)

        card = tk.Frame(dlg, bg=C["card"], padx=24, pady=24)
        card.pack(fill=tk.BOTH, expand=True, padx=16, pady=(16, 0))

        text = tk.Text(card, wrap=tk.WORD, font=F["body"], padx=4, pady=4,
                        relief=tk.FLAT, bg=C["card"], fg=C["text"],
                        highlightthickness=0, spacing1=2, spacing3=2)
        text.insert(tk.END, s["guide_text"])
        text.config(state=tk.DISABLED)
        text.pack(fill=tk.BOTH, expand=True)

        btn_area = tk.Frame(dlg, bg=C["bg"], padx=16, pady=16)
        btn_area.pack(fill=tk.X)

        var = tk.BooleanVar(value=True)
        ttk.Checkbutton(btn_area, text=s["guide_confirm"], variable=var).pack(anchor=tk.W, pady=(0, 10))
        ttk.Button(btn_area, text=s["guide_ok"], command=lambda: self._close_guide(dlg, var),
                    style="Accent.TButton").pack(fill=tk.X)

    def _close_guide(self, dlg, var):
        if var.get():
            self.cfg["guide_shown"] = True
            _save_config(self.cfg)
        dlg.destroy()

    def _center_child(self, win, w, h):
        px = self.root.winfo_x()
        py = self.root.winfo_y()
        pw = self.root.winfo_width()
        ph = self.root.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")

    # ── Update Check ───────────────────────────────────────────────────────

    def _async_update_check(self):
        threading.Thread(target=_check_update_async, args=(self.lang, self._on_update_found), daemon=True).start()

    def _on_update_found(self, new_ver):
        s = STRINGS[self.lang]
        self.root.after(0, lambda: self._show_update_dialog(new_ver, s))

    def _show_update_dialog(self, new_ver, s):
        if messagebox.askyesno(s["update_title"], s["update_msg"].format(cur=APP_VERSION, new=new_ver)):
            webbrowser.open(f"https://github.com/user/recycle-cleaner/releases/tag/v{new_ver}")

    # ── Error Dialog ───────────────────────────────────────────────────────

    def _show_error(self, exc: Exception):
        s = STRINGS[self.lang]
        err_text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        logging.error(err_text)
        dlg = tk.Toplevel(self.root)
        dlg.title(s["err_title"])
        dlg.geometry("540x340")
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.configure(bg=C["bg"])
        self._center_child(dlg, 540, 340)

        header = tk.Frame(dlg, bg=C["card"], padx=20, pady=16)
        header.pack(fill=tk.X, padx=16, pady=(16, 0))
        tk.Label(header, text=s["err_msg"].format(err=str(exc)[:200]),
                 wraplength=480, justify=tk.LEFT, font=F["body"],
                 bg=C["card"], fg=C["danger"]).pack(anchor=tk.W)

        t = tk.Text(dlg, wrap=tk.WORD, font=F["mono"], height=8,
                     bg=C["log_bg"], fg=C["log_fg"], relief=tk.FLAT,
                     borderwidth=0, padx=16, pady=12, highlightthickness=0)
        t.insert(tk.END, err_text)
        t.config(state=tk.DISABLED)
        t.pack(fill=tk.BOTH, expand=True, padx=16, pady=(8, 8))

        btn_row = tk.Frame(dlg, bg=C["bg"], padx=16, pady=16)
        btn_row.pack(fill=tk.X)
        ttk.Button(btn_row, text=s["err_copy"], command=lambda: self._copy_text(err_text),
                    style="Tool.TButton").pack(side=tk.LEFT)
        ttk.Button(btn_row, text=s["close"], command=dlg.destroy,
                    style="Accent.TButton").pack(side=tk.RIGHT)

    def _copy_text(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)

    # ── Scan Recycle Bin ───────────────────────────────────────────────────

    def _scan_recycle_bin(self):
        s = STRINGS[self.lang]
        self._log(s["scanning"].rstrip("."))
        try:
            ps_script = '''$Encoding = [System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$shell = New-Object -ComObject Shell.Application
$rb = $shell.NameSpace(0xa)
$items = $rb.Items()
foreach ($item in $items) {
    $n = $rb.GetDetailsOf($item, 0)
    $l = $rb.GetDetailsOf($item, 1)
    $d = $rb.GetDetailsOf($item, 2)
    $s = $rb.GetDetailsOf($item, 3)
    $p = $item.Path
    if (-not $n) { $n = "" }
    if (-not $l) { $l = "" }
    if (-not $d) { $d = "" }
    if (-not $s) { $s = "" }
    if (-not $p) { $p = "" }
    $n = $n -replace "`r|`n"," "
    $l = $l -replace "`r|`n"," "
    Write-Host ("PSVB1|" + $n + "|" + $l + "|" + $d + "|" + $s + "|" + $p)
}
'''
            ps_file = os.path.join(tempfile.gettempdir(), 'scan_rb.ps1')
            with open(ps_file, 'wb') as f:
                f.write(ps_script.encode('utf-8-sig'))

            result = subprocess.run(
                ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ps_file],
                capture_output=True, timeout=300,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode != 0:
                err = result.stderr.decode('utf-8', errors='replace')[:200]
                self._log(s["scan_err_ps"] + err)
                return False

            raw = result.stdout.decode('utf-8', errors='replace').strip()
            if not raw:
                self._log(s["scan_err_empty"])
                return False

            self.scanned_items = []
            errors = 0
            for line in raw.split('\n'):
                line = line.strip()
                if not line:
                    continue
                if not line.startswith('PSVB1|'):
                    continue
                parts = line.split('|', 5)
                if len(parts) < 6:
                    errors += 1
                    continue
                n = parts[1]
                l = parts[2]
                d = parts[3]
                sz = parts[4]
                p = parts[5]

                orig_path = os.path.join(l, n) if l and n else None
                file_size = parse_size_str(sz)
                delete_time = parse_date_str(d)

                self.scanned_items.append((p, orig_path, file_size, delete_time, n))

            self._log(s["scan_done"].format(n=len(self.scanned_items)))
            if errors:
                self._log(s["scan_skip"].format(n=errors))
            return True

        except subprocess.TimeoutExpired:
            self._log(s["scan_timeout"])
            return False
        except Exception as e:
            self._log(s["scan_exception"] + str(e))
            logging.error("Scan exception", exc_info=True)
            return False

    # ── Parsers ────────────────────────────────────────────────────────────

    def _parse_extensions(self, raw):
        separators = [',', ' ', '\uff0c', ';', '\uff1b', '\n']
        tokens = [raw]
        for sep in separators:
            new_tokens = []
            for t in tokens:
                new_tokens.extend(t.split(sep))
            tokens = new_tokens
        exts = set()
        for t in tokens:
            t = t.strip().lower()
            if not t:
                continue
            if not t.startswith('.'):
                t = '.' + t
            exts.add(t)
        return exts

    def _parse_date(self, s):
        s = s.strip()
        if not s:
            return None
        for fmt in ['%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        return 'invalid'

    # ── Run ────────────────────────────────────────────────────────────────

    def _run(self):
        try:
            self._do_run()
        except Exception as e:
            self._show_error(e)

    def _do_run(self):
        if self._busy:
            return
        self._busy = True
        s = STRINGS[self.lang]
        self._clear_log()
        self.status_var.set(s["scanning"])
        self.status_dot.configure(bg=C["warning"])
        threading.Thread(target=self._scan_thread, daemon=True).start()

    def _scan_thread(self):
        ok = self._scan_recycle_bin()
        if ok:
            self.root.after(0, self._continue_clean)
        else:
            self.root.after(0, self._on_scan_failed)

    def _on_scan_failed(self):
        s = STRINGS[self.lang]
        self._busy = False
        self.status_var.set(s["scan_failed"])
        self.status_dot.configure(bg=C["danger"])

    def _continue_clean(self):
        tab_idx = self._active_mode
        if tab_idx == 0:
            self._clean_by_ext()
        elif tab_idx == 1:
            self._clean_by_path()
        elif tab_idx == 2:
            self._clean_by_folder_name()
        elif tab_idx == 3:
            self._clean_by_date()
        else:
            self._clean_by_size()

    # ── Preview & Delete ───────────────────────────────────────────────────

    def _show_preview(self, targets) -> bool:
        s = STRINGS[self.lang]
        self._last_targets = targets
        total_size = sum(t[2] for t in targets)
        sample_lines = []
        for t in targets[:5]:
            display = t[1] if t[1] else t[4]
            sample_lines.append(f"  - {display} ({format_size(t[2])})")
        if len(targets) > 5:
            sample_lines.append(f"  ...")
        samples = "\n".join(sample_lines)
        msg = s["preview_msg"].format(n=len(targets), sz=format_size(total_size), samples=samples)
        return messagebox.askyesno(s["preview_title"], msg)

    def _do_delete(self, targets):
        s = STRINGS[self.lang]
        if not targets:
            self._log(s["no_match"])
            self.status_var.set(s["ready"])
            self.status_dot.configure(bg=C["success"])
            self._busy = False
            return

        if not self._show_preview(targets):
            self._log(s["user_cancel"])
            self.status_var.set(s["cancelled"])
            self.status_dot.configure(bg=C["text3"])
            self._busy = False
            return

        self.status_var.set(s["cleaning"])
        self.status_dot.configure(bg=C["accent"])
        threading.Thread(target=self._delete_thread, args=(targets,), daemon=True).start()

    def _delete_thread(self, targets):
        s = STRINGS[self.lang]
        try:
            ps_lines = ['$ErrorActionPreference = "SilentlyContinue"']
            for r_path, orig_path, size, _, name in targets:
                r_dir = os.path.dirname(r_path)
                r_name = os.path.basename(r_path)
                i_path = os.path.join(r_dir, '$I' + r_name[2:])
                ep = r_path.replace("'", "''")
                ei = i_path.replace("'", "''")
                ps_lines.append(f"Remove-Item -LiteralPath '{ep}' -Force -Recurse -ErrorAction SilentlyContinue")
                ps_lines.append(f"Remove-Item -LiteralPath '{ei}' -Force -ErrorAction SilentlyContinue")

            ps_lines.append("Write-Host 'DONE'")
            ps_script = '\n'.join(ps_lines)
            ps_file = os.path.join(tempfile.gettempdir(), 'delete_rb.ps1')
            with open(ps_file, 'wb') as f:
                f.write(ps_script.encode('utf-8-sig'))

            subprocess.run(
                ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ps_file],
                capture_output=True, timeout=120,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except Exception as e:
            self._log(s["scan_exception"] + str(e))
            logging.error("Delete exception", exc_info=True)
            self.root.after(0, self._on_delete_failed, str(e))
            return

        deleted, failed, freed = 0, 0, 0
        for r_path, orig_path, size, _, name in targets:
            if os.path.exists(r_path):
                failed += 1
            else:
                deleted += 1
                freed += size
            i_path = os.path.join(os.path.dirname(r_path), '$I' + os.path.basename(r_path)[2:])
            if os.path.exists(i_path):
                try:
                    os.remove(i_path)
                except Exception:
                    pass
            display = orig_path if orig_path else name
            self._log(s["delete_item"] + f"{display} ({format_size(size)})")

        self.root.after(0, self._finish_delete, deleted, failed, freed)

    def _on_delete_failed(self, err=""):
        s = STRINGS[self.lang]
        self._busy = False
        self.status_var.set(s["scan_failed"])
        self.status_dot.configure(bg=C["danger"])
        messagebox.showerror(s["err_title"], s["del_fail_msg"].format(err=err))

    def _finish_delete(self, deleted, failed, freed):
        s = STRINGS[self.lang]
        self._log("")
        self._log("=" * 50)
        self._log(s["clean_done"])
        self._log(s["deleted"] + str(deleted))
        self._log(s["freed"] + format_size(freed))
        if failed:
            self._log(s["failed"] + str(failed) + s["failed_reason"])
        self._log("=" * 50)
        self.status_var.set(s["done_status"].format(n=deleted, sz=format_size(freed)))
        self.status_dot.configure(bg=C["success"])
        self._busy = False
        messagebox.showinfo(
            s["done_title"],
            s["done_msg"].format(deleted=deleted, freed=format_size(freed), failed=failed),
        )

    # ── Clean Modes ────────────────────────────────────────────────────────

    def _clean_by_ext(self):
        s = STRINGS[self.lang]
        raw = self.ext_entry.get().strip()
        if not raw:
            messagebox.showwarning(s["selfcheck_title"], s["prompt_ext"])
            self.status_var.set(s["ready"])
            return
        extensions = self._parse_extensions(raw)
        if not extensions:
            messagebox.showwarning(s["selfcheck_title"], s["prompt_ext_fmt"])
            self.status_var.set(s["ready"])
            return
        self._log(s["mode_ext"])
        self._log(s["target_ext"] + ", ".join(sorted(extensions)))
        targets = []
        for r_path, orig_path, size, delete_time, name in self.scanned_items:
            target = orig_path if orig_path else name
            ext = os.path.splitext(target)[1].lower()
            if ext in extensions:
                targets.append((r_path, orig_path, size, delete_time, name))
        self._do_delete(targets)

    def _clean_by_path(self):
        s = STRINGS[self.lang]
        folder = self.path_entry.get().strip()
        if not folder:
            messagebox.showwarning(s["selfcheck_title"], s["prompt_path"])
            self.status_var.set(s["ready"])
            return
        folder_lower = folder.lower().rstrip('\\').rstrip('/')
        self._log(s["mode_path"])
        self._log(s["target_path"] + folder)
        targets = []
        for r_path, orig_path, size, delete_time, name in self.scanned_items:
            if orig_path and orig_path.lower().rstrip('\\').rstrip('/').startswith(folder_lower):
                targets.append((r_path, orig_path, size, delete_time, name))
        self._do_delete(targets)

    def _clean_by_folder_name(self):
        s = STRINGS[self.lang]
        folder_name = self.folder_entry.get().strip().lower()
        if not folder_name:
            messagebox.showwarning(s["selfcheck_title"], s["prompt_folder"])
            self.status_var.set(s["ready"])
            return
        self._log(s["mode_folder"])
        self._log(s["target_folder"] + folder_name)
        targets = []
        for r_path, orig_path, size, delete_time, name in self.scanned_items:
            if not orig_path:
                continue
            parts = orig_path.lower().replace('\\', '/').split('/')
            if folder_name in parts:
                targets.append((r_path, orig_path, size, delete_time, name))
        if not targets:
            self._log(s["no_folder_match"].format(name=folder_name))
        self._do_delete(targets)

    def _clean_by_date(self):
        s = STRINGS[self.lang]
        from_str = self.date_from_entry.get()
        to_str = self.date_to_entry.get()

        date_from = self._parse_date(from_str)
        if date_from == 'invalid':
            messagebox.showwarning(s["selfcheck_title"], s["prompt_date_fmt_s"])
            self.status_var.set(s["ready"])
            return

        date_to = self._parse_date(to_str)
        if date_to == 'invalid':
            messagebox.showwarning(s["selfcheck_title"], s["prompt_date_fmt_e"])
            self.status_var.set(s["ready"])
            return

        if date_to and date_to.hour == 0 and date_to.minute == 0:
            date_to = date_to.replace(hour=23, minute=59, second=59)

        if not date_from and not date_to:
            messagebox.showwarning(s["selfcheck_title"], s["prompt_date_at_least"])
            self.status_var.set(s["ready"])
            return

        self._log(s["mode_date"])
        if date_from and date_to:
            self._log(s["date_range"] + f"{date_from.strftime('%Y-%m-%d %H:%M')} ~ {date_to.strftime('%Y-%m-%d %H:%M')}")
        elif date_from:
            self._log(s["date_from_only"] + date_from.strftime('%Y-%m-%d %H:%M'))
        else:
            self._log(s["date_to_only"] + date_to.strftime('%Y-%m-%d %H:%M'))

        targets = []
        skipped = 0
        for r_path, orig_path, size, delete_time, name in self.scanned_items:
            if delete_time is None:
                skipped += 1
                continue
            if date_from and delete_time < date_from:
                continue
            if date_to and delete_time > date_to:
                continue
            targets.append((r_path, orig_path, size, delete_time, name))

        if skipped > 0:
            self._log(s["skipped_no_date"].format(n=skipped))
        self._do_delete(targets)

    def _clean_by_size(self):
        s = STRINGS[self.lang]
        raw_from = self.size_from_entry.get().strip()
        raw_to = self.size_to_entry.get().strip()

        if not raw_from and not raw_to:
            messagebox.showwarning(s["selfcheck_title"], s["prompt_size"])
            self.status_var.set(s["ready"])
            return

        size_from = None
        if raw_from:
            try:
                num = float(raw_from)
                size_from = int(num * {"KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}[self.size_from_unit.get()])
                if size_from <= 0:
                    raise ValueError
            except (ValueError, KeyError):
                messagebox.showwarning(s["selfcheck_title"], s["prompt_size_fmt"])
                self.status_var.set(s["ready"])
                return

        size_to = None
        if raw_to:
            try:
                num = float(raw_to)
                size_to = int(num * {"KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}[self.size_to_unit.get()])
                if size_to <= 0:
                    raise ValueError
            except (ValueError, KeyError):
                messagebox.showwarning(s["selfcheck_title"], s["prompt_size_fmt"])
                self.status_var.set(s["ready"])
                return

        self._log(s["mode_size"])
        if size_from is not None and size_to is not None:
            self._log(s["target_size"] + f"{raw_from}{self.size_from_unit.get()} ~ {raw_to}{self.size_to_unit.get()}")
        elif size_from is not None:
            self._log(s["target_size"] + f">= {raw_from}{self.size_from_unit.get()}")
        else:
            self._log(s["target_size"] + f"<= {raw_to}{self.size_to_unit.get()}")

        targets = []
        for r_path, orig_path, size, delete_time, name in self.scanned_items:
            if size_from is not None and size < size_from:
                continue
            if size_to is not None and size > size_to:
                continue
            targets.append((r_path, orig_path, size, delete_time, name))
        self._do_delete(targets)

    # ── Utilities ──────────────────────────────────────────────────────────

    def _open_log_dir(self):
        if LOG_DIR.exists():
            os.startfile(str(LOG_DIR))
        else:
            messagebox.showinfo("", str(LOG_DIR))

    def _export_csv(self):
        s = STRINGS[self.lang]
        items = self.scanned_items
        if not items and self._last_targets:
            items = self._last_targets
        if not items:
            messagebox.showinfo(s["export_title"], s["export_empty"])
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            title=s["export_title"],
        )
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Name", "Original Path", "Size", "Size Bytes", "Delete Time", "Recycle Path"])
                for item in items:
                    r_path, orig_path, size, delete_time, name = item
                    writer.writerow([
                        name,
                        orig_path or "",
                        format_size(size),
                        size,
                        delete_time.strftime("%Y-%m-%d %H:%M:%S") if delete_time else "",
                        r_path,
                    ])
            logging.info("CSV exported to %s", path)
            messagebox.showinfo(s["export_title"], s["export_success"].format(path=path))
        except Exception as e:
            self._show_error(e)

    # ── Main Loop ──────────────────────────────────────────────────────────

    def run(self):
        if not _run_self_check_ui(self.lang):
            return
        self.root.mainloop()


# ── Uninstall Cleanup ──────────────────────────────────────────────────────────

def _run_uninstall_cleanup() -> None:
    import shutil
    cleanup_targets = []
    data_dir = APP_DIR / "data"
    if data_dir.exists():
        cleanup_targets.append(data_dir)
    local_app = Path(os.environ.get("LOCALAPPDATA", "")) / "RecycleCleaner"
    if local_app.exists():
        cleanup_targets.append(local_app)
    app_data = Path(os.environ.get("APPDATA", "")) / "RecycleCleaner"
    if app_data.exists():
        cleanup_targets.append(app_data)
    home_cfg = Path.home() / "RecycleCleaner"
    if home_cfg.exists():
        cleanup_targets.append(home_cfg)
    for pattern in ["*.log", "*.tmp"]:
        for item in APP_DIR.glob(pattern):
            cleanup_targets.append(item)
    for target in cleanup_targets:
        try:
            if target.is_dir():
                shutil.rmtree(target, ignore_errors=True)
            elif target.is_file():
                target.unlink(missing_ok=True)
        except Exception:
            pass


if __name__ == '__main__':
    if "--uninstall-cleanup" in sys.argv:
        _run_uninstall_cleanup()
    else:
        app = RecycleCleaner()
        app.run()
