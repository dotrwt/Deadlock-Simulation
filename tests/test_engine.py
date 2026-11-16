"""Unit tests for the Simulation Engine.

Course: Solving Problems Using Modelling and Simulation (SPMS) - NEC00091
"""

import unittest
from simulation.simulation_engine import SimulationEngine
from data.sample_scenarios import (
    SCENARIO_1_SAFE,
    SCENARIO_2_UNSAFE,
    SCENARIO_3_DEADLOCK,
    SCENARIO_4_RECOVERY,
    SCENARIO_5_CYCLE_NO_DEADLOCK,
)


class TestSimulationEngine(unittest.TestCase):
    """Test suite for the Simulation Engine state transitions and scenarios."""

    def test_load_scenario_1_safe(self):
        engine = SimulationEngine(SCENARIO_1_SAFE)
        self.assertEqual(engine.system_status, "SAFE")
        self.assertIsNotNone(engine.last_bankers_result)
        self.assertTrue(engine.last_bankers_result.is_safe)
        self.assertFalse(engine.last_detection_result.is_deadlocked)

    def test_load_scenario_2_unsafe(self):
        engine = SimulationEngine(SCENARIO_2_UNSAFE)
        self.assertEqual(engine.system_status, "UNSAFE")
        self.assertFalse(engine.last_bankers_result.is_safe)
        # Unsafe is not deadlocked yet unless requests are made that cannot be met
        stats = engine.get_statistics()
        self.assertEqual(stats["system_status"], "UNSAFE")

    def test_load_scenario_3_deadlock(self):
        engine = SimulationEngine(SCENARIO_3_DEADLOCK)
        self.assertEqual(engine.system_status, "DEADLOCKED")
        self.assertTrue(engine.last_detection_result.is_deadlocked)
        self.assertGreater(len(engine.last_detection_result.deadlocked_processes), 0)

    def test_load_scenario_4_and_auto_recover(self):
        engine = SimulationEngine(SCENARIO_4_RECOVERY)
        self.assertEqual(engine.system_status, "DEADLOCKED")

        # Auto recover by terminating victim with largest allocation (P2)
        record = engine.auto_recover()
        self.assertIsNotNone(record)
        self.assertEqual(record.victim_name, "P2")
        self.assertTrue(record.is_resolved)
        self.assertEqual(engine.system_status, "SAFE")

    def test_scenario_5_cycle_no_deadlock(self):
        """Silberschatz Figure 5.3: cycle exists but no deadlock."""
        engine = SimulationEngine(SCENARIO_5_CYCLE_NO_DEADLOCK)
        self.assertFalse(engine.last_detection_result.is_deadlocked)
        self.assertEqual(len(engine.last_detection_result.deadlocked_processes), 0)


if __name__ == "__main__":
    unittest.main()

