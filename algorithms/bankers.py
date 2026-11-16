"""Banker's Algorithm for Deadlock Avoidance.

Course: Solving Problems Using Modelling and Simulation (SPMS) - NEC00091
Theoretical Foundation: Edsger W. Dijkstra (1965)
"""

from dataclasses import dataclass, field
import numpy as np


@dataclass
class SafetyStep:
    """Detailed record of a single step in the Safety Algorithm."""
    step_num: int
    process_idx: int
    process_name: str
    work_before: list[int]
    need_vector: list[int]
    allocation_vector: list[int]
    can_allocate: bool
    work_after: list[int]
    finish_vector: list[bool]
    message: str


@dataclass
class BankersResult:
    """Comprehensive result of Banker's safety check."""
    is_safe: bool
    safe_sequence: list[int]
    safe_sequence_names: list[str]
    steps: list[SafetyStep]
    final_work: list[int]
    unfinished_processes: list[int]
    explanation: str
    need_matrix: list[list[int]] = field(default_factory=list)


@dataclass
class RequestResult:
    """Result of Banker's resource-request evaluation."""
    granted: bool
    reason: str
    safety_result: BankersResult | None
    new_available: list[int] | None = None
    new_allocation: list[list[int]] | None = None
    new_need: list[list[int]] | None = None


def calculate_need(
    max_matrix: np.ndarray | list[list[int]],
    allocation_matrix: np.ndarray | list[list[int]],
) -> np.ndarray:
    """Calculate Need Matrix = Max Matrix - Allocation Matrix.
    
    Validates that:
    1. Dimensions match.
    2. Allocation does not exceed Max claim for any process/resource.
    """
    max_mat = np.array(max_matrix, dtype=int)
    alloc_mat = np.array(allocation_matrix, dtype=int)

    if max_mat.shape != alloc_mat.shape:
        raise ValueError(
            f"Shape mismatch: Max matrix {max_mat.shape} != Allocation matrix {alloc_mat.shape}"
        )

    if np.any(alloc_mat < 0):
        raise ValueError("Allocation matrix cannot have negative values.")
    if np.any(max_mat < 0):
        raise ValueError("Max matrix cannot have negative values.")

    if np.any(alloc_mat > max_mat):
        violating = np.argwhere(alloc_mat > max_mat)
        details = ", ".join([f"P{p} for R{r} (alloc={alloc_mat[p, r]} > max={max_mat[p, r]})" for p, r in violating])
        raise ValueError(f"Allocation exceeds Max claim: {details}")

    return max_mat - alloc_mat


def check_safety(
    available: np.ndarray | list[int],
    allocation: np.ndarray | list[list[int]],
    max_matrix: np.ndarray | list[list[int]],
    process_names: list[str] | None = None,
) -> BankersResult:
    """Execute Dijkstra's Safety Algorithm step-by-step.
    
    Mathematical Formulation:
    - Work = Available
    - Finish[i] = False for all i in [0, n-1]
    - Find process i such that:
        Finish[i] == False and Need[i] <= Work
    - Work = Work + Allocation[i]; Finish[i] = True
    - Continue until all Finish[i] == True (Safe) or no candidate exists (Unsafe).
    """
    avail = np.array(available, dtype=int).copy()
    alloc = np.array(allocation, dtype=int).copy()
    max_m = np.array(max_matrix, dtype=int).copy()

    n_proc, n_res = alloc.shape
    if avail.shape[0] != n_res:
        raise ValueError(f"Available vector length ({avail.shape[0]}) != resource count ({n_res})")

    need = calculate_need(max_m, alloc)

    if process_names is None or len(process_names) != n_proc:
        names = [f"P{i}" for i in range(n_proc)]
    else:
        names = process_names

    work = avail.copy()
    finish = [False] * n_proc
    safe_seq: list[int] = []
    steps: list[SafetyStep] = []

    step_counter = 1
    progress_made = True

    while progress_made and len(safe_seq) < n_proc:
        progress_made = False

        for i in range(n_proc):
            if not finish[i]:
                need_i = need[i]
                alloc_i = alloc[i]
                can_allocate = bool(np.all(need_i <= work))

                work_before = work.tolist()

                if can_allocate:
                    work = work + alloc_i
                    finish[i] = True
                    safe_seq.append(i)
                    progress_made = True

                    step = SafetyStep(
                        step_num=step_counter,
                        process_idx=i,
                        process_name=names[i],
                        work_before=work_before,
                        need_vector=need_i.tolist(),
                        allocation_vector=alloc_i.tolist(),
                        can_allocate=True,
                        work_after=work.tolist(),
                        finish_vector=list(finish),
                        message=(
                            f"Step {step_counter}: Process {names[i]} satisfied! "
                            f"Need {need_i.tolist()} <= Work {work_before}. "
                            f"Process completes and releases {alloc_i.tolist()}. "
                            f"New Work = {work.tolist()}."
                        ),
                    )
                    steps.append(step)
                    step_counter += 1
                else:
                    step = SafetyStep(
                        step_num=step_counter,
                        process_idx=i,
                        process_name=names[i],
                        work_before=work_before,
                        need_vector=need_i.tolist(),
                        allocation_vector=alloc_i.tolist(),
                        can_allocate=False,
                        work_after=work_before,
                        finish_vector=list(finish),
                        message=(
                            f"Step {step_counter}: Process {names[i]} cannot run now. "
                            f"Need {need_i.tolist()} > Work {work_before}. Waiting for resources."
                        ),
                    )
                    steps.append(step)
                    step_counter += 1

    is_safe = (len(safe_seq) == n_proc)
    unfinished = [i for i, f in enumerate(finish) if not f]

    if is_safe:
        seq_str = " -> ".join([names[i] for i in safe_seq])
        explanation = (
            f"The system is in a SAFE STATE. A valid execution sequence exists: <{seq_str}>. "
            f"All {n_proc} processes can execute to completion without entering a deadlock."
        )
    else:
        unf_str = ", ".join([names[i] for i in unfinished])
        seq_str = " -> ".join([names[i] for i in safe_seq]) if safe_seq else "None"
        explanation = (
            f"The system is in an UNSAFE STATE! No complete safe sequence could be formed. "
            f"Partial sequence: <{seq_str}>. Unfinished processes: [{unf_str}]. "
            f"Insufficient available resources to satisfy remaining maximum demands."
        )

    return BankersResult(
        is_safe=is_safe,
        safe_sequence=safe_seq,
        safe_sequence_names=[names[i] for i in safe_seq],
        steps=steps,
        final_work=work.tolist(),
        unfinished_processes=unfinished,
        explanation=explanation,
        need_matrix=need.tolist(),
    )


def evaluate_resource_request(
    pid: int,
    request: np.ndarray | list[int],
    available: np.ndarray | list[int],
    allocation: np.ndarray | list[list[int]],
    max_matrix: np.ndarray | list[list[int]],
    process_names: list[str] | None = None,
) -> RequestResult:
    """Evaluate a dynamic resource request using Banker's Algorithm.
    
    Algorithm Rules:
    1. If Request[i] > Need[i]: Error (Process exceeded maximum claim)
    2. If Request[i] > Available: Process must wait (insufficient available)
    3. Pretend to allocate:
         Available' = Available - Request[i]
         Allocation'[i] = Allocation[i] + Request[i]
         Max'[i] = unchanged (Need'[i] = Need[i] - Request[i])
       Run Safety Algorithm on simulated state:
       - If Safe: Grant allocation.
       - If Unsafe: Rollback and wait.
    """
    req = np.array(request, dtype=int)
    avail = np.array(available, dtype=int)
    alloc = np.array(allocation, dtype=int)
    max_m = np.array(max_matrix, dtype=int)

    n_proc, n_res = alloc.shape
    if pid < 0 or pid >= n_proc:
        return RequestResult(
            granted=False,
            reason=f"Invalid Process ID {pid}. Must be between 0 and {n_proc - 1}.",
            safety_result=None,
        )

    if req.shape[0] != n_res:
        return RequestResult(
            granted=False,
            reason=f"Request length ({req.shape[0]}) does not match resource count ({n_res}).",
            safety_result=None,
        )

    if np.any(req < 0):
        return RequestResult(
            granted=False,
            reason="Resource request cannot contain negative quantities.",
            safety_result=None,
        )

    need = calculate_need(max_m, alloc)
    need_i = need[pid]
    p_name = process_names[pid] if process_names and pid < len(process_names) else f"P{pid}"

    # Rule 1: Request <= Need
    if np.any(req > need_i):
        violating = np.argwhere(req > need_i).flatten()
        return RequestResult(
            granted=False,
            reason=(
                f"Error: {p_name} has requested {req.tolist()}, which exceeds its "
                f"remaining Need {need_i.tolist()} on resource index {violating.tolist()}."
            ),
            safety_result=None,
        )

    # Rule 2: Request <= Available
    if np.any(req > avail):
        violating = np.argwhere(req > avail).flatten()
        return RequestResult(
            granted=False,
            reason=(
                f"Wait: {p_name} requested {req.tolist()}, but current Available is "
                f"{avail.tolist()}. Insufficient resources on index {violating.tolist()}."
            ),
            safety_result=None,
        )

    # Tentative allocation
    sim_avail = avail - req
    sim_alloc = alloc.copy()
    sim_alloc[pid] = sim_alloc[pid] + req

    # Run safety algorithm
    safety = check_safety(sim_avail, sim_alloc, max_m, process_names)

    if safety.is_safe:
        return RequestResult(
            granted=True,
            reason=(
                f"Request GRANTED for {p_name}: Allocating {req.tolist()} keeps the system in a "
                f"SAFE STATE. Valid safe sequence: <{' -> '.join(safety.safe_sequence_names)}>."
            ),
            safety_result=safety,
            new_available=sim_avail.tolist(),
            new_allocation=sim_alloc.tolist(),
            new_need=calculate_need(max_m, sim_alloc).tolist(),
        )
    else:
        return RequestResult(
            granted=False,
            reason=(
                f"Request DENIED for {p_name}: Allocating {req.tolist()} would leave the system in "
                f"an UNSAFE STATE (potential deadlock). Request must wait; state rolled back."
            ),
            safety_result=safety,
        )

