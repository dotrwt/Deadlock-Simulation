"""Unit tests for Deadlock Recovery Strategies.

Course: Solving Problems Using Modelling and Simulation (SPMS) - NEC00091
"""

import unittest
import numpy as np
from algorithms.recovery import (
    select_victim,
    recover_by_termination,
    recover_by_preemption,
    VictimSelectionHeuristic,
)


class TestDeadlockRecovery(unittest.TestCase):
    """Test suite for Deadlock Recovery algorithms."""

    def setUp(self):
        """Deadlocked setup with 5 processes and 3 resources."""
        self.allocation = np.array([
            [0, 1, 0],  # P0
            [2, 0, 0],  # P1
            [3, 0, 3],  # P2
            [2, 1, 1],  # P3
            [0, 0, 2],  # P4
        ])
        self.request = np.array([
            [0, 0, 0],  # P0
            [2, 0, 2],  # P1
            [0, 0, 1],  # P2
            [1, 0, 0],  # P3
            [0, 0, 2],  # P4
        ])
        self.available = np.array([0, 0, 0])
        self.names = ["P0", "P1", "P2", "P3", "P4"]
        self.priorities = [1, 2, 5, 3, 4]  # P0 has priority 1, P1 has 2, etc.

    def test_victim_selection_largest_allocation(self):
        """P2 holds sum([3,0,3])=6 resources, the highest among deadlocked P1, P2, P3, P4."""
        deadlocked = [1, 2, 3, 4]
        victim = select_victim(
            deadlocked,
            self.allocation,
            self.priorities,
            heuristic=VictimSelectionHeuristic.LARGEST_ALLOCATION,
        )
        self.assertEqual(victim, 2)

    def test_victim_selection_lowest_priority(self):
        """Among [1, 2, 3, 4], P1 has priority 2, which is lowest."""
        deadlocked = [1, 2, 3, 4]
        victim = select_victim(
            deadlocked,
            self.allocation,
            self.priorities,
            heuristic=VictimSelectionHeuristic.LOWEST_PRIORITY,
        )
        self.assertEqual(victim, 1)

    def test_recover_by_terminating_p2(self):
        """Terminating P2 releases [3, 0, 3] resources, which should resolve the deadlock."""
        new_avail, new_alloc, new_req, record = recover_by_termination(
            victim_idx=2,
            available=self.available,
            allocation=self.allocation,
            request=self.request,
            process_names=self.names,
        )
        self.assertEqual(record.victim_name, "P2")
        self.assertEqual(record.resources_reclaimed, [3, 0, 3])
        self.assertTrue(record.is_resolved)
        self.assertEqual(len(record.deadlocked_after), 0)
        # Allocation of P2 must be cleared
        np.testing.assert_array_equal(new_alloc[2], [0, 0, 0])

    def test_recover_by_preemption(self):
        """Preempting 1 unit of resource C (index 2) from P3 (holds [2, 1, 1])."""
        new_avail, new_alloc, new_req, record = recover_by_preemption(
            victim_idx=3,
            resource_idx=2,
            amount=1,
            available=self.available,
            allocation=self.allocation,
            request=self.request,
            process_names=self.names,
        )
        self.assertEqual(record.victim_name, "P3")
        self.assertEqual(new_alloc[3, 2], 0)
        self.assertEqual(new_req[3, 2], 1)  # was 0, increased by 1
        self.assertEqual(new_avail[2], 1)   # was 0, increased by 1


if __name__ == "__main__":
    unittest.main()
