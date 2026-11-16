"""Results, Analytics, and Graphical Charts View.

Course: Solving Problems Using Modelling and Simulation (SPMS) - NEC00091
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from ui.theme import Theme
from simulation.simulation_engine import SimulationEngine
from visualization.charts import (
    plot_resource_utilization,
    plot_process_allocation_breakdown,
    plot_need_vs_allocation,
)


class ResultsView(ttk.Frame):
    """Visual analytics dashboard and simulation report generator."""

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

        ttk.Label(header_card, text="Simulation Results & Analytical Graphs", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            header_card,
            text="Interactive Matplotlib visualizations and academic report generation based on live simulation data.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        # Top Control Bar
        ctrl_card = ttk.Frame(self, style="Card.TFrame", padding=10)
        ctrl_card.pack(fill="x", padx=16, pady=4)

        row = ttk.Frame(ctrl_card, style="Card.TFrame")
        row.pack(fill="x")

        btn_refresh = ttk.Button(row, text="Refresh All Charts", style="Primary.TButton", command=self.refresh)
        btn_refresh.pack(side="left", padx=(0, 12))

        btn_export = ttk.Button(row, text="Export Comprehensive Report", style="Success.TButton", command=self._export_report)
        btn_export.pack(side="left", padx=6)

        # Tabbed Notebook for Matplotlib Charts + Report Text
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=(6, 16))

        # Chart 1 Tab: Resource Utilization
        self.tab1 = ttk.Frame(self.notebook, style="Card.TFrame", padding=8)
        self.notebook.add(self.tab1, text="  📊 Resource Utilization  ")
        self.fig1 = Figure(figsize=(7, 4.2), dpi=100)
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self.tab1)
        self.canvas1.get_tk_widget().pack(fill="both", expand=True)

        # Chart 2 Tab: Process Allocation Breakdown
        self.tab2 = ttk.Frame(self.notebook, style="Card.TFrame", padding=8)
        self.notebook.add(self.tab2, text="  👥 Process Allocation Breakdown  ")
        self.fig2 = Figure(figsize=(7, 4.2), dpi=100)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.tab2)
        self.canvas2.get_tk_widget().pack(fill="both", expand=True)

        # Chart 3 Tab: Need vs Allocation
        self.tab3 = ttk.Frame(self.notebook, style="Card.TFrame", padding=8)
        self.notebook.add(self.tab3, text="  ⚖️ Need vs Allocation Profile  ")
        self.fig3 = Figure(figsize=(7, 4.2), dpi=100)
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=self.tab3)
        self.canvas3.get_tk_widget().pack(fill="both", expand=True)

        # Tab 4: Academic Report Summary
        self.tab4 = ttk.Frame(self.notebook, style="Card.TFrame", padding=12)
        self.notebook.add(self.tab4, text="  📝 Academic Report & Model Summary  ")

        self.report_text = tk.Text(
            self.tab4,
            bg="#f8fafc",
            fg="#0f172a",
            font=Theme.FONT_MONO,
            wrap="word",
            relief="flat",
            padx=12,
            pady=12,
        )
        report_scroll = ttk.Scrollbar(self.tab4, orient="vertical", command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=report_scroll.set)
        self.report_text.pack(side="left", fill="both", expand=True)
        report_scroll.pack(side="right", fill="y")

    def _generate_report_content(self) -> str:
        stats = self.engine.get_statistics()
        alloc, max_m, need, req, avail, total = self.engine.get_matrices()
        r_names = self.engine.resource_manager.resource_names
        p_names = [p.name for p in self.engine.processes]

        report_lines = [
            "=" * 78,
            "OPERATING SYSTEM DEADLOCK SIMULATION – ACADEMIC REPORT",
            "Subject: Solving Problems Using Modelling and Simulation (SPMS)",
            "Course Code: NEC00091 | Academic Demonstration Project",
            "=" * 78,
            "",
            "1. SIMULATION CONFIGURATION & METRICS",
            f"• Current Scenario:            {self.engine.scenario.name}",
            f"• Theoretical Focus:           {self.engine.scenario.theoretical_concept}",
            f"• Number of Processes (N):     {stats['total_processes']}",
            f"• Number of Resource Types (M): {stats['total_resource_types']}",
            f"• Total Resource Capacity:     {stats['total_resource_instances']} instances",
            f"• Allocated Capacity:          {stats['allocated_instances']} instances",
            f"• Available Capacity:          {stats['available_instances']} instances",
            f"• Overall Utilization:         {stats['overall_utilization_pct']}%",
            f"• System Status:               {stats['system_status']}",
            f"• Deadlocked Process Count:    {stats['deadlocked_count']}",
            "",
            "2. MATHEMATICAL MODEL FORMULATION",
            "• Let P = {P_0, P_1, ..., P_{n-1}} be the set of concurrent processes.",
            "• Let R = {R_0, R_1, ..., R_{m-1}} be the finite set of resource types.",
            "• Allocation[i][j]: Instances of resource R_j held by process P_i.",
            "• Max[i][j]: Maximum instances of resource R_j process P_i will require.",
            "• Need[i][j] = Max[i][j] - Allocation[i][j] (Remaining requirement).",
            "• Available[j] = Total[j] - Σ_i Allocation[i][j].",
            "",
            "3. CURRENT SYSTEM MATRICES",
            f"Resource Names: {r_names}",
            f"Total Capacity: {total.tolist()}",
            f"Available:      {avail.tolist()}",
            "",
            "Process Data Breakdown:",
        ]

        for i, p in enumerate(self.engine.processes):
            report_lines.append(
                f"  {p.name:<4} | State: {p.state.value:<10} | Alloc: {str(alloc[i].tolist()):<15} | "
                f"Max: {str(max_m[i].tolist()):<15} | Need: {str(need[i].tolist()):<15} | Req: {str(req[i].tolist())}"
            )

        report_lines.extend([
            "",
            "4. BANKER'S ALGORITHM (DEADLOCK AVOIDANCE)",
            f"• Avoidance State: {'SAFE' if stats['is_safe'] else 'UNSAFE'}",
            f"• Safe Sequence:   < {' -> '.join(stats['safe_sequence']) if stats['safe_sequence'] else 'None' } >",
            f"• Explanation:     {self.engine.last_bankers_result.explanation if self.engine.last_bankers_result else 'N/A'}",
            "",
            "5. DEADLOCK DETECTION & ANALYSIS",
            f"• Deadlock Present: {'YES' if stats['deadlocked_count'] > 0 else 'NO'}",
            f"• Deadlocked PIDs:  {self.engine.last_detection_result.deadlocked_names if self.engine.last_detection_result else 'None'}",
            f"• Explanation:      {self.engine.last_detection_result.explanation if self.engine.last_detection_result else 'N/A'}",
            "",
            "6. GRAPH THEORY & DEADLOCK CRITERIA",
            "• Single-Instance Resource Graph: Directed cycle is NECESSARY and SUFFICIENT for deadlock.",
            "• Multiple-Instance Resource Graph: Directed cycle is NECESSARY but NOT SUFFICIENT for deadlock.",
            "=" * 78,
            "End of Report | Generated by OS Deadlock Simulation Engine",
            "=" * 78,
        ])

        return "\n".join(report_lines)

    def _export_report(self) -> None:
        content = self._generate_report_content()
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("Markdown Files", "*.md"), ("All Files", "*.*")],
            title="Save Academic Simulation Report",
            initialfile="OS_Deadlock_Simulation_Report.txt",
        )
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)
                messagebox.showinfo("Export Successful", f"Simulation report saved to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Export Failed", str(e))

    def refresh(self) -> None:
        """Redraw all three charts and refresh the report text."""
        alloc, max_m, need, req, avail, total = self.engine.get_matrices()
        r_names = self.engine.resource_manager.resource_names
        p_names = [p.name for p in self.engine.processes]

        # 1. Resource Utilization Chart
        plot_resource_utilization(
            fig=self.fig1,
            resource_names=r_names,
            total_resources=total,
            available_resources=avail,
            allocated_resources=self.engine.resource_manager.allocated_vector,
        )
        self.canvas1.draw()

        # 2. Process Allocation Breakdown
        plot_process_allocation_breakdown(
            fig=self.fig2,
            process_names=p_names,
            resource_names=r_names,
            allocation_matrix=alloc,
        )
        self.canvas2.draw()

        # 3. Need vs Allocation Profile
        plot_need_vs_allocation(
            fig=self.fig3,
            process_names=p_names,
            allocation_matrix=alloc,
            need_matrix=need,
        )
        self.canvas3.draw()

        # 4. Report Text
        report_content = self._generate_report_content()
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, report_content)

