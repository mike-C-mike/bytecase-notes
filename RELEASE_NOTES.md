# ByteCase Notes v0.9.0 Release Candidate

ByteCase Notes is a local-first examiner notes workspace for writing narrative notes while maintaining a structured artifact index.

## Release status

This is a pre-release candidate.

The Windows executable is expected to be unsigned until a code signing certificate is available.

## Highlights through v0.9.0

- Case and examiner information
- Free-form narrative notes
- Structured artifact index
- Automatic artifact IDs such as `ART-001`
- Manual and button-based artifact reference insertion
- Reference checker for `[ART-001]` style references
- Forgiving reference detection for common variants
- Missing/unused/duplicate artifact reference checks
- Supporting file and screenshot attachment support
- Artifact image preview
- Optional DOCX image embedding
- Optional department patch/logo image in DOCX reports
- Saved JSON workspace reopening
- Start tab with simple workflow and Ready Check
- JSON/TXT/DOCX export support
- ByteCase output structure under `ByteCase\<case_number>\notes\`
- Release build files and documentation

## v0.9.0 changes

- Bumped app version to v0.9.0.
- Added release candidate build documentation.
- Added PowerShell release build script.
- Added PyInstaller spec file.
- Added release checklist.
- Added known limitations.
- Added unsigned Windows notice.
- Added simple workflow guide.
- Added requirements files.
- Added MIT license file.

## Boundary notice

ByteCase Notes does not parse evidence, extract forensic artifacts, interpret user activity, or determine investigative conclusions. It supports examiner documentation, artifact indexing, reference checking, and report-ready note outputs.
