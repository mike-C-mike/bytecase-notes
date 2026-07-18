"""GUI for ByteCase Notes."""
import os
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from bytecase_theme import apply_theme, configure_toplevel, get_current_theme, style_text_widget
from notes_core import build_notes_record, build_reference_audit_text, load_notes_json, next_artifact_id, save_notes_outputs
from settings_service import (
    APP_NAME,
    APP_SUBTITLE,
    APP_VERSION,
    PRODUCT_DOMAIN,
    PUBLISHER_NAME,
    ensure_directories,
    get_output_paths,
    load_or_create_settings,
    save_settings,
)
from validators import validate_notes_record

PHASES = ["Initial Review", "Acquisition Review", "Analysis", "Reporting", "Court / Disclosure Prep", "Other"]


class ScrollableFrame(ttk.Frame):
    def __init__(self, parent, colors, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.colors = colors
        self.canvas = tk.Canvas(self, highlightthickness=0, background=colors["app_background"])
        self.v_scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.h_scroll = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.inner = ttk.Frame(self.canvas)
        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    def _on_inner_configure(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.window_id, width=max(event.width, 1080))

    def _bind_mousewheel(self, _event=None):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_shift_mousewheel)

    def _unbind_mousewheel(self, _event=None):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Shift-MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_shift_mousewheel(self, event):
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")


class ByteCaseNotesApp:
    def __init__(self, root):
        self.root = root
        self.settings = load_or_create_settings()
        self.colors = apply_theme(self.root, self.settings)
        self.artifacts = []
        self.last_saved_folder = None

        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("1180x780")
        self.root.minsize(1080, 700)

        self.build_gui()
        self.load_defaults()

    def build_gui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        header = ttk.Frame(self.root, padding=(12, 10))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text=f"{APP_NAME} v{APP_VERSION}", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text=f"{APP_SUBTITLE} · {PUBLISHER_NAME} · {PRODUCT_DOMAIN}", style="Muted.TLabel").grid(row=1, column=0, sticky="w")
        ttk.Button(header, text="New", command=self.clear_workspace).grid(row=0, column=1, rowspan=2, padx=4)
        ttk.Button(header, text="Open Notes JSON", command=self.load_notes_workspace).grid(row=0, column=2, rowspan=2, padx=4)
        ttk.Button(header, text="Settings", command=self.open_settings_window).grid(row=0, column=3, rowspan=2, padx=4)
        ttk.Button(header, text="About", command=self.open_about).grid(row=0, column=4, rowspan=2, padx=4)
        ttk.Button(header, text="Open Output", command=self.open_output_folder).grid(row=0, column=5, rowspan=2, padx=4)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.build_case_tab()
        self.build_notes_tab()
        self.build_artifacts_tab()
        self.build_export_tab()

    def build_case_tab(self):
        frame = ScrollableFrame(self.notebook, self.colors)
        self.notebook.add(frame, text="Case")
        body = frame.inner
        body.columnconfigure(1, weight=1)

        ttk.Label(body, text="1. Case information", style="Title.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", pady=(8, 10))
        ttk.Label(body, text="Start here. This information appears in the notes report and artifact index.", style="Muted.TLabel").grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 12))

        self.case_number_var = tk.StringVar()
        self.agency_case_number_var = tk.StringVar()
        self.examiner_var = tk.StringVar()
        self.reviewed_by_var = tk.StringVar()
        self.source_description_var = tk.StringVar()
        self.phase_var = tk.StringVar(value="Analysis")

        self.add_labeled_entry(body, "Case Number", self.case_number_var, 2)
        self.add_labeled_entry(body, "Agency Case Number", self.agency_case_number_var, 3)
        self.add_labeled_combo(body, "Examiner", self.examiner_var, self.get_examiner_values(), 4)
        self.add_labeled_entry(body, "Reviewed By", self.reviewed_by_var, 5)
        self.add_labeled_entry(body, "Source Description", self.source_description_var, 6)
        self.add_labeled_combo(body, "Examination Phase", self.phase_var, PHASES, 7, readonly=True)

        notice = (
            "ByteCase Notes is for examiner documentation and artifact references. It does not parse evidence, "
            "interpret artifacts, infer user intent, or replace examiner review."
        )
        ttk.Label(body, text=notice, wraplength=920, style="Muted.TLabel").grid(row=8, column=0, columnspan=3, sticky="w", pady=(20, 0))

        ttk.Button(body, text="Next: Notes", style="Accent.TButton", command=lambda: self.notebook.select(1)).grid(row=9, column=2, sticky="e", pady=18)

    def build_notes_tab(self):
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text="Notes")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        top = ttk.Frame(frame)
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(0, weight=1)
        ttk.Label(top, text="2. Narrative notes", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(top, text="Write normally. Use artifact references like [ART-001] when you need to tie an observation to the artifact index.", style="Muted.TLabel").grid(row=1, column=0, sticky="w")

        button_row = ttk.Frame(frame)
        button_row.grid(row=1, column=0, sticky="ew", pady=(8, 8))
        ttk.Button(button_row, text="Insert Selected Artifact Reference", command=self.insert_selected_artifact_reference).pack(side="left", padx=4)
        ttk.Button(button_row, text="Add Artifact", command=self.open_artifact_window).pack(side="left", padx=4)
        ttk.Button(button_row, text="Check Refs", command=self.check_artifact_references).pack(side="left", padx=4)
        ttk.Button(button_row, text="Ref Help", command=self.open_reference_help).pack(side="left", padx=4)
        ttk.Button(button_row, text="Insert Note Block", command=self.open_note_block_window).pack(side="left", padx=4)
        ttk.Button(button_row, text="Next: Artifacts", style="Accent.TButton", command=lambda: self.notebook.select(2)).pack(side="right", padx=4)

        text_frame = ttk.Frame(frame)
        text_frame.grid(row=2, column=0, sticky="nsew")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        self.notes_text = tk.Text(text_frame, height=22)
        self.notes_text.grid(row=0, column=0, sticky="nsew")
        y = ttk.Scrollbar(text_frame, orient="vertical", command=self.notes_text.yview)
        y.grid(row=0, column=1, sticky="ns")
        self.notes_text.configure(yscrollcommand=y.set)
        style_text_widget(self.notes_text, self.colors)

    def build_artifacts_tab(self):
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text="Artifacts")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)
        ttk.Label(frame, text="3. Artifact index", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(frame, text="Add manually identified artifacts, screenshots, exports, or observations. Then reference them in notes as [ART-###].", style="Muted.TLabel").grid(row=1, column=0, sticky="w", pady=(0, 8))

        columns = ("artifact_id", "title", "category", "source_item", "tool_source", "location", "supporting_file")
        self.artifact_tree = ttk.Treeview(frame, columns=columns, show="headings", height=16)
        headings = {
            "artifact_id": "ID",
            "title": "Title",
            "category": "Category",
            "source_item": "Source Item",
            "tool_source": "Tool / Source",
            "location": "Location",
            "supporting_file": "Supporting File",
        }
        widths = {"artifact_id": 80, "title": 220, "category": 140, "source_item": 160, "tool_source": 160, "location": 300, "supporting_file": 260}
        for column in columns:
            self.artifact_tree.heading(column, text=headings[column])
            self.artifact_tree.column(column, width=widths[column], anchor="w")
        self.artifact_tree.grid(row=2, column=0, sticky="nsew")
        y = ttk.Scrollbar(frame, orient="vertical", command=self.artifact_tree.yview)
        x = ttk.Scrollbar(frame, orient="horizontal", command=self.artifact_tree.xview)
        self.artifact_tree.configure(yscrollcommand=y.set, xscrollcommand=x.set)
        y.grid(row=2, column=1, sticky="ns")
        x.grid(row=3, column=0, sticky="ew")

        buttons = ttk.Frame(frame)
        buttons.grid(row=4, column=0, sticky="ew", pady=10)
        ttk.Button(buttons, text="Add Artifact", command=self.open_artifact_window).pack(side="left", padx=4)
        ttk.Button(buttons, text="Edit Selected", command=self.edit_selected_artifact).pack(side="left", padx=4)
        ttk.Button(buttons, text="Remove Selected", command=self.remove_selected_artifact).pack(side="left", padx=4)
        ttk.Button(buttons, text="Copy Ref", command=self.copy_selected_artifact_reference).pack(side="left", padx=4)
        ttk.Button(buttons, text="Insert Reference in Notes", command=self.insert_selected_artifact_reference).pack(side="left", padx=4)
        ttk.Button(buttons, text="Open Supporting File", command=self.open_selected_supporting_file).pack(side="left", padx=4)
        ttk.Button(buttons, text="Next: Export", style="Accent.TButton", command=lambda: self.notebook.select(3)).pack(side="right", padx=4)

    def build_export_tab(self):
        frame = ScrollableFrame(self.notebook, self.colors)
        self.notebook.add(frame, text="Export")
        body = frame.inner
        body.columnconfigure(0, weight=1)
        ttk.Label(body, text="4. Review and export", style="Title.TLabel").grid(row=0, column=0, sticky="w", pady=(8, 8))
        ttk.Label(body, text="JSON is always saved for continuity. TXT and DOCX follow Settings defaults.", style="Muted.TLabel").grid(row=1, column=0, sticky="w", pady=(0, 8))

        self.limitations_text = tk.Text(body, height=7)
        ttk.Label(body, text="Limitations / Review Notes").grid(row=2, column=0, sticky="w", pady=(10, 4))
        self.limitations_text.grid(row=3, column=0, sticky="ew")
        style_text_widget(self.limitations_text, self.colors)

        preview_frame = ttk.LabelFrame(body, text="Current Summary", padding=10)
        preview_frame.grid(row=4, column=0, sticky="ew", pady=14)
        self.summary_var = tk.StringVar(value="No export has been reviewed yet.")
        ttk.Label(preview_frame, textvariable=self.summary_var, wraplength=980).pack(fill="x")

        buttons = ttk.Frame(body)
        buttons.grid(row=5, column=0, sticky="ew", pady=12)
        ttk.Button(buttons, text="Review Summary", command=self.review_summary).pack(side="left", padx=4)
        ttk.Button(buttons, text="Check Refs", command=self.check_artifact_references).pack(side="left", padx=4)
        ttk.Button(buttons, text="Export Notes", style="Accent.TButton", command=self.export_notes).pack(side="left", padx=4)
        ttk.Button(buttons, text="Save + Open Folder", command=self.export_and_open).pack(side="left", padx=4)
        ttk.Button(buttons, text="Open Last Folder", command=self.open_last_folder).pack(side="right", padx=4)

    def add_labeled_entry(self, parent, label, variable, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 8))
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, columnspan=2, sticky="ew", pady=5)

    def add_labeled_combo(self, parent, label, variable, values, row, readonly=False):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 8))
        state = "readonly" if readonly else "normal"
        ttk.Combobox(parent, textvariable=variable, values=values, state=state).grid(row=row, column=1, columnspan=2, sticky="ew", pady=5)

    def get_examiner_values(self):
        values = self.settings.get("examiners", [])
        return values if isinstance(values, list) else []

    def load_defaults(self):
        self.examiner_var.set(self.settings.get("default_examiner", ""))

    def build_record(self):
        return build_notes_record(
            settings=self.settings,
            case_number=self.case_number_var.get(),
            agency_case_number=self.agency_case_number_var.get(),
            examiner=self.examiner_var.get(),
            reviewed_by=self.reviewed_by_var.get(),
            source_description=self.source_description_var.get(),
            examination_phase=self.phase_var.get(),
            narrative_notes=self.notes_text.get("1.0", "end").strip(),
            artifacts=self.artifacts,
            limitations=self.limitations_text.get("1.0", "end").strip(),
        )

    def refresh_artifact_tree(self):
        for item in self.artifact_tree.get_children():
            self.artifact_tree.delete(item)
        for artifact in self.artifacts:
            self.artifact_tree.insert("", "end", iid=artifact["artifact_id"], values=(
                artifact.get("artifact_id", ""),
                artifact.get("title", ""),
                artifact.get("category", ""),
                artifact.get("source_item", ""),
                artifact.get("tool_source", ""),
                artifact.get("artifact_location", ""),
                artifact.get("supporting_file_path", ""),
            ))

    def clear_workspace(self):
        confirm = messagebox.askyesno("New Notes Workspace", "Clear the current notes workspace and start a new one?")
        if not confirm:
            return
        self.case_number_var.set("")
        self.agency_case_number_var.set("")
        self.examiner_var.set(self.settings.get("default_examiner", ""))
        self.reviewed_by_var.set("")
        self.source_description_var.set("")
        self.phase_var.set("Analysis")
        self.notes_text.delete("1.0", "end")
        self.limitations_text.delete("1.0", "end")
        self.artifacts = []
        self.refresh_artifact_tree()
        self.summary_var.set("New notes workspace started.")
        self.notebook.select(0)

    def load_notes_workspace(self):
        path = filedialog.askopenfilename(
            title="Open ByteCase Notes JSON",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
        )
        if not path:
            return
        try:
            record = load_notes_json(path)
        except Exception as exc:
            messagebox.showerror("Open Notes Error", f"Could not open notes JSON.\n\nDetails:\n{exc}")
            return
        self.populate_from_record(record)
        self.summary_var.set(f"Loaded notes workspace from:\n{path}")
        self.notebook.select(1)

    def populate_from_record(self, record):
        case_info = record.get("case_info", {})
        self.case_number_var.set(case_info.get("case_number", ""))
        self.agency_case_number_var.set(case_info.get("agency_case_number", ""))
        self.examiner_var.set(case_info.get("examiner", ""))
        self.reviewed_by_var.set(case_info.get("reviewed_by", ""))
        self.source_description_var.set(case_info.get("source_description", ""))
        self.phase_var.set(case_info.get("examination_phase", "Analysis") or "Analysis")

        self.notes_text.delete("1.0", "end")
        self.notes_text.insert("1.0", record.get("narrative_notes", ""))

        self.limitations_text.delete("1.0", "end")
        self.limitations_text.insert("1.0", record.get("limitations", ""))

        artifacts = record.get("artifacts", [])
        self.artifacts = artifacts if isinstance(artifacts, list) else []
        self.refresh_artifact_tree()

    def open_artifact_window(self, artifact=None):
        ArtifactWindow(self, artifact=artifact)

    def edit_selected_artifact(self):
        selected = self.artifact_tree.selection()
        if not selected:
            messagebox.showinfo("Edit Artifact", "Select an artifact first.")
            return
        artifact_id = selected[0]
        artifact = next((item for item in self.artifacts if item.get("artifact_id") == artifact_id), None)
        if artifact:
            self.open_artifact_window(artifact=artifact)

    def remove_selected_artifact(self):
        selected = self.artifact_tree.selection()
        if not selected:
            messagebox.showinfo("Remove Artifact", "Select an artifact first.")
            return
        artifact_id = selected[0]
        confirm = messagebox.askyesno("Remove Artifact", f"Remove {artifact_id} from the artifact index?")
        if not confirm:
            return
        self.artifacts = [item for item in self.artifacts if item.get("artifact_id") != artifact_id]
        self.refresh_artifact_tree()

    def save_artifact(self, artifact):
        existing_id = artifact.get("artifact_id")
        for index, item in enumerate(self.artifacts):
            if item.get("artifact_id") == existing_id:
                self.artifacts[index] = artifact
                break
        else:
            self.artifacts.append(artifact)
        self.refresh_artifact_tree()

    def insert_selected_artifact_reference(self):
        selected = self.artifact_tree.selection()
        if not selected and self.artifacts:
            selected = [self.artifacts[-1].get("artifact_id")]
        if not selected:
            messagebox.showinfo("Insert Artifact Reference", "Add or select an artifact first.")
            return
        ref = f"[{selected[0]}]"
        self.notes_text.insert("insert", ref)
        self.notebook.select(1)
        self.notes_text.focus_set()

    def copy_selected_artifact_reference(self):
        selected = self.artifact_tree.selection()
        if not selected:
            messagebox.showinfo("Copy Artifact Reference", "Select an artifact first.")
            return
        ref = f"[{selected[0]}]"
        self.root.clipboard_clear()
        self.root.clipboard_append(ref)
        self.summary_var.set(f"Copied artifact reference: {ref}")

    def get_selected_artifact(self):
        selected = self.artifact_tree.selection()
        if not selected:
            return None
        artifact_id = selected[0]
        return next((item for item in self.artifacts if item.get("artifact_id") == artifact_id), None)

    def open_selected_supporting_file(self):
        artifact = self.get_selected_artifact()
        if not artifact:
            messagebox.showinfo("Open Supporting File", "Select an artifact first.")
            return
        path = artifact.get("supporting_file_path") or artifact.get("copied_supporting_file")
        if not path:
            messagebox.showinfo("Open Supporting File", "The selected artifact does not have a supporting file path.")
            return
        if not os.path.exists(path):
            messagebox.showerror("Open Supporting File", f"The supporting file was not found:\n\n{path}")
            return
        try:
            os.startfile(path)
        except OSError as exc:
            messagebox.showerror("Open Supporting File", str(exc))

    def check_artifact_references(self):
        record = self.build_record()
        audit = record.get("reference_audit", {})
        audit_text = build_reference_audit_text(audit)
        self.summary_var.set(audit_text)
        messagebox.showinfo("Artifact Reference Check", audit_text)

    def open_reference_help(self):
        messagebox.showinfo(
            "Artifact Reference Help",
            "Preferred reference format:\n"
            "  [ART-001]\n\n"
            "You may type references directly into notes. ByteCase Notes recognizes [ART-001] as the clean standard. "
            "The reference checker also looks for common variants like ART-001 or art 001 so they are not missed.\n\n"
            "Suggested workflow:\n"
            "1. Add the artifact to the Artifact Index.\n"
            "2. Reference it in narrative notes using [ART-001].\n"
            "3. Click Check Refs before export.\n\n"
            "Check Refs flags references that are missing from the artifact index, duplicate artifact IDs, indexed artifacts "
            "not mentioned in notes, and references typed outside the preferred bracketed format."
        )

    def open_note_block_window(self):
        NoteBlockWindow(self)

    def insert_note_block(self, block_name):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        blocks = {
            "Observation": (
                f"\nObservation - {now}\n"
                "Artifact reference: [ART-___]\n"
                "Observed item / location:\n"
                "Summary of observation:\n"
                "Follow-up needed:\n"
            ),
            "Artifact Review": (
                f"\nArtifact Review - {now}\n"
                "Artifact reference: [ART-___]\n"
                "Source item:\n"
                "Tool / view used:\n"
                "What was reviewed:\n"
                "Notes:\n"
            ),
            "Follow-Up": (
                f"\nFollow-Up - {now}\n"
                "Related artifact/reference: [ART-___]\n"
                "Question or issue:\n"
                "Action taken / next step:\n"
                "Status:\n"
            ),
            "Limitation": (
                f"\nLimitation / Caveat - {now}\n"
                "Related artifact/reference: [ART-___]\n"
                "Limitation observed:\n"
                "Impact on review/reporting:\n"
                "How it was handled:\n"
            ),
            "Tool / Process Note": (
                f"\nTool / Process Note - {now}\n"
                "Tool / process used:\n"
                "Version / settings if relevant:\n"
                "Purpose:\n"
                "Result / notes:\n"
            ),
            "Timestamp Note": f"\nTimestamp - {now}\nNotes:\n",
        }
        block = blocks.get(block_name)
        if not block:
            return
        self.notes_text.insert("insert", block)
        self.notebook.select(1)
        self.notes_text.focus_set()

    def review_summary(self):
        record = self.build_record()
        errors, warnings = validate_notes_record(record)
        artifact_count = len(record.get("artifacts", []))
        note_chars = len(record.get("narrative_notes", ""))
        summary = [
            f"Case: {record.get('case_info', {}).get('case_number', '') or '(blank)'}",
            f"Examiner: {record.get('case_info', {}).get('examiner', '') or '(blank)'}",
            f"Narrative characters: {note_chars}",
            f"Artifacts indexed: {artifact_count}",
        ]
        audit = record.get("reference_audit", {})
        if audit.get("missing_from_artifact_index"):
            summary.append("Missing artifact index entries: " + ", ".join(audit.get("missing_from_artifact_index", [])))
        if audit.get("not_referenced_in_notes"):
            summary.append("Indexed but not referenced in notes: " + ", ".join(audit.get("not_referenced_in_notes", [])))
        if warnings:
            summary.append("Warnings: " + "; ".join(warnings))
        if errors:
            summary.append("Blocking issue: " + "; ".join(errors))
        self.summary_var.set("\n".join(summary))

    def export_notes(self):
        record = self.build_record()
        errors, warnings = validate_notes_record(record)
        if errors:
            messagebox.showerror("Export Error", "Fix the following before export:\n\n" + "\n".join(errors))
            return None
        if warnings:
            proceed = messagebox.askyesno("Export Warnings", "Review these warnings:\n\n" + "\n".join(warnings) + "\n\nExport anyway?")
            if not proceed:
                return None
        try:
            outputs = save_notes_outputs(record, self.settings)
            first_path = next(iter(outputs.values()))
            self.last_saved_folder = first_path.parent
            details = "\n\n".join([f"{key}:\n{path}" for key, path in outputs.items()])
            messagebox.showinfo("Notes Exported", "ByteCase Notes exported successfully.\n\n" + details)
            return outputs
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not export notes.\n\nDetails:\n{e}")
            return None

    def export_and_open(self):
        outputs = self.export_notes()
        if outputs:
            self.open_last_folder()

    def open_last_folder(self):
        if not self.last_saved_folder:
            messagebox.showinfo("Open Folder", "No saved notes folder is available yet.")
            return
        try:
            os.startfile(self.last_saved_folder)
        except OSError as e:
            messagebox.showerror("Open Folder Error", str(e))

    def open_output_folder(self):
        paths = ensure_directories(self.settings, case_number=self.case_number_var.get().strip() or None)
        try:
            os.startfile(paths["base_path"])
        except OSError as e:
            messagebox.showerror("Open Output Error", str(e))

    def open_about(self):
        messagebox.showinfo(
            "About ByteCase Notes",
            f"{APP_NAME} v{APP_VERSION}\n{APP_SUBTITLE}\n\n"
            f"Part of the ByteCase toolset by {PUBLISHER_NAME}.\n{PRODUCT_DOMAIN}\n\n"
            "ByteCase Notes provides a narrative examiner notes workspace with a structured artifact index. "
            "It does not parse evidence, interpret artifacts, infer user intent, or replace examiner review."
        )

    def open_settings_window(self):
        SettingsWindow(self)

    def refresh_after_settings(self):
        self.settings = load_or_create_settings()
        self.colors = apply_theme(self.root, self.settings)
        style_text_widget(self.notes_text, self.colors)
        style_text_widget(self.limitations_text, self.colors)
        self.load_defaults()


class NoteBlockWindow:
    def __init__(self, app):
        self.app = app
        self.window = tk.Toplevel(app.root)
        self.window.title("Insert Note Block")
        self.window.geometry("540x420")
        self.window.transient(app.root)
        self.window.grab_set()
        configure_toplevel(self.window, app.colors)
        self.build_window()

    def build_window(self):
        self.window.columnconfigure(0, weight=1)
        ttk.Label(self.window, text="Insert Note Block", style="Title.TLabel").grid(row=0, column=0, sticky="w", padx=12, pady=(12, 4))
        ttk.Label(
            self.window,
            text="Choose a simple note structure to insert at the current cursor position. Edit the inserted text as needed.",
            wraplength=500,
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))

        button_frame = ttk.Frame(self.window, padding=(12, 4))
        button_frame.grid(row=2, column=0, sticky="nsew")
        button_frame.columnconfigure(0, weight=1)
        note_blocks = [
            "Observation",
            "Artifact Review",
            "Follow-Up",
            "Limitation",
            "Tool / Process Note",
            "Timestamp Note",
        ]
        for row, block_name in enumerate(note_blocks):
            ttk.Button(
                button_frame,
                text=block_name,
                command=lambda name=block_name: self.insert_and_close(name),
            ).grid(row=row, column=0, sticky="ew", pady=4)

        ttk.Button(self.window, text="Cancel", command=self.window.destroy).grid(row=3, column=0, sticky="e", padx=12, pady=12)

    def insert_and_close(self, block_name):
        self.app.insert_note_block(block_name)
        self.window.destroy()


class ArtifactWindow:
    def __init__(self, app, artifact=None):
        self.app = app
        self.artifact = artifact or {}
        self.window = tk.Toplevel(app.root)
        self.window.title("Artifact Reference")
        self.window.geometry("820x740")
        self.window.transient(app.root)
        self.window.grab_set()
        configure_toplevel(self.window, app.colors)
        self.build_window()
        self.load_values()

    def build_window(self):
        self.window.columnconfigure(1, weight=1)
        self.window.rowconfigure(9, weight=1)
        self.artifact_id_var = tk.StringVar(value=next_artifact_id(self.app.artifacts))
        self.title_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.source_item_var = tk.StringVar()
        self.tool_source_var = tk.StringVar()
        self.location_var = tk.StringVar()
        self.supporting_file_path_var = tk.StringVar()
        self.date_time_var = tk.StringVar()

        fields = [
            ("Artifact ID", self.artifact_id_var, 0),
            ("Title", self.title_var, 1),
            ("Category", self.category_var, 2),
            ("Source Item", self.source_item_var, 3),
            ("Tool / Source", self.tool_source_var, 4),
            ("Artifact Location", self.location_var, 5),
            ("Supporting File / Screenshot", self.supporting_file_path_var, 6),
            ("Date / Time", self.date_time_var, 7),
        ]
        for label, var, row in fields:
            ttk.Label(self.window, text=label).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            if label == "Category":
                ttk.Combobox(self.window, textvariable=var, values=self.app.settings.get("artifact_categories", []), state="normal").grid(row=row, column=1, sticky="ew", padx=10, pady=5)
            elif label == "Supporting File / Screenshot":
                ttk.Entry(self.window, textvariable=var).grid(row=row, column=1, sticky="ew", padx=10, pady=5)
                ttk.Button(self.window, text="Browse", command=self.browse_supporting_file).grid(row=row, column=2, sticky="e", padx=(0, 10), pady=5)
            else:
                ttk.Entry(self.window, textvariable=var).grid(row=row, column=1, sticky="ew", padx=10, pady=5)

        ttk.Label(self.window, text="Summary").grid(row=8, column=0, sticky="nw", padx=10, pady=5)
        self.summary_text = tk.Text(self.window, height=5)
        self.summary_text.grid(row=8, column=1, sticky="ew", padx=10, pady=5)
        style_text_widget(self.summary_text, self.app.colors)

        ttk.Label(self.window, text="Notes").grid(row=9, column=0, sticky="nw", padx=10, pady=5)
        self.notes_text = tk.Text(self.window, height=8)
        self.notes_text.grid(row=9, column=1, sticky="nsew", padx=10, pady=5)
        style_text_widget(self.notes_text, self.app.colors)

        buttons = ttk.Frame(self.window, padding=10)
        buttons.grid(row=10, column=0, columnspan=2, sticky="e")
        ttk.Button(buttons, text="Cancel", command=self.window.destroy).pack(side="right", padx=4)
        ttk.Button(buttons, text="Save Artifact", style="Accent.TButton", command=self.save).pack(side="right", padx=4)

    def load_values(self):
        if not self.artifact:
            return
        self.artifact_id_var.set(self.artifact.get("artifact_id", ""))
        self.title_var.set(self.artifact.get("title", ""))
        self.category_var.set(self.artifact.get("category", ""))
        self.source_item_var.set(self.artifact.get("source_item", ""))
        self.tool_source_var.set(self.artifact.get("tool_source", ""))
        self.location_var.set(self.artifact.get("artifact_location", ""))
        self.supporting_file_path_var.set(self.artifact.get("supporting_file_path", ""))
        self.date_time_var.set(self.artifact.get("date_time", ""))
        self.summary_text.insert("1.0", self.artifact.get("summary", ""))
        self.notes_text.insert("1.0", self.artifact.get("notes", ""))

    def browse_supporting_file(self):
        path = filedialog.askopenfilename(
            title="Select Supporting File or Screenshot",
            filetypes=[("All Files", "*.*")],
        )
        if path:
            self.supporting_file_path_var.set(path)

    def save(self):
        artifact_id = self.artifact_id_var.get().strip()
        if not artifact_id:
            messagebox.showerror("Artifact Error", "Artifact ID is required.")
            return
        artifact = {
            "artifact_id": artifact_id,
            "title": self.title_var.get().strip(),
            "category": self.category_var.get().strip(),
            "source_item": self.source_item_var.get().strip(),
            "tool_source": self.tool_source_var.get().strip(),
            "artifact_location": self.location_var.get().strip(),
            "supporting_file_path": self.supporting_file_path_var.get().strip(),
            "date_time": self.date_time_var.get().strip(),
            "summary": self.summary_text.get("1.0", "end").strip(),
            "notes": self.notes_text.get("1.0", "end").strip(),
        }
        self.app.save_artifact(artifact)
        self.window.destroy()


class SettingsWindow:
    def __init__(self, app):
        self.app = app
        self.settings = app.settings.copy()
        self.window = tk.Toplevel(app.root)
        self.window.title("Settings")
        self.window.geometry("760x620")
        self.window.transient(app.root)
        self.window.grab_set()
        configure_toplevel(self.window, app.colors)
        self.build_window()
        self.load_values()

    def build_window(self):
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        notebook = ttk.Notebook(self.window)
        notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.build_general_tab(notebook)
        self.build_output_tab(notebook)
        buttons = ttk.Frame(self.window, padding=10)
        buttons.grid(row=1, column=0, sticky="e")
        ttk.Button(buttons, text="Cancel", command=self.window.destroy).pack(side="right", padx=4)
        ttk.Button(buttons, text="Save", style="Accent.TButton", command=self.save).pack(side="right", padx=4)

    def build_general_tab(self, notebook):
        frame = ttk.Frame(notebook, padding=10)
        notebook.add(frame, text="General")
        frame.columnconfigure(1, weight=1)
        self.theme_var = tk.StringVar(value="system")
        self.department_name_var = tk.StringVar()
        self.unit_name_var = tk.StringVar()
        self.default_examiner_var = tk.StringVar()
        ttk.Label(frame, text="Theme").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Combobox(frame, textvariable=self.theme_var, values=["system", "dark", "light"], state="readonly").grid(row=0, column=1, sticky="ew", pady=5)
        ttk.Label(frame, text="Department / Agency").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(frame, textvariable=self.department_name_var).grid(row=1, column=1, sticky="ew", pady=5)
        ttk.Label(frame, text="Unit").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(frame, textvariable=self.unit_name_var).grid(row=2, column=1, sticky="ew", pady=5)
        ttk.Label(frame, text="Default Examiner").grid(row=3, column=0, sticky="w", pady=5)
        ttk.Entry(frame, textvariable=self.default_examiner_var).grid(row=3, column=1, sticky="ew", pady=5)
        ttk.Label(frame, text="Examiner List\n(one per line)").grid(row=4, column=0, sticky="nw", pady=5)
        self.examiners_text = tk.Text(frame, height=8)
        self.examiners_text.grid(row=4, column=1, sticky="ew", pady=5)
        style_text_widget(self.examiners_text, self.app.colors)
        ttk.Label(frame, text="Artifact Categories\n(one per line)").grid(row=5, column=0, sticky="nw", pady=5)
        self.categories_text = tk.Text(frame, height=8)
        self.categories_text.grid(row=5, column=1, sticky="ew", pady=5)
        style_text_widget(self.categories_text, self.app.colors)

    def build_output_tab(self, notebook):
        frame = ttk.Frame(notebook, padding=10)
        notebook.add(frame, text="Output")
        frame.columnconfigure(1, weight=1)
        self.output_root_var = tk.StringVar()
        self.reports_folder_var = tk.StringVar()
        self.saved_notes_folder_var = tk.StringVar()
        self.attachments_folder_var = tk.StringVar()
        self.export_txt_var = tk.BooleanVar(value=True)
        self.export_docx_var = tk.BooleanVar(value=True)
        ttk.Label(frame, text="ByteCase Output Root").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(frame, textvariable=self.output_root_var).grid(row=0, column=1, sticky="ew", pady=5)
        ttk.Button(frame, text="Browse", command=self.browse_output_root).grid(row=0, column=2, padx=4)
        ttk.Button(frame, text="Clear", command=lambda: self.output_root_var.set("")).grid(row=0, column=3, padx=4)
        helper = "Leave blank to use C:\\Users\\<user>\\ByteCase. Custom roots create <root>\\<case_number>\\notes."
        ttk.Label(frame, text=helper, wraplength=620, style="Muted.TLabel").grid(row=1, column=0, columnspan=4, sticky="w", pady=(0, 12))
        ttk.Label(frame, text="Reports Folder Name").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(frame, textvariable=self.reports_folder_var).grid(row=2, column=1, sticky="ew", pady=5)
        ttk.Label(frame, text="Saved Notes Folder Name").grid(row=3, column=0, sticky="w", pady=5)
        ttk.Entry(frame, textvariable=self.saved_notes_folder_var).grid(row=3, column=1, sticky="ew", pady=5)
        ttk.Label(frame, text="Attachments Folder Name").grid(row=4, column=0, sticky="w", pady=5)
        ttk.Entry(frame, textvariable=self.attachments_folder_var).grid(row=4, column=1, sticky="ew", pady=5)
        ttk.Checkbutton(frame, text="Export TXT reports by default", variable=self.export_txt_var).grid(row=5, column=0, columnspan=3, sticky="w", pady=8)
        ttk.Checkbutton(frame, text="Export DOCX reports by default", variable=self.export_docx_var).grid(row=6, column=0, columnspan=3, sticky="w", pady=8)
        ttk.Label(frame, text="JSON is always exported for continuity and later loading.", style="Muted.TLabel").grid(row=7, column=0, columnspan=4, sticky="w", pady=8)

    def load_values(self):
        self.theme_var.set(self.settings.get("appearance", {}).get("theme", "system"))
        self.department_name_var.set(self.settings.get("department_name", ""))
        self.unit_name_var.set(self.settings.get("unit_name", ""))
        self.default_examiner_var.set(self.settings.get("default_examiner", ""))
        self.examiners_text.insert("1.0", "\n".join(self.settings.get("examiners", [])))
        self.categories_text.insert("1.0", "\n".join(self.settings.get("artifact_categories", [])))
        output_paths = self.settings.get("output_paths", {})
        self.output_root_var.set(output_paths.get("base_output_dir", ""))
        self.reports_folder_var.set(output_paths.get("reports_folder_name", "reports"))
        self.saved_notes_folder_var.set(output_paths.get("saved_notes_folder_name", "saved_notes"))
        self.attachments_folder_var.set(output_paths.get("attachments_folder_name", "attachments"))
        defaults = self.settings.get("report_defaults", {})
        self.export_txt_var.set(bool(defaults.get("export_txt", True)))
        self.export_docx_var.set(bool(defaults.get("export_docx", True)))

    def browse_output_root(self):
        folder = filedialog.askdirectory(title="Select ByteCase Output Root")
        if folder:
            self.output_root_var.set(folder)

    def get_lines(self, widget):
        values = []
        seen = set()
        for line in widget.get("1.0", "end").splitlines():
            value = line.strip()
            if value and value.lower() not in seen:
                values.append(value)
                seen.add(value.lower())
        return values

    def save(self):
        self.settings["appearance"] = {"theme": self.theme_var.get()}
        self.settings["department_name"] = self.department_name_var.get().strip()
        self.settings["unit_name"] = self.unit_name_var.get().strip()
        self.settings["default_examiner"] = self.default_examiner_var.get().strip()
        self.settings["examiners"] = self.get_lines(self.examiners_text)
        self.settings["artifact_categories"] = self.get_lines(self.categories_text)
        self.settings["output_paths"] = {
            "base_output_dir": self.output_root_var.get().strip(),
            "reports_folder_name": self.reports_folder_var.get().strip() or "reports",
            "saved_notes_folder_name": self.saved_notes_folder_var.get().strip() or "saved_notes",
            "attachments_folder_name": self.attachments_folder_var.get().strip() or "attachments",
        }
        self.settings["report_defaults"] = {
            "export_txt": self.export_txt_var.get(),
            "export_docx": self.export_docx_var.get(),
        }
        save_settings(self.settings)
        self.app.refresh_after_settings()
        self.window.destroy()
        messagebox.showinfo("Settings Saved", "Settings saved successfully.")


def main():
    root = tk.Tk()
    ByteCaseNotesApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
