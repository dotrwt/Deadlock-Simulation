"""Unit tests for Banker's Algorithm.

Course: Solving Problems Using Modelling and Simulation (SPMS) - NEC00091
"""

import unittest
import numpy as np
from algorithms.bankers import (
    calculate_need,
    check_safety,
    evaluate_resource_request,
)


class TestBankersAlgorithm(unittest.TestCase):
    """Test suite for Banker's Algorithm safety and resource request."""

    def setUp(self):
        """Standard classic Silberschatz textbook scenario:
        5 Processes (P0 to P4), 3 Resource types (A: 10, B: 5, C: 7).
        """
        self.allocation = np.array([
            [0, 1, 0],  # P0
            [2, 0, 0],  # P1
            [3, 0, 2],  # P2
            [2, 1, 1],  # P3
            [0, 0, 2],  # P4
        ])

        self.max_matrix = np.array([
            [7, 5, 3],  # P0
            [3, 2, 2],  # P1
            [9, 0, 2],  # P2
            [2, 2, 2],  # P3
            [4, 3, 3],  # P4
        ])

        self.available = np.array([3, 3, 2])
        self.names = ["P0", "P1", "P2", "P3", "P4"]

    def test_need_calculation(self):
        """Test Need = Max - Allocation."""
        expected_need = np.array([
            [7, 4, 3],
            [1, 2, 2],
            [6, 0, 0],
            [0, 1, 1],
            [4, 3, 1],
        ])
        calculated_need = calculate_need(self.max_matrix, self.allocation)
        np.testing.assert_array_equal(calculated_need, expected_need)

    def test_safe_state(self):
        """Test standard safe state detection and safe sequence derivation."""
        result = check_safety(self.available, self.allocation, self.max_matrix, self.names)
        self.assertTrue(result.is_safe)
        self.assertEqual(len(result.safe_sequence), 5)
        # All 5 processes should be finished
        self.assertEqual(len(result.unfinished_processes), 0)
        # P1 has need [1, 2, 2] <= [3, 3, 2], so P1 should be able to run first
        self.assertEqual(result.safe_sequence[0], 1)
        self.assertEqual(result.safe_sequence_names[0], "P1")

    def test_unsafe_state(self):
        """Test detection of an unsafe state."""
        # Deplete available resources so no process can run
        low_available = np.array([0, 0, 0])
        result = check_safety(low_available, self.allocation, self.max_matrix, self.names)
        self.assertFalse(result.is_safe)
        self.assertGreater(len(result.unfinished_processes), 0)

    def test_valid_resource_request(self):
        """P1 requests [1, 0, 2] -> Should be granted."""
        req = [1, 0, 2]
        res = evaluate_resource_request(
            pid=1,
            request=req,
            available=self.available,
            allocation=self.allocation,
            max_matrix=self.max_matrix,
            process_names=self.names,
        )
        self.assertTrue(res.granted)
        self.assertIsNotNone(res.safety_result)
        self.assertTrue(res.safety_result.is_safe)
        self.assertEqual(res.new_available, [2, 3, 0])
        self.assertEqual(res.new_allocation[1], [3, 0, 2])

    def test_request_exceeding_need(self):
        """P1 requests more than its need -> Should be rejected immediately."""
        req = [2, 0, 0]  # P1 need is [1, 2, 2], so req[0] > need[0]
        res = evaluate_resource_request(
            pid=1,
            request=req,
            available=self.available,
            allocation=self.allocation,
            max_matrix=self.max_matrix,
            process_names=self.names,
        )
        self.assertFalse(res.granted)
        self.assertIn("exceeds its remaining Need", res.reason)

    def test_request_exceeding_available(self):
        """P0 requests [4, 0, 0] when Available is [3, 3, 2] -> Must wait."""
        req = [4, 0, 0]
        res = evaluate_resource_request(
            pid=0,
            request=req,
            available=self.available,
            allocation=self.allocation,
            max_matrix=self.max_matrix,
            process_names=self.names,
        )
        self.assertFalse(res.granted)
        self.assertIn("Wait", res.reason)

    def test_invalid_allocation_exceeding_max(self):
        """Allocation higher than Max must raise ValueError."""
        invalid_alloc = self.allocation.copy()
        invalid_alloc[0, 0] = 99  # max is 7
        with self.assertRaises(ValueError):
            calculate_need(self.max_matrix, invalid_alloc)


if __name__ == "__main__":
    unittest.main()

