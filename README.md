# ByteCase Notes

**ByteCase Notes** is a local-first examiner notes workspace for writing narrative notes while maintaining a structured artifact index.

It is part of the **ByteCase** toolset by **Forensics Byte**.

## Version

```text
v0.9.0 - Release candidate prep
```

## What this tool does

ByteCase Notes helps an examiner:

- Use a simple Start page with quick workflow actions and a readiness check.
- Record narrative examination notes.
- Add manually identified artifact references.
- Assign artifact IDs such as `ART-001`.
- Insert artifact references into narrative notes.
- Type artifact references directly in notes.
- Check whether artifact references in the notes exist in the artifact index.
- Identify artifact index entries that have not yet been referenced in narrative notes.
- Identify references typed outside the preferred `[ART-001]` format.
- Insert simple note blocks for observations, artifact review, follow-up, limitations, tool/process notes, and timestamps.
- Export notes with an artifact index.
- Save structured JSON for continuity.
- Reopen prior ByteCase Notes JSON workspaces.
- Add optional supporting files or screenshots to artifact references.
- Preview selected artifact images/screenshots using the system image viewer.
- Copy supporting files into the case notes attachments folder during export.
- Embed artifact images/screenshots in DOCX reports when enabled.
- Copy selected artifact references to the clipboard.
- Open a selected artifact's supporting file from the artifact index.
- Export optional TXT and DOCX reports.
- Save a department patch/logo image in Settings for DOCX branding and case packet capture.
- Review a workspace snapshot before export.
- Save an artifact and insert its reference into notes in one step.

## What this tool does not do

ByteCase Notes does **not**:

- Parse evidence.
- Extract artifacts.
- Interpret user activity.
- Determine evidentiary relevance.
- Make investigative conclusions.
- Replace examiner review.
- Replace forensic platforms such as Cellebrite, Magnet, EnCase, FTK, AXIOM, or other analysis tools.

It is a documentation and workflow companion.

## Basic workflow

The app is organized around a simple workflow:

```text
1. Case
2. Notes
3. Artifacts
4. Export
```

A **Start** page provides quick actions for continuing notes, adding an artifact, checking references, and moving to export. It also includes a **Ready Check** so the examiner can quickly see whether the workspace is missing case information, notes/artifacts, or artifact reference cleanup.

Suggested use:

```text
1. Enter case information.
2. Write narrative notes.
3. Add artifact references.
4. Use **Save + Insert Ref** when adding an artifact to immediately place `[ART-001]` into the narrative.
5. Reference artifacts in notes using [ART-001], [ART-002], etc.
6. Use Note Block when a simple structure helps.
7. Use Check Refs to compare narrative references against the artifact index.
8. Add optional supporting files/screenshots to artifact references.
9. Optional: add a department patch/logo in Settings for branded DOCX exports.
10. Review and export.
11. Reopen the saved JSON later when the notes need to continue.
```

## v0.9.0 release candidate notes

This sprint prepares ByteCase Notes for a GitHub pre-release candidate. The app keeps the simplified workflow from prior polish rounds and adds the files needed to build, package, verify, and publish a Windows pre-release.

Release prep additions include:

- Build instructions.
- PowerShell release build script.
- PyInstaller spec file.
- Release checklist.
- Known limitations.
- Unsigned Windows notice.
- Simple workflow guide.
- Requirements files.
- MIT license file.

No new runtime dependencies were added.

## Reference check

The preferred artifact reference format is:

```text
[ART-001]
```

The **Check Refs** action compares narrative references against the structured artifact index.

It reports:

- Artifact references found in the notes.
- Artifact IDs present in the artifact index.
- References used in notes but missing from the artifact index.
- Artifact index entries not yet referenced in the narrative notes.
- Duplicate artifact IDs.
- References typed outside the preferred `[ART-001]` format.

The checker also recognizes common variants such as `ART-001`, `art-001`, and `ART 001` so manually typed notes are not missed. The preferred export/report style remains `[ART-001]`.

This is a quality-control helper. It does not decide whether an artifact is relevant or important.

## Note blocks

The **Insert Note Block** button inserts simple editable structures into the narrative notes field.

Current blocks:

- Observation
- Artifact Review
- Follow-Up
- Limitation
- Tool / Process Note
- Timestamp Note

These blocks are only writing aids. The examiner should edit or delete any fields that do not apply.


## Artifact images / screenshots

Artifact records include a **Supporting File / Screenshot** field. Use it for a screenshot, exported image, PDF, text export, or other file that supports the note entry.

When the supporting file is an image (`.png`, `.jpg`, `.jpeg`, `.bmp`, `.gif`, `.tif`, or `.tiff`), ByteCase Notes can:

- Open the image with the system viewer from the artifact index.
- Copy the image into the case notes `attachments` folder during export.
- Mark the copied supporting file as an image in JSON/TXT/DOCX outputs.
- Embed the image under that artifact in the DOCX report when **Embed artifact images/screenshots in DOCX reports** is enabled.

Image embedding is optional and non-blocking. If an image cannot be embedded, the report still exports and records the issue.

## Department patch / logo

Settings includes an optional **Department Patch / Logo** image path. Use **Browse** to select a local image file such as a PNG or JPG department patch.

When notes are exported, ByteCase Notes:

- Stores the original image path in JSON/TXT/DOCX metadata.
- Copies the image into the case notes packet under `attachments\branding\`.
- Embeds the copied image near the top of the DOCX report when available.

Supported image extensions are `.png`, `.jpg`, `.jpeg`, `.bmp`, `.gif`, `.tif`, and `.tiff`. For best results, use a clear PNG or JPG patch/logo image.

## Output structure

Default output root:

```text
C:\Users\<user>\ByteCase\
```

Case output:

```text
ByteCase\
  <case_number>\
    notes\
      reports\
      saved_notes\
      attachments\
```

JSON is always exported. TXT and DOCX follow Settings defaults. Supporting files listed on artifact records are copied into `attachments` during export when the source file is available. Image supporting files can be embedded in DOCX reports when enabled. Department patch/logo images are copied into `attachments\branding` during export when configured and available.

## Dependency notes

Runtime dependencies:

- Python standard library
- Tkinter
- python-docx

`python-docx` is MIT licensed.

## License

This project is released under the MIT License. See `LICENSE`.
