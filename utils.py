
from config import edges

def already_in_edges(s, e):
    """Check if edge (s, e) already exists."""
    for a, b in edges:
        if a == s and b == e:
            return True
    return False


def add_to_edges(node_s, node_e):
    """Add edge (node_s, node_e) to global edges list."""
    edges.append([node_s, node_e])

def print_data_summary():
    """
    Prints all parsed metadata before matrix display:
    - Attributes
    - Decision classes (union)
    - Rules
    - Unique elementary conditions
    - Matrix size
    """

    from config import (
        attributes_list,
        decision_conditions,
        rules_list,
        elementary_conditions
    )

    print("\n==================== ATTRIBUTES ====================")
    for attr_id, prefer, name in attributes_list:
        print(f"{attr_id}\t{prefer}\t{name}")

    print("\n==================== DECISION CLASSES (UNION) ====================")
    for u in decision_conditions:
        print(u)

    print("\n==================== RULES ====================")
    for r in rules_list:
        print(r)

    print("\n==================== UNIQUE ELEMENTARY CONDITIONS ====================")
    for c in elementary_conditions:
        print(c)

    # Matrix size (if matrix already loaded)
    try:
        from config import initial_binary_matrix
        if initial_binary_matrix:
            rows = len(initial_binary_matrix)
            cols = len(initial_binary_matrix[0])
            print(f"\nMatrix size: {rows} rows × {cols} columns")
    except:
        pass

    print("\n====================================================\n")
