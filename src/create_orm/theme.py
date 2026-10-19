"""高 DPI 支持、字体选择、主题样式、资源路径与窗口图标。"""

import ctypes
import os
import sys
import tkinter as tk
from tkinter import font as tkfont, ttk

from .config import (
    ACCENT, ACCENT_HV, BG_INPUT, BG_PAGE, BORDER, BORDER_FS, FG_TEXT,
)


def enable_high_dpi():
    if sys.platform != "win32":
        return
    for fn in (
        lambda: ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4)),
        lambda: ctypes.windll.shcore.SetProcessDpiAwareness(2),
        lambda: ctypes.windll.user32.SetProcessDPIAware(),
    ):
        try:
            fn()
            return
        except Exception:
            continue


def get_dpi_scale(root):
    try:
        dpi = root.winfo_fpixels("1i")
    except Exception:
        dpi = 96
    return dpi / 96.0, dpi


def resource_path(relative_path: str) -> str:
    """兼容源码运行和 PyInstaller 打包的资源路径"""
    base = getattr(sys, "_MEIPASS", None) or os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


def set_window_icon(root: tk.Tk, icon_name: str = "app.ico") -> bool:
    """优先 .ico，回退同名 .png，返回是否成功"""
    ico_path = resource_path(icon_name)
    if os.path.exists(ico_path):
        try:
            root.iconbitmap(ico_path)
            return True
        except Exception:
            pass

    png_path = resource_path(os.path.splitext(icon_name)[0] + ".png")
    if os.path.exists(png_path):
        try:
            img = tk.PhotoImage(file=png_path)
            root.iconphoto(True, img)
            root._icon_photo = img  # 防止被 GC 回收
            return True
        except Exception:
            pass
    return False


def pick_font_family(root):
    families = set(tkfont.families(root))
    for name in ("Microsoft YaHei UI", "Microsoft YaHei",
                 "PingFang SC", "Noto Sans CJK SC",
                 "Segoe UI", "Helvetica Neue", "Helvetica", "Arial"):
        if name in families:
            return name
    return "TkDefaultFont"


def setup_modern_theme(root, family, scale):
    def px(n):
        return max(1, round(n * scale))

    base = (family, 10)
    bold = (family, 10, "bold")
    root.configure(bg=BG_PAGE)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(".", font=base)
    style.configure("TFrame", background=BG_PAGE)
    style.configure("TLabel", background=BG_PAGE, foreground=FG_TEXT, font=base)

    style.configure(
        "TEntry",
        fieldbackground=BG_INPUT, foreground=FG_TEXT,
        bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER,
        insertcolor=FG_TEXT, padding=(px(8), px(6)), font=base,
    )
    style.map(
        "TEntry",
        fieldbackground=[("disabled", "#e2e8f0"), ("!disabled", BG_INPUT)],
        foreground=[("disabled", "#94a3b8"), ("!disabled", FG_TEXT)],
        bordercolor=[("focus", BORDER_FS)],
        lightcolor=[("focus", BORDER_FS)],
        darkcolor=[("focus", BORDER_FS)],
    )

    style.configure(
        "TCombobox",
        fieldbackground=BG_INPUT, background=BG_INPUT, foreground=FG_TEXT,
        arrowcolor=FG_TEXT, arrowsize=px(6),
        bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER,
        padding=(px(8), px(5), px(28), px(5)), font=base,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", BG_INPUT), ("disabled", "#e2e8f0")],
        foreground=[("disabled", "#94a3b8"), ("!disabled", FG_TEXT)],
        bordercolor=[("focus", BORDER_FS)],
    )
    try:
        style.layout("TCombobox", [
            ("Combobox.field", {"sticky": "nswe", "children": [
                ("Combobox.padding", {"sticky": "nswe", "children": [
                    ("Combobox.textarea", {"sticky": "nswe"}),
                ]}),
            ]}),
        ])
    except Exception:
        pass

    style.configure(
        "TButton",
        background=BG_INPUT, foreground=FG_TEXT,
        bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER,
        padding=(px(14), px(7)), font=base, focuscolor="",
    )
    style.map(
        "TButton",
        background=[("active", "#f1f5f9"),
                    ("pressed", "#e2e8f0"),
                    ("disabled", "#f8fafc")],
        foreground=[("disabled", "#94a3b8")],
        bordercolor=[("active", BORDER_FS)],
    )

    style.configure(
        "Accent.TButton",
        background=ACCENT, foreground="#ffffff",
        bordercolor=ACCENT, lightcolor=ACCENT, darkcolor=ACCENT,
        padding=(px(18), px(8)), font=bold, focuscolor="",
    )
    style.map(
        "Accent.TButton",
        background=[("active", ACCENT_HV),
                    ("pressed", ACCENT_HV),
                    ("disabled", "#93c5fd")],
        foreground=[("disabled", "#ffffff")],
        bordercolor=[("active", ACCENT_HV)],
        lightcolor=[("active", ACCENT_HV)],
        darkcolor=[("active", ACCENT_HV)],
    )

    root.option_add("*TCombobox*Listbox.font", base)
    root.option_add("*TCombobox*Listbox.background", BG_INPUT)
    root.option_add("*TCombobox*Listbox.foreground", FG_TEXT)
    root.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
    root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")
    root.option_add("*TCombobox*Listbox.borderWidth", 0)