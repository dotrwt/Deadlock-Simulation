"""Unit tests for Deadlock Detection Algorithm.

Course: Solving Problems Using Modelling and Simulation (SPMS) - NEC00091
"""

import unittest
import numpy as np
from algorithms.detection import detect_deadlock


class TestDeadlockDetection(unittest.TestCase):
    """Test suite for Deadlock Detection in multiple-instance systems."""

    def setUp(self):
        """Standard 5 processes, 3 resource types."""
        self.allocation = np.array([
            [0, 1, 0],  # P0
            [2, 0, 0],  # P1
            [3, 0, 3],  # P2
            [2, 1, 1],  # P3
            [0, 0, 2],  # P4
        ])
        self.available = np.array([0, 0, 0])
        self.names = ["P0", "P1", "P2", "P3", "P4"]

    def test_no_deadlock_scenario(self):
        """Standard scenario where requests can be completely satisfied."""
        request = np.array([
            [0, 0, 0],  # P0 has no pending request
            [2, 0, 2],  # P1 requests [2, 0, 2]
            [0, 0, 0],  # P2 has no pending request
            [1, 0, 0],  # P3 requests [1, 0, 0]
            [0, 0, 2],  # P4 requests [0, 0, 2]
        ])

        result = detect_deadlock(self.available, self.allocation, request, self.names)
        self.assertFalse(result.is_deadlocked)
        self.assertEqual(len(result.deadlocked_processes), 0)
        self.assertEqual(len(result.completed_processes), 5)
        # P0 and P2 have zero requests, so P0 or P2 finish first and release their allocations
        self.assertIn("NO DEADLOCK", result.explanation)

    def test_deadlock_scenario(self):
        """Scenario where P2 requests [0, 0, 1], creating deadlock among P1, P2, P3, P4."""
        request = np.array([
            [0, 0, 0],  # P0
            [2, 0, 2],  # P1
            [0, 0, 1],  # P2 now requests 1 of C!
            [1, 0, 0],  # P3
            [0, 0, 2],  # P4
        ])

        result = detect_deadlock(self.available, self.allocation, request, self.names)
        self.assertTrue(result.is_deadlocked)
        self.assertEqual(set(result.deadlocked_processes), {1, 2, 3, 4})
        self.assertEqual(result.completed_processes, [0])
        self.assertIn("P1", result.deadlocked_names)
        self.assertIn("P2", result.deadlocked_names)
        self.assertIn("P3", result.deadlocked_names)
        self.assertIn("P4", result.deadlocked_names)

    def test_all_idle_processes_not_deadlocked(self):
        """Processes with no allocation and no request are not deadlocked."""
        alloc = np.zeros((3, 2), dtype=int)
        req = np.zeros((3, 2), dtype=int)
        avail = np.array([1, 1])
        res = detect_deadlock(avail, alloc, req)
        self.assertFalse(res.is_deadlocked)
        self.assertEqual(len(res.deadlocked_processes), 0)


if __name__ == "__main__":
    unittest.main()

