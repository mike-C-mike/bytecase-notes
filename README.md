# ByteCase Notes

**ByteCase Notes** is a local-first examiner notes workspace for writing narrative notes while maintaining a structured artifact index.

It is part of the **ByteCase** toolset by **Forensics Byte**.

## Version

```text
v0.3.0 - Artifact reference check and artifact workflow polish
```

## What this tool does

ByteCase Notes helps an examiner:

- Record narrative examination notes.
- Add manually identified artifact references.
- Assign artifact IDs such as `ART-001`.
- Insert artifact references into narrative notes.
- Export notes with an artifact index.
- Save structured JSON for continuity.
- Reopen prior ByteCase Notes JSON workspaces.
- Add optional supporting files or screenshots to artifact references.
- Copy supporting files into the case notes attachments folder during export.
- Check whether `[ART-###]` references in narrative notes exist in the artifact index.
- Identify artifact index entries that have not yet been referenced in narrative notes.
- Copy selected artifact references to the clipboard.
- Open a selected artifact's supporting file from the artifact index.
- Export optional TXT and DOCX reports.

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

```text
1. Enter case information.
2. Write narrative notes.
3. Add artifact references.
4. Insert artifact IDs into notes as needed.
5. Use Check Refs to compare narrative references against the artifact index.
6. Add optional supporting files/screenshots to artifact references.
7. Review and export.
8. Reopen the saved JSON later when the notes need to continue.
```

## Reference check

The **Check Refs** action compares narrative references such as:

```text
[ART-001]
```

against the structured artifact index.

It reports:

- Artifact references found in the notes.
- Artifact IDs present in the artifact index.
- References used in notes but missing from the artifact index.
- Artifact index entries not yet referenced in the narrative notes.
- Duplicate artifact IDs.

This is a quality-control helper. It does not decide whether an artifact is relevant or important.

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

JSON is always exported. TXT and DOCX follow Settings defaults. Supporting files listed on artifact records are copied into `attachments` during export when the source file is available.

## Dependency notes

Runtime dependencies:

- Python standard library
- Tkinter
- python-docx

`python-docx` is MIT licensed.

## License

This project is intended for MIT License release.
