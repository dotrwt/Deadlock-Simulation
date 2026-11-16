"""Resource Allocation Graph (RAG) Interactive View.

Course: Solving Problems Using Modelling and Simulation (SPMS) - NEC00091
"""

import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from ui.theme import Theme
from simulation.simulation_engine import SimulationEngine
from visualization.allocation_graph import draw_rag_on_figure


class RagView(ttk.Frame):
    """Visualizes the Resource Allocation Graph and highlights circular wait cycles."""

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

        ttk.Label(header_card, text="Resource Allocation Graph (RAG)", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            header_card,
            text="Interactive directed graph representation: Process nodes (circles), Resource nodes (squares), "
                 "Allocations (solid arrows), and Requests (dashed arrows). Detected cycles are highlighted in red.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        # Controls & Info Bar
        ctrl_card = ttk.Frame(self, style="Card.TFrame", padding=10)
        ctrl_card.pack(fill="x", padx=16, pady=4)

        row = ttk.Frame(ctrl_card, style="Card.TFrame")
        row.pack(fill="x")

        btn_refresh = ttk.Button(row, text="Redraw RAG Graph", style="Primary.TButton", command=self.refresh)
        btn_refresh.pack(side="left", padx=(0, 16))

        self.info_lbl = ttk.Label(row, text="Analyzing graph cycles...", style="Card.TLabel", font=Theme.FONT_BODY_BOLD)
        self.info_lbl.pack(side="left", padx=8)

        # Matplotlib Canvas Container Card
        canvas_card = ttk.Frame(self, style="Card.TFrame", padding=8)
        canvas_card.pack(fill="both", expand=True, padx=16, pady=(6, 16))

        self.fig = Figure(figsize=(8, 4.8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=canvas_card)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

        self.toolbar_frame = ttk.Frame(canvas_card, style="Card.TFrame")
        self.toolbar_frame.pack(fill="x")
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        self.toolbar.update()

    def refresh(self) -> None:
        """Regenerate and redraw the graph from current engine state."""
        alloc, max_m, need, req, avail, total = self.engine.get_matrices()
        p_names = [p.name for p in self.engine.processes]
        r_names = self.engine.resource_manager.resource_names

        deadlocked_idx = (
            self.engine.last_detection_result.deadlocked_processes
            if self.engine.last_detection_result
            else []
        )

        num_cycles, has_deadlock, explanation = draw_rag_on_figure(
            fig=self.fig,
            process_names=p_names,
            resource_names=r_names,
            allocation_matrix=alloc,
            request_matrix=req,
            total_resources=total.tolist(),
            available_resources=avail.tolist(),
            deadlocked_indices=deadlocked_idx,
        )

        self.canvas.draw()

        if num_cycles > 0:
            self.info_lbl.config(
                text=f"⚠️ {num_cycles} Circular Wait Cycle(s) Identified in Graph | Deadlock: {'YES' if has_deadlock else 'NO (Multiple Instances Free Cycle)'}",
                foreground=Theme.DANGER if has_deadlock else Theme.WARNING,
            )
        else:
            self.info_lbl.config(
                text="✓ No Cycles Detected. Graph is acyclic; Deadlock is impossible.",
                foreground=Theme.SUCCESS,
            )

