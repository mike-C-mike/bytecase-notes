# ByteCase Notes

**ByteCase Notes** is a local-first examiner notes workspace for writing narrative notes while maintaining a structured artifact index.

It is part of the **ByteCase** toolset by **Forensics Byte**.

## Version

```text
v0.1.0 - Initial development sprint
```

## What this tool does

ByteCase Notes helps an examiner:

- Record narrative examination notes.
- Add manually identified artifact references.
- Assign artifact IDs such as `ART-001`.
- Insert artifact references into narrative notes.
- Export notes with an artifact index.
- Save structured JSON for continuity.
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
5. Review and export.
```

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
```

JSON is always exported. TXT and DOCX follow Settings defaults.

## Dependency notes

Runtime dependencies:

- Python standard library
- Tkinter
- python-docx

`python-docx` is MIT licensed.

## License

This project is intended for MIT License release.
