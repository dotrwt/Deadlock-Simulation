"""Simulation Analytics and Charts using Matplotlib.

Course: Solving Problems Using Modelling and Simulation (SPMS) - NEC00091
Implements:
1. Resource utilization bar chart (Allocated vs Available vs Total).
2. Process allocation stacked breakdown.
3. Process Remaining Need vs Current Allocation comparison.
4. Simulation state history timeline.
"""

from matplotlib.figure import Figure
import numpy as np


def plot_resource_utilization(
    fig: Figure,
    resource_names: list[str],
    total_resources: list[int] | np.ndarray,
    available_resources: list[int] | np.ndarray,
    allocated_resources: list[int] | np.ndarray,
) -> None:
    """Plot grouped bar chart of Total, Allocated, and Available resource instances."""
    fig.clear()
    ax = fig.add_subplot(111)

    r_names = resource_names if resource_names else [f"R{i}" for i in range(len(total_resources))]
    tot = np.array(total_resources, dtype=int)
    avail = np.array(available_resources, dtype=int)
    alloc = np.array(allocated_resources, dtype=int)

    x = np.arange(len(r_names))
    width = 0.26

    rects1 = ax.bar(x - width, tot, width, label="Total Capacity", color="#64748b")
    rects2 = ax.bar(x, alloc, width, label="Allocated", color="#3b82f6")
    rects3 = ax.bar(x + width, avail, width, label="Available", color="#10b981")

    ax.set_ylabel("Resource Instances", fontsize=10, fontweight="bold")
    ax.set_title("Resource Utilization and Availability by Type", fontsize=11, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(r_names, fontsize=9, fontweight="bold")
    ax.legend(loc="upper right", framealpha=0.9)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    # Add numeric labels on bars
    for rects in [rects1, rects2, rects3]:
        for rect in rects:
            height = rect.get_height()
            ax.annotate(
                f"{height}",
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    fig.tight_layout()


def plot_process_allocation_breakdown(
    fig: Figure,
    process_names: list[str],
    resource_names: list[str],
    allocation_matrix: np.ndarray | list[list[int]],
) -> None:
    """Plot stacked bar chart showing resource allocation distribution across processes."""
    fig.clear()
    ax = fig.add_subplot(111)

    alloc = np.array(allocation_matrix, dtype=int)
    n_proc, n_res = alloc.shape
    p_names = process_names if process_names else [f"P{i}" for i in range(n_proc)]
    r_names = resource_names if resource_names else [f"R{j}" for j in range(n_res)]

    colors = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#14b8a6", "#6366f1"]
    bottom = np.zeros(n_proc)

    for j in range(n_res):
        c = colors[j % len(colors)]
        values = alloc[:, j]
        ax.bar(p_names, values, bottom=bottom, label=f"Resource {r_names[j]}", color=c, width=0.5)
        bottom += values

    ax.set_ylabel("Total Instances Held", fontsize=10, fontweight="bold")
    ax.set_title("Current Process Resource Allocation Breakdown", fontsize=11, fontweight="bold")
    ax.set_xlabel("Processes", fontsize=10, fontweight="bold")
    ax.legend(loc="upper right", framealpha=0.9)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for i, total_held in enumerate(bottom):
        if total_held > 0:
            ax.annotate(
                f"Held: {int(total_held)}",
                xy=(i, total_held),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold",
            )

    fig.tight_layout()


def plot_need_vs_allocation(
    fig: Figure,
    process_names: list[str],
    allocation_matrix: np.ndarray | list[list[int]],
    need_matrix: np.ndarray | list[list[int]],
) -> None:
    """Plot side-by-side comparison of total held vs remaining total need for each process."""
    fig.clear()
    ax = fig.add_subplot(111)

    alloc = np.array(allocation_matrix, dtype=int)
    need = np.array(need_matrix, dtype=int)
    n_proc = alloc.shape[0]
    p_names = process_names if process_names else [f"P{i}" for i in range(n_proc)]

    tot_alloc_per_proc = np.sum(alloc, axis=1)
    tot_need_per_proc = np.sum(need, axis=1)

    x = np.arange(n_proc)
    width = 0.35

    rects1 = ax.bar(x - width / 2, tot_alloc_per_proc, width, label="Current Allocation (Held)", color="#3b82f6")
    rects2 = ax.bar(x + width / 2, tot_need_per_proc, width, label="Remaining Need (Required)", color="#ef4444")

    ax.set_ylabel("Resource Units Sum", fontsize=10, fontweight="bold")
    ax.set_title("Process Demand Profile: Allocation vs Remaining Need", fontsize=11, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(p_names, fontsize=9, fontweight="bold")
    ax.legend(loc="upper right", framealpha=0.9)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for rects in [rects1, rects2]:
        for rect in rects:
            height = rect.get_height()
            ax.annotate(
                f"{height}",
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 2),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    fig.tight_layout()

