"""Simulation Setup View for Custom Matrix Configuration.

Course: Solving Problems Using Modelling and Simulation (SPMS) - NEC00091
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np

from ui.theme import Theme
from simulation.simulation_engine import SimulationEngine
from data.sample_scenarios import ALL_SCENARIOS


class SimulationSetupView(ttk.Frame):
    """Provides editable matrices for Allocation, Max Claim, Request, and Total Resources."""

    def __init__(self, parent: ttk.Frame, engine: SimulationEngine, on_update_callback=None):
        super().__init__(parent, style="TFrame")
        self.engine = engine
        self.on_update = on_update_callback

        self.num_proc_var = tk.IntVar(value=len(self.engine.processes))
        self.num_res_var = tk.IntVar(value=self.engine.resource_manager.num_resources if self.engine.resource_manager else 3)

        self.total_entries: list[tk.Entry] = []
        self.alloc_entries: list[list[tk.Entry]] = []
        self.max_entries: list[list[tk.Entry]] = []
        self.req_entries: list[list[tk.Entry]] = []

        self._build_ui()
        self.populate_from_engine()

    def _build_ui(self) -> None:
        # Header Card
        header_card = ttk.Frame(self, style="Card.TFrame", padding=14)
        header_card.pack(fill="x", padx=16, pady=(16, 8))

        ttk.Label(header_card, text="Simulation Matrix Setup & Mathematical Inputs", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            header_card,
            text="Configure process count, resource dimensions, Total, Allocation, Max, and Request matrices.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        # Dimensions & Preset Card
        dim_card = ttk.Frame(self, style="Card.TFrame", padding=12)
        dim_card.pack(fill="x", padx=16, pady=4)

        row = ttk.Frame(dim_card, style="Card.TFrame")
        row.pack(fill="x")

        ttk.Label(row, text="Processes (N):", style="Card.TLabel", font=Theme.FONT_BODY_BOLD).pack(side="left", padx=(0, 4))
        sp_proc = ttk.Spinbox(row, from_=2, to=8, textvariable=self.num_proc_var, width=5, command=self._rebuild_grid)
        sp_proc.pack(side="left", padx=(0, 16))

        ttk.Label(row, text="Resource Types (M):", style="Card.TLabel", font=Theme.FONT_BODY_BOLD).pack(side="left", padx=(0, 4))
        sp_res = ttk.Spinbox(row, from_=2, to=6, textvariable=self.num_res_var, width=5, command=self._rebuild_grid)
        sp_res.pack(side="left", padx=(0, 24))

        ttk.Label(row, text="Load Preset:", style="Card.TLabel", font=Theme.FONT_BODY_BOLD).pack(side="left", padx=(0, 4))
        self.preset_var = tk.StringVar(value=ALL_SCENARIOS[0].name)
        preset_combo = ttk.Combobox(
            row,
            textvariable=self.preset_var,
            values=[s.name for s in ALL_SCENARIOS],
            state="readonly",
            width=38,
            font=Theme.FONT_BODY,
        )
        preset_combo.pack(side="left", padx=4)
        ttk.Button(row, text="Populate Fields", style="Secondary.TButton", command=self._load_preset_to_fields).pack(side="left", padx=6)

        # Scrollable Canvas for Matrix Grids
        container = ttk.Frame(self, style="TFrame")
        container.pack(fill="both", expand=True, padx=16, pady=8)

        self.canvas = tk.Canvas(container, bg=Theme.BG_MAIN, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.grid_frame = ttk.Frame(self.canvas, style="TFrame")

        self.grid_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bottom Button Bar
        btn_bar = ttk.Frame(self, style="Card.TFrame", padding=12)
        btn_bar.pack(fill="x", padx=16, pady=(4, 16))

        btn_apply = ttk.Button(btn_bar, text="Validate & Apply Matrix Configuration", style="Primary.TButton", command=self._apply_custom)
        btn_apply.pack(side="left", padx=6)

        btn_reset = ttk.Button(btn_bar, text="Reset to Current Engine State", style="Secondary.TButton", command=self.populate_from_engine)
        btn_reset.pack(side="left", padx=6)

    def _rebuild_grid(self) -> None:
        """Create entry fields for Total, Allocation, Max, and Request matrices."""
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        n_proc = self.num_proc_var.get()
        n_res = self.num_res_var.get()

        res_names = [f"R{j}" for j in range(n_res)]
        proc_names = [f"P{i}" for i in range(n_proc)]

        # 1. Total Resources Card
        tot_card = ttk.Frame(self.grid_frame, style="Card.TFrame", padding=12)
        tot_card.pack(fill="x", expand=True, pady=6)
        ttk.Label(tot_card, text="1. Total System Resource Capacity Vector (Total)", style="Section.TLabel").pack(anchor="w", pady=(0, 6))

        tot_row = ttk.Frame(tot_card, style="Card.TFrame")
        tot_row.pack(anchor="w")

        self.total_entries = []
        for j in range(n_res):
            col_box = ttk.Frame(tot_row, style="Card.TFrame")
            col_box.pack(side="left", padx=6)
            ttk.Label(col_box, text=res_names[j], style="Card.TLabel", font=Theme.FONT_BODY_BOLD).pack()
            ent = tk.Entry(col_box, width=6, justify="center", font=Theme.FONT_BODY)
            ent.insert(0, "10")
            ent.pack(pady=2)
            self.total_entries.append(ent)

        # 2. Matrix Grids Side-by-Side or Sequential
        matrices_card = ttk.Frame(self.grid_frame, style="Card.TFrame", padding=12)
        matrices_card.pack(fill="x", expand=True, pady=6)

        # We display three columns: Allocation Matrix, Max Claim Matrix, Request Matrix
        mat_container = ttk.Frame(matrices_card, style="Card.TFrame")
        mat_container.pack(fill="x")

        # Section A: Allocation Matrix
        f_alloc = ttk.Frame(mat_container, style="Card.TFrame")
        f_alloc.pack(side="left", fill="both", expand=True, padx=8)
        ttk.Label(f_alloc, text="2. Allocation Matrix", style="Section.TLabel").pack(anchor="w", pady=(0, 4))
        self.alloc_entries = self._build_matrix_entries(f_alloc, n_proc, n_res, proc_names, res_names)

        # Section B: Max Matrix
        f_max = ttk.Frame(mat_container, style="Card.TFrame")
        f_max.pack(side="left", fill="both", expand=True, padx=8)
        ttk.Label(f_max, text="3. Maximum Claim Matrix", style="Section.TLabel").pack(anchor="w", pady=(0, 4))
        self.max_entries = self._build_matrix_entries(f_max, n_proc, n_res, proc_names, res_names)

        # Section C: Request Matrix
        f_req = ttk.Frame(mat_container, style="Card.TFrame")
        f_req.pack(side="left", fill="both", expand=True, padx=8)
        ttk.Label(f_req, text="4. Current Request Matrix", style="Section.TLabel").pack(anchor="w", pady=(0, 4))
        self.req_entries = self._build_matrix_entries(f_req, n_proc, n_res, proc_names, res_names)

    def _build_matrix_entries(
        self, parent: ttk.Frame, n_proc: int, n_res: int, proc_names: list[str], res_names: list[str]
    ) -> list[list[tk.Entry]]:
        grid = ttk.Frame(parent, style="Card.TFrame")
        grid.pack(anchor="w")

        # Header row
        ttk.Label(grid, text="Proc", style="Card.TLabel", font=Theme.FONT_BODY_BOLD).grid(row=0, column=0, padx=4, pady=2)
        for j in range(n_res):
            ttk.Label(grid, text=res_names[j], style="Card.TLabel", font=Theme.FONT_BODY_BOLD).grid(row=0, column=j + 1, padx=4, pady=2)

        entries = []
        for i in range(n_proc):
            row_entries = []
            ttk.Label(grid, text=proc_names[i], style="Card.TLabel", font=Theme.FONT_BODY_BOLD).grid(row=i + 1, column=0, padx=4, pady=2)
            for j in range(n_res):
                ent = tk.Entry(grid, width=5, justify="center", font=Theme.FONT_BODY)
                ent.insert(0, "0")
                ent.grid(row=i + 1, column=j + 1, padx=2, pady=2)
                row_entries.append(ent)
            entries.append(row_entries)

        return entries

    def populate_from_engine(self) -> None:
        """Populate setup form with values currently in the simulation engine."""
        alloc, max_m, need, req, avail, total = self.engine.get_matrices()
        n_proc, n_res = alloc.shape

        self.num_proc_var.set(n_proc)
        self.num_res_var.set(n_res)
        self._rebuild_grid()

        for j in range(n_res):
            self.total_entries[j].delete(0, tk.END)
            self.total_entries[j].insert(0, str(int(total[j])))

        for i in range(n_proc):
            for j in range(n_res):
                self.alloc_entries[i][j].delete(0, tk.END)
                self.alloc_entries[i][j].insert(0, str(int(alloc[i, j])))

                self.max_entries[i][j].delete(0, tk.END)
                self.max_entries[i][j].insert(0, str(int(max_m[i, j])))

                self.req_entries[i][j].delete(0, tk.END)
                self.req_entries[i][j].insert(0, str(int(req[i, j])))

    def _load_preset_to_fields(self) -> None:
        selected_name = self.preset_var.get()
        target_scenario = None
        for sc in ALL_SCENARIOS:
            if sc.name == selected_name:
                target_scenario = sc
                break

        if not target_scenario:
            return

        self.num_proc_var.set(target_scenario.num_processes)
        self.num_res_var.set(target_scenario.num_resources)
        self._rebuild_grid()

        for j in range(target_scenario.num_resources):
            self.total_entries[j].delete(0, tk.END)
            self.total_entries[j].insert(0, str(target_scenario.total_resources[j]))

        for i in range(target_scenario.num_processes):
            for j in range(target_scenario.num_resources):
                self.alloc_entries[i][j].delete(0, tk.END)
                self.alloc_entries[i][j].insert(0, str(target_scenario.allocation_matrix[i][j]))

                self.max_entries[i][j].delete(0, tk.END)
                self.max_entries[i][j].insert(0, str(target_scenario.max_matrix[i][j]))

                self.req_entries[i][j].delete(0, tk.END)
                self.req_entries[i][j].insert(0, str(target_scenario.request_matrix[i][j]))

    def _apply_custom(self) -> None:
        """Validate all entries and apply to engine."""
        n_proc = self.num_proc_var.get()
        n_res = self.num_res_var.get()

        try:
            total = [int(ent.get().strip()) for ent in self.total_entries]
            alloc = [[int(ent.get().strip()) for ent in row] for row in self.alloc_entries]
            max_m = [[int(ent.get().strip()) for ent in row] for row in self.max_entries]
            req = [[int(ent.get().strip()) for ent in row] for row in self.req_entries]
        except ValueError:
            messagebox.showerror("Input Error", "All matrix entries must be valid non-negative integers.")
            return

        res_names = [f"R{j}" for j in range(n_res)]
        proc_names = [f"P{i}" for i in range(n_proc)]

        try:
            self.engine.setup_custom(
                resource_names=res_names,
                total_resources=total,
                process_names=proc_names,
                allocation_matrix=alloc,
                max_matrix=max_m,
                request_matrix=req,
            )
            messagebox.showinfo("Success", "Custom matrix configuration validated and applied successfully!")
            if self.on_update:
                self.on_update()
        except Exception as e:
            messagebox.showerror("Validation Error", str(e))

