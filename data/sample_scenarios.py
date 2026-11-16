"""Predefined academic simulation scenarios for Operating System Deadlocks.

Course: Solving Problems Using Modelling and Simulation (SPMS) - NEC00091
Includes:
- Scenario 1: Safe State (Banker's Avoidance)
- Scenario 2: Unsafe State (Dijkstra's Avoidance Warning)
- Scenario 3: Deadlock Condition (Mutual Circular Wait)
- Scenario 4: Deadlock Recovery (Victim Termination/Preemption)
- Scenario 5: Multi-Instance Cycle Without Deadlock (Educational Highlight)
"""

from dataclasses import dataclass
import numpy as np


@dataclass
class Scenario:
    """Descriptor for a predefined simulation configuration."""
    name: str
    scenario_id: str
    description: str
    theoretical_concept: str
    num_processes: int
    num_resources: int
    resource_names: list[str]
    total_resources: list[int]
    available_resources: list[int]
    allocation_matrix: list[list[int]]
    max_matrix: list[list[int]]
    request_matrix: list[list[int]]
    process_names: list[str]
    priorities: list[int]
    expected_status: str


SCENARIO_1_SAFE = Scenario(
    name="Scenario 1: Safe State (Banker's Avoidance)",
    scenario_id="scenario_1_safe",
    description=(
        "Standard classic 5 processes (P0 to P4) and 3 resource types (A: 10, B: 5, C: 7). "
        "Available resources [3, 3, 2] allow P1 to satisfy its need [1, 2, 2], release its resources, "
        "enabling an orderly execution of all processes."
    ),
    theoretical_concept="Deadlock Avoidance - Safe Sequence Guarantees No Deadlock",
    num_processes=5,
    num_resources=3,
    resource_names=["A", "B", "C"],
    total_resources=[10, 5, 7],
    available_resources=[3, 3, 2],
    allocation_matrix=[
        [0, 1, 0],  # P0
        [2, 0, 0],  # P1
        [3, 0, 2],  # P2
        [2, 1, 1],  # P3
        [0, 0, 2],  # P4
    ],
    max_matrix=[
        [7, 5, 3],  # P0 (Need: [7, 4, 3])
        [3, 2, 2],  # P1 (Need: [1, 2, 2])
        [9, 0, 2],  # P2 (Need: [6, 0, 0])
        [2, 2, 2],  # P3 (Need: [0, 1, 1])
        [4, 3, 3],  # P4 (Need: [4, 3, 1])
    ],
    request_matrix=[
        [0, 0, 0],
        [1, 0, 2],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
    ],
    process_names=["P0", "P1", "P2", "P3", "P4"],
    priorities=[3, 1, 4, 2, 5],
    expected_status="SAFE",
)


SCENARIO_2_UNSAFE = Scenario(
    name="Scenario 2: Unsafe State (Dijkstra's Warning)",
    scenario_id="scenario_2_unsafe",
    description=(
        "Allocations have consumed critical resource margins. Available resources are [1, 0, 0]. "
        "No single process can satisfy its remaining Need from current Available resources. "
        "The system is unsafe; if processes insist on maximum claims simultaneously, deadlock is guaranteed."
    ),
    theoretical_concept="Unsafe State != Deadlock (Unsafe is a Precursor Risk)",
    num_processes=4,
    num_resources=3,
    resource_names=["A", "B", "C"],
    total_resources=[8, 5, 5],
    available_resources=[1, 0, 0],
    allocation_matrix=[
        [2, 1, 1],  # P0
        [2, 2, 1],  # P1
        [2, 1, 2],  # P2
        [1, 1, 1],  # P3
    ],
    max_matrix=[
        [4, 3, 2],  # P0 Need: [2, 2, 1] > [1, 0, 0]
        [3, 4, 2],  # P1 Need: [1, 2, 1] > [1, 0, 0]
        [4, 2, 4],  # P2 Need: [2, 1, 2] > [1, 0, 0]
        [3, 3, 2],  # P3 Need: [2, 2, 1] > [1, 0, 0]
    ],
    request_matrix=[
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
        [0, 1, 0],
    ],
    process_names=["P0", "P1", "P2", "P3"],
    priorities=[2, 1, 3, 4],
    expected_status="UNSAFE",
)


SCENARIO_3_DEADLOCK = Scenario(
    name="Scenario 3: Deadlock Condition (Circular Wait)",
    scenario_id="scenario_3_deadlock",
    description=(
        "Classic 4-process circular wait. Total resources are [4, 4, 4], Available is [0, 0, 0]. "
        "P0 holds A and requests B; P1 holds B and requests C; P2 holds C and requests D/A; "
        "P3 holds remaining units and waits. Every process is blocked awaiting resources held by another."
    ),
    theoretical_concept="Deadlock Detection - Closed Circular Wait in Multi-Instance System",
    num_processes=4,
    num_resources=3,
    resource_names=["R1", "R2", "R3"],
    total_resources=[3, 3, 3],
    available_resources=[0, 0, 0],
    allocation_matrix=[
        [1, 0, 0],  # P0 holds R1
        [0, 1, 0],  # P1 holds R2
        [0, 0, 1],  # P2 holds R3
        [2, 2, 2],  # P3 holds remaining
    ],
    max_matrix=[
        [1, 1, 0],
        [0, 1, 1],
        [1, 0, 1],
        [2, 2, 3],
    ],
    request_matrix=[
        [0, 1, 0],  # P0 requests R2 (held by P1)
        [0, 0, 1],  # P1 requests R3 (held by P2)
        [1, 0, 0],  # P2 requests R1 (held by P0)
        [0, 0, 1],  # P3 requests R3
    ],
    process_names=["P0", "P1", "P2", "P3"],
    priorities=[4, 3, 2, 1],
    expected_status="DEADLOCKED",
)


SCENARIO_4_RECOVERY = Scenario(
    name="Scenario 4: Deadlock Recovery via Victim Selection",
    scenario_id="scenario_4_recovery",
    description=(
        "A 5-process deadlocked state where P1, P2, P3, and P4 are entangled in a deadlock. "
        "P2 holds the largest resource footprint ([3, 0, 3]). Selecting and terminating P2 "
        "as the victim reclaims 6 instances, immediately breaking the deadlock and freeing all remaining processes."
    ),
    theoretical_concept="Deadlock Recovery - Heuristic Victim Selection & Resource Preemption",
    num_processes=5,
    num_resources=3,
    resource_names=["Cpu", "Mem", "Disk"],
    total_resources=[7, 2, 6],
    available_resources=[0, 0, 0],
    allocation_matrix=[
        [0, 1, 0],  # P0 (idle, finishes first)
        [2, 0, 0],  # P1 (entangled)
        [3, 0, 3],  # P2 (entangled, heavy allocation)
        [2, 1, 1],  # P3 (entangled)
        [0, 0, 2],  # P4 (entangled)
    ],
    max_matrix=[
        [1, 1, 0],
        [4, 0, 2],
        [3, 0, 4],
        [3, 1, 1],
        [0, 0, 4],
    ],
    request_matrix=[
        [0, 0, 0],  # P0 (no requests)
        [2, 0, 2],  # P1
        [0, 0, 1],  # P2
        [1, 0, 0],  # P3
        [0, 0, 2],  # P4
    ],
    process_names=["P0", "P1", "P2", "P3", "P4"],
    priorities=[1, 2, 5, 3, 4],
    expected_status="DEADLOCKED_RECOVERABLE",
)


SCENARIO_5_CYCLE_NO_DEADLOCK = Scenario(
    name="Scenario 5: Multi-Instance Cycle Without Deadlock (Vital Academic Concept)",
    scenario_id="scenario_5_cycle_no_deadlock",
    description=(
        "Silberschatz Figure 5.3: P1 and P2 participate in a circular wait cycle with R1 and R2. "
        "However, P3 and P4 also hold instances of R1 and R2 and have NO pending requests. "
        "P3 and P4 execute and release their instances, providing the needed resources to P1 and P2! "
        "Conclusion: In multi-instance systems, a cycle is NOT sufficient to cause a deadlock."
    ),
    theoretical_concept="Graph Theory - Cycle is Necessary but NOT Sufficient with Multiple Instances",
    num_processes=4,
    num_resources=2,
    resource_names=["R1 (2 units)", "R2 (2 units)"],
    total_resources=[2, 2],
    available_resources=[0, 0],
    allocation_matrix=[
        [1, 0],  # P1 holds 1 of R1
        [0, 1],  # P2 holds 1 of R2
        [1, 0],  # P3 holds 1 of R1
        [0, 1],  # P4 holds 1 of R2
    ],
    max_matrix=[
        [1, 1],
        [1, 1],
        [1, 0],
        [0, 1],
    ],
    request_matrix=[
        [0, 1],  # P1 requests R2 (Cycle: P1 -> R2 -> P2 -> R1 -> P1)
        [1, 0],  # P2 requests R1
        [0, 0],  # P3 requests NOTHING!
        [0, 0],  # P4 requests NOTHING!
    ],
    process_names=["P1", "P2", "P3", "P4"],
    priorities=[1, 2, 3, 4],
    expected_status="NO_DEADLOCK_DESPITE_CYCLE",
)


ALL_SCENARIOS = [
    SCENARIO_1_SAFE,
    SCENARIO_2_UNSAFE,
    SCENARIO_3_DEADLOCK,
    SCENARIO_4_RECOVERY,
    SCENARIO_5_CYCLE_NO_DEADLOCK,
]


def get_scenario_by_id(scenario_id: str) -> Scenario:
    for sc in ALL_SCENARIOS:
        if sc.scenario_id == scenario_id:
            return sc
    return SCENARIO_1_SAFE

