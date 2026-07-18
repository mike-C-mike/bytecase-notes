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

    audit = record.get("reference_audit", {})
    missing = audit.get("missing_from_artifact_index", []) if isinstance(audit, dict) else []
    duplicates = audit.get("duplicate_artifact_ids", []) if isinstance(audit, dict) else []
    if missing:
        warnings.append("Notes reference artifact IDs that are not in the artifact index: " + ", ".join(missing))
    if duplicates:
        warnings.append("Duplicate artifact IDs exist in the artifact index: " + ", ".join(duplicates))
    non_standard = audit.get("non_standard_references", []) if isinstance(audit, dict) else []
    if non_standard:
        warnings.append("Some artifact references were found outside the preferred [ART-001] format: " + "; ".join(non_standard))
    return errors, warnings
