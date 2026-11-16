"""Banker's Algorithm Avoidance View.

Course: Solving Problems Using Modelling and Simulation (SPMS) - NEC00091
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np

from ui.theme import Theme
from simulation.simulation_engine import SimulationEngine
from algorithms.bankers import BankersResult, RequestResult


class BankersView(ttk.Frame):
    """Interactive GUI for Banker's Algorithm safety analysis and request simulation."""

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

        ttk.Label(header_card, text="Banker's Algorithm – Deadlock Avoidance", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            header_card,
            text="Calculates Need = Max - Allocation, derives safe sequences, and evaluates resource requests.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        # Top Control & Available Bar
        ctrl_card = ttk.Frame(self, style="Card.TFrame", padding=12)
        ctrl_card.pack(fill="x", padx=16, pady=4)

        row = ttk.Frame(ctrl_card, style="Card.TFrame")
        row.pack(fill="x")

        btn_run = ttk.Button(row, text="Run Safety Algorithm", style="Success.TButton", command=self._run_bankers)
        btn_run.pack(side="left", padx=(0, 16))

        self.avail_lbl = ttk.Label(row, text="Available Resources: [ - ]", style="Card.TLabel", font=Theme.FONT_BODY_BOLD)
        self.avail_lbl.pack(side="left", padx=8)

        # Status & Sequence Banner
        self.status_banner = tk.Frame(self, bg=Theme.INFO_BG, padx=12, pady=10, highlightbackground=Theme.BORDER_COLOR, highlightthickness=1)
        self.status_banner.pack(fill="x", padx=16, pady=6)

        self.status_title = tk.Label(self.status_banner, text="STATE: UNCHECKED", font=Theme.FONT_BODY_BOLD, bg=Theme.INFO_BG, fg=Theme.INFO)
        self.status_title.pack(anchor="w")

        self.seq_lbl = tk.Label(self.status_banner, text="Safe Sequence: Run algorithm to determine safe ordering.", font=Theme.FONT_BODY, bg=Theme.INFO_BG, fg=Theme.TEXT_MAIN)
        self.seq_lbl.pack(anchor="w", pady=(2, 0))

        # Main Split: Left = Matrices Table, Right = Step-by-Step Trace Table
        split_frame = ttk.Frame(self, style="TFrame")
        split_frame.pack(fill="both", expand=True, padx=16, pady=6)
        split_frame.columnconfigure(0, weight=1)
        split_frame.columnconfigure(1, weight=1)
        split_frame.rowconfigure(0, weight=1)

        # Left Card: Matrices Table
        left_card = ttk.Frame(split_frame, style="Card.TFrame", padding=12)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        ttk.Label(left_card, text="Resource Matrices (Allocation, Max, Need)", style="Section.TLabel").pack(anchor="w", pady=(0, 6))

        mat_cols = ("proc", "alloc", "max", "need")
        self.mat_tree = ttk.Treeview(left_card, columns=mat_cols, show="headings", height=8)
        self.mat_tree.heading("proc", text="Process")
        self.mat_tree.heading("alloc", text="Allocation")
        self.mat_tree.heading("max", text="Maximum Claim")
        self.mat_tree.heading("need", text="Need (Max - Alloc)")

        self.mat_tree.column("proc", width=80, anchor="center")
        self.mat_tree.column("alloc", width=110, anchor="center")
        self.mat_tree.column("max", width=110, anchor="center")
        self.mat_tree.column("need", width=110, anchor="center")

        mat_scroll = ttk.Scrollbar(left_card, orient="vertical", command=self.mat_tree.yview)
        self.mat_tree.configure(yscrollcommand=mat_scroll.set)
        self.mat_tree.pack(side="left", fill="both", expand=True)
        mat_scroll.pack(side="right", fill="y")

        # Right Card: Step-by-Step Trace
        right_card = ttk.Frame(split_frame, style="Card.TFrame", padding=12)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        ttk.Label(right_card, text="Step-by-Step Safety Algorithm Trace", style="Section.TLabel").pack(anchor="w", pady=(0, 6))

        trace_cols = ("step", "proc", "work_before", "can_run", "work_after")
        self.trace_tree = ttk.Treeview(right_card, columns=trace_cols, show="headings", height=8)
        self.trace_tree.heading("step", text="Step")
        self.trace_tree.heading("proc", text="Process")
        self.trace_tree.heading("work_before", text="Work Before")
        self.trace_tree.heading("can_run", text="Need <= Work?")
        self.trace_tree.heading("work_after", text="Work After")

        self.trace_tree.column("step", width=50, anchor="center")
        self.trace_tree.column("proc", width=70, anchor="center")
        self.trace_tree.column("work_before", width=100, anchor="center")
        self.trace_tree.column("can_run", width=95, anchor="center")
        self.trace_tree.column("work_after", width=100, anchor="center")

        trace_scroll = ttk.Scrollbar(right_card, orient="vertical", command=self.trace_tree.yview)
        self.trace_tree.configure(yscrollcommand=trace_scroll.set)
        self.trace_tree.pack(side="left", fill="both", expand=True)
        trace_scroll.pack(side="right", fill="y")

        # Bottom Card: Resource-Request Simulator
        req_card = ttk.Frame(self, style="Card.TFrame", padding=12)
        req_card.pack(fill="x", padx=16, pady=(6, 16))

        ttk.Label(req_card, text="Dynamic Resource-Request Algorithm Simulator", style="Section.TLabel").pack(anchor="w", pady=(0, 6))

        req_row = ttk.Frame(req_card, style="Card.TFrame")
        req_row.pack(fill="x")

        ttk.Label(req_row, text="Requesting Process:", style="Card.TLabel", font=Theme.FONT_BODY_BOLD).pack(side="left", padx=(0, 4))
        self.req_proc_var = tk.StringVar()
        self.req_proc_combo = ttk.Combobox(req_row, textvariable=self.req_proc_var, state="readonly", width=8, font=Theme.FONT_BODY)
        self.req_proc_combo.pack(side="left", padx=(0, 16))

        ttk.Label(req_row, text="Request Vector (comma-separated):", style="Card.TLabel", font=Theme.FONT_BODY_BOLD).pack(side="left", padx=(0, 4))
        self.req_vec_entry = tk.Entry(req_row, width=18, font=Theme.FONT_MONO)
        self.req_vec_entry.pack(side="left", padx=(0, 16))

        btn_req = ttk.Button(req_row, text="Evaluate Request", style="Primary.TButton", command=self._evaluate_request)
        btn_req.pack(side="left", padx=6)

        self.req_feedback_lbl = ttk.Label(req_card, text="", style="Muted.TLabel")
        self.req_feedback_lbl.pack(anchor="w", pady=(6, 0))

    def _run_bankers(self) -> None:
        result = self.engine.run_bankers()
        self._display_safety_result(result)

    def _display_safety_result(self, result: BankersResult) -> None:
        if result.is_safe:
            self.status_banner.config(bg=Theme.SUCCESS_BG)
            self.status_title.config(text="SYSTEM STATE: SAFE", fg=Theme.SUCCESS, bg=Theme.SUCCESS_BG)
            seq_str = "  ➔  ".join(result.safe_sequence_names)
            self.seq_lbl.config(
                text=f"Safe Execution Sequence: < {seq_str} >\n{result.explanation}",
                bg=Theme.SUCCESS_BG,
            )
        else:
            self.status_banner.config(bg=Theme.DANGER_BG)
            self.status_title.config(text="SYSTEM STATE: UNSAFE (POTENTIAL DEADLOCK)", fg=Theme.DANGER, bg=Theme.DANGER_BG)
            self.seq_lbl.config(
                text=f"No complete safe sequence could be formed!\n{result.explanation}",
                bg=Theme.DANGER_BG,
            )

        # Populate trace table
        for item in self.trace_tree.get_children():
            self.trace_tree.delete(item)

        for step in result.steps:
            can_str = "YES (Satisfied)" if step.can_allocate else "NO (Blocked)"
            self.trace_tree.insert(
                "",
                "end",
                values=(
                    step.step_num,
                    step.process_name,
                    str(step.work_before),
                    can_str,
                    str(step.work_after),
                ),
            )

    def _evaluate_request(self) -> None:
        p_name = self.req_proc_var.get()
        if not p_name:
            messagebox.showwarning("Input Error", "Please select a requesting process.")
            return

        pid = next((p.pid for p in self.engine.processes if p.name == p_name), None)
        if pid is None:
            return

        raw_vec = self.req_vec_entry.get().strip()
        try:
            req_vec = [int(x.strip()) for x in raw_vec.split(",") if x.strip()]
        except ValueError:
            messagebox.showerror("Format Error", "Request vector must be comma-separated integers (e.g. '1, 0, 2').")
            return

        num_res = self.engine.resource_manager.num_resources
        if len(req_vec) != num_res:
            messagebox.showerror("Dimension Error", f"Request vector must contain exactly {num_res} values.")
            return

        result = self.engine.request_resources(pid, req_vec)

        if result.granted:
            self.req_feedback_lbl.config(
                text=f"✓ GRANTED: {result.reason}",
                foreground=Theme.SUCCESS,
            )
            messagebox.showinfo("Request Granted", result.reason)
            self.refresh()
            if self.on_update:
                self.on_update()
        else:
            self.req_feedback_lbl.config(
                text=f"✗ DENIED: {result.reason}",
                foreground=Theme.DANGER,
            )
            messagebox.showwarning("Request Denied", result.reason)

    def refresh(self) -> None:
        """Update tables and available resources."""
        alloc, max_m, need, req, avail, total = self.engine.get_matrices()
        r_names = self.engine.resource_manager.resource_names

        avail_text = ", ".join([f"{r_names[j]}={avail[j]}" for j in range(len(r_names))])
        self.avail_lbl.config(text=f"Available Resources: [ {avail_text} ]")

        # Update process choices
        p_names = [p.name for p in self.engine.processes]
        self.req_proc_combo["values"] = p_names
        if p_names and not self.req_proc_var.get():
            self.req_proc_combo.current(0)

        # Update matrices table
        for item in self.mat_tree.get_children():
            self.mat_tree.delete(item)

        for i, p in enumerate(self.engine.processes):
            self.mat_tree.insert(
                "",
                "end",
                values=(
                    p.name,
                    str(alloc[i].tolist()),
                    str(max_m[i].tolist()),
                    str(need[i].tolist()),
                ),
            )

        # Auto-run safety check if not executed yet
        if self.engine.last_bankers_result:
            self._display_safety_result(self.engine.last_bankers_result)
        else:
            self._run_bankers()

