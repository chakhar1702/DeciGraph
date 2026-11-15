import config

from utils import already_in_edges, add_to_edges, print_data_summary
from read_data import read_data_for_graph, load_unseen_objects
from column_duplication_vers import column_duplication_vers
from column_ordering_vers import column_ordering_vers
from mixed_vers import mixed_vers
from optimised_mixed_version import  optimised_mixed_version
from exploitation import ExploitationGraph, path_to_rule
from print_on_screen_routines import (
    print_binary_matrix,
    print_final_binary_matrix,
    print_graph_code
)
from aggregate_decision import (
    parse_decision,
    compute_interval,
    aggregate_decisions
)

from bfs_algorithm import Graph
from printAllRulesasPaths import GraphPaths


def main():

    # ------------------------------------------------------------
    # RESET CONFIG STATE
    # ------------------------------------------------------------
    config.attributes_list.clear()
    config.conditions_list.clear()
    config.decisions_list.clear()
    config.edges.clear()
    config.node_id.clear()
    config.node_data_id.clear()
    config.node_label.clear()
    config.edge_label.clear()

    # ------------------------------------------------------------
    # READ DATA
    # ------------------------------------------------------------
    initial_binary_matrix = read_data_for_graph("4emka2")

    # Update config counts
    config.nb_elem_conditions = len(config.elementary_conditions)
    config.nb_decisions = len(config.decision_conditions)

    #print("nb_elem_conditions =", config.nb_elem_conditions)
    #print("nb_decisions =", config.nb_decisions)
    #print("decisions_list =", config.decisions_list)
    #print("decision_conditions =", config.decision_conditions)

    print_data_summary()

    nb_total_cols = len(initial_binary_matrix[0])
    print_binary_matrix(initial_binary_matrix, nb_total_cols, 0)

    # Count number of 1s in condition part
    nb_of_1s = sum(
        1
        for j in range(config.nb_elem_conditions)
        for i in range(len(initial_binary_matrix))
        if initial_binary_matrix[i][j] == 1
    )

    # ------------------------------------------------------------
    # SELECT VERSION
    # ------------------------------------------------------------
    version = 2 # 0=no preprocessing, 1=duplication, 2=ordering, 3=mixed

    config.node_label.append("0")  # root label

    # ------------------------------------------------------------
    # PREPROCESSING
    # ------------------------------------------------------------
    if version == 0 or nb_of_1s == config.nb_elem_conditions:
        print("\n\n___decision_graph_construction_algo_-_with_no_pre-processing___\n")

        final_binary_matrix = initial_binary_matrix
        config.nb_final_elem_conditions = config.nb_elem_conditions
        config.final_conditions_list = list(config.conditions_list)

    else:
        if version == 1:
            print("\n\n___decision_graph_construction_algo_-_by_column_duplication___\n")
            final_binary_matrix = column_duplication_vers(initial_binary_matrix)

        elif version == 2:
            print("\n\n___decision_graph_construction_algo_-_by_column_ordering___\n")
            final_binary_matrix = column_ordering_vers(initial_binary_matrix)

        elif version == 3:
            print("\n\n___decision_graph_construction_algo_-_mixed_version___\n")
            final_binary_matrix = mixed_vers(initial_binary_matrix)

        elif version == 4:
            print("\n\n___decision_graph_construction_algo_-_optimised_mixed_version___\n")
            final_binary_matrix = optimised_mixed_version(initial_binary_matrix)


        print(
            "FINAL MATRIX SIZE:",
            len(final_binary_matrix),
            "x",
            len(final_binary_matrix[0])
        )
        print("nb_final_elem_conditions =", config.nb_final_elem_conditions)

    print_final_binary_matrix(final_binary_matrix)

    # ------------------------------------------------------------
    # BUILD NODE LIST
    # ------------------------------------------------------------
    config.node_data_id.clear()
    config.node_data_id.append(0)  # root

    # Recompute number of condition columns from matrix
    config.nb_final_elem_conditions = len(final_binary_matrix[0]) - config.nb_decisions

    # Condition nodes
    for j in range(config.nb_final_elem_conditions):
        config.node_data_id.append(j + 1)

    # Decision nodes
    for j in range(config.nb_decisions):
        config.node_data_id.append(config.nb_final_elem_conditions + 1 + j)

    # ------------------------------------------------------------
    # BUILD EDGES
    # ------------------------------------------------------------

    # Root → first condition with 1
    for row in final_binary_matrix:
        j = 0
        while j < len(row) and row[j] != 1:
            j += 1
        if j < len(row):
            if not already_in_edges(0, j + 1):
                add_to_edges(0, j + 1)

    # Condition → condition edges
    if version != 1:
        for j in range(config.nb_final_elem_conditions):
            for i in range(len(final_binary_matrix)):
                if final_binary_matrix[i][j] == 1:
                    h = j + 1
                    while final_binary_matrix[i][h] != 1:
                        h += 1
                    if not already_in_edges(j + 1, h + 1):
                        add_to_edges(j + 1, h + 1)
    else:
        # version == 1 logic
        for j in range(config.nb_final_elem_conditions):
            i = 0
            while final_binary_matrix[i][j] != 1:
                i += 1
            h = j + 1
            while final_binary_matrix[i][h] != 1:
                h += 1
            if not already_in_edges(j + 1, h + 1):
                add_to_edges(j + 1, h + 1)

    # ------------------------------------------------------------
    # PRINT GRAPHVIZ CODE
    # ------------------------------------------------------------
    print("\n\n______decision_graph_code_for_graphvis___\n")
    print_graph_code()

    # ------------------------------------------------------------
    # LINEARISATION OF DECISION GRAPH
    # ------------------------------------------------------------
    print("\n___linearisation of decision graph___\n")

    V = config.nb_final_elem_conditions + config.nb_decisions + 1
    graph = GraphPaths(V)

    for (u, v) in config.edges:
        graph.addEdge(u, v)

    source = 0

    for i in range(config.nb_decisions):
        dest = config.nb_final_elem_conditions + i + 1
        print(f"\n->All rules for class union {config.decisions_list[i][1]} {config.decisions_list[i][2]}:\n")
        graph.printAllPaths(source, dest)
        print()

    # ------------------------------------------------------------
    # BATCH EXPLOITATION (Unified Output)
    # ------------------------------------------------------------
    print("\n___Batch exploitation of decision graph___\n")

    xpl = ExploitationGraph(V)

    for (u, v) in config.edges:
        xpl.addEdge(u, v)

    objects = load_unseen_objects()

    final_decisions = []

    # Extract class labels from decisions_list
    #raw_labels = [entry[1].split("_")[-1] for entry in config.decisions_list]

    # Deduplicate while preserving order
    #classes_list = []
    #for lbl in raw_labels:
    #    if lbl not in classes_list:
    #        classes_list.append(lbl)

    # Build classes_list directly from decision_classes.txt
    #classes_list = [order_class_map[i] for i in sorted(order_class_map.keys())]

    classes_list = [config.order_class_map[i] for i in sorted(config.order_class_map.keys())]

    # ------------------------------------------------------------
    # Process each object once
    # ------------------------------------------------------------
    for idx, obj in enumerate(objects):

        print(f"\n=== Object {idx + 1} ===")
        print("Attributes:", obj)

        # Run exploitation
        results = xpl.classify(obj)

        if not results:
            print("No rules satisfied.")
            print(f"Interval = [Cl1, Cl{len(classes_list)}]")
            print("Final decision: None")
            final_decisions.append(None)
            continue

        # Extract decisions and rule paths
        decisions = [decision for (decision, path) in results]
        rule_paths = [path for (decision, path) in results]

        # --------------------------------------------------------
        # Print rules covered
        # --------------------------------------------------------
        print("\nRules satisfied:")
        for path in rule_paths:
            print(" -", path_to_rule(path))

        # --------------------------------------------------------
        # Print decision unions
        # --------------------------------------------------------
        print("\nDecisions extracted:")
        print(" ", decisions)

        # --------------------------------------------------------
        # Compute interval
        # --------------------------------------------------------
        lx, ux = compute_interval(decisions, classes_list)

        # --------------------------------------------------------
        # Aggregate final decision
        # --------------------------------------------------------
        final_class = aggregate_decisions(decisions, classes_list, strategy="max")
        final_decisions.append(final_class)

        print(f"\nInterval = [{lx}, {ux}]")
        print(f"Final aggregated decision = {final_class}")

    print("\n___All objects processed___\n")

    # ------------------------------------------------------------
    # SUMMARY TABLE
    # ------------------------------------------------------------
    print("\n___Summary Table: Object → Final Decision___\n")

    # Header
    print(f"{'Object':<10} | {'Final Decision'}")
    print("-" * 30)

    for idx, decision in enumerate(final_decisions, start=1):
        label = decision if decision is not None else "None"
        print(f"{idx:<10} | {label}")

    print("\nDone.\n")


if __name__ == "__main__":
    main()
