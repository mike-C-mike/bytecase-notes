# Build ByteCase Notes

ByteCase Notes can be run from source or packaged into a Windows executable with PyInstaller.

## Runtime requirements

- Python 3.10 or newer recommended
- python-docx

Install runtime dependencies:

```powershell
py -m pip install -r requirements.txt
```

Run from source:

```powershell
py main.py
```

## Build requirements

Install build dependencies:

```powershell
py -m pip install -r requirements-build.txt
```

## Build release package

From the repository root:

```powershell
Unblock-File .\build_release.ps1
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\build_release.ps1 -Version 0.9.0
```

Expected outputs:

```text
release\ByteCaseNotes-v0.9.0\
release\ByteCaseNotes-v0.9.0.zip
release\ByteCaseNotes-v0.9.0-SHA256SUMS.txt
```

## Signing note

This pre-release build is expected to be unsigned until a code signing certificate is available. See `UNSIGNED_WINDOWS_NOTICE.md`.
