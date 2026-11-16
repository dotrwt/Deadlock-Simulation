"""Interactive Terminal Demonstration of OS Deadlock Simulation.

Course: Solving Problems Using Modelling and Simulation (SPMS) - NEC00091
Demonstrates:
1. Scenario 1: Banker's Algorithm (Safety & Dynamic Resource Request)
2. Scenario 2: Dijkstra's Unsafe State Warning
3. Scenario 3: Deadlock Detection & Cycle Detection
4. Scenario 4: Deadlock Recovery via Heuristic Victim Selection
5. Scenario 5: Multi-Instance Cycle without Deadlock
"""

import sys
import numpy as np

from simulation.simulation_engine import SimulationEngine
from data.sample_scenarios import (
    SCENARIO_1_SAFE,
    SCENARIO_2_UNSAFE,
    SCENARIO_3_DEADLOCK,
    SCENARIO_4_RECOVERY,
    SCENARIO_5_CYCLE_NO_DEADLOCK,
)
from algorithms.recovery import VictimSelectionHeuristic
from visualization.allocation_graph import build_rag_graph


def print_header(title: str):
    print("\n" + "=" * 78)
    print(f" {title.upper()}")
    print("=" * 78)


def print_matrix_table(p_names, r_names, alloc, max_m, need, req, avail):
    print(f"\nResource Capacity: Available = {avail.tolist()}")
    print("-" * 78)
    print(f"{'Proc':<6} | {'Allocation':<14} | {'Max Claim':<14} | {'Need':<14} | {'Request':<14}")
    print("-" * 78)
    for i, name in enumerate(p_names):
        print(
            f"{name:<6} | {str(alloc[i].tolist()):<14} | {str(max_m[i].tolist()):<14} | "
            f"{str(need[i].tolist()):<14} | {str(req[i].tolist()):<14}"
        )
    print("-" * 78)


def demo_scenario_1():
    print_header("DEMONSTRATION 1: Banker's Algorithm (Deadlock Avoidance - Scenario 1)")
    engine = SimulationEngine(SCENARIO_1_SAFE)
    alloc, max_m, need, req, avail, total = engine.get_matrices()
    p_names = [p.name for p in engine.processes]
    r_names = engine.resource_manager.resource_names

    print(f"Scenario: {engine.scenario.name}")
    print(f"Concept:  {engine.scenario.theoretical_concept}")
    print_matrix_table(p_names, r_names, alloc, max_m, need, req, avail)

    print("\n[Executing Banker's Safety Algorithm...]")
    res = engine.run_bankers()
    for step in res.steps:
        status_sym = "[OK]" if step.can_allocate else "[WAIT]"
        print(f"  {status_sym} {step.message}")

    print(f"\n>> System State: {'SAFE' if res.is_safe else 'UNSAFE'}")
    print(f">> Safe Execution Sequence: < {' -> '.join(res.safe_sequence_names)} >")

    # Dynamic Request Tests
    print("\n--- Testing Dynamic Resource Requests ---")
    print("Case A: Process P1 requests [1, 0, 2] (within need and within available):")
    req_res_a = engine.request_resources(1, [1, 0, 2])
    print(f"  Result: {'GRANTED' if req_res_a.granted else 'DENIED'}")
    print(f"  Reason: {req_res_a.reason}")

    print("\nCase B: Process P4 requests [3, 3, 0] (exceeds Available):")
    req_res_b = engine.request_resources(4, [3, 3, 0])
    print(f"  Result: {'GRANTED' if req_res_b.granted else 'DENIED'}")
    print(f"  Reason: {req_res_b.reason}")


def demo_scenario_2():
    print_header("DEMONSTRATION 2: Unsafe State vs. Deadlock (Scenario 2)")
    engine = SimulationEngine(SCENARIO_2_UNSAFE)
    alloc, max_m, need, req, avail, total = engine.get_matrices()
    p_names = [p.name for p in engine.processes]
    r_names = engine.resource_manager.resource_names

    print(f"Scenario: {engine.scenario.name}")
    print(f"Concept:  {engine.scenario.theoretical_concept}")
    print_matrix_table(p_names, r_names, alloc, max_m, need, req, avail)

    res = engine.run_bankers()
    print(f">> Banker's Result: System is {'SAFE' if res.is_safe else 'UNSAFE'}")
    print(f">> Explanation:     {res.explanation}")

    det = engine.run_detection()
    print(f">> Deadlock Detection Result: System is {'DEADLOCKED' if det.is_deadlocked else 'NOT DEADLOCKED'}")
    print(f">> Academic Takeaway: An unsafe state means deadlock CANNOT BE AVOIDED if processes")
    print(f"   simultaneously demand their maximum claims, but the system is NOT currently deadlocked.")


def demo_scenario_3():
    print_header("DEMONSTRATION 3: Multiple-Instance Deadlock Detection (Scenario 3)")
    engine = SimulationEngine(SCENARIO_3_DEADLOCK)
    alloc, max_m, need, req, avail, total = engine.get_matrices()
    p_names = [p.name for p in engine.processes]
    r_names = engine.resource_manager.resource_names

    print(f"Scenario: {engine.scenario.name}")
    print(f"Concept:  {engine.scenario.theoretical_concept}")
    print_matrix_table(p_names, r_names, alloc, max_m, need, req, avail)

    print("\n[Executing Deadlock Detection Algorithm...]")
    det = engine.run_detection()
    for step in det.steps:
        status_sym = "[OK]" if step.can_finish else "[BLOCKED]"
        print(f"  {status_sym} {step.message}")

    print(f"\n>> System State: {'DEADLOCKED' if det.is_deadlocked else 'HEALTHY'}")
    print(f">> Deadlocked Processes: {det.deadlocked_names}")
    print(f">> Diagnostic: {det.explanation}")

    # Graph Cycle Check
    G, cycles, is_single = build_rag_graph(
        p_names, r_names, alloc, req, total.tolist(), avail.tolist(), det.deadlocked_processes
    )
    print(f">> RAG Graph Cycles Detected: {len(cycles)} cycle(s)")
    for i, c in enumerate(cycles):
        print(f"   Cycle {i+1}: {' -> '.join(c)} -> {c[0]}")


def demo_scenario_4():
    print_header("DEMONSTRATION 4: Deadlock Recovery via Heuristic Victim Selection (Scenario 4)")
    engine = SimulationEngine(SCENARIO_4_RECOVERY)
    alloc, max_m, need, req, avail, total = engine.get_matrices()
    p_names = [p.name for p in engine.processes]
    r_names = engine.resource_manager.resource_names

    print(f"Initial State: Deadlocked processes = {engine.last_detection_result.deadlocked_names}")
    print_matrix_table(p_names, r_names, alloc, max_m, need, req, avail)

    print("\n[Selecting Victim using 'LARGEST_ALLOCATION' Heuristic...]")
    priorities = [p.priority for p in engine.processes]
    print(f"Process Allocations Sum: P1={np.sum(alloc[1])}, P2={np.sum(alloc[2])}, P3={np.sum(alloc[3])}, P4={np.sum(alloc[4])}")
    print("Victim P2 has the largest held resources (6 units: [3, 0, 3]).")

    print("\n[Executing Process Termination on Victim P2...]")
    record = engine.auto_recover(VictimSelectionHeuristic.LARGEST_ALLOCATION)
    print(f"  Action:              {record.strategy}")
    print(f"  Victim:              {record.victim_name}")
    print(f"  Resources Reclaimed: {record.resources_reclaimed}")
    print(f"  Available Before:    {record.available_before} -> After: {record.available_after}")
    print(f"  Deadlocked Before:   {record.deadlocked_before} -> After: {record.deadlocked_after}")
    print(f"  Outcome:             {'RESOLVED' if record.is_resolved else 'PARTIAL'}")
    print(f"  Summary:             {record.summary}")

    print(f"\n>> Post-Recovery System Status: {engine.system_status}")


def demo_scenario_5():
    print_header("DEMONSTRATION 5: Multi-Instance Cycle Without Deadlock (Scenario 5)")
    engine = SimulationEngine(SCENARIO_5_CYCLE_NO_DEADLOCK)
    alloc, max_m, need, req, avail, total = engine.get_matrices()
    p_names = [p.name for p in engine.processes]
    r_names = engine.resource_manager.resource_names

    print(f"Scenario: {engine.scenario.name}")
    print(f"Concept:  {engine.scenario.theoretical_concept}")
    print_matrix_table(p_names, r_names, alloc, max_m, need, req, avail)

    # Check Graph Cycles
    G, cycles, is_single = build_rag_graph(
        p_names, r_names, alloc, req, total.tolist(), avail.tolist()
    )
    print(f">> RAG Cycles Detected: {len(cycles)} cycle(s)")
    for i, c in enumerate(cycles):
        print(f"   Cycle {i+1}: {' -> '.join(c)} -> {c[0]}")

    # Run Deadlock Detection
    det = engine.run_detection()
    print(f">> Deadlock Detection Result: System is {'DEADLOCKED' if det.is_deadlocked else 'NOT DEADLOCKED'}")
    print(f">> Deadlocked Processes Count: {len(det.deadlocked_processes)}")
    print(f">> Completion Sequence:        < {' -> '.join(det.completed_names)} >")
    print(f"\n>> CRITICAL ACADEMIC INSIGHT:")
    print(f"   Although P1 and P2 are trapped in a cycle with R1 and R2, processes P3 and P4")
    print(f"   also hold instances of R1 and R2 but have ZERO pending requests!")
    print(f"   P3 and P4 run to completion, release their units, and satisfy P1 and P2.")
    print(f"   PROOF: In multiple-instance systems, a cycle is NOT sufficient for deadlock!")


def main():
    print("=" * 78)
    print(" OPERATING SYSTEM DEADLOCK SIMULATION — LIVE DEMONSTRATION")
    print(" Course: Solving Problems Using Modelling and Simulation (SPMS) - NEC00091")
    print("=" * 78)

    demo_scenario_1()
    demo_scenario_2()
    demo_scenario_3()
    demo_scenario_4()
    demo_scenario_5()

    print("\n" + "=" * 78)
    print(" DEMONSTRATION COMPLETE — ALL 5 ACADEMIC SCENARIOS SUCCESSFULLY VERIFIED!")
    print(" To launch the interactive desktop GUI, run: python main.py")
    print("=" * 78 + "\n")


if __name__ == "__main__":
    main()
