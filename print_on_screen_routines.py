# print_on_screen_routines.py

import config


# ------------------------------------------------------------
# ReplaceAll
# ------------------------------------------------------------
def ReplaceAll(s: str, from_str: str, to_str: str) -> str:
    """Python equivalent of C++ ReplaceAll."""
    return s.replace(from_str, to_str)


# ------------------------------------------------------------
# print_binary_matrix
# ------------------------------------------------------------
def print_binary_matrixOLD(binary_matrix, nb_conditions, what):
    if what == 0:
        print("\n___initial_binary_matrix___")
    elif what == 1:
        print("\n___duplicated_binary_matrix___")
    elif what == 2:
        print("\n___ordered_binary_matrix___")
    elif what == 3:
        print("\n___mixed_binary_matrix___")

    for i, row in enumerate(binary_matrix):
        print(f"i={i}: ", end="")
        for j in range(nb_conditions + config.nb_decisions):
            if j == nb_conditions:
                print(" | ", end="")
            print(f"{row[j]} ", end="")
        print()

def print_binary_matrix(matrix, nb_cols, split_at):
    print("\n___initial_binary_matrix___")
    for i, row in enumerate(matrix):
        print(f"i={i}: ", end="")
        for j in range(len(row)):
            if j == split_at:
                print(" | ", end="")
            print(f"{row[j]} ", end="")
        print()

# ------------------------------------------------------------
# print_final_binary_matrix
# ------------------------------------------------------------

def print_final_binary_matrix(final_binary_matrix):
    print("\n___final_binary_matrix___")

    for i, row in enumerate(final_binary_matrix):
        print(f"i={i}: ", end="")

        # Compute where to place the separator
        split_at = len(row) - config.nb_decisions

        for j in range(len(row)):
            if j == split_at:
                print(" | ", end="")
            print(f"{row[j]} ", end="")

        print()

# ------------------------------------------------------------
# print_meta_data
# ------------------------------------------------------------
def print_meta_data():
    print("\n___condition attributes___")
    for attr in config.attributes_list:
        print(attr[0], attr[1])

    print("\n___elementary conditions___")
    for cond in config.conditions_list:
        print(cond[0], cond[1], cond[2], cond[3])

    print("\n___decision attributes___")
    for dec in config.decisions_list:
        print(dec[0], dec[1], dec[2])


# ------------------------------------------------------------
# print_nodes
# ------------------------------------------------------------
def print_nodes():
    print("\n___nodes___")
    for j, nd in enumerate(config.node_data_id):
        print(f"\n#{j}: -> {nd}")


# ------------------------------------------------------------
# print_edges
# ------------------------------------------------------------
def print_edges():
    print("\n___edges___")
    for s, e in config.edges:
        print(f"\n{s}->{e}")
    print("\n")


# ------------------------------------------------------------
# get_operator (HTML-friendly)
# ------------------------------------------------------------
def get_operator(op):
    mapping = {
        "EQL": " = ",
        "LEQ": "&le; ",
        "SL": "&lt; ",
        "GEQ": "&ge; ",
        "SG": "&gt; ",
        "OGE": "&#8829; ",
        "OLE": "&#8828; "
    }
    return mapping.get(op, " = ")


# ------------------------------------------------------------
# print_graph_code (GraphViz DOT output)
# ------------------------------------------------------------
def print_graph_code():
    import config

    print("\ndigraph preferenceGraph{")
    print('overlap = false;')
    print('splines = true;')

    # ------------------------------------------------------------
    # 1. Print ROOT node
    # ------------------------------------------------------------
    print(f'0 [label = "{config.root_label}", color = grey, fillcolor = lightgrey, style = filled];')

    # ------------------------------------------------------------
    # 2. Print CONDITION nodes (1 .. nb_final_elem_conditions)
    # ------------------------------------------------------------
    for cond_id in range(1, config.nb_final_elem_conditions + 1):

        # final_conditions_list entry: [new_id, original_condition_index]
        orig_cond_index = int(config.final_conditions_list[cond_id - 1][1])

        if config.label_on_nodes == 0:
            # Only attribute name
            label = config.conditions_list[orig_cond_index][0]
        else:
            # Attribute + operator + rhs
            label = (
                f"{config.conditions_list[orig_cond_index][0]} "
                f"{config.conditions_list[orig_cond_index][1]} "
                f"{config.conditions_list[orig_cond_index][2]}"
            )

        print(f'{cond_id} [label = "{label}", color = grey, fillcolor = lightgrey, style = filled];')

    # ------------------------------------------------------------
    # 3. Print DECISION nodes (after condition nodes)
    # ------------------------------------------------------------

    #print(config.decisions_list)
    for j in range(config.nb_decisions):
        node_id = config.nb_final_elem_conditions + j+1

        if config.label_on_nodes == 0:
            label = f"{config.decisions_list[j][1]}"
        else:
            label = f"{config.decisions_list[j][1]} {config.decisions_list[j][2]}"

        print(f'{node_id} [label = "{label}", color = grey, fillcolor = lightgrey, style = filled];')

    # ------------------------------------------------------------
    # 4. Print EDGES
    # ------------------------------------------------------------
    for (s, e) in config.edges:

        if config.label_on_edges == 0:
            edge_label = ""
        else:
            # label_on_edges == 1 → operator + rhs
            if s == 0:
                # Root → condition: no operator
                edge_label = ""
            else:
                # Condition → next condition or decision
                orig_cond_index = int(config.final_conditions_list[s - 1][1])
                edge_label = config.conditions_list[orig_cond_index][1]  # operator only

        if edge_label:
            print(f'{s} -> {e} [label="{edge_label}", color="green", arrowhead="vee", penwidth=1];')
        else:
            print(f'{s} -> {e} [color="green", arrowhead="vee", penwidth=1];')

    print("}")


# ------------------------------------------------------------
# print_graph_code2 (alternate DOT output)
# ------------------------------------------------------------
def print_graph_code2():
    print("digraph preferenceGraph{")
    print(f'0 [label=<<I>{config.root_label}</I>>,color=grey,fillcolor=lightgrey,style=filled];')

    # Condition nodes
    for j in range(config.nb_final_elem_conditions):
        orig = int(config.final_conditions_list[j][1])
        digits = list(str(orig))
        subscript = "".join(f"&#832{d};" for d in digits)
        print(f'{j+1} [label=<<I>C{subscript}</I>>,color=grey,fillcolor=lightgrey,style=filled];')

    # Decision nodes
    for j in range(config.nb_decisions):
        digits = list(str(config.decisions_list[j][0]))
        subscript = "".join(f"&#832{d};" for d in digits)
        print(f'{config.nb_final_elem_conditions + 1 + j} [label=<<I>K{subscript}</I>>,'
              f'shape={config.deci_node_shape}, color=grey, fillcolor=lightgrey, style=filled];')

    print("overlap = false;")
    print("splines = true;")

    for s, e in config.edges:
        if s == 0:
            print(f'{s}->{e} [color="green",arrowhead="vee",penwidth=1];')
        else:
            print(f'{s}->{e} [color="black",arrowhead="vee",penwidth=1];')

    print("}")

def debug_print_chain_and_duplications(ordered_cols, duplicated_cols, S):
    print("\n=== OPTIMISATION DEBUG INFO ===")

    print("\nSafe ordered columns (maximum chain):")
    print("  ordered_cols =", ordered_cols)

    print("\nColumns that must be duplicated:")
    print("  duplicated_cols =", duplicated_cols)

    print("\nCo-occurrence sets S_j:")
    for j, Sj in enumerate(S):
        print(f"  S[{j}] = {sorted(list(Sj))}")

    print("\n================================\n")


def debug_visualise_poset(S):
    print("\n=== POSET VISUALISATION (S_j ⊆ S_k) ===")

    n = len(S)
    for j in range(n):
        arrows = []
        for k in range(n):
            if j != k and S[j].issubset(S[k]):
                arrows.append(k)
        print(f"  {j} --> {arrows}")

    print("=======================================\n")

def export_poset_to_dot(S, filename="poset.dot"):
    """
    Export the poset (subset relations S_j ⊆ S_k) to a Graphviz DOT file.
    Each column j is a node; an arrow j -> k means S_j ⊆ S_k.
    """
    n = len(S)

    with open(filename, "w") as f:
        f.write("digraph Poset {\n")
        f.write("  rankdir=LR;\n")  # left-to-right layout

        # Nodes
        for j in range(n):
            label = f"S{j} = {sorted(list(S[j]))}"
            f.write(f'  {j} [label="{label}"];\n')

        # Edges
        for j in range(n):
            for k in range(n):
                if j != k and S[j].issubset(S[k]):
                    f.write(f"  {j} -> {k};\n")

        f.write("}\n")

    print(f"\nDOT file written to: {filename}\n")
