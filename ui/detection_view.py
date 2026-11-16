"""Deadlock Detection View.

Course: Solving Problems Using Modelling and Simulation (SPMS) - NEC00091
"""

import tkinter as tk
from tkinter import ttk
import numpy as np

from ui.theme import Theme
from simulation.simulation_engine import SimulationEngine
from algorithms.detection import DetectionResult


class DetectionView(ttk.Frame):
    """Interactive GUI for Multiple-Instance Deadlock Detection algorithm."""

    def __init__(self, parent: ttk.Frame, engine: SimulationEngine, on_update_callback=None):
        super().__init__(parent, style="TFrame")
        self.engine = engine
        self.on_update = on_update_callback

        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        # Header Card
        header_card = ttk.Frame(self, style="Card.TFrame", padding=14)
        header_card.pack(fill="x", padx=16, pady=(16, 8))

        ttk.Label(header_card, text="Deadlock Detection Algorithm", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            header_card,
            text="Examines Available vector, Allocation matrix, and Request matrix to identify circular wait deadlocks.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        # Top Control & Available Bar
        ctrl_card = ttk.Frame(self, style="Card.TFrame", padding=12)
        ctrl_card.pack(fill="x", padx=16, pady=4)

        row = ttk.Frame(ctrl_card, style="Card.TFrame")
        row.pack(fill="x")

        btn_run = ttk.Button(row, text="Run Deadlock Detection", style="Danger.TButton", command=self._run_detection)
        btn_run.pack(side="left", padx=(0, 16))

        self.avail_lbl = ttk.Label(row, text="Available Resources: [ - ]", style="Card.TLabel", font=Theme.FONT_BODY_BOLD)
        self.avail_lbl.pack(side="left", padx=8)

        # Status Banner
        self.status_banner = tk.Frame(self, bg=Theme.INFO_BG, padx=12, pady=10, highlightbackground=Theme.BORDER_COLOR, highlightthickness=1)
        self.status_banner.pack(fill="x", padx=16, pady=6)

        self.status_title = tk.Label(self.status_banner, text="DETECTION STATUS: UNCHECKED", font=Theme.FONT_BODY_BOLD, bg=Theme.INFO_BG, fg=Theme.INFO)
        self.status_title.pack(anchor="w")

        self.status_desc = tk.Label(self.status_banner, text="Click 'Run Deadlock Detection' to inspect process requests.", font=Theme.FONT_BODY, bg=Theme.INFO_BG, fg=Theme.TEXT_MAIN)
        self.status_desc.pack(anchor="w", pady=(2, 0))

        # Split: Left = Matrices (Alloc & Request), Right = Step Trace
        split_frame = ttk.Frame(self, style="TFrame")
        split_frame.pack(fill="both", expand=True, padx=16, pady=6)
        split_frame.columnconfigure(0, weight=1)
        split_frame.columnconfigure(1, weight=1)
        split_frame.rowconfigure(0, weight=1)

        # Left Card: Allocation vs Request Matrix
        left_card = ttk.Frame(split_frame, style="Card.TFrame", padding=12)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        ttk.Label(left_card, text="Current Allocation and Active Request Matrices", style="Section.TLabel").pack(anchor="w", pady=(0, 6))

        columns = ("proc", "alloc", "request", "is_deadlocked")
        self.matrix_tree = ttk.Treeview(left_card, columns=columns, show="headings", height=9)
        self.matrix_tree.heading("proc", text="Process")
        self.matrix_tree.heading("alloc", text="Allocation Matrix")
        self.matrix_tree.heading("request", text="Request Matrix")
        self.matrix_tree.heading("is_deadlocked", text="Deadlock Status")

        self.matrix_tree.column("proc", width=70, anchor="center")
        self.matrix_tree.column("alloc", width=120, anchor="center")
        self.matrix_tree.column("request", width=120, anchor="center")
        self.matrix_tree.column("is_deadlocked", width=110, anchor="center")

        mat_scroll = ttk.Scrollbar(left_card, orient="vertical", command=self.matrix_tree.yview)
        self.matrix_tree.configure(yscrollcommand=mat_scroll.set)
        self.matrix_tree.pack(side="left", fill="both", expand=True)
        mat_scroll.pack(side="right", fill="y")

        # Right Card: Step Trace
        right_card = ttk.Frame(split_frame, style="Card.TFrame", padding=12)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        ttk.Label(right_card, text="Detection Step-by-Step Execution Log", style="Section.TLabel").pack(anchor="w", pady=(0, 6))

        trace_cols = ("step", "proc", "req", "work_before", "can_finish", "work_after")
        self.trace_tree = ttk.Treeview(right_card, columns=trace_cols, show="headings", height=9)
        self.trace_tree.heading("step", text="Step")
        self.trace_tree.heading("proc", text="Process")
        self.trace_tree.heading("req", text="Request")
        self.trace_tree.heading("work_before", text="Work Before")
        self.trace_tree.heading("can_finish", text="Req <= Work?")
        self.trace_tree.heading("work_after", text="Work After")

        self.trace_tree.column("step", width=45, anchor="center")
        self.trace_tree.column("proc", width=65, anchor="center")
        self.trace_tree.column("req", width=85, anchor="center")
        self.trace_tree.column("work_before", width=95, anchor="center")
        self.trace_tree.column("can_finish", width=90, anchor="center")
        self.trace_tree.column("work_after", width=95, anchor="center")

        trace_scroll = ttk.Scrollbar(right_card, orient="vertical", command=self.trace_tree.yview)
        self.trace_tree.configure(yscrollcommand=trace_scroll.set)
        self.trace_tree.pack(side="left", fill="both", expand=True)
        trace_scroll.pack(side="right", fill="y")

        # Bottom Card: Academic Theorem Note
        note_card = ttk.Frame(self, style="Card.TFrame", padding=12)
        note_card.pack(fill="x", padx=16, pady=(4, 16))

        ttk.Label(
            note_card,
            text="Theoretical Principle: In multiple-instance systems, a process is deadlocked if and only if Finish[i] == False after "
                 "exhausting all processes whose pending requests can be met by current Work resources.",
            style="Muted.TLabel",
            wraplength=900,
        ).pack(anchor="w")

    def _run_detection(self) -> None:
        result = self.engine.run_detection()
        self._display_result(result)
        if self.on_update:
            self.on_update()

    def _display_result(self, result: DetectionResult) -> None:
        if result.is_deadlocked:
            self.status_banner.config(bg=Theme.DANGER_BG)
            self.status_title.config(text="STATUS: DEADLOCK DETECTED!", fg=Theme.DANGER, bg=Theme.DANGER_BG)
            dl_names = ", ".join(result.deadlocked_names)
            self.status_desc.config(
                text=f"Deadlocked Processes: [ {dl_names} ]\n{result.explanation}",
                bg=Theme.DANGER_BG,
            )
        else:
            self.status_banner.config(bg=Theme.SUCCESS_BG)
            self.status_title.config(text="STATUS: NO DEADLOCK DETECTED", fg=Theme.SUCCESS, bg=Theme.SUCCESS_BG)
            comp_names = "  ➔  ".join(result.completed_names)
            self.status_desc.config(
                text=f"Completion Sequence: < {comp_names} >\n{result.explanation}",
                bg=Theme.SUCCESS_BG,
            )

        # Update trace table
        for item in self.trace_tree.get_children():
            self.trace_tree.delete(item)

        for step in result.steps:
            can_str = "YES (Finished)" if step.can_finish else "NO (Blocked)"
            self.trace_tree.insert(
                "",
                "end",
                values=(
                    step.step_num,
                    step.process_name,
                    str(step.request_vector),
                    str(step.work_before),
                    can_str,
                    str(step.work_after),
                ),
            )

        # Update Matrix tree
        alloc, _, _, req, _, _ = self.engine.get_matrices()
        for item in self.matrix_tree.get_children():
            self.matrix_tree.delete(item)

        for i, p in enumerate(self.engine.processes):
            is_dl = i in result.deadlocked_processes
            status_tag = "DEADLOCKED" if is_dl else "Normal"
            self.matrix_tree.insert(
                "",
                "end",
                values=(
                    p.name,
                    str(alloc[i].tolist()),
                    str(req[i].tolist()),
                    status_tag,
                ),
            )

    def refresh(self) -> None:
        """Update tables and run detection."""
        alloc, max_m, need, req, avail, total = self.engine.get_matrices()
        r_names = self.engine.resource_manager.resource_names
        avail_text = ", ".join([f"{r_names[j]}={avail[j]}" for j in range(len(r_names))])
        self.avail_lbl.config(text=f"Available Resources: [ {avail_text} ]")

        if self.engine.last_detection_result:
            self._display_result(self.engine.last_detection_result)
        else:
            self._run_detection()

