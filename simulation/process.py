"""Process representation and state management for Deadlock Simulation.

Course: Solving Problems Using Modelling and Simulation (SPMS) - NEC00091
"""

from enum import Enum
import numpy as np


class ProcessState(Enum):
    """Execution state of a process."""
    NEW = "NEW"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    DEADLOCKED = "DEADLOCKED"
    TERMINATED = "TERMINATED"
    FINISHED = "FINISHED"


class Process:
    """Represents a simulated operating system process."""

    def __init__(
        self,
        pid: int,
        name: str | None = None,
        max_claim: list[int] | np.ndarray | None = None,
        allocation: list[int] | np.ndarray | None = None,
        request: list[int] | np.ndarray | None = None,
        priority: int = 1,
    ):
        self.pid = pid
        self.name = name if name is not None else f"P{pid}"
        self.priority = priority
        self.state = ProcessState.READY

        self.max_claim = (
            np.array(max_claim, dtype=int)
            if max_claim is not None
            else np.array([], dtype=int)
        )
        self.allocation = (
            np.array(allocation, dtype=int)
            if allocation is not None
            else np.zeros_like(self.max_claim, dtype=int)
        )
        self.request = (
            np.array(request, dtype=int)
            if request is not None
            else np.zeros_like(self.max_claim, dtype=int)
        )

    @property
    def need(self) -> np.ndarray:
        """Need vector: Max Claim - Current Allocation."""
        if len(self.max_claim) == 0:
            return np.array([], dtype=int)
        calc_need = self.max_claim - self.allocation
        return np.maximum(calc_need, 0)

    @property
    def total_allocated(self) -> int:
        """Sum of all resource instances currently held."""
        return int(np.sum(self.allocation)) if len(self.allocation) > 0 else 0

    @property
    def total_requested(self) -> int:
        """Sum of all resource instances currently requested."""
        return int(np.sum(self.request)) if len(self.request) > 0 else 0

    def copy(self) -> "Process":
        """Create a deep copy of the process."""
        p = Process(
            pid=self.pid,
            name=self.name,
            max_claim=self.max_claim.copy(),
            allocation=self.allocation.copy(),
            request=self.request.copy(),
            priority=self.priority,
        )
        p.state = self.state
        return p

    def to_dict(self) -> dict:
        """Serialize process data for reporting or export."""
        return {
            "pid": self.pid,
            "name": self.name,
            "state": self.state.value,
            "priority": self.priority,
            "allocation": self.allocation.tolist(),
            "max_claim": self.max_claim.tolist(),
            "need": self.need.tolist(),
            "request": self.request.tolist(),
            "total_allocated": self.total_allocated,
        }

    def __repr__(self) -> str:
        return f"Process({self.name}, state={self.state.value}, alloc={self.allocation.tolist()}, need={self.need.tolist()})"

