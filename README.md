# Operating System Deadlock Simulation Using Python

### Academic Information
- **Subject:** Solving Problems Using Modelling and Simulation (SPMS)
- **Course Code:** NEC00091
- **Project Type:** Python-Based Modelling & Simulation Mini Project
- **Target Platform:** Windows (Python 3.11+ / Python 3.14)
- **Academic Purpose:** College-Level Practical Modelling, Simulation, and Viva Demonstration

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Libraries and Technology Stack](#2-libraries-and-technology-stack)
3. [System Architecture & How It Works](#3-system-architecture--how-it-works)
4. [Mathematical Model & Matrix Formulation](#4-mathematical-model--matrix-formulation)
5. [Core Algorithms Explained](#5-core-algorithms-explained)
   - [Module 1: Banker's Algorithm (Deadlock Avoidance)](#module-1-bankers-algorithm-deadlock-avoidance)
   - [Module 2: Deadlock Detection (Multiple Instances)](#module-2-deadlock-detection-multiple-instances)
   - [Module 3: Resource Allocation Graph (RAG) & Cycle Theory](#module-3-resource-allocation-graph-rag--cycle-theory)
   - [Module 4: Deadlock Recovery (Termination & Preemption)](#module-4-deadlock-recovery-termination--preemption)
6. [Graphical User Interface (7 Application Views)](#6-graphical-user-interface-7-application-views)
7. [Predefined Simulation Scenarios](#7-predefined-simulation-scenarios)
8. [File & Directory Structure](#8-file--directory-structure)
9. [Three-Member Academic Team Division](#9-three-member-academic-team-division)
10. [Installation & Windows Execution Guide](#10-installation--windows-execution-guide)
11. [Testing & Validation Suite](#11-testing--validation-suite)
12. [Sample Simulation Outputs](#12-sample-simulation-outputs)
13. [Limitations & Future Scope](#13-limitations--future-scope)

---

## 1. Project Overview

In a multi-programmed operating system, concurrent processes compete for a finite set of non-shareable resources (CPU cores, memory, I/O devices, printer buffers, mutexes). When resource requests are granted without coordination, a set of processes can become permanently blocked, each holding resources while waiting for other resources held by other processes in the set. This state is known as a **Deadlock**.

This application is an interactive, mathematically sound desktop simulator designed to model:
1. **Dynamic Process Contention:** Processes competing for multiple discrete resource types with finite multiple instances.
2. **Dijkstra's Banker's Algorithm:** Determining whether states are safe or unsafe, finding safe execution sequences, and testing whether runtime resource requests can be safely granted.
3. **Multiple-Instance Deadlock Detection:** Using the Work-Finish matrix reduction algorithm to identify deadlocked processes.
4. **Interactive Resource Allocation Graphs (RAG):** Drawing bipartite process-resource graphs, highlighting directed cycles, and demonstrating why a cycle in a multi-instance graph does not guarantee deadlock.
5. **Deadlock Recovery:** Resolving deadlocks through heuristic-driven process termination and resource preemption.
6. **Visual Analytics:** Real-time Matplotlib charts for resource utilization, process allocations, and demand profiles.

All core algorithms are **implemented from first principles** in pure Python and NumPy without reliance on third-party deadlock libraries.

---

## 2. Libraries and Technology Stack

| Library / Tool | Version | Role in Project | Why It Was Chosen |
| :--- | :--- | :--- | :--- |
| **Python** | 3.11+ / 3.14 | Core language | Modular object-oriented programming, readability, and extensive standard library support. |
| **Tkinter & `ttk`** | Standard Library (Tk 9.0) | Desktop GUI Dashboard | Runs natively on Windows without requiring heavy webview runtimes (e.g. Electron) or external browser servers. Customized with a modern slate-navy visual theme. |
| **NumPy** | $\ge 2.0.0$ | Matrix calculations & vector math | High-performance matrix operations: $\mathbf{Need} = \mathbf{Max} - \mathbf{Allocation}$, matrix dimension checking, vector comparisons ($\mathbf{Need}[i] \le \mathbf{Work}$), and resource accounting. |
| **NetworkX** | $\ge 3.0$ | Graph modeling & cycle detection | Creates directed bipartite graph models of processes and resources. Detects elementary directed circular wait cycles via `nx.simple_cycles(G)`. |
| **Matplotlib** | $\ge 3.9.0$ | Interactive charts & graph drawing | Renders the Resource Allocation Graph and generates analytical simulation charts. Embedded directly into Tkinter frames via `FigureCanvasTkAgg` and `NavigationToolbar2Tk`. |
| **Pillow (PIL)** | $\ge 10.0$ | Image handling | Supports high-DPI scaling and graphics rasterization for Matplotlib canvas rendering inside Tkinter. |
| **`unittest`** | Standard Library | Automated testing | Built-in test runner executing 25 unit and UI integration tests to guarantee 100% mathematical accuracy. |

---

## 3. System Architecture & How It Works

### High-Level Workflow
```
┌────────────────────────────────────────────────────────┐
│             PRESET SCENARIOS / USER MATRICES           │
│   (Scenario 1-5 or Custom Spinboxes & Entry Grids)     │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                 SIMULATION ENGINE                      │
│   (State Machine, Process Pool, Resource Manager)       │
└─────────────┬────────────────────────────┬─────────────┘
              │                            │
              ▼                            ▼
┌───────────────────────────┐┌───────────────────────────┐
│    BANKER'S ALGORITHM     ││    DEADLOCK DETECTION     │
│  • Need = Max - Alloc     ││  • Work = Available       │
│  • Safety Sequence Search ││  • Unfinished Search      │
│  • Request Adjudication   ││  • Deadlocked PID Flags   │
└─────────────┬─────────────┘└─────────────┬─────────────┘
              │                            │
              └─────────────┬──────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│             VISUALIZATION & RECOVERY ENGINE            │
│  • NetworkX RAG with Bold Cycle Highlighting           │
│  • Termination & Preemption Heuristic Engines          │
│  • Matplotlib Stacked & Grouped Analytical Charts      │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                 TKINTER DESKTOP GUI                    │
│   (7 Dedicated Views with Sidebar Navigation)          │
└────────────────────────────────────────────────────────┘
```

---

## 4. Mathematical Model & Matrix Formulation

### 4.1 System Sets & Vectors
- Let $P = \{P_0, P_1, \dots, P_{n-1}\}$ be $n$ concurrent processes.
- Let $R = \{R_0, R_1, \dots, R_{m-1}\}$ be $m$ distinct resource types.
- $\mathbf{Total} = [T_0, T_1, \dots, T_{m-1}] \in \mathbb{Z}_{\ge 0}^m$: Total capacity of each resource type.
- $\mathbf{Available} = [A_0, A_1, \dots, A_{m-1}] \in \mathbb{Z}_{\ge 0}^m$: Currently unallocated instances of each resource type.

### 4.2 State Matrices
- $\mathbf{Allocation} \in \mathbb{Z}_{\ge 0}^{n \times m}$: Matrix where $Allocation[i][j]$ is the number of instances of resource $R_j$ currently allocated to process $P_i$.
- $\mathbf{Max} \in \mathbb{Z}_{\ge 0}^{n \times m}$: Matrix where $Max[i][j]$ is the maximum number of instances of resource $R_j$ that process $P_i$ can claim.
- $\mathbf{Need} \in \mathbb{Z}_{\ge 0}^{n \times m}$: Matrix where $Need[i][j]$ is the remaining instances of resource $R_j$ process $P_i$ may request to finish execution.
- $\mathbf{Request} \in \mathbb{Z}_{\ge 0}^{n \times m}$: Matrix where $Request[i][j]$ is the active outstanding request of process $P_i$ for resource $R_j$.

### 4.3 Fundamental Equations & Invariants

$$\mathbf{Need}[i][j] = \mathbf{Max}[i][j] - \mathbf{Allocation}[i][j] \quad \forall i \in [0, n-1], \, j \in [0, m-1]$$

$$\mathbf{Available}[j] = \mathbf{Total}[j] - \sum_{i=0}^{n-1} \mathbf{Allocation}[i][j] \quad \forall j \in [0, m-1]$$

$$\mathbf{Allocation}[i][j] \le \mathbf{Max}[i][j] \quad \text{and} \quad \sum_{i=0}^{n-1} \mathbf{Allocation}[i][j] \le \mathbf{Total}[j]$$

### 4.4 Safe-State Criterion
A state is **Safe** if there exists at least one ordering $\langle P_{\pi(0)}, P_{\pi(1)}, \dots, P_{\pi(n-1)} \rangle$ such that for every process $P_{\pi(k)}$:

$$\mathbf{Need}[\pi(k)] \le \mathbf{Work}_k$$

where $\mathbf{Work}_0 = \mathbf{Available}$, and $\mathbf{Work}_{k+1} = \mathbf{Work}_k + \mathbf{Allocation}[\pi(k)]$.

> **Academic Concept:** An **Unsafe State** is **NOT** synonymous with a deadlocked state. An unsafe state is a state from which the OS cannot guarantee avoidance of deadlock if processes simultaneously request their maximum claims. Every deadlocked state is unsafe, but not every unsafe state is currently deadlocked.

---

## 5. Core Algorithms Explained

### Module 1: Banker's Algorithm (Deadlock Avoidance)
*Implemented in [`algorithms/bankers.py`](file:///d:/NEC/algorithms/bankers.py)*

1. **Safety Algorithm:**
   - Initialize $\mathbf{Work} = \mathbf{Available}$ and $\mathbf{Finish}[i] = \text{False}$ for all $i$.
   - Search for an index $i$ such that $\mathbf{Finish}[i] == \text{False}$ and $\mathbf{Need}[i] \le \mathbf{Work}$.
   - If found:
     - Assume process $P_i$ completes and returns its held resources:
       $$\mathbf{Work} \leftarrow \mathbf{Work} + \mathbf{Allocation}[i], \quad \mathbf{Finish}[i] \leftarrow \text{True}$$
     - Append $P_i$ to the safe sequence list. Repeat the search.
   - If all $\mathbf{Finish}[i] == \text{True}$, the system is **SAFE**. Otherwise, it is **UNSAFE**.

2. **Resource-Request Algorithm:**
   When process $P_i$ requests vector $\mathbf{Req}_i$:
   - **Check 1:** If $\mathbf{Req}_i[j] > \mathbf{Need}[i][j]$, reject with error: *Process exceeded maximum claim*.
   - **Check 2:** If $\mathbf{Req}_i[j] > \mathbf{Available}[j]$, process must wait: *Resources currently unavailable*.
   - **Trial Allocation:** Tentatively update vectors:
     $$\mathbf{Available}' = \mathbf{Available} - \mathbf{Req}_i$$
     $$\mathbf{Allocation}'[i] = \mathbf{Allocation}[i] + \mathbf{Req}_i$$
     $$\mathbf{Need}'[i] = \mathbf{Need}[i] - \mathbf{Req}_i$$
   - Run the Safety Algorithm on the trial state:
     - If safe $\rightarrow$ permanently commit allocation.
     - If unsafe $\rightarrow$ rollback to previous state and place process in `WAITING` state.

---

### Module 2: Deadlock Detection (Multiple Instances)
*Implemented in [`algorithms/detection.py`](file:///d:/NEC/algorithms/detection.py)*

- Unlike Banker's algorithm (which evaluates worst-case maximum claims $\mathbf{Max}$), Deadlock Detection evaluates **actual current outstanding requests** ($\mathbf{Request}$).
- Initialize $\mathbf{Work} = \mathbf{Available}$.
- For all $i$: if $\mathbf{Allocation}[i] == \mathbf{0}$, then $\mathbf{Finish}[i] = \text{True}$ (processes with zero resources cannot cause deadlock); otherwise $\mathbf{Finish}[i] = \text{False}$.
- Repeatedly find $i$ where $\mathbf{Finish}[i] == \text{False}$ and $\mathbf{Request}[i] \le \mathbf{Work}$.
- When found: $\mathbf{Work} \leftarrow \mathbf{Work} + \mathbf{Allocation}[i]$, $\mathbf{Finish}[i] \leftarrow \text{True}$.
- When no more processes can be satisfied, any process with $\mathbf{Finish}[i] == \text{False}$ is **DEADLOCKED**.

---

### Module 3: Resource Allocation Graph (RAG) & Cycle Theory
*Implemented in [`visualization/allocation_graph.py`](file:///d:/NEC/visualization/allocation_graph.py)*

- **Bipartite Nodes:**
  - Circles = Processes (Blue for normal, Red for deadlocked).
  - Squares = Resources (Orange with instance counts).
- **Directed Edges:**
  - Solid Blue Arrows ($R_j \rightarrow P_i$): Resource allocation.
  - Dashed Orange Arrows ($P_i \rightarrow R_j$): Resource request.
- **Cycle Highlighting:** NetworkX detects all simple directed cycles and draws cycle edges in **bold red** with thick arrows.
- **Theoretical Distinction:**
  - **Single-Instance Resources:** Directed cycle $\iff$ Deadlock (necessary and sufficient).
  - **Multiple-Instance Resources:** Directed cycle is **necessary but NOT sufficient** (demonstrated in Scenario 5, where a cycle exists but processes outside the cycle complete and break the circular wait).

---

### Module 4: Deadlock Recovery (Termination & Preemption)
*Implemented in [`algorithms/recovery.py`](file:///d:/NEC/algorithms/recovery.py)*

1. **Process Termination:**
   - Aborts one or all deadlocked processes.
   - Reclaims all allocated resources of the victim to $\mathbf{Available}$.
   - **Victim Selection Heuristics:**
     - *Largest Allocation:* Frees the most resources immediately to maximize probability of recovery.
     - *Smallest Allocation:* Minimizes wasted computation time for young processes.
     - *Lowest Priority:* Terminates low-importance background processes first.
     - *Manual Selection:* Allows user to pick the exact victim.
2. **Resource Preemption:**
   - Preempts specific units of a resource from a victim process without killing it.
   - Reclaimed units return to $\mathbf{Available}$, while the victim's $\mathbf{Request}$ vector increases (to re-acquire it later).
3. **Audit Log:** Automatically records a before-and-after snapshot comparing Available vectors, reclaimed resources, and remaining deadlocked processes.

---

## 6. Graphical User Interface (7 Application Views)

The application launches with a persistent navigation sidebar giving access to 7 dedicated modules:

1. **📊 Dashboard (`ui/dashboard.py`):**
   - Summary metric cards: Total Processes, Resource Types, System State Badge (`SAFE`, `UNSAFE`, `DEADLOCKED`), Resource Utilization %, and Deadlocked Process Count.
   - Preset Scenario selector with one-click loader.
   - Process states table showing PID, name, state, allocation, max, need, and request.
   - Real-time simulation audit log.

2. **⚙️ Simulation Setup (`ui/simulation_setup.py`):**
   - Dynamic configuration for Process Count ($2$ to $8$) and Resource Count ($2$ to $6$).
   - Editable numeric grids for Total, Allocation, Maximum Claim, and Request matrices.
   - Real-time validation checking non-negativity, allocation $\le$ max claim, and total allocated $\le$ resource capacity.
   - Quick "Load Preset" button to populate fields from any scenario.

3. **🛡️ Banker's Algorithm (`ui/bankers_view.py`):**
   - Tabular view of Allocation, Max, and Need matrices.
   - "Run Safety Algorithm" button with dynamic Safe Sequence banner.
   - Step-by-step trace table tracking step number, process evaluated, Work vector before, Need $\le$ Work result, and Work vector after.
   - Dynamic Resource-Request Simulator to test hypothetical requests ($P_i$ requesting vector $[x, y, z]$) with instant accept/reject safety analysis.

4. **🔍 Deadlock Detection (`ui/detection_view.py`):**
   - Displays Request Matrix alongside Allocation Matrix and Available vector.
   - "Run Deadlock Detection" button.
   - Deadlock status banner highlighting deadlocked processes in crimson red.
   - Step-by-step trace showing which processes could satisfy their requests and which remained blocked.

5. **🕸️ Allocation Graph (`ui/rag_view.py`):**
   - Real-time NetworkX bipartite graph rendered on an interactive Matplotlib canvas.
   - Zoom, pan, and save controls using `NavigationToolbar2Tk`.
   - Distinct process circles and resource squares.
   - Elementary directed cycles automatically highlighted in bold red.
   - Educational banner explaining single vs. multi-instance cycle theorems.

6. **🚑 Deadlock Recovery (`ui/recovery_view.py`):**
   - Strategy 1: Process Termination with heuristic dropdown (Largest Allocation, Smallest Allocation, Lowest Priority, Manual).
   - "Terminate Victim" and "Abort All Deadlocked" buttons.
   - Strategy 2: Resource Preemption controls (select process, resource, and amount to preempt).
   - Recovery Audit log displaying exact before-and-after resource transitions and resolution status.

7. **📈 Results & Charts (`ui/results_view.py`):**
   - Three tabbed Matplotlib visualizations:
     1. *Resource Utilization Bar Chart:* Total capacity vs Allocated vs Available instances.
     2. *Process Allocation Breakdown:* Stacked bar chart showing resource distribution.
     3. *Need vs Allocation Demand Profile:* Side-by-side comparison of held resources vs remaining need.
   - Academic Report Generator summarizing the mathematical model, matrix values, and simulation outcomes.
   - One-click "Export Comprehensive Report" button to save the analysis as a `.txt` or `.md` file.

---

## 7. Predefined Simulation Scenarios

All scenarios are defined and mathematically verified in [`data/sample_scenarios.py`](file:///d:/NEC/data/sample_scenarios.py):

| Scenario ID | Name | Mathematical Configuration | Academic Outcome |
| :--- | :--- | :--- | :--- |
| **Scenario 1** | Safe State | 5 Processes ($P_0$–$P_4$), 3 Resources (10, 5, 7). Available: $[3, 3, 2]$. | **SAFE:** Valid safe sequence $\langle P_1 \rightarrow P_3 \rightarrow P_4 \rightarrow P_0 \rightarrow P_2 \rangle$. All processes complete without deadlock. |
| **Scenario 2** | Unsafe State | 4 Processes, 3 Resources (8, 5, 5). Available: $[1, 0, 0]$. | **UNSAFE:** No single process can satisfy its remaining Need from current Available resources. Avoidance warning triggered. |
| **Scenario 3** | Deadlock Condition | 4 Processes, 3 Resources (3, 3, 3). Available: $[0, 0, 0]$. Closed circular wait. | **DEADLOCKED:** Detection flags all 4 processes ($P_0, P_1, P_2, P_3$). RAG displays closed cycles. |
| **Scenario 4** | Deadlock Recovery | 5 Processes, 3 Resources. Processes $P_1, P_2, P_3, P_4$ deadlocked. | **RECOVERABLE:** Terminating victim $P_2$ (holds $[3, 0, 3]$) frees 6 units, breaking circular wait and resolving the deadlock completely. |
| **Scenario 5** | Multi-Instance Cycle No Deadlock | 4 Processes, 2 Resources (2 units each). $P_1$ and $P_2$ in a cycle; $P_3$ and $P_4$ hold units with no requests. | **NO DEADLOCK DESPITE CYCLE:** Silberschatz Fig 5.3 proof: $P_3$ and $P_4$ finish and release resources to $P_1$ and $P_2$, resolving the cycle. Demonstrates cycles $\ne$ deadlock in multi-instance systems. |

---

## 8. File & Directory Structure

```
d:/NEC/
├── main.py                           # Master application launcher & navigation sidebar
├── requirements.txt                  # Python dependencies
├── README.md                         # Project documentation
│
├── algorithms/                       # Manual algorithm implementations
│   ├── __init__.py
│   ├── bankers.py                    # Need calculation, Safety check, Resource-Request
│   ├── detection.py                  # Multiple-instance Deadlock Detection & step trace
│   └── recovery.py                   # Process termination & resource preemption heuristics
│
├── simulation/                       # Simulation engine & core state machine
│   ├── __init__.py
│   ├── process.py                    # Process entity & states (READY, WAITING, DEADLOCKED)
│   ├── resource_manager.py           # Resource pooling, capacity limits, and accounting
│   └── simulation_engine.py          # Central coordinator, snapshots, undo & state evaluation
│
├── visualization/                    # Graph & analytical plotting
│   ├── __init__.py
│   ├── allocation_graph.py           # NetworkX + Matplotlib bipartite RAG with cycle detection
│   └── charts.py                     # Utilization bars, process breakdowns, and demand profiles
│
├── ui/                               # Modern Tkinter / ttk graphical interface
│   ├── __init__.py
│   ├── theme.py                      # Slate-navy color palette, badges, and ttk styles
│   ├── dashboard.py                  # Overview metrics, system banner, live audit log
│   ├── simulation_setup.py           # Custom matrix grid editor with real-time validation
│   ├── bankers_view.py               # Tabular matrices, safe sequence display, request simulator
│   ├── detection_view.py             # Active request matrix, deadlocked process list, trace table
│   ├── rag_view.py                   # Interactive RAG canvas with cycle highlight
│   ├── recovery_view.py              # Termination / Preemption controls & before-after audit
│   └── results_view.py               # Embedded analytical charts & text report exporter
│
├── data/                             # Predefined academic simulation datasets
│   ├── __init__.py
│   └── sample_scenarios.py           # 5 mathematically verified test scenarios
│
└── tests/                            # Automated test suite (Python unittest)
    ├── __init__.py
    ├── test_bankers.py               # Banker's safety and request tests (7 tests)
    ├── test_detection.py             # Multiple-instance detection tests (3 tests)
    ├── test_recovery.py              # Termination and preemption tests (4 tests)
    ├── test_engine.py                # Engine state transition tests (5 tests)
    └── test_ui_integration.py        # Tkinter view initialization & refresh tests (6 tests)
```

---

## 9. Three-Member Academic Team Division

This project is partitioned into three distinct functional modules for college-level team collaboration:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        MAIN COORDINATION (main.py)                    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
       ┌────────────────────────────┼────────────────────────────┐
       ▼                            ▼                            ▼
┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────────┐
│       MEMBER 1        │ │       MEMBER 2        │ │       MEMBER 3        │
│ Mathematical Modeling │ │  Deadlock Detection   │ │   GUI, Visualization  │
│  & Banker's Algorithm │ │      & Recovery       │ │     & Integration     │
├───────────────────────┤ ├───────────────────────┤ ├───────────────────────┤
│ • Mathematical Model  │ │ • Detection Algorithm │ │ • Main Application UI │
│ • Need Matrix Calc    │ │ • Request Simulation  │ │ • NetworkX RAG Graph  │
│ • Safety Algorithm    │ │ • Process Termination │ │ • Matplotlib Charts   │
│ • Resource Requests   │ │ • Resource Preemption │ │ • View Integration    │
│ • test_bankers.py     │ │ • test_detection.py   │ │ • test_ui_integration│
│                       │ │ • test_recovery.py    │ │                       │
└───────────────────────┘ └───────────────────────┘ └───────────────────────┘
```

- **Member 1 – Mathematical Modelling & Banker's Algorithm:**
  - Formulated the matrix mathematical model and system constraints.
  - Implemented [`algorithms/bankers.py`](file:///d:/NEC/algorithms/bankers.py) (`calculate_need`, `check_safety`, `evaluate_resource_request`).
  - Authored [`tests/test_bankers.py`](file:///d:/NEC/tests/test_bankers.py) (7 unit tests).

- **Member 2 – Deadlock Detection & Recovery:**
  - Implemented multiple-instance Deadlock Detection in [`algorithms/detection.py`](file:///d:/NEC/algorithms/detection.py).
  - Implemented recovery strategies and victim heuristics in [`algorithms/recovery.py`](file:///d:/NEC/algorithms/recovery.py).
  - Authored [`tests/test_detection.py`](file:///d:/NEC/tests/test_detection.py) and [`tests/test_recovery.py`](file:///d:/NEC/tests/test_recovery.py).

- **Member 3 – GUI, Visualization & Integration:**
  - Designed the Tkinter dashboard, theme, and 7 view pages in [`ui/`](file:///d:/NEC/ui/).
  - Implemented Resource Allocation Graph with cycle highlighting in [`visualization/allocation_graph.py`](file:///d:/NEC/visualization/allocation_graph.py).
  - Created dynamic simulation charts in [`visualization/charts.py`](file:///d:/NEC/visualization/charts.py).
  - Integrated all modules into [`simulation/simulation_engine.py`](file:///d:/NEC/simulation/simulation_engine.py) and [`main.py`](file:///d:/NEC/main.py).
  - Authored [`tests/test_ui_integration.py`](file:///d:/NEC/tests/test_ui_integration.py).

---

## 10. Installation & Windows Execution Guide

### Step 1: Open PowerShell
Open Windows PowerShell or Command Prompt and change directory to `D:\NEC`:
```powershell
cd D:\NEC
```

### Step 2: Install Required Dependencies
```powershell
python -m pip install -r requirements.txt
```

### Step 3: Run the Automated Unit Tests
Verify that all algorithms, simulation states, and UI components execute correctly:
```powershell
python -m unittest discover tests
```
*(Expected output: `Ran 25 tests in ~32s — OK`)*

### Step 4: Launch the Desktop Application
```powershell
python main.py
```

---

## 11. Testing & Validation Suite

The project includes **25 automated tests** across 5 test suites in `tests/`:

1. **`test_bankers.py` (7 tests):**
   - Correct Need Matrix calculation ($Need = Max - Allocation$).
   - Standard safe state detection and safe sequence derivation.
   - Unsafe state detection when resources are depleted.
   - Dynamic resource request granted when state remains safe.
   - Immediate denial when request exceeds declared Need.
   - Process waiting when request exceeds Available capacity.
   - Validation exception when Allocation exceeds Max.
2. **`test_detection.py` (3 tests):**
   - Non-deadlocked system with active requests.
   - Deadlocked system identifying exact blocked processes.
   - Idle processes with zero allocation correctly excluded from deadlock.
3. **`test_recovery.py` (4 tests):**
   - Victim selection heuristic for largest allocation.
   - Victim selection heuristic for lowest priority.
   - Complete deadlock resolution following victim termination.
   - Resource preemption correctly decreasing allocation and increasing available units.
4. **`test_engine.py` (5 tests):**
   - End-to-end scenario loading (Scenarios 1, 2, 3, 4, 5).
   - Automatic recovery execution via engine coordinator.
   - Multi-instance cycle without deadlock verification.
5. **`test_ui_integration.py` (6 tests):**
   - Headless cycling through all 7 views.
   - Dashboard refresh and metric calculations.
   - Banker's view safety algorithm execution.
   - Detection view runner and matrix display.
   - RAG canvas redrawing and cycle detection.
   - Analytical report generator content verification.

---

## 12. Sample Simulation Outputs

### Sample 1: Banker's Safe Sequence Output (Scenario 1)
```
SYSTEM STATE: SAFE
Safe Execution Sequence: < P1 -> P3 -> P4 -> P0 -> P2 >
Explanation: The system is in a SAFE STATE. All 5 processes can execute to completion
without entering a deadlock.

Step-by-Step Execution Trace:
• Step 1: Process P1 satisfied! Need [1, 2, 2] <= Work [3, 3, 2]. Releases [2, 0, 0]. New Work: [5, 3, 2]
• Step 2: Process P3 satisfied! Need [0, 1, 1] <= Work [5, 3, 2]. Releases [2, 1, 1]. New Work: [7, 4, 3]
• Step 3: Process P4 satisfied! Need [4, 3, 1] <= Work [7, 4, 3]. Releases [0, 0, 2]. New Work: [7, 4, 5]
• Step 4: Process P0 satisfied! Need [7, 4, 3] <= Work [7, 4, 5]. Releases [0, 1, 0]. New Work: [7, 5, 5]
• Step 5: Process P2 satisfied! Need [6, 0, 0] <= Work [7, 5, 5]. Releases [3, 0, 2]. New Work: [10, 5, 7]
```

### Sample 2: Deadlock Detection Output (Scenario 3)
```
DETECTION STATUS: DEADLOCK DETECTED!
Deadlocked Processes: [ P0, P1, P2, P3 ]
Explanation: 4 process(es) cannot complete: [P0, P1, P2, P3]. Mutual circular waiting prevents
these processes from receiving their pending requests.
Work Vector: [0, 0, 0]
Finish Vector: [False, False, False, False]
```

### Sample 3: Recovery via Process Termination (Scenario 4)
```
RECOVERY ACTION EXECUTED: PROCESS_TERMINATION
Target Victim: P2 (Heuristic: Largest Allocation)
Resources Reclaimed: [3, 0, 3]
Available Resources: Before [0, 0, 0] -> After [3, 0, 3]
Deadlocked Indices:  Before [1, 2, 3, 4] -> After []
Outcome: RESOLVED ✓
Summary: Terminated process P2 and reclaimed [3, 0, 3] resource instances. Deadlock is completely
resolved! All remaining processes can now finish.
```

---

## 13. Limitations & Future Scope

### Limitations
1. **Static Pre-declaration:** Banker's Algorithm assumes each process knows its maximum resource claim in advance, which is difficult to predict in modern general-purpose operating systems.
2. **Synchronous Discrete-Event Model:** Processes transition in discrete logical steps rather than asynchronous physical OS threads.
3. **Abstract Rollback:** Preemption is modeled mathematically by shifting resource units between vectors rather than physical disk/memory state checkpointing.

### Future Scope
1. **Multithreaded Execution:** Incorporate Python's `threading` module with mutex locks (`threading.Lock`, `threading.Semaphore`) to simulate physical concurrency.
2. **Distributed Deadlock Detection:** Extend the model to distributed systems using the Chandy-Misra-Haas edge-chasing probe algorithm.
3. **Automated State Checkpointing:** Add process memory serialization (pickling) for rollback recovery.
4. **Web UI Extension:** Port the interface to a web-based dashboard using Streamlit or FastAPI + React.

---

### Academic Attribution
Developed for the course **Solving Problems Using Modelling and Simulation (SPMS)**, Course Code **NEC00091**.  
Suitable for university laboratory demonstration, Viva Voce examination, and OS concept presentations.
