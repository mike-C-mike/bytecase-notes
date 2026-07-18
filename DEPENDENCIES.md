# Dependencies

## Runtime

| Dependency | Purpose | License note |
|---|---|---|
| Python standard library | App logic, JSON, paths, datetime | Python Software Foundation License |
| Tkinter / Tcl-Tk | GUI | Bundled with Python installers on Windows |
| python-docx | DOCX report export | MIT License |

No parsing libraries or forensic artifact extraction dependencies are used. Department patch/logo image embedding uses python-docx and supported image files; no additional image-processing dependency is added.

## Build

Build packaging is not included in this sprint. PyInstaller packaging can be added in a later release sprint.
