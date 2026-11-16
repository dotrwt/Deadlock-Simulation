"""Dashboard View for the Deadlock Simulation application.

Course: Solving Problems Using Modelling and Simulation (SPMS) - NEC00091
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ui.theme import Theme
from simulation.simulation_engine import SimulationEngine
from data.sample_scenarios import ALL_SCENARIOS


class DashboardView(ttk.Frame):
    """Main dashboard displaying high-level system metrics and quick controls."""

    def __init__(self, parent: ttk.Frame, engine: SimulationEngine, on_navigate_callback=None):
        super().__init__(parent, style="TFrame")
        self.engine = engine
        self.on_navigate = on_navigate_callback

        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        # Title Card
        header_card = ttk.Frame(self, style="Card.TFrame", padding=16)
        header_card.pack(fill="x", padx=16, pady=(16, 8))

        title_lbl = ttk.Label(
            header_card,
            text="Operating System Deadlock Simulation",
            style="Header.TLabel",
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = ttk.Label(
            header_card,
            text="Course: Solving Problems Using Modelling and Simulation (SPMS) | Code: NEC00091",
            style="Subtitle.TLabel",
        )
        subtitle_lbl.pack(anchor="w", pady=(2, 0))

        # Metrics Row
        self.metrics_frame = ttk.Frame(self, style="TFrame")
        self.metrics_frame.pack(fill="x", padx=16, pady=8)

        self.card_status = self._create_metric_card(self.metrics_frame, "System Status", "SAFE", Theme.SUCCESS)
        self.card_proc = self._create_metric_card(self.metrics_frame, "Total Processes", "5", Theme.PRIMARY)
        self.card_res = self._create_metric_card(self.metrics_frame, "Resource Types", "3", Theme.INFO)
        self.card_util = self._create_metric_card(self.metrics_frame, "Resource Utilization", "0%", Theme.WARNING)
        self.card_deadlock = self._create_metric_card(self.metrics_frame, "Deadlocked Count", "0", Theme.DANGER)

        for i in range(5):
            self.metrics_frame.columnconfigure(i, weight=1)

        # Quick Control and Scenario Selection Card
        ctrl_card = ttk.Frame(self, style="Card.TFrame", padding=16)
        ctrl_card.pack(fill="x", padx=16, pady=8)

        ctrl_title = ttk.Label(ctrl_card, text="Quick Scenario Loader & Experiment Controls", style="Section.TLabel")
        ctrl_title.pack(anchor="w", pady=(0, 8))

        row1 = ttk.Frame(ctrl_card, style="Card.TFrame")
        row1.pack(fill="x")

        ttk.Label(row1, text="Preset Scenario:", style="Card.TLabel", font=Theme.FONT_BODY_BOLD).pack(side="left", padx=(0, 8))

        self.scenario_var = tk.StringVar(value=self.engine.scenario.name)
        scenario_names = [s.name for s in ALL_SCENARIOS]
        self.scenario_combo = ttk.Combobox(
            row1,
            textvariable=self.scenario_var,
            values=scenario_names,
            state="readonly",
            width=50,
            font=Theme.FONT_BODY,
        )
        self.scenario_combo.pack(side="left", padx=4)
        self.scenario_combo.bind("<<ComboboxSelected>>", self._on_scenario_selected)

        btn_load = ttk.Button(row1, text="Load Scenario", style="Primary.TButton", command=self._load_selected_scenario)
        btn_load.pack(side="left", padx=6)

        btn_auto_rec = ttk.Button(row1, text="Auto Recover Deadlock", style="Danger.TButton", command=self._auto_recover)
        btn_auto_rec.pack(side="left", padx=6)

        # Description Label
        self.desc_lbl = ttk.Label(
            ctrl_card,
            text=self.engine.scenario.description,
            style="Muted.TLabel",
            wraplength=850,
            justify="left",
        )
        self.desc_lbl.pack(anchor="w", pady=(8, 0))

        # Bottom Grid: Process Status Table & Live Activity Log
        content_panes = ttk.Frame(self, style="TFrame")
        content_panes.pack(fill="both", expand=True, padx=16, pady=(8, 16))
        content_panes.columnconfigure(0, weight=3)
        content_panes.columnconfigure(1, weight=2)
        content_panes.rowconfigure(0, weight=1)

        # Left: Process Table Card
        table_card = ttk.Frame(content_panes, style="Card.TFrame", padding=12)
        table_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ttk.Label(table_card, text="Current Process States & Resource Allocation", style="Section.TLabel").pack(anchor="w", pady=(0, 6))

        columns = ("pid", "name", "state", "allocation", "max", "need", "request")
        self.proc_tree = ttk.Treeview(table_card, columns=columns, show="headings", height=7)
        self.proc_tree.heading("pid", text="ID")
        self.proc_tree.heading("name", text="Process")
        self.proc_tree.heading("state", text="State")
        self.proc_tree.heading("allocation", text="Allocated")
        self.proc_tree.heading("max", text="Max Claim")
        self.proc_tree.heading("need", text="Need")
        self.proc_tree.heading("request", text="Request")

        self.proc_tree.column("pid", width=40, anchor="center")
        self.proc_tree.column("name", width=70, anchor="center")
        self.proc_tree.column("state", width=100, anchor="center")
        self.proc_tree.column("allocation", width=90, anchor="center")
        self.proc_tree.column("max", width=90, anchor="center")
        self.proc_tree.column("need", width=90, anchor="center")
        self.proc_tree.column("request", width=90, anchor="center")

        tree_scroll = ttk.Scrollbar(table_card, orient="vertical", command=self.proc_tree.yview)
        self.proc_tree.configure(yscrollcommand=tree_scroll.set)
        self.proc_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

        # Right: Log Card
        log_card = ttk.Frame(content_panes, style="Card.TFrame", padding=12)
        log_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        ttk.Label(log_card, text="Live Simulation Audit Log", style="Section.TLabel").pack(anchor="w", pady=(0, 6))

        self.log_text = tk.Text(
            log_card,
            bg="#f8fafc",
            fg="#0f172a",
            font=Theme.FONT_MONO,
            wrap="word",
            relief="flat",
            padx=8,
            pady=8,
        )
        log_scroll = ttk.Scrollbar(log_card, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scroll.pack(side="right", fill="y")

    def _create_metric_card(self, parent: ttk.Frame, title: str, initial_val: str, accent_color: str) -> dict:
        card = tk.Frame(parent, bg=Theme.BG_CARD, highlightbackground=Theme.BORDER_COLOR, highlightthickness=1, padx=12, pady=10)
        card.pack(side="left", fill="both", expand=True, padx=4)

        title_lbl = tk.Label(card, text=title.upper(), bg=Theme.BG_CARD, fg=Theme.TEXT_MUTED, font=("Segoe UI", 8, "bold"))
        title_lbl.pack(anchor="w")

        val_lbl = tk.Label(card, text=initial_val, bg=Theme.BG_CARD, fg=accent_color, font=Theme.FONT_METRIC)
        val_lbl.pack(anchor="w", pady=(4, 0))

        return {"card": card, "val_lbl": val_lbl, "accent": accent_color}

    def _on_scenario_selected(self, event=None) -> None:
        selected_name = self.scenario_var.get()
        for sc in ALL_SCENARIOS:
            if sc.name == selected_name:
                self.desc_lbl.config(text=f"[{sc.theoretical_concept}]\n{sc.description}")
                break

    def _load_selected_scenario(self) -> None:
        selected_name = self.scenario_var.get()
        for sc in ALL_SCENARIOS:
            if sc.name == selected_name:
                self.engine.load_scenario(sc)
                self.refresh()
                messagebox.showinfo("Scenario Loaded", f"Successfully loaded '{sc.name}'.")
                break

    def _auto_recover(self) -> None:
        record = self.engine.auto_recover()
        if record:
            messagebox.showinfo("Recovery Result", record.summary)
        else:
            messagebox.showinfo("Recovery Info", "The system has no deadlocked processes to recover.")
        self.refresh()

    def refresh(self) -> None:
        """Update metrics, process table, and logs from current engine state."""
        stats = self.engine.get_statistics()

        # Update metric cards
        status_text = stats["system_status"]
        if status_text == "SAFE":
            status_color = Theme.SUCCESS
        elif status_text == "UNSAFE":
            status_color = Theme.WARNING
        else:
            status_color = Theme.DANGER

        self.card_status["val_lbl"].config(text=status_text, fg=status_color)
        self.card_proc["val_lbl"].config(text=str(stats["total_processes"]))
        self.card_res["val_lbl"].config(text=str(stats["total_resource_types"]))
        self.card_util["val_lbl"].config(text=f"{stats['overall_utilization_pct']}%")
        self.card_deadlock["val_lbl"].config(text=str(stats["deadlocked_count"]))

        # Update process table
        for item in self.proc_tree.get_children():
            self.proc_tree.delete(item)

        for p in self.engine.processes:
            self.proc_tree.insert(
                "",
                "end",
                values=(
                    p.pid,
                    p.name,
                    p.state.value,
                    str(p.allocation.tolist()),
                    str(p.max_claim.tolist()),
                    str(p.need.tolist()),
                    str(p.request.tolist()),
                ),
            )

        # Update log
        self.log_text.delete("1.0", tk.END)
        for msg in self.engine.log_messages[-100:]:
            self.log_text.insert(tk.END, f"• {msg}\n")
        self.log_text.see(tk.END)

