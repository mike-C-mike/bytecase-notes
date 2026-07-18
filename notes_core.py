"""Core record building and exports for ByteCase Notes."""
import copy
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from docx_exporter import save_docx_notes
from settings_service import APP_NAME, APP_VERSION, ensure_directories, safe_filename

ARTIFACT_REF_PATTERN = re.compile(
    r"(?<![A-Z0-9])(?P<open>\[?)\s*ART\s*[- ]\s*(?P<number>\d{3,})\s*(?P<close>\]?)(?![A-Z0-9])",
    re.IGNORECASE,
)


def normalize_artifact_reference(number: str) -> str:
    """Return the standard ART-### form for a captured artifact reference number."""
    return f"ART-{int(number):03d}"


def extract_artifact_reference_matches(text: str) -> List[Dict[str, str]]:
    """Return artifact reference matches with raw text and canonical IDs.

    The preferred writing style is [ART-001], but the checker also recognizes
    common variants such as ART-001, art-001, and ART 001 so handwritten notes
    are not missed.
    """
    matches = []
    for match in ARTIFACT_REF_PATTERN.finditer(text or ""):
        number = match.group("number")
        canonical = normalize_artifact_reference(number)
        raw_text = match.group(0)
        standard_text = f"[{canonical}]"
        is_standard = raw_text.strip().upper() == standard_text
        matches.append({
            "artifact_id": canonical,
            "raw_text": raw_text,
            "standard_text": standard_text,
            "is_standard": is_standard,
        })
    return matches


def extract_artifact_references(text: str) -> List[str]:
    """Return unique artifact references found in narrative notes, preserving first-seen order."""
    refs = []
    seen = set()
    for match in extract_artifact_reference_matches(text):
        ref = match["artifact_id"]
        if ref not in seen:
            refs.append(ref)
            seen.add(ref)
    return refs


def build_reference_audit(narrative_notes: str, artifacts: List[Dict[str, str]]) -> Dict[str, object]:
    """Compare [ART-###] references in notes against the structured artifact index."""
    reference_matches = extract_artifact_reference_matches(narrative_notes)
    referenced_ids = []
    seen_refs = set()
    non_standard_references = []
    for ref_match in reference_matches:
        ref = ref_match["artifact_id"]
        if ref not in seen_refs:
            referenced_ids.append(ref)
            seen_refs.add(ref)
        if not ref_match.get("is_standard"):
            display_value = f"{ref_match.get('raw_text', '').strip()} -> {ref_match.get('standard_text', '')}"
            if display_value not in non_standard_references:
                non_standard_references.append(display_value)

    artifact_ids = []
    seen_artifacts = set()
    duplicate_artifact_ids = []

    for artifact in artifacts or []:
        artifact_id = str(artifact.get("artifact_id", "")).strip().upper()
        if not artifact_id:
            continue
        if artifact_id in seen_artifacts and artifact_id not in duplicate_artifact_ids:
            duplicate_artifact_ids.append(artifact_id)
        if artifact_id not in seen_artifacts:
            artifact_ids.append(artifact_id)
            seen_artifacts.add(artifact_id)

    missing_from_index = [ref for ref in referenced_ids if ref not in seen_artifacts]
    not_referenced_in_notes = [artifact_id for artifact_id in artifact_ids if artifact_id not in referenced_ids]

    return {
        "referenced_artifact_ids": referenced_ids,
        "indexed_artifact_ids": artifact_ids,
        "missing_from_artifact_index": missing_from_index,
        "not_referenced_in_notes": not_referenced_in_notes,
        "duplicate_artifact_ids": duplicate_artifact_ids,
        "non_standard_references": non_standard_references,
        "preferred_reference_style": "[ART-001]",
        "reference_count": len(referenced_ids),
        "artifact_count": len(artifact_ids),
    }


def build_reference_audit_text(audit: Dict[str, object]) -> str:
    lines = []
    lines.append("Referenced in notes: " + (", ".join(audit.get("referenced_artifact_ids", [])) or "None"))
    lines.append("Indexed artifacts: " + (", ".join(audit.get("indexed_artifact_ids", [])) or "None"))

    missing = audit.get("missing_from_artifact_index", [])
    unused = audit.get("not_referenced_in_notes", [])
    duplicates = audit.get("duplicate_artifact_ids", [])
    non_standard = audit.get("non_standard_references", [])

    if missing:
        lines.append("References missing from artifact index: " + ", ".join(missing))
    else:
        lines.append("References missing from artifact index: None")

    if unused:
        lines.append("Indexed artifacts not referenced in notes: " + ", ".join(unused))
    else:
        lines.append("Indexed artifacts not referenced in notes: None")

    if duplicates:
        lines.append("Duplicate artifact IDs: " + ", ".join(duplicates))
    else:
        lines.append("Duplicate artifact IDs: None")

    if non_standard:
        lines.append("References found outside preferred [ART-001] format: " + "; ".join(non_standard))
    else:
        lines.append("References found outside preferred [ART-001] format: None")

    return "\n".join(lines)


def next_artifact_id(artifacts: List[Dict[str, str]]) -> str:
    highest = 0
    for artifact in artifacts:
        value = str(artifact.get("artifact_id", "")).upper().replace("ART-", "")
        try:
            highest = max(highest, int(value))
        except ValueError:
            continue
    return f"ART-{highest + 1:03d}"


def load_notes_json(path: str) -> Dict[str, object]:
    notes_path = Path(path)
    with notes_path.open("r", encoding="utf-8") as f:
        record = json.load(f)

    if not isinstance(record, dict):
        raise ValueError("Notes JSON did not contain an object.")

    case_info = record.get("case_info")
    if not isinstance(case_info, dict):
        raise ValueError("Notes JSON does not contain a valid case_info object.")

    artifacts = record.get("artifacts", [])
    if not isinstance(artifacts, list):
        raise ValueError("Notes JSON does not contain a valid artifacts list.")

    return record


def copy_supporting_files(record: Dict[str, object], attachments_dir: Path) -> Dict[str, object]:
    updated = copy.deepcopy(record)
    attachments_dir.mkdir(parents=True, exist_ok=True)

    for artifact in updated.get("artifacts", []):
        original_path = str(artifact.get("supporting_file_path", "")).strip()

        if not original_path:
            continue

        source_path = Path(original_path)

        if not source_path.exists() or not source_path.is_file():
            artifact["attachment_copy_error"] = "Supporting file path was not found or was not a file."
            continue

        artifact_id = safe_filename(artifact.get("artifact_id", "ART"), "ART")
        destination_name = f"{artifact_id}_{safe_filename(source_path.stem, 'supporting_file')}{source_path.suffix}"
        destination_path = attachments_dir / destination_name

        counter = 1
        while destination_path.exists():
            destination_name = f"{artifact_id}_{safe_filename(source_path.stem, 'supporting_file')}_{counter}{source_path.suffix}"
            destination_path = attachments_dir / destination_name
            counter += 1

        try:
            shutil.copy2(source_path, destination_path)
            artifact["copied_supporting_file"] = str(destination_path)
            artifact["supporting_file_name"] = destination_path.name
        except OSError as exc:
            artifact["attachment_copy_error"] = str(exc)

    return updated


def build_notes_record(
    settings: Dict[str, object],
    case_number: str,
    agency_case_number: str,
    examiner: str,
    reviewed_by: str,
    source_description: str,
    examination_phase: str,
    narrative_notes: str,
    artifacts: List[Dict[str, str]],
    limitations: str,
) -> Dict[str, object]:
    return {
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
        "record_type": "Examiner notes workspace",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "department": {
            "department_name": settings.get("department_name", ""),
            "unit_name": settings.get("unit_name", ""),
        },
        "case_info": {
            "case_number": case_number.strip(),
            "agency_case_number": agency_case_number.strip(),
            "examiner": examiner.strip(),
            "reviewed_by": reviewed_by.strip(),
            "source_description": source_description.strip(),
            "examination_phase": examination_phase.strip(),
        },
        "narrative_notes": narrative_notes.strip(),
        "artifacts": artifacts,
        "limitations": limitations.strip(),
        "reference_audit": build_reference_audit(narrative_notes, artifacts),
        "boundary_notice": (
            "ByteCase Notes helps examiners document observations and artifact references. "
            "It does not parse evidence, determine evidentiary relevance, infer user intent, "
            "or replace examiner review."
        ),
    }


def build_txt_notes(record: Dict[str, object]) -> str:
    department = record.get("department", {})
    case_info = record.get("case_info", {})
    artifacts = record.get("artifacts", [])

    lines = []
    lines.append("BYTECASE NOTES REPORT")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"Generated By: {record.get('app_name', '')} v{record.get('app_version', '')}")
    lines.append(f"Created At: {record.get('created_at', '')}")
    lines.append(f"Department / Agency: {department.get('department_name', '')}")
    lines.append(f"Unit: {department.get('unit_name', '')}")
    lines.append("")

    lines.append("CASE INFORMATION")
    lines.append("-" * 80)
    lines.append(f"Case Number: {case_info.get('case_number', '')}")
    lines.append(f"Agency Case Number: {case_info.get('agency_case_number', '')}")
    lines.append(f"Examiner: {case_info.get('examiner', '')}")
    lines.append(f"Reviewed By: {case_info.get('reviewed_by', '')}")
    lines.append(f"Source Description: {case_info.get('source_description', '')}")
    lines.append(f"Examination Phase: {case_info.get('examination_phase', '')}")
    lines.append("")

    lines.append("NARRATIVE NOTES")
    lines.append("-" * 80)
    lines.append(record.get("narrative_notes", ""))
    lines.append("")

    lines.append("ARTIFACT INDEX")
    lines.append("-" * 80)
    if artifacts:
        for artifact in artifacts:
            lines.append(f"{artifact.get('artifact_id', '')}: {artifact.get('title', '')}")
            lines.append(f"  Category: {artifact.get('category', '')}")
            lines.append(f"  Source Item: {artifact.get('source_item', '')}")
            lines.append(f"  Tool / Source: {artifact.get('tool_source', '')}")
            lines.append(f"  Artifact Location: {artifact.get('artifact_location', '')}")
            lines.append(f"  Supporting File: {artifact.get('supporting_file_path', '')}")
            if artifact.get("copied_supporting_file"):
                lines.append(f"  Copied Supporting File: {artifact.get('copied_supporting_file', '')}")
            if artifact.get("attachment_copy_error"):
                lines.append(f"  Supporting File Copy Error: {artifact.get('attachment_copy_error', '')}")
            lines.append(f"  Date / Time: {artifact.get('date_time', '')}")
            lines.append(f"  Summary: {artifact.get('summary', '')}")
            lines.append(f"  Notes: {artifact.get('notes', '')}")
            lines.append("")
    else:
        lines.append("No artifact references were added.")
        lines.append("")

    lines.append("REFERENCE CHECK")
    lines.append("-" * 80)
    audit = record.get("reference_audit") or build_reference_audit(record.get("narrative_notes", ""), artifacts)
    lines.append(build_reference_audit_text(audit))
    lines.append("")

    limitations = record.get("limitations", "")
    if limitations:
        lines.append("LIMITATIONS / REVIEW NOTES")
        lines.append("-" * 80)
        lines.append(limitations)
        lines.append("")

    lines.append("BOUNDARY NOTICE")
    lines.append("-" * 80)
    lines.append(record.get("boundary_notice", ""))
    lines.append("")
    lines.append("=" * 80)
    lines.append("End of ByteCase Notes Report")
    lines.append("=" * 80)
    return "\n".join(lines)


def save_notes_outputs(record: Dict[str, object], settings: Dict[str, object]) -> Dict[str, Path]:
    case_number = record.get("case_info", {}).get("case_number", "")
    source = record.get("case_info", {}).get("source_description", "")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_filename = f"{safe_filename(case_number, 'NO_CASE')}_{safe_filename(source, 'notes')}_{timestamp}_notes"

    paths = ensure_directories(settings, case_number=case_number)
    record = copy_supporting_files(record, paths["attachments_dir"])
    outputs = {}

    json_path = paths["saved_notes_dir"] / f"{base_filename}.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
    outputs["JSON"] = json_path

    report_defaults = settings.get("report_defaults", {})
    if report_defaults.get("export_txt", True):
        txt_path = paths["reports_dir"] / f"{base_filename}.txt"
        with txt_path.open("w", encoding="utf-8") as f:
            f.write(build_txt_notes(record))
        outputs["TXT"] = txt_path

    if report_defaults.get("export_docx", True):
        docx_path = paths["reports_dir"] / f"{base_filename}.docx"
        save_docx_notes(record, docx_path)
        outputs["DOCX"] = docx_path

    return outputs
