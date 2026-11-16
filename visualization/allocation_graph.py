"""Resource Allocation Graph (RAG) visualization using NetworkX and Matplotlib.

Course: Solving Problems Using Modelling and Simulation (SPMS) - NEC00091
Implements:
- Bipartite process (circle) and resource (square) nodes.
- Directed allocation edges (Resource -> Process).
- Directed request edges (Process -> Resource).
- Elementary directed cycle detection and visual highlight.
- Multi-instance vs single-instance educational annotations.
"""

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np


def build_rag_graph(
    process_names: list[str],
    resource_names: list[str],
    allocation_matrix: np.ndarray | list[list[int]],
    request_matrix: np.ndarray | list[list[int]],
    total_resources: list[int] | None = None,
    available_resources: list[int] | None = None,
    deadlocked_indices: list[int] | None = None,
) -> tuple[nx.DiGraph, list[list[str]], bool]:
    """Construct directed graph and detect circular wait cycles.
    
    Returns:
        (graph, cycles, is_single_instance)
    """
    alloc = np.array(allocation_matrix, dtype=int)
    req = np.array(request_matrix, dtype=int)
    n_proc, n_res = alloc.shape

    G = nx.DiGraph()

    # Determine if system is single-instance
    is_single_instance = True
    if total_resources is not None:
        is_single_instance = all(t == 1 for t in total_resources)
    elif np.max(alloc) > 1 or (req.size > 0 and np.max(req) > 1):
        is_single_instance = False

    deadlocked_set = set(deadlocked_indices) if deadlocked_indices else set()

    # Add Process nodes (type='process')
    for i in range(n_proc):
        p_name = process_names[i] if i < len(process_names) else f"P{i}"
        is_dl = i in deadlocked_set
        G.add_node(
            p_name,
            node_type="process",
            index=i,
            is_deadlocked=is_dl,
            label=f"{p_name}\n(DEADLOCKED)" if is_dl else p_name,
        )

    # Add Resource nodes (type='resource')
    for j in range(n_res):
        r_name = resource_names[j] if j < len(resource_names) else f"R{j}"
        tot_str = f"/{total_resources[j]}" if total_resources and j < len(total_resources) else ""
        avail_str = f"Avail: {available_resources[j]}" if available_resources and j < len(available_resources) else ""
        label = f"{r_name}{tot_str}\n{avail_str}".strip()
        G.add_node(
            r_name,
            node_type="resource",
            index=j,
            label=label,
        )

    # Add Allocation Edges: Resource -> Process
    for i in range(n_proc):
        p_name = process_names[i] if i < len(process_names) else f"P{i}"
        for j in range(n_res):
            units = int(alloc[i, j])
            if units > 0:
                r_name = resource_names[j] if j < len(resource_names) else f"R{j}"
                G.add_edge(
                    r_name,
                    p_name,
                    edge_type="allocation",
                    weight=units,
                    label=f"{units}" if units > 1 else "",
                )

    # Add Request Edges: Process -> Resource
    for i in range(n_proc):
        p_name = process_names[i] if i < len(process_names) else f"P{i}"
        for j in range(n_res):
            units = int(req[i, j])
            if units > 0:
                r_name = resource_names[j] if j < len(resource_names) else f"R{j}"
                G.add_edge(
                    p_name,
                    r_name,
                    edge_type="request",
                    weight=units,
                    label=f"{units}" if units > 1 else "",
                )

    # Detect elementary cycles
    try:
        cycles = list(nx.simple_cycles(G))
    except Exception:
        cycles = []

    return G, cycles, is_single_instance


def draw_rag_on_figure(
    fig: Figure,
    process_names: list[str],
    resource_names: list[str],
    allocation_matrix: np.ndarray | list[list[int]],
    request_matrix: np.ndarray | list[list[int]],
    total_resources: list[int] | None = None,
    available_resources: list[int] | None = None,
    deadlocked_indices: list[int] | None = None,
) -> tuple[int, bool, str]:
    """Render the Resource Allocation Graph onto a Matplotlib figure.
    
    Returns:
        (cycle_count, has_deadlock, explanation_string)
    """
    fig.clear()
    ax = fig.add_subplot(111)

    G, cycles, is_single_instance = build_rag_graph(
        process_names=process_names,
        resource_names=resource_names,
        allocation_matrix=allocation_matrix,
        request_matrix=request_matrix,
        total_resources=total_resources,
        available_resources=available_resources,
        deadlocked_indices=deadlocked_indices,
    )

    n_proc = len(process_names)
    n_res = len(resource_names)

    # Bipartite custom layout: Processes on left / top, Resources on right / bottom
    pos = {}
    # Arrange in two distinct vertical or horizontal columns
    p_x, r_x = 0.2, 0.8
    y_p = np.linspace(0.85, 0.15, max(n_proc, 1))
    y_r = np.linspace(0.85, 0.15, max(n_res, 1))

    for i, p_name in enumerate(process_names):
        pos[p_name] = np.array([p_x, y_p[i]])

    for j, r_name in enumerate(resource_names):
        pos[r_name] = np.array([r_x, y_r[j]])

    # Collect cycle edges for highlight
    cycle_edge_set = set()
    for cycle in cycles:
        c_len = len(cycle)
        for k in range(c_len):
            u = cycle[k]
            v = cycle[(k + 1) % c_len]
            cycle_edge_set.add((u, v))

    # Separate nodes by type
    process_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "process"]
    resource_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "resource"]

    # Colors for process nodes
    proc_colors = []
    for n in process_nodes:
        if G.nodes[n].get("is_deadlocked", False):
            proc_colors.append("#ef4444")  # red
        else:
            proc_colors.append("#3b82f6")  # blue

    # Draw Process Nodes (Circles)
    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=process_nodes,
        node_shape="o",
        node_size=1800,
        node_color=proc_colors,
        edgecolors="#1e293b",
        linewidths=2.0,
        ax=ax,
    )

    # Draw Resource Nodes (Squares)
    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=resource_nodes,
        node_shape="s",
        node_size=2000,
        node_color="#f59e0b",  # Amber/Orange
        edgecolors="#78350f",
        linewidths=2.0,
        ax=ax,
    )

    # Node Labels
    labels = {n: d.get("label", n) for n, d in G.nodes(data=True)}
    nx.draw_networkx_labels(
        G,
        pos,
        labels=labels,
        font_size=8,
        font_weight="bold",
        font_color="#ffffff",
        ax=ax,
    )

    # Separate edges into:
    # 1. Normal allocation edges (Res -> Proc)
    # 2. Normal request edges (Proc -> Res)
    # 3. Cycle edges (highlighted in red)
    alloc_edges_normal = []
    req_edges_normal = []
    cycle_edges = []

    for u, v, d in G.edges(data=True):
        is_in_cycle = (u, v) in cycle_edge_set
        if is_in_cycle:
            cycle_edges.append((u, v))
        elif d.get("edge_type") == "allocation":
            alloc_edges_normal.append((u, v))
        else:
            req_edges_normal.append((u, v))

    # Draw Normal Allocation Edges (Resource -> Process, Solid Blue/Cyan)
    if alloc_edges_normal:
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=alloc_edges_normal,
            edge_color="#0284c7",
            style="solid",
            width=2.0,
            arrows=True,
            arrowstyle="-|>",
            arrowsize=16,
            connectionstyle="arc3,rad=0.1",
            ax=ax,
        )

    # Draw Normal Request Edges (Process -> Resource, Dashed Orange)
    if req_edges_normal:
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=req_edges_normal,
            edge_color="#ea580c",
            style="dashed",
            width=2.0,
            arrows=True,
            arrowstyle="-|>",
            arrowsize=16,
            connectionstyle="arc3,rad=-0.1",
            ax=ax,
        )

    # Draw Cycle Edges (Bold Red with Highlight)
    if cycle_edges:
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=cycle_edges,
            edge_color="#dc2626",
            style="solid",
            width=3.5,
            arrows=True,
            arrowstyle="-|>",
            arrowsize=20,
            connectionstyle="arc3,rad=0.15",
            ax=ax,
        )

    # Edge labels (weights if > 1)
    edge_labels = {(u, v): d.get("label", "") for u, v, d in G.edges(data=True) if d.get("label")}
    if edge_labels:
        nx.draw_networkx_edge_labels(
            G,
            pos,
            edge_labels=edge_labels,
            font_size=8,
            font_color="#b91c1c",
            ax=ax,
        )

    # Academic explanation banner
    num_cycles = len(cycles)
    has_deadlock = bool(deadlocked_indices and len(deadlocked_indices) > 0)

    if num_cycles > 0:
        if is_single_instance:
            theory_text = (
                f"CYCLE DETECTED ({num_cycles} cycle[s]) in Single-Instance System.\n"
                f"Theoretical Principle: In single-instance systems, a cycle is NECESSARY & SUFFICIENT for deadlock. DEADLOCK EXISTS."
            )
            banner_color = "#fecaca"
            border_color = "#dc2626"
        else:
            if has_deadlock:
                theory_text = (
                    f"CYCLE DETECTED ({num_cycles} cycle[s]) with Multiple Instances.\n"
                    f"Multiple-Instance Principle: Cycle is NECESSARY but NOT SUFFICIENT. Deadlock Detection confirms DEADLOCK."
                )
                banner_color = "#fecaca"
                border_color = "#dc2626"
            else:
                theory_text = (
                    f"CYCLE DETECTED ({num_cycles} cycle[s]) but NO DEADLOCK!\n"
                    f"Crucial Academic Insight: Multiple instances allow external processes to break circular dependency."
                )
                banner_color = "#fef08a"
                border_color = "#ca8a04"
    else:
        theory_text = (
            "NO CYCLES DETECTED in Resource Allocation Graph.\n"
            "Graph Theory Theorem: A system without cycles in its RAG can never be in a deadlocked state."
        )
        banner_color = "#dcfce7"
        border_color = "#16a34a"

    ax.text(
        0.5,
        0.03,
        theory_text,
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=8.5,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.5", facecolor=banner_color, edgecolor=border_color, linewidth=1.5),
    )

    ax.set_title("Resource Allocation Graph (RAG) - Real-Time Dynamic View", fontsize=11, fontweight="bold", pad=12)
    ax.axis("off")
    fig.tight_layout()

    return num_cycles, has_deadlock, theory_text

