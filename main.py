"""Main Entry Point for the Operating System Deadlock Simulation Application.

Course: Solving Problems Using Modelling and Simulation (SPMS)
Course Code: NEC00091
Academic Purpose: College-level modelling, simulation and demonstration.

Execution:
    python main.py
"""

import sys
import tkinter as tk
from tkinter import ttk

from simulation.simulation_engine import SimulationEngine
from ui.theme import Theme, apply_theme_styles
from ui.dashboard import DashboardView
from ui.simulation_setup import SimulationSetupView
from ui.bankers_view import BankersView
from ui.detection_view import DetectionView
from ui.rag_view import RagView
from ui.recovery_view import RecoveryView
from ui.results_view import ResultsView


class DeadlockSimulationApp:
    """Master application coordinator managing the navigation sidebar and views."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Operating System Deadlock Simulation | SPMS (NEC00091)")
        self.root.geometry("1200x750")
        self.root.minsize(1050, 680)

        # Apply custom styling
        apply_theme_styles(self.root)

        # Core Simulation Engine
        self.engine = SimulationEngine()

        # Layout containers: Sidebar (Left) and Content (Right)
        self.main_container = ttk.Frame(self.root, style="TFrame")
        self.main_container.pack(fill="both", expand=True)

        self._build_sidebar()
        self._build_content_area()

        # Default View
        self.show_view("dashboard")

    def _build_sidebar(self) -> None:
        self.sidebar = ttk.Frame(self.main_container, style="Sidebar.TFrame", width=230)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # App Brand Header
        brand_frame = tk.Frame(self.sidebar, bg=Theme.BG_SIDEBAR, padx=16, pady=18)
        brand_frame.pack(fill="x")

        lbl_app = tk.Label(
            brand_frame,
            text="OS DEADLOCK",
            bg=Theme.BG_SIDEBAR,
            fg="#ffffff",
            font=("Segoe UI", 13, "bold"),
        )
        lbl_app.pack(anchor="w")

        lbl_course = tk.Label(
            brand_frame,
            text="SPMS • NEC00091",
            bg=Theme.BG_SIDEBAR,
            fg="#94a3b8",
            font=("Segoe UI", 8, "bold"),
        )
        lbl_course.pack(anchor="w", pady=(2, 0))

        # Nav Buttons Container
        self.nav_frame = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        self.nav_frame.pack(fill="x", pady=10)

        self.nav_buttons: dict[str, ttk.Button] = {}
        nav_items = [
            ("dashboard", "📊  Dashboard"),
            ("setup", "⚙️  Simulation Setup"),
            ("bankers", "🛡️  Banker's Algorithm"),
            ("detection", "🔍  Deadlock Detection"),
            ("rag", "🕸️  Allocation Graph"),
            ("recovery", "🚑  Deadlock Recovery"),
            ("results", "📈  Results & Charts"),
        ]

        for key, text in nav_items:
            btn = ttk.Button(
                self.nav_frame,
                text=text,
                style="Nav.TButton",
                command=lambda k=key: self.show_view(k),
            )
            btn.pack(fill="x", padx=10, pady=3)
            self.nav_buttons[key] = btn

        # Bottom Team & Academic Footer in Sidebar
        footer_frame = tk.Frame(self.sidebar, bg=Theme.BG_SIDEBAR, padx=14, pady=16)
        footer_frame.pack(side="bottom", fill="x")

        lbl_team = tk.Label(
            footer_frame,
            text="Academic Demonstration\nThree-Member Team Architecture\nPython 3.11+ • Tkinter • NumPy",
            bg=Theme.BG_SIDEBAR,
            fg="#64748b",
            font=("Segoe UI", 7),
            justify="left",
        )
        lbl_team.pack(anchor="w")

    def _build_content_area(self) -> None:
        self.content_frame = ttk.Frame(self.main_container, style="TFrame")
        self.content_frame.pack(side="right", fill="both", expand=True)

        # Instantiate View Pages
        self.views = {
            "dashboard": DashboardView(self.content_frame, self.engine, on_navigate_callback=self.show_view),
            "setup": SimulationSetupView(self.content_frame, self.engine, on_update_callback=self.on_state_updated),
            "bankers": BankersView(self.content_frame, self.engine, on_update_callback=self.on_state_updated),
            "detection": DetectionView(self.content_frame, self.engine, on_update_callback=self.on_state_updated),
            "rag": RagView(self.content_frame, self.engine, on_update_callback=self.on_state_updated),
            "recovery": RecoveryView(self.content_frame, self.engine, on_update_callback=self.on_state_updated),
            "results": ResultsView(self.content_frame, self.engine, on_update_callback=self.on_state_updated),
        }

    def show_view(self, view_key: str) -> None:
        """Switch the visible view in the content area."""
        for k, v in self.views.items():
            v.pack_forget()

        if view_key in self.views:
            target_view = self.views[view_key]
            target_view.pack(fill="both", expand=True)
            if hasattr(target_view, "refresh"):
                target_view.refresh()

        # Update button highlights
        for k, btn in self.nav_buttons.items():
            if k == view_key:
                btn.configure(style="NavActive.TButton")
            else:
                btn.configure(style="Nav.TButton")

    def on_state_updated(self) -> None:
        """Propagate state change to all views."""
        for v in self.views.values():
            if hasattr(v, "refresh"):
                v.refresh()


def main():
    root = tk.Tk()
    app = DeadlockSimulationApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
