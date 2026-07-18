"""Settings and output path helpers for ByteCase Notes."""
import json
import sys
from pathlib import Path

APP_NAME = "ByteCase Notes"
APP_SUBTITLE = "Examiner Notes Workspace"
APP_VERSION = "0.4.0"
SUITE_NAME = "ByteCase"
PUBLISHER_NAME = "Forensics Byte"
PRODUCT_DOMAIN = "byte-case.com"
TOOL_FOLDER_NAME = "notes"
DEFAULT_ROOT_FOLDER_NAME = "ByteCase"


def get_app_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


APP_DIR = get_app_dir()
SETTINGS_PATH = APP_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "department_name": "",
    "unit_name": "",
    "default_examiner": "",
    "examiners": [],
    "appearance": {"theme": "system"},
    "output_paths": {
        "base_output_dir": "",
        "reports_folder_name": "reports",
        "saved_notes_folder_name": "saved_notes",
        "attachments_folder_name": "attachments"
    },
    "report_defaults": {
        "export_txt": True,
        "export_docx": True
    },
    "artifact_categories": [
        "Communication",
        "Account / User",
        "Media",
        "Location",
        "Browser / Internet",
        "File System",
        "Application Data",
        "System / Device",
        "Other"
    ]
}


def deep_merge(default, loaded):
    result = default.copy()
    for key, value in loaded.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def normalize_settings(settings):
    appearance = settings.get("appearance", {})
    if not isinstance(appearance, dict):
        appearance = {}
    theme = str(appearance.get("theme", "system")).lower()
    if theme not in {"system", "dark", "light"}:
        theme = "system"
    settings["appearance"] = {"theme": theme}

    examiners = settings.get("examiners", [])
    if not isinstance(examiners, list):
        examiners = []
    cleaned = []
    seen = set()
    for name in examiners:
        name = str(name).strip()
        if not name:
            continue
        key = name.lower()
        if key not in seen:
            cleaned.append(name)
            seen.add(key)
    default_examiner = str(settings.get("default_examiner", "")).strip()
    if default_examiner and default_examiner.lower() not in seen:
        cleaned.insert(0, default_examiner)
    settings["examiners"] = cleaned

    categories = settings.get("artifact_categories", [])
    if not isinstance(categories, list):
        categories = DEFAULT_SETTINGS["artifact_categories"]
    cat_clean = []
    cat_seen = set()
    for item in categories:
        item = str(item).strip()
        if item and item.lower() not in cat_seen:
            cat_clean.append(item)
            cat_seen.add(item.lower())
    settings["artifact_categories"] = cat_clean or DEFAULT_SETTINGS["artifact_categories"][:]

    report_defaults = settings.get("report_defaults", {})
    if not isinstance(report_defaults, dict):
        report_defaults = {}
    settings["report_defaults"] = {
        "export_txt": bool(report_defaults.get("export_txt", True)),
        "export_docx": bool(report_defaults.get("export_docx", True)),
    }
    return settings


def load_or_create_settings():
    if not SETTINGS_PATH.exists():
        save_settings(DEFAULT_SETTINGS.copy())
        return DEFAULT_SETTINGS.copy()
    try:
        with SETTINGS_PATH.open("r", encoding="utf-8") as f:
            loaded = json.load(f)
        return normalize_settings(deep_merge(DEFAULT_SETTINGS, loaded))
    except (OSError, json.JSONDecodeError):
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    settings = normalize_settings(settings)
    with SETTINGS_PATH.open("w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def safe_filename(value, fallback="NO_CASE"):
    value = str(value or "").strip() or fallback
    for char in '<>:"/\\|?*':
        value = value.replace(char, "_")
    value = value.replace(" ", "_")
    while "__" in value:
        value = value.replace("__", "_")
    return value.strip("_") or fallback


def get_default_root():
    return Path.home() / DEFAULT_ROOT_FOLDER_NAME


def get_output_paths(settings, case_number=None):
    output_settings = settings.get("output_paths", {})
    base_output_dir = str(output_settings.get("base_output_dir", "")).strip()
    reports_folder_name = str(output_settings.get("reports_folder_name", "reports")).strip() or "reports"
    saved_notes_folder_name = str(output_settings.get("saved_notes_folder_name", "saved_notes")).strip() or "saved_notes"
    attachments_folder_name = str(output_settings.get("attachments_folder_name", "attachments")).strip() or "attachments"

    root_path = Path(base_output_dir) if base_output_dir else get_default_root()
    if case_number:
        base_path = root_path / safe_filename(case_number) / TOOL_FOLDER_NAME
    else:
        base_path = root_path

    return {
        "root_path": root_path,
        "base_path": base_path,
        "reports_dir": base_path / reports_folder_name,
        "saved_notes_dir": base_path / saved_notes_folder_name,
        "attachments_dir": base_path / attachments_folder_name,
    }


def ensure_directories(settings, case_number=None):
    paths = get_output_paths(settings, case_number=case_number)
    paths["base_path"].mkdir(parents=True, exist_ok=True)
    paths["reports_dir"].mkdir(parents=True, exist_ok=True)
    paths["saved_notes_dir"].mkdir(parents=True, exist_ok=True)
    paths["attachments_dir"].mkdir(parents=True, exist_ok=True)
    return paths
