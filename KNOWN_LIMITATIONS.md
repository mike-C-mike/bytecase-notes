# Known Limitations

ByteCase Notes is an examiner notes workspace. It is intentionally limited to documentation support.

## Scope limitations

- Does not parse evidence.
- Does not extract forensic artifacts.
- Does not determine relevance, intent, authorship, attribution, or investigative conclusions.
- Does not replace examiner review, agency policy, lab SOP, legal review, or disclosure obligations.
- Does not replace a full DEMS, RMS, forensic suite, or case management platform.

## File handling limitations

- Supporting files and images are copied into the case notes attachments folder during export.
- The original source files are not modified by ByteCase Notes.
- DOCX image embedding is best effort and non-blocking.
- Very large images may increase DOCX size or fail to embed depending on Word/python-docx behavior.
- Preview support depends on image support available through Tkinter on the local workstation.

## Reference limitations

- The reference checker is a documentation quality-control helper.
- It checks whether narrative references such as `[ART-001]` match the artifact index.
- It does not prove that an artifact is relevant, accurate, complete, or correctly interpreted.

## Output limitations

- JSON is intended for continuity and later reopening in ByteCase Notes.
- TXT and DOCX reports are documentation outputs and may still require agency review, formatting, and redaction before disclosure or court use.
