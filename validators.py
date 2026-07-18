"""Validation helpers for ByteCase Notes."""

def validate_notes_record(record):
    errors = []
    warnings = []
    case_info = record.get("case_info", {})
    if not case_info.get("case_number", "").strip():
        warnings.append("Case Number is blank.")
    if not case_info.get("examiner", "").strip():
        warnings.append("Examiner is blank.")
    if not record.get("narrative_notes", "").strip() and not record.get("artifacts", []):
        errors.append("Enter narrative notes or add at least one artifact reference before export.")
    return errors, warnings
