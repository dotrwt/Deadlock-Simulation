"""Deadlock Recovery Algorithms and Strategies.

Course: Solving Problems Using Modelling and Simulation (SPMS) - NEC00091
Techniques: Process Termination and Resource Preemption with Heuristic Victim Selection.
"""

from enum import Enum
from dataclasses import dataclass
import numpy as np
from algorithms.detection import detect_deadlock, DetectionResult


class VictimSelectionHeuristic(Enum):
    """Heuristic strategies for choosing a victim process."""
    LARGEST_ALLOCATION = "Largest Allocation (Reclaims Most Resources)"
    SMALLEST_ALLOCATION = "Smallest Allocation (Minimizes Wasted Work)"
    LOWEST_PRIORITY = "Lowest Priority Process"
    MANUAL = "Manual Selection (User Specified)"


@dataclass
class RecoveryRecord:
    """Audit record capturing the exact state before and after recovery."""
    strategy: str  # "TERMINATION" or "PREEMPTION"
    victim_idx: int
    victim_name: str
    resources_reclaimed: list[int]
    available_before: list[int]
    available_after: list[int]
    deadlocked_before: list[int]
    deadlocked_after: list[int]
    is_resolved: bool
    summary: str
    detection_after: DetectionResult


def select_victim(
    deadlocked_indices: list[int],
    allocation_matrix: np.ndarray | list[list[int]],
    priorities: list[int] | None = None,
    heuristic: VictimSelectionHeuristic = VictimSelectionHeuristic.LARGEST_ALLOCATION,
    manual_idx: int | None = None,
) -> int:
    """Select the victim process from the deadlocked set based on a chosen heuristic."""
    if not deadlocked_indices:
        raise ValueError("Cannot select victim: No processes are currently deadlocked.")

    if heuristic == VictimSelectionHeuristic.MANUAL:
        if manual_idx is not None and manual_idx in deadlocked_indices:
            return manual_idx
        return deadlocked_indices[0]

    alloc = np.array(allocation_matrix, dtype=int)

    if heuristic == VictimSelectionHeuristic.LARGEST_ALLOCATION:
        # Pick the process holding the maximum total resource units
        best_idx = deadlocked_indices[0]
        max_held = -1
        for idx in deadlocked_indices:
            total_held = int(np.sum(alloc[idx]))
            if total_held > max_held:
                max_held = total_held
                best_idx = idx
        return best_idx

    elif heuristic == VictimSelectionHeuristic.SMALLEST_ALLOCATION:
        # Pick the process holding the minimum resource units
        best_idx = deadlocked_indices[0]
        min_held = float("inf")
        for idx in deadlocked_indices:
            total_held = int(np.sum(alloc[idx]))
            if total_held < min_held:
                min_held = total_held
                best_idx = idx
        return best_idx

    elif heuristic == VictimSelectionHeuristic.LOWEST_PRIORITY:
        # Pick the process with lowest priority value (or highest integer if 1 is lowest)
        if priorities is None or len(priorities) <= max(deadlocked_indices):
            return deadlocked_indices[0]
        # Assume smaller integer = lower priority
        best_idx = min(deadlocked_indices, key=lambda idx: priorities[idx])
        return best_idx

    return deadlocked_indices[0]


def recover_by_termination(
    victim_idx: int,
    available: np.ndarray | list[int],
    allocation: np.ndarray | list[list[int]],
    request: np.ndarray | list[list[int]],
    process_names: list[str] | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, RecoveryRecord]:
    """Terminate the designated victim process, reclaim all its resources, and re-check."""
    avail = np.array(available, dtype=int).copy()
    alloc = np.array(allocation, dtype=int).copy()
    req = np.array(request, dtype=int).copy()

    n_proc = alloc.shape[0]
    names = process_names if process_names else [f"P{i}" for i in range(n_proc)]
    victim_name = names[victim_idx]

    # Pre-recovery detection check
    initial_detection = detect_deadlock(avail, alloc, req, names)
    deadlocked_before = list(initial_detection.deadlocked_processes)
    available_before = avail.tolist()

    # Reclaim resources from terminated process
    reclaimed = alloc[victim_idx].copy()
    avail = avail + reclaimed
    alloc[victim_idx] = 0
    req[victim_idx] = 0

    # Post-recovery detection check
    post_detection = detect_deadlock(avail, alloc, req, names)
    deadlocked_after = list(post_detection.deadlocked_processes)
    is_resolved = len(deadlocked_after) == 0

    if is_resolved:
        summary = (
            f"RECOVERY SUCCESSFUL: Terminated process {victim_name} and reclaimed "
            f"{reclaimed.tolist()} resource instances. Deadlock is completely resolved! "
            f"All remaining processes can now finish."
        )
    else:
        remaining_names = [names[i] for i in deadlocked_after]
        summary = (
            f"PARTIAL RECOVERY: Terminated process {victim_name} and reclaimed "
            f"{reclaimed.tolist()} resource instances. Deadlock persists for: "
            f"[{', '.join(remaining_names)}]. Additional process termination may be required."
        )

    record = RecoveryRecord(
        strategy="PROCESS_TERMINATION",
        victim_idx=victim_idx,
        victim_name=victim_name,
        resources_reclaimed=reclaimed.tolist(),
        available_before=available_before,
        available_after=avail.tolist(),
        deadlocked_before=deadlocked_before,
        deadlocked_after=deadlocked_after,
        is_resolved=is_resolved,
        summary=summary,
        detection_after=post_detection,
    )

    return avail, alloc, req, record


def recover_by_preemption(
    victim_idx: int,
    resource_idx: int,
    amount: int,
    available: np.ndarray | list[int],
    allocation: np.ndarray | list[list[int]],
    request: np.ndarray | list[list[int]],
    process_names: list[str] | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, RecoveryRecord]:
    """Preempt a specified quantity of a resource from a victim, returning it to Available."""
    avail = np.array(available, dtype=int).copy()
    alloc = np.array(allocation, dtype=int).copy()
    req = np.array(request, dtype=int).copy()

    n_proc = alloc.shape[0]
    names = process_names if process_names else [f"P{i}" for i in range(n_proc)]
    victim_name = names[victim_idx]

    current_held = alloc[victim_idx, resource_idx]
    if amount > current_held:
        raise ValueError(
            f"Cannot preempt {amount} units of resource R{resource_idx} from {victim_name}; "
            f"it only holds {current_held} unit(s)."
        )

    initial_detection = detect_deadlock(avail, alloc, req, names)
    deadlocked_before = list(initial_detection.deadlocked_processes)
    available_before = avail.tolist()

    # Preempt: decrease allocation, increase request, increase available
    alloc[victim_idx, resource_idx] -= amount
    req[victim_idx, resource_idx] += amount
    avail[resource_idx] += amount

    reclaimed_vector = [0] * len(avail)
    reclaimed_vector[resource_idx] = amount

    post_detection = detect_deadlock(avail, alloc, req, names)
    deadlocked_after = list(post_detection.deadlocked_processes)
    is_resolved = len(deadlocked_after) == 0

    if is_resolved:
        summary = (
            f"PREEMPTION SUCCESSFUL: Preempted {amount} unit(s) of R{resource_idx} from {victim_name}. "
            f"Deadlock has been resolved without aborting the process."
        )
    else:
        remaining_names = [names[i] for i in deadlocked_after]
        summary = (
            f"PARTIAL PREEMPTION: Preempted {amount} unit(s) of R{resource_idx} from {victim_name}. "
            f"Deadlock persists for: [{', '.join(remaining_names)}]."
        )

    record = RecoveryRecord(
        strategy="RESOURCE_PREEMPTION",
        victim_idx=victim_idx,
        victim_name=victim_name,
        resources_reclaimed=reclaimed_vector,
        available_before=available_before,
        available_after=avail.tolist(),
        deadlocked_before=deadlocked_before,
        deadlocked_after=deadlocked_after,
        is_resolved=is_resolved,
        summary=summary,
        detection_after=post_detection,
    )

    return avail, alloc, req, record

