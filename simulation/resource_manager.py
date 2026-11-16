"""Resource Management and Accounting for Deadlock Simulation.

Course: Solving Problems Using Modelling and Simulation (SPMS) - NEC00091
"""

import numpy as np


class Resource:
    """Represents a specific resource type with finite multiple instances."""

    def __init__(self, rid: int, name: str, total_instances: int):
        if total_instances < 0:
            raise ValueError(f"Total instances for resource {name} cannot be negative.")
        self.rid = rid
        self.name = name
        self.total_instances = int(total_instances)
        self.allocated_instances = 0

    @property
    def available_instances(self) -> int:
        return max(0, self.total_instances - self.allocated_instances)

    def to_dict(self) -> dict:
        return {
            "rid": self.rid,
            "name": self.name,
            "total": self.total_instances,
            "allocated": self.allocated_instances,
            "available": self.available_instances,
            "utilization_pct": (
                round((self.allocated_instances / self.total_instances) * 100, 2)
                if self.total_instances > 0
                else 0.0
            ),
        }

    def __repr__(self) -> str:
        return f"Resource({self.name}, total={self.total_instances}, avail={self.available_instances})"


class ResourceManager:
    """Manages the pool of system resources and performs consistency checks."""

    def __init__(self, resource_names: list[str], total_instances: list[int] | np.ndarray):
        if len(resource_names) != len(total_instances):
            raise ValueError("Number of resource names must match number of total instance counts.")

        self.resources: list[Resource] = [
            Resource(i, name, total)
            for i, (name, total) in enumerate(zip(resource_names, total_instances))
        ]

    @property
    def num_resources(self) -> int:
        return len(self.resources)

    @property
    def resource_names(self) -> list[str]:
        return [r.name for r in self.resources]

    @property
    def total_vector(self) -> np.ndarray:
        return np.array([r.total_instances for r in self.resources], dtype=int)

    @property
    def available_vector(self) -> np.ndarray:
        return np.array([r.available_instances for r in self.resources], dtype=int)

    @property
    def allocated_vector(self) -> np.ndarray:
        return np.array([r.allocated_instances for r in self.resources], dtype=int)

    def update_allocations(self, allocation_matrix: np.ndarray | list[list[int]]) -> None:
        """Update resource allocation counters from an Allocation matrix (n x m)."""
        mat = np.array(allocation_matrix, dtype=int)
        if mat.size == 0:
            for r in self.resources:
                r.allocated_instances = 0
            return

        col_sums = np.sum(mat, axis=0)
        if len(col_sums) != self.num_resources:
            raise ValueError(
                f"Allocation matrix columns ({len(col_sums)}) must match resource count ({self.num_resources})."
            )

        for j, r in enumerate(self.resources):
            allocated_count = int(col_sums[j])
            if allocated_count > r.total_instances:
                raise ValueError(
                    f"Resource {r.name} over-allocated: requested total {allocated_count} exceeds capacity {r.total_instances}."
                )
            r.allocated_instances = allocated_count

    def get_summary(self) -> list[dict]:
        return [r.to_dict() for r in self.resources]

