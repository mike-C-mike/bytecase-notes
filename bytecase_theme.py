"""Shared ByteCase Tkinter theme helpers."""
import tkinter as tk
from tkinter import ttk

DARK_COLORS = {
    "app_background": "#0E1116",
    "panel_background": "#151B22",
    "elevated_surface": "#1B2128",
    "input_background": "#10161D",
    "border": "#2D3742",
    "border_strong": "#3A4654",
    "text_primary": "#F5F7FA",
    "text_secondary": "#C5CDD6",
    "text_muted": "#8D98A5",
    "accent": "#10B981",
    "accent_hover": "#18C98D",
    "accent_pressed": "#0D9668",
    "accent_soft": "#123B32",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "info": "#3B82F6",
    "selection": "#164C40",
    "focus_ring": "#34D399",
    "disabled_background": "#202731",
    "disabled_text": "#66717E",
}

LIGHT_COLORS = {
    "app_background": "#F4F7F9",
    "panel_background": "#FFFFFF",
    "elevated_surface": "#EAF0F4",
    "input_background": "#FFFFFF",
    "border": "#CBD5DF",
    "border_strong": "#9EABB8",
    "text_primary": "#17212B",
    "text_secondary": "#364656",
    "text_muted": "#667585",
    "accent": "#07875F",
    "accent_hover": "#069B6C",
    "accent_pressed": "#056B4C",
    "accent_soft": "#DDF5EB",
    "success": "#15803D",
    "warning": "#B45309",
    "error": "#B91C1C",
    "info": "#1D4ED8",
    "selection": "#C9EDDF",
    "focus_ring": "#0EA875",
    "disabled_background": "#E4E9ED",
    "disabled_text": "#8B97A3",
}


def resolve_theme(preference):
    value = str(preference or "system").strip().lower()
    if value == "light":
        return "light"
    if value == "dark":
        return "dark"
    return "dark"


def get_current_theme(settings_or_preference):
    if isinstance(settings_or_preference, dict):
        preference = settings_or_preference.get("appearance", {}).get("theme", "system")
    else:
        preference = settings_or_preference
    mode = resolve_theme(preference)
    return LIGHT_COLORS.copy() if mode == "light" else DARK_COLORS.copy()


def apply_theme(root, settings_or_preference):
    colors = get_current_theme(settings_or_preference)
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    root.configure(bg=colors["app_background"])
    default_font = ("Segoe UI", 10)
    heading_font = ("Segoe UI", 15, "bold")
    small_font = ("Segoe UI", 9)

    style.configure(".", background=colors["app_background"], foreground=colors["text_primary"], font=default_font)
    style.configure("TFrame", background=colors["app_background"])
    style.configure("Panel.TFrame", background=colors["panel_background"], relief="solid", borderwidth=1)
    style.configure("TLabel", background=colors["app_background"], foreground=colors["text_primary"])
    style.configure("Panel.TLabel", background=colors["panel_background"], foreground=colors["text_primary"])
    style.configure("Title.TLabel", background=colors["app_background"], foreground=colors["accent"], font=heading_font)
    style.configure("Muted.TLabel", background=colors["app_background"], foreground=colors["text_muted"], font=small_font)
    style.configure("PanelMuted.TLabel", background=colors["panel_background"], foreground=colors["text_muted"], font=small_font)
    style.configure("TLabelframe", background=colors["app_background"], foreground=colors["accent"], bordercolor=colors["border_strong"])
    style.configure("TLabelframe.Label", background=colors["app_background"], foreground=colors["accent"], font=("Segoe UI", 10, "bold"))

    style.configure("TButton", background=colors["elevated_surface"], foreground=colors["text_primary"], bordercolor=colors["border_strong"], padding=(10, 6))
    style.map("TButton", background=[("active", colors["accent_soft"]), ("pressed", colors["accent_pressed"])])
    style.configure("Accent.TButton", background=colors["accent"], foreground="#FFFFFF", bordercolor=colors["accent_pressed"], padding=(12, 7))
    style.map("Accent.TButton", background=[("active", colors["accent_hover"]), ("pressed", colors["accent_pressed"])])

    style.configure("TEntry", fieldbackground=colors["input_background"], foreground=colors["text_primary"], insertcolor=colors["accent"], bordercolor=colors["border_strong"], lightcolor=colors["border_strong"], darkcolor=colors["border_strong"], borderwidth=1, padding=4)
    style.configure("TCombobox", fieldbackground=colors["input_background"], foreground=colors["text_primary"], background=colors["elevated_surface"], arrowcolor=colors["accent"], bordercolor=colors["border_strong"], padding=4)
    style.map("TCombobox", fieldbackground=[("readonly", colors["input_background"])], foreground=[("readonly", colors["text_primary"])])
    style.configure("TCheckbutton", background=colors["app_background"], foreground=colors["text_primary"])
    style.configure("TNotebook", background=colors["app_background"], borderwidth=0)
    style.configure("TNotebook.Tab", background=colors["elevated_surface"], foreground=colors["text_secondary"], padding=(12, 7))
    style.map("TNotebook.Tab", background=[("selected", colors["panel_background"])], foreground=[("selected", colors["accent"])])
    style.configure("Treeview", background=colors["input_background"], fieldbackground=colors["input_background"], foreground=colors["text_primary"], rowheight=26, bordercolor=colors["border_strong"], borderwidth=1)
    style.configure("Treeview.Heading", background=colors["elevated_surface"], foreground=colors["text_primary"], font=("Segoe UI", 10, "bold"))
    style.map("Treeview", background=[("selected", colors["selection"])], foreground=[("selected", colors["text_primary"])])
    return colors


def style_text_widget(widget, colors):
    widget.configure(
        background=colors["input_background"],
        foreground=colors["text_primary"],
        insertbackground=colors["accent"],
        selectbackground=colors["selection"],
        selectforeground=colors["text_primary"],
        relief="solid",
        borderwidth=1,
        highlightthickness=1,
        highlightbackground=colors["border_strong"],
        highlightcolor=colors["focus_ring"],
        font=("Segoe UI", 10),
        wrap="word",
    )


def configure_toplevel(window, colors):
    window.configure(bg=colors["app_background"])
