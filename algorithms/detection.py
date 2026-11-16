"""Deadlock Detection Algorithm for Multiple Resource Instances.

Course: Solving Problems Using Modelling and Simulation (SPMS) - NEC00091
Theoretical Foundation: Coffman, Elphick & Shoshani (1971), Silberschatz et al.
"""

from dataclasses import dataclass, field
import numpy as np


@dataclass
class DetectionStep:
    """Detailed record of a single step in the Deadlock Detection algorithm."""
    step_num: int
    process_idx: int
    process_name: str
    request_vector: list[int]
    work_before: list[int]
    allocation_vector: list[int]
    can_finish: bool
    work_after: list[int]
    finish_vector: list[bool]
    message: str


@dataclass
class DetectionResult:
    """Comprehensive result of Deadlock Detection evaluation."""
    is_deadlocked: bool
    deadlocked_processes: list[int]
    deadlocked_names: list[str]
    completed_processes: list[int]
    completed_names: list[str]
    finish_vector: list[bool]
    steps: list[DetectionStep]
    work_final: list[int]
    explanation: str
    allocation_matrix: list[list[int]] = field(default_factory=list)
    request_matrix: list[list[int]] = field(default_factory=list)
    available_vector: list[int] = field(default_factory=list)


def detect_deadlock(
    available: np.ndarray | list[int],
    allocation: np.ndarray | list[list[int]],
    request: np.ndarray | list[list[int]],
    process_names: list[str] | None = None,
) -> DetectionResult:
    """Execute multiple-instance Deadlock Detection algorithm.

    Algorithm:
    1. Let Work = Available.copy()
    2. For i = 0, 1, ..., n-1:
         If Allocation[i] != 0:
             Finish[i] = False
         Else:
             Finish[i] = True (processes holding no resources cannot be part of deadlock)
    3. Find an index i such that:
         Finish[i] == False and Request[i] <= Work
       If found:
         Work = Work + Allocation[i]
         Finish[i] = True
         Repeat Step 3.
    4. If Finish[i] == False for any i:
         System is in DEADLOCK.
         Deadlocked processes = {P_i | Finish[i] == False}.
    """
    avail = np.array(available, dtype=int).copy()
    alloc = np.array(allocation, dtype=int).copy()
    req = np.array(request, dtype=int).copy()

    n_proc, n_res = alloc.shape
    if avail.shape[0] != n_res:
        raise ValueError(f"Available length ({avail.shape[0]}) != resource count ({n_res})")
    if req.shape != alloc.shape:
        raise ValueError(f"Request shape {req.shape} != Allocation shape {alloc.shape}")

    if process_names is None or len(process_names) != n_proc:
        names = [f"P{i}" for i in range(n_proc)]
    else:
        names = process_names

    work = avail.copy()

    # Step 2: Initialize Finish array
    finish = [False] * n_proc
    for i in range(n_proc):
        if np.all(alloc[i] == 0):
            finish[i] = True

    steps: list[DetectionStep] = []
    completed_seq: list[int] = []
    step_counter = 1
    progress_made = True

    while progress_made and not all(finish):
        progress_made = False

        for i in range(n_proc):
            if not finish[i]:
                req_i = req[i]
                alloc_i = alloc[i]
                can_satisfy = bool(np.all(req_i <= work))
                work_before = work.tolist()

                if can_satisfy:
                    work = work + alloc_i
                    finish[i] = True
                    completed_seq.append(i)
                    progress_made = True

                    step = DetectionStep(
                        step_num=step_counter,
                        process_idx=i,
                        process_name=names[i],
                        request_vector=req_i.tolist(),
                        work_before=work_before,
                        allocation_vector=alloc_i.tolist(),
                        can_finish=True,
                        work_after=work.tolist(),
                        finish_vector=list(finish),
                        message=(
                            f"Step {step_counter}: Process {names[i]} request {req_i.tolist()} <= Work {work_before}. "
                            f"Process can acquire remaining requests, finish, and reclaim its allocation {alloc_i.tolist()}. "
                            f"New Work = {work.tolist()}."
                        ),
                    )
                    steps.append(step)
                    step_counter += 1
                else:
                    step = DetectionStep(
                        step_num=step_counter,
                        process_idx=i,
                        process_name=names[i],
                        request_vector=req_i.tolist(),
                        work_before=work_before,
                        allocation_vector=alloc_i.tolist(),
                        can_finish=False,
                        work_after=work_before,
                        finish_vector=list(finish),
                        message=(
                            f"Step {step_counter}: Process {names[i]} cannot proceed. "
                            f"Request {req_i.tolist()} > Work {work_before}. Blocked."
                        ),
                    )
                    steps.append(step)
                    step_counter += 1

    deadlocked_idx = [i for i, f in enumerate(finish) if not f]
    is_deadlocked = len(deadlocked_idx) > 0

    if is_deadlocked:
        d_names = [names[i] for i in deadlocked_idx]
        explanation = (
            f"DEADLOCK DETECTED! {len(deadlocked_idx)} process(es) cannot complete: "
            f"[{', '.join(d_names)}]. Mutual circular waiting or resource withholding prevents "
            f"these processes from receiving their pending requests."
        )
    else:
        c_names = [names[i] for i in completed_seq]
        explanation = (
            f"NO DEADLOCK DETECTED. All processes can acquire their requested resources and run to "
            f"completion. An orderly completion sequence was identified: <{' -> '.join(c_names)}>."
        )

    return DetectionResult(
        is_deadlocked=is_deadlocked,
        deadlocked_processes=deadlocked_idx,
        deadlocked_names=[names[i] for i in deadlocked_idx],
        completed_processes=completed_seq,
        completed_names=[names[i] for i in completed_seq],
        finish_vector=finish,
        steps=steps,
        work_final=work.tolist(),
        explanation=explanation,
        allocation_matrix=alloc.tolist(),
        request_matrix=req.tolist(),
        available_vector=avail.tolist(),
    )

