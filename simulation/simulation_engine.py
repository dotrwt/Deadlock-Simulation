"""Central Simulation Engine for Operating System Deadlock Modeling.

Course: Solving Problems Using Modelling and Simulation (SPMS) - NEC00091
Coordinates processes, resource allocation, Banker's avoidance, detection, and recovery.
"""

from dataclasses import dataclass
import copy
import numpy as np

from simulation.process import Process, ProcessState
from simulation.resource_manager import ResourceManager
from algorithms.bankers import (
    check_safety,
    evaluate_resource_request,
    calculate_need,
    BankersResult,
    RequestResult,
)
from algorithms.detection import detect_deadlock, DetectionResult
from algorithms.recovery import (
    recover_by_termination,
    recover_by_preemption,
    select_victim,
    VictimSelectionHeuristic,
    RecoveryRecord,
)
from data.sample_scenarios import Scenario, SCENARIO_1_SAFE, get_scenario_by_id


@dataclass
class SimulationSnapshot:
    """Immutable state snapshot for simulation history and playback."""
    step_index: int
    description: str
    available: list[int]
    allocation: list[list[int]]
    max_matrix: list[list[int]]
    request: list[list[int]]
    process_states: list[str]
    system_status: str


class SimulationEngine:
    """The central state machine and coordinator for deadlock simulations."""

    def __init__(self, initial_scenario: Scenario | None = None):
        self.scenario: Scenario = initial_scenario if initial_scenario else SCENARIO_1_SAFE
        self.processes: list[Process] = []
        self.resource_manager: ResourceManager | None = None
        self.system_status: str = "IDLE"
        self.history: list[SimulationSnapshot] = []
        self.log_messages: list[str] = []
        self.current_step_index: int = 0

        self.last_bankers_result: BankersResult | None = None
        self.last_detection_result: DetectionResult | None = None
        self.last_recovery_record: RecoveryRecord | None = None

        self.load_scenario(self.scenario)

    def log(self, message: str) -> None:
        self.log_messages.append(message)

    def load_scenario(self, scenario: Scenario) -> None:
        """Load a predefined or custom scenario configuration."""
        self.scenario = scenario
        self.processes.clear()
        self.log_messages.clear()
        self.history.clear()
        self.current_step_index = 0

        self.resource_manager = ResourceManager(
            resource_names=scenario.resource_names,
            total_instances=scenario.total_resources,
        )

        alloc_mat = np.array(scenario.allocation_matrix, dtype=int)
        max_mat = np.array(scenario.max_matrix, dtype=int)
        req_mat = np.array(scenario.request_matrix, dtype=int)

        for i in range(scenario.num_processes):
            name = scenario.process_names[i] if i < len(scenario.process_names) else f"P{i}"
            prio = scenario.priorities[i] if i < len(scenario.priorities) else 1
            proc = Process(
                pid=i,
                name=name,
                max_claim=max_mat[i],
                allocation=alloc_mat[i],
                request=req_mat[i],
                priority=prio,
            )
            self.processes.append(proc)

        self.resource_manager.update_allocations(alloc_mat)
        self.system_status = scenario.expected_status
        self.log(f"Loaded scenario: '{scenario.name}' ({scenario.num_processes} processes, {scenario.num_resources} resources).")

        self.record_snapshot("Initial scenario loaded")
        # Pre-evaluate state
        self.evaluate_system_state()

    def setup_custom(
        self,
        resource_names: list[str],
        total_resources: list[int],
        process_names: list[str],
        allocation_matrix: list[list[int]],
        max_matrix: list[list[int]],
        request_matrix: list[list[int]] | None = None,
        priorities: list[int] | None = None,
    ) -> None:
        """Configure the engine with user-defined matrices."""
        num_proc = len(process_names)
        num_res = len(resource_names)

        alloc = np.array(allocation_matrix, dtype=int)
        max_m = np.array(max_matrix, dtype=int)
        total = np.array(total_resources, dtype=int)

        if alloc.shape != (num_proc, num_res):
            raise ValueError(f"Allocation shape {alloc.shape} != expected ({num_proc}, {num_res})")
        if max_m.shape != (num_proc, num_res):
            raise ValueError(f"Max matrix shape {max_m.shape} != expected ({num_proc}, {num_res})")

        req = (
            np.array(request_matrix, dtype=int)
            if request_matrix is not None
            else np.zeros_like(alloc)
        )

        col_sums = np.sum(alloc, axis=0)
        avail = total - col_sums
        if np.any(avail < 0):
            violating = np.argwhere(avail < 0).flatten()
            details = [f"{resource_names[v]} (allocated={col_sums[v]}, total={total[v]})" for v in violating]
            raise ValueError(f"Total allocated exceeds total resources: {', '.join(details)}")

        prio = priorities if priorities else [1] * num_proc

        custom_scenario = Scenario(
            name="Custom Scenario",
            scenario_id="custom",
            description="User-configured matrix configuration.",
            theoretical_concept="Interactive Custom Model Simulation",
            num_processes=num_proc,
            num_resources=num_res,
            resource_names=resource_names,
            total_resources=total.tolist(),
            available_resources=avail.tolist(),
            allocation_matrix=alloc.tolist(),
            max_matrix=max_m.tolist(),
            request_matrix=req.tolist(),
            process_names=process_names,
            priorities=prio,
            expected_status="CUSTOM",
        )

        self.load_scenario(custom_scenario)

    def record_snapshot(self, description: str) -> None:
        """Save a snapshot of the current state into simulation history."""
        self.current_step_index += 1
        alloc, max_m, need, req, avail, total = self.get_matrices()
        snap = SimulationSnapshot(
            step_index=self.current_step_index,
            description=description,
            available=avail.tolist(),
            allocation=alloc.tolist(),
            max_matrix=max_m.tolist(),
            request=req.tolist(),
            process_states=[p.state.value for p in self.processes],
            system_status=self.system_status,
        )
        self.history.append(snap)

    def get_matrices(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Return (allocation, max, need, request, available, total) matrices as numpy arrays."""
        if not self.processes or not self.resource_manager:
            return (
                np.array([[]]),
                np.array([[]]),
                np.array([[]]),
                np.array([[]]),
                np.array([]),
                np.array([]),
            )

        alloc = np.array([p.allocation for p in self.processes], dtype=int)
        max_m = np.array([p.max_claim for p in self.processes], dtype=int)
        need = np.array([p.need for p in self.processes], dtype=int)
        req = np.array([p.request for p in self.processes], dtype=int)
        avail = self.resource_manager.available_vector
        total = self.resource_manager.total_vector

        return alloc, max_m, need, req, avail, total

    def evaluate_system_state(self) -> None:
        """Run both Banker's algorithm and Deadlock Detection to synchronize process states."""
        alloc, max_m, need, req, avail, total = self.get_matrices()
        names = [p.name for p in self.processes]

        # 1. Deadlock Detection
        det = detect_deadlock(avail, alloc, req, names)
        self.last_detection_result = det

        # Update process states based on detection
        for p in self.processes:
            if p.state == ProcessState.TERMINATED:
                continue
            if p.pid in det.deadlocked_processes:
                p.state = ProcessState.DEADLOCKED
            elif np.all(p.allocation == 0) and np.all(p.request == 0):
                p.state = ProcessState.FINISHED
            elif np.any(p.request > 0):
                p.state = ProcessState.WAITING
            else:
                p.state = ProcessState.READY

        # 2. Banker's Safety
        safety = check_safety(avail, alloc, max_m, names)
        self.last_bankers_result = safety

        if det.is_deadlocked:
            self.system_status = "DEADLOCKED"
        elif safety.is_safe:
            self.system_status = "SAFE"
        else:
            self.system_status = "UNSAFE"

    def run_bankers(self) -> BankersResult:
        """Execute Banker's Algorithm safety verification on current state."""
        alloc, max_m, need, req, avail, total = self.get_matrices()
        names = [p.name for p in self.processes]
        res = check_safety(avail, alloc, max_m, names)
        self.last_bankers_result = res
        self.log(f"Bankers Safety Checked: System is {'SAFE' if res.is_safe else 'UNSAFE'}.")
        return res

    def run_detection(self) -> DetectionResult:
        """Execute Deadlock Detection algorithm on current state."""
        alloc, max_m, need, req, avail, total = self.get_matrices()
        names = [p.name for p in self.processes]
        res = detect_deadlock(avail, alloc, req, names)
        self.last_detection_result = res
        self.log(f"Detection Executed: System {'has DEADLOCK' if res.is_deadlocked else 'has NO DEADLOCK'}.")
        self.evaluate_system_state()
        return res

    def request_resources(self, pid: int, request_vector: list[int] | np.ndarray) -> RequestResult:
        """Request resources dynamically for a process via Banker's algorithm."""
        alloc, max_m, need, req, avail, total = self.get_matrices()
        names = [p.name for p in self.processes]

        result = evaluate_resource_request(
            pid=pid,
            request=request_vector,
            available=avail,
            allocation=alloc,
            max_matrix=max_m,
            process_names=names,
        )

        if result.granted and result.new_allocation is not None:
            # Commit new allocation
            self.processes[pid].allocation = np.array(result.new_allocation[pid], dtype=int)
            self.resource_manager.update_allocations(
                np.array([p.allocation for p in self.processes], dtype=int)
            )
            self.log(f"Granted resource request {request_vector} to {names[pid]}.")
            self.record_snapshot(f"Request granted to {names[pid]}: {request_vector}")
            self.evaluate_system_state()
        else:
            self.log(f"Denied resource request {request_vector} for {names[pid]}: {result.reason}")

        return result

    def terminate_process(self, pid: int) -> RecoveryRecord:
        """Recover from deadlock by terminating process pid and releasing its resources."""
        alloc, max_m, need, req, avail, total = self.get_matrices()
        names = [p.name for p in self.processes]

        new_avail, new_alloc, new_req, record = recover_by_termination(
            victim_idx=pid,
            available=avail,
            allocation=alloc,
            request=req,
            process_names=names,
        )

        self.processes[pid].state = ProcessState.TERMINATED
        self.processes[pid].allocation = np.zeros_like(self.processes[pid].allocation)
        self.processes[pid].request = np.zeros_like(self.processes[pid].request)

        self.resource_manager.update_allocations(
            np.array([p.allocation for p in self.processes], dtype=int)
        )

        self.last_recovery_record = record
        self.log(f"Recovery: Terminated {names[pid]}. {record.summary}")
        self.record_snapshot(f"Terminated {names[pid]}")
        self.evaluate_system_state()
        return record

    def preempt_resource(self, pid: int, resource_idx: int, amount: int) -> RecoveryRecord:
        """Recover from deadlock by preempting amount units of resource_idx from process pid."""
        alloc, max_m, need, req, avail, total = self.get_matrices()
        names = [p.name for p in self.processes]

        new_avail, new_alloc, new_req, record = recover_by_preemption(
            victim_idx=pid,
            resource_idx=resource_idx,
            amount=amount,
            available=avail,
            allocation=alloc,
            request=req,
            process_names=names,
        )

        self.processes[pid].allocation = new_alloc[pid]
        self.processes[pid].request = new_req[pid]

        self.resource_manager.update_allocations(
            np.array([p.allocation for p in self.processes], dtype=int)
        )

        self.last_recovery_record = record
        self.log(f"Recovery: Preempted {amount} units of R{resource_idx} from {names[pid]}.")
        self.record_snapshot(f"Preempted R{resource_idx} from {names[pid]}")
        self.evaluate_system_state()
        return record

    def auto_recover(
        self, heuristic: VictimSelectionHeuristic = VictimSelectionHeuristic.LARGEST_ALLOCATION
    ) -> RecoveryRecord | None:
        """Automatically select a victim using the specified heuristic and terminate it."""
        self.evaluate_system_state()
        if not self.last_detection_result or not self.last_detection_result.is_deadlocked:
            self.log("Auto-recover skipped: System is not deadlocked.")
            return None

        alloc, _, _, _, _, _ = self.get_matrices()
        priorities = [p.priority for p in self.processes]
        victim_idx = select_victim(
            deadlocked_indices=self.last_detection_result.deadlocked_processes,
            allocation_matrix=alloc,
            priorities=priorities,
            heuristic=heuristic,
        )
        return self.terminate_process(victim_idx)

    def get_statistics(self) -> dict:
        """Calculate simulation and performance statistics for charts and dashboard."""
        alloc, max_m, need, req, avail, total = self.get_matrices()
        n_proc = len(self.processes)
        n_res = self.resource_manager.num_resources if self.resource_manager else 0

        tot_res_instances = int(np.sum(total)) if total.size > 0 else 0
        tot_alloc_instances = int(np.sum(alloc)) if alloc.size > 0 else 0
        tot_avail_instances = int(np.sum(avail)) if avail.size > 0 else 0
        overall_utilization = (
            round((tot_alloc_instances / tot_res_instances) * 100, 2)
            if tot_res_instances > 0
            else 0.0
        )

        deadlocked_count = (
            len(self.last_detection_result.deadlocked_processes)
            if self.last_detection_result
            else 0
        )
        terminated_count = sum(1 for p in self.processes if p.state == ProcessState.TERMINATED)
        finished_count = sum(1 for p in self.processes if p.state == ProcessState.FINISHED)

        return {
            "total_processes": n_proc,
            "total_resource_types": n_res,
            "total_resource_instances": tot_res_instances,
            "allocated_instances": tot_alloc_instances,
            "available_instances": tot_avail_instances,
            "overall_utilization_pct": overall_utilization,
            "deadlocked_count": deadlocked_count,
            "terminated_count": terminated_count,
            "finished_count": finished_count,
            "system_status": self.system_status,
            "is_safe": bool(self.last_bankers_result.is_safe) if self.last_bankers_result else False,
            "safe_sequence": self.last_bankers_result.safe_sequence_names if self.last_bankers_result else [],
        }

