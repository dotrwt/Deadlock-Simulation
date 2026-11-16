"""Deadlock Recovery View.

Course: Solving Problems Using Modelling and Simulation (SPMS) - NEC00091
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np

from ui.theme import Theme
from simulation.simulation_engine import SimulationEngine
from algorithms.recovery import (
    VictimSelectionHeuristic,
    RecoveryRecord,
    select_victim,
)


class RecoveryView(ttk.Frame):
    """Interactive GUI for Deadlock Recovery via Termination and Preemption."""

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

        ttk.Label(header_card, text="Deadlock Recovery Mechanisms", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            header_card,
            text="Break circular wait conditions via Process Termination (heuristic or manual) or Resource Preemption.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        # Deadlocked Status & Overview Banner
        self.status_banner = tk.Frame(self, bg=Theme.INFO_BG, padx=12, pady=10, highlightbackground=Theme.BORDER_COLOR, highlightthickness=1)
        self.status_banner.pack(fill="x", padx=16, pady=4)

        self.status_lbl = tk.Label(self.status_banner, text="DEADLOCKED PROCESSES: [ None ]", font=Theme.FONT_BODY_BOLD, bg=Theme.INFO_BG, fg=Theme.INFO)
        self.status_lbl.pack(anchor="w")

        # Two-Column Recovery Strategies
        strategies_frame = ttk.Frame(self, style="TFrame")
        strategies_frame.pack(fill="x", padx=16, pady=6)
        strategies_frame.columnconfigure(0, weight=1)
        strategies_frame.columnconfigure(1, weight=1)

        # Strategy A: Process Termination Card
        term_card = ttk.Frame(strategies_frame, style="Card.TFrame", padding=12)
        term_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        ttk.Label(term_card, text="Strategy 1: Process Termination", style="Section.TLabel").pack(anchor="w", pady=(0, 6))

        ttk.Label(term_card, text="Heuristic Victim Selection Strategy:", style="Card.TLabel", font=Theme.FONT_BODY_BOLD).pack(anchor="w")
        self.heuristic_var = tk.StringVar(value=VictimSelectionHeuristic.LARGEST_ALLOCATION.value)
        heuristic_options = [h.value for h in VictimSelectionHeuristic]
        self.heuristic_combo = ttk.Combobox(
            term_card,
            textvariable=self.heuristic_var,
            values=heuristic_options,
            state="readonly",
            width=36,
            font=Theme.FONT_BODY,
        )
        self.heuristic_combo.pack(anchor="w", pady=(2, 8))
        self.heuristic_combo.bind("<<ComboboxSelected>>", self._on_heuristic_changed)

        # Manual Victim selector
        manual_row = ttk.Frame(term_card, style="Card.TFrame")
        manual_row.pack(fill="x", pady=2)
        ttk.Label(manual_row, text="Target Victim Process:", style="Card.TLabel").pack(side="left", padx=(0, 6))
        self.victim_var = tk.StringVar()
        self.victim_combo = ttk.Combobox(manual_row, textvariable=self.victim_var, state="readonly", width=12, font=Theme.FONT_BODY)
        self.victim_combo.pack(side="left")

        term_btn_row = ttk.Frame(term_card, style="Card.TFrame")
        term_btn_row.pack(fill="x", pady=(10, 0))

        btn_term_one = ttk.Button(term_btn_row, text="Terminate Victim", style="Danger.TButton", command=self._terminate_victim)
        btn_term_one.pack(side="left", padx=(0, 8))

        btn_term_all = ttk.Button(term_btn_row, text="Abort All Deadlocked", style="Secondary.TButton", command=self._abort_all_deadlocked)
        btn_term_all.pack(side="left")

        # Strategy B: Resource Preemption Card
        preempt_card = ttk.Frame(strategies_frame, style="Card.TFrame", padding=12)
        preempt_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        ttk.Label(preempt_card, text="Strategy 2: Resource Preemption", style="Section.TLabel").pack(anchor="w", pady=(0, 6))

        p_row1 = ttk.Frame(preempt_card, style="Card.TFrame")
        p_row1.pack(fill="x", pady=2)

        ttk.Label(p_row1, text="Victim Process:", style="Card.TLabel").pack(side="left", padx=(0, 6))
        self.preempt_proc_var = tk.StringVar()
        self.preempt_proc_combo = ttk.Combobox(p_row1, textvariable=self.preempt_proc_var, state="readonly", width=10, font=Theme.FONT_BODY)
        self.preempt_proc_combo.pack(side="left", padx=(0, 16))

        ttk.Label(p_row1, text="Resource:", style="Card.TLabel").pack(side="left", padx=(0, 6))
        self.preempt_res_var = tk.StringVar()
        self.preempt_res_combo = ttk.Combobox(p_row1, textvariable=self.preempt_res_var, state="readonly", width=10, font=Theme.FONT_BODY)
        self.preempt_res_combo.pack(side="left")

        p_row2 = ttk.Frame(preempt_card, style="Card.TFrame")
        p_row2.pack(fill="x", pady=(8, 2))

        ttk.Label(p_row2, text="Units to Preempt:", style="Card.TLabel").pack(side="left", padx=(0, 6))
        self.preempt_amount_var = tk.IntVar(value=1)
        sp_amt = ttk.Spinbox(p_row2, from_=1, to=20, textvariable=self.preempt_amount_var, width=5)
        sp_amt.pack(side="left", padx=(0, 16))

        btn_preempt = ttk.Button(p_row2, text="Execute Preemption", style="Primary.TButton", command=self._preempt_resource)
        btn_preempt.pack(side="left")

        # Before & After Audit Comparison Card
        audit_card = ttk.Frame(self, style="Card.TFrame", padding=12)
        audit_card.pack(fill="both", expand=True, padx=16, pady=(6, 16))

        ttk.Label(audit_card, text="Recovery Audit & State Transition Comparison", style="Section.TLabel").pack(anchor="w", pady=(0, 6))

        self.audit_text = tk.Text(
            audit_card,
            bg="#f8fafc",
            fg="#0f172a",
            font=Theme.FONT_MONO,
            wrap="word",
            relief="flat",
            padx=10,
            pady=10,
        )
        audit_scroll = ttk.Scrollbar(audit_card, orient="vertical", command=self.audit_text.yview)
        self.audit_text.configure(yscrollcommand=audit_scroll.set)
        self.audit_text.pack(side="left", fill="both", expand=True)
        audit_scroll.pack(side="right", fill="y")

    def _on_heuristic_changed(self, event=None) -> None:
        self._update_victim_options()

    def _update_victim_options(self) -> None:
        det = self.engine.last_detection_result
        if not det or not det.is_deadlocked:
            self.victim_combo["values"] = []
            self.preempt_proc_combo["values"] = []
            return

        dl_names = det.deadlocked_names
        self.victim_combo["values"] = dl_names
        self.preempt_proc_combo["values"] = dl_names

        # Auto-select victim based on chosen heuristic
        h_val = self.heuristic_var.get()
        heuristic = next((h for h in VictimSelectionHeuristic if h.value == h_val), VictimSelectionHeuristic.LARGEST_ALLOCATION)

        alloc, _, _, _, _, _ = self.engine.get_matrices()
        priorities = [p.priority for p in self.engine.processes]

        if heuristic != VictimSelectionHeuristic.MANUAL:
            rec_victim_idx = select_victim(
                deadlocked_indices=det.deadlocked_processes,
                allocation_matrix=alloc,
                priorities=priorities,
                heuristic=heuristic,
            )
            rec_victim_name = self.engine.processes[rec_victim_idx].name
            self.victim_var.set(rec_victim_name)
        elif dl_names and not self.victim_var.get():
            self.victim_combo.current(0)

        if dl_names and not self.preempt_proc_var.get():
            self.preempt_proc_combo.current(0)

    def _terminate_victim(self) -> None:
        v_name = self.victim_var.get()
        if not v_name:
            messagebox.showwarning("Selection", "No victim process is selected or system is not deadlocked.")
            return

        pid = next((p.pid for p in self.engine.processes if p.name == v_name), None)
        if pid is None:
            return

        record = self.engine.terminate_process(pid)
        self._display_recovery_record(record)
        messagebox.showinfo("Termination Recovery", record.summary)
        self.refresh()
        if self.on_update:
            self.on_update()

    def _abort_all_deadlocked(self) -> None:
        det = self.engine.last_detection_result
        if not det or not det.is_deadlocked:
            messagebox.showinfo("Notice", "System is not currently deadlocked.")
            return

        dl_pids = list(det.deadlocked_processes)
        for pid in dl_pids:
            self.engine.terminate_process(pid)

        messagebox.showinfo("Abort All", f"Terminated all {len(dl_pids)} deadlocked processes.")
        self.refresh()
        if self.on_update:
            self.on_update()

    def _preempt_resource(self) -> None:
        v_name = self.preempt_proc_var.get()
        r_name = self.preempt_res_var.get()
        amount = self.preempt_amount_var.get()

        if not v_name or not r_name:
            messagebox.showwarning("Selection", "Please select both a process and a resource to preempt.")
            return

        pid = next((p.pid for p in self.engine.processes if p.name == v_name), None)
        rid = next((i for i, name in enumerate(self.engine.resource_manager.resource_names) if name == r_name), None)

        if pid is None or rid is None:
            return

        try:
            record = self.engine.preempt_resource(pid, rid, amount)
            self._display_recovery_record(record)
            messagebox.showinfo("Preemption Result", record.summary)
            self.refresh()
            if self.on_update:
                self.on_update()
        except Exception as e:
            messagebox.showerror("Preemption Error", str(e))

    def _display_recovery_record(self, record: RecoveryRecord) -> None:
        self.audit_text.insert(tk.END, "=" * 70 + "\n")
        self.audit_text.insert(tk.END, f"RECOVERY ACTION EXECUTED: {record.strategy}\n")
        self.audit_text.insert(tk.END, f"Target Victim: {record.victim_name}\n")
        self.audit_text.insert(tk.END, f"Resources Reclaimed: {record.resources_reclaimed}\n")
        self.audit_text.insert(tk.END, f"Available Resources: Before {record.available_before} -> After {record.available_after}\n")
        self.audit_text.insert(tk.END, f"Deadlocked Indices:  Before {record.deadlocked_before} -> After {record.deadlocked_after}\n")
        self.audit_text.insert(tk.END, f"Outcome: {'RESOLVED ✓' if record.is_resolved else 'PARTIAL (Still Deadlocked) ⚠️'}\n")
        self.audit_text.insert(tk.END, f"Summary: {record.summary}\n\n")
        self.audit_text.see(tk.END)

    def refresh(self) -> None:
        """Update deadlocked status banner and options."""
        det = self.engine.last_detection_result
        if det and det.is_deadlocked:
            self.status_banner.config(bg=Theme.DANGER_BG)
            dl_names = ", ".join(det.deadlocked_names)
            self.status_lbl.config(
                text=f"⚠️ DEADLOCK ACTIVE: {len(det.deadlocked_processes)} Process(es) Deadlocked: [ {dl_names} ]",
                fg=Theme.DANGER,
                bg=Theme.DANGER_BG,
            )
        else:
            self.status_banner.config(bg=Theme.SUCCESS_BG)
            self.status_lbl.config(
                text="✓ SYSTEM HEALTHY: No deadlocked processes currently exist.",
                fg=Theme.SUCCESS,
                bg=Theme.SUCCESS_BG,
            )

        # Update resource options
        if self.engine.resource_manager:
            r_names = self.engine.resource_manager.resource_names
            self.preempt_res_combo["values"] = r_names
            if r_names and not self.preempt_res_var.get():
                self.preempt_res_combo.current(0)

        self._update_victim_options()

