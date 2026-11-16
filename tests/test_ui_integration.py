"""Automated UI Integration and View Switching Tests.

Course: Solving Problems Using Modelling and Simulation (SPMS) - NEC00091
"""

import unittest
import tkinter as tk
from main import DeadlockSimulationApp


class TestUIIntegration(unittest.TestCase):
    """Test suite ensuring that all Tkinter views and components initialize and refresh cleanly."""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide GUI window during automated testing
        self.app = DeadlockSimulationApp(self.root)

    def tearDown(self):
        try:
            self.root.destroy()
        except Exception:
            pass

    def test_view_switching_and_refresh(self):
        """Cycle through every view in the application and verify no crashes."""
        view_keys = ["dashboard", "setup", "bankers", "detection", "rag", "recovery", "results"]
        for key in view_keys:
            self.app.show_view(key)
            self.root.update_idletasks()
            self.assertIn(key, self.app.views)

    def test_dashboard_interactions(self):
        self.app.show_view("dashboard")
        dashboard = self.app.views["dashboard"]
        dashboard.refresh()
        self.root.update_idletasks()

    def test_bankers_view_interactions(self):
        self.app.show_view("bankers")
        bankers = self.app.views["bankers"]
        bankers._run_bankers()
        self.root.update_idletasks()
        self.assertIsNotNone(self.app.engine.last_bankers_result)

    def test_detection_view_interactions(self):
        self.app.show_view("detection")
        det_view = self.app.views["detection"]
        det_view._run_detection()
        self.root.update_idletasks()
        self.assertIsNotNone(self.app.engine.last_detection_result)

    def test_rag_view_interactions(self):
        self.app.show_view("rag")
        rag_view = self.app.views["rag"]
        rag_view.refresh()
        self.root.update_idletasks()

    def test_results_view_interactions(self):
        self.app.show_view("results")
        res_view = self.app.views["results"]
        res_view.refresh()
        self.root.update_idletasks()
        report = res_view._generate_report_content()
        self.assertIn("OPERATING SYSTEM DEADLOCK SIMULATION", report)


if __name__ == "__main__":
    unittest.main()

