"""Theme and visual styling configuration for the Tkinter desktop dashboard.

Course: Solving Problems Using Modelling and Simulation (SPMS) - NEC00091
"""

import tkinter as tk
from tkinter import ttk


class Theme:
    """Modern dark-accent and clean slate visual theme."""
    # Palette
    BG_DARK = "#0f172a"        # Deep slate navy
    BG_SIDEBAR = "#1e293b"     # Sidebar dark slate
    BG_CARD = "#ffffff"        # Clean white card surface
    BG_MAIN = "#f8fafc"        # Light background for content
    BORDER_COLOR = "#e2e8f0"   # Light border line

    TEXT_MAIN = "#0f172a"      # High contrast dark text
    TEXT_MUTED = "#64748b"     # Muted grey text
    TEXT_LIGHT = "#f8fafc"     # White text on dark surfaces

    PRIMARY = "#2563eb"        # Royal blue
    PRIMARY_HOVER = "#1d4ed8"  # Darker royal blue
    SECONDARY = "#64748b"      # Slate grey
    SUCCESS = "#16a34a"        # Emerald green
    SUCCESS_BG = "#dcfce7"     # Emerald light bg
    WARNING = "#d97706"        # Amber
    WARNING_BG = "#fef3c7"     # Amber light bg
    DANGER = "#dc2626"         # Crimson red
    DANGER_BG = "#fee2e2"      # Red light bg
    INFO = "#0284c7"           # Cyan blue
    INFO_BG = "#e0f2fe"        # Cyan light bg

    # Fonts
    FONT_TITLE = ("Segoe UI", 16, "bold")
    FONT_SUBTITLE = ("Segoe UI", 12, "bold")
    FONT_SECTION = ("Segoe UI", 10, "bold")
    FONT_BODY = ("Segoe UI", 9)
    FONT_BODY_BOLD = ("Segoe UI", 9, "bold")
    FONT_MONO = ("Consolas", 9)
    FONT_MONO_BOLD = ("Consolas", 9, "bold")
    FONT_METRIC = ("Segoe UI", 20, "bold")


def apply_theme_styles(root: tk.Tk) -> None:
    """Configure modern ttk styles across the entire application."""
    style = ttk.Style(root)
    style.theme_use("clam")

    # Frame backgrounds
    style.configure("TFrame", background=Theme.BG_MAIN)
    style.configure("Card.TFrame", background=Theme.BG_CARD, relief="flat")
    style.configure("Sidebar.TFrame", background=Theme.BG_SIDEBAR)

    # Label styles
    style.configure("TLabel", background=Theme.BG_MAIN, foreground=Theme.TEXT_MAIN, font=Theme.FONT_BODY)
    style.configure("Card.TLabel", background=Theme.BG_CARD, foreground=Theme.TEXT_MAIN, font=Theme.FONT_BODY)
    style.configure("Header.TLabel", background=Theme.BG_CARD, foreground=Theme.TEXT_MAIN, font=Theme.FONT_TITLE)
    style.configure("Subtitle.TLabel", background=Theme.BG_CARD, foreground=Theme.TEXT_MUTED, font=Theme.FONT_SUBTITLE)
    style.configure("Section.TLabel", background=Theme.BG_CARD, foreground=Theme.TEXT_MAIN, font=Theme.FONT_SECTION)
    style.configure("Muted.TLabel", background=Theme.BG_CARD, foreground=Theme.TEXT_MUTED, font=Theme.FONT_BODY)

    # Button styles
    style.configure(
        "Primary.TButton",
        background=Theme.PRIMARY,
        foreground="#ffffff",
        font=Theme.FONT_BODY_BOLD,
        borderwidth=0,
        focuscolor="none",
        padding=(12, 6),
    )
    style.map(
        "Primary.TButton",
        background=[("active", Theme.PRIMARY_HOVER), ("pressed", "#1e40af")],
    )

    style.configure(
        "Success.TButton",
        background=Theme.SUCCESS,
        foreground="#ffffff",
        font=Theme.FONT_BODY_BOLD,
        borderwidth=0,
        focuscolor="none",
        padding=(12, 6),
    )
    style.map("Success.TButton", background=[("active", "#15803d")])

    style.configure(
        "Danger.TButton",
        background=Theme.DANGER,
        foreground="#ffffff",
        font=Theme.FONT_BODY_BOLD,
        borderwidth=0,
        focuscolor="none",
        padding=(12, 6),
    )
    style.map("Danger.TButton", background=[("active", "#b91c1c")])

    style.configure(
        "Secondary.TButton",
        background=Theme.SECONDARY,
        foreground="#ffffff",
        font=Theme.FONT_BODY_BOLD,
        borderwidth=0,
        focuscolor="none",
        padding=(10, 5),
    )

    # Sidebar Navigation Button
    style.configure(
        "Nav.TButton",
        background=Theme.BG_SIDEBAR,
        foreground="#e2e8f0",
        font=Theme.FONT_BODY_BOLD,
        borderwidth=0,
        focuscolor="none",
        anchor="w",
        padding=(14, 10),
    )
    style.map(
        "Nav.TButton",
        background=[("active", "#334155"), ("pressed", "#475569")],
        foreground=[("active", "#ffffff")],
    )

    style.configure(
        "NavActive.TButton",
        background=Theme.PRIMARY,
        foreground="#ffffff",
        font=Theme.FONT_BODY_BOLD,
        borderwidth=0,
        focuscolor="none",
        anchor="w",
        padding=(14, 10),
    )

    # Treeview (Modern Tables)
    style.configure(
        "Treeview",
        background="#ffffff",
        foreground=Theme.TEXT_MAIN,
        rowheight=26,
        fieldbackground="#ffffff",
        font=Theme.FONT_BODY,
    )
    style.configure(
        "Treeview.Heading",
        background="#f1f5f9",
        foreground=Theme.TEXT_MAIN,
        font=Theme.FONT_SECTION,
        padding=(6, 4),
    )
    style.map("Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", "#1e3a8a")])

