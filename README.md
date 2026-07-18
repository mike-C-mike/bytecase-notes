# ByteCase Notes

**ByteCase Notes** is a local-first examiner notes workspace for writing narrative notes while maintaining a structured artifact index.

It is part of the **ByteCase** toolset by **Forensics Byte**.

## Version

```text
v0.4.0 - Reference helper and note block workflow
```

## What this tool does

ByteCase Notes helps an examiner:

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
- Copy supporting files into the case notes attachments folder during export.
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
4. Reference artifacts in notes using [ART-001], [ART-002], etc.
5. Use Insert Note Block when a simple structure helps.
6. Use Check Refs to compare narrative references against the artifact index.
7. Add optional supporting files/screenshots to artifact references.
8. Review and export.
9. Reopen the saved JSON later when the notes need to continue.
```

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
