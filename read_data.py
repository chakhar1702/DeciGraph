import os
import re
import config

from config import (
    attributes_list,
    conditions_list,
    decisions_list,
    elementary_conditions,
    decision_conditions,
    rules_list
)

def load_unseen_objects():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(script_dir, "data")

    unseen_data_file = os.path.join(data_folder, "unseen_data.txt")
    objects = []
    with open(unseen_data_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Split by comma or space
            if "," in line:
                values = line.split(",")
            else:
                values = line.split()

            # Build object dict: {"1": val1, "2": val2, ...}
            obj = {str(i+1): values[i] for i in range(len(values))}
            objects.append(obj)

    return objects


def parse_rhs_jmaf(cond):
    parts = cond.split()
    if len(parts) != 3:
        return None
    attr, op, label = parts
    if op == ">=":
        return f"at_least_{label}"
    elif op == "<=":
        return f"at_most_{label}"
    return None


def parse_rhs_4emka2(cond):
    parts = cond.split()
    if len(parts) != 4:
        return None
    attr, at_word, bound_type, label = parts
    if at_word != "at":
        return None
    if bound_type == "most":
        return f"at_most_{label}"
    elif bound_type == "least":
        return f"at_least_{label}"
    return None


def read_data_for_graph(rule_format="jmaf"):

    # ------------------------------------------------------------
    # Reset global lists
    # ------------------------------------------------------------
    attributes_list.clear()
    conditions_list.clear()
    decisions_list.clear()
    elementary_conditions.clear()
    decision_conditions.clear()
    rules_list.clear()

    # ------------------------------------------------------------
    # Locate files
    # ------------------------------------------------------------
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(script_dir, "data")

    rules_file   = os.path.join(data_folder, "list_of_rules.txt")
    attrs_file   = os.path.join(data_folder, "attrs_list.txt")
    classes_file = os.path.join(data_folder, "decision_classes.txt")

    # ------------------------------------------------------------
    # Step 1: Read classes
    # ------------------------------------------------------------
    class_order_map = {}
    order_class_map = {}

    with open(classes_file, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                order = int(parts[0])
                label = parts[1]
                class_order_map[label] = order
                order_class_map[order] = label

    config.order_class_map = order_class_map

    # ------------------------------------------------------------
    # Step 2: Read attributes
    # ------------------------------------------------------------
    attr_map = {}
    attr_order = []
    attr_names = []

    with open(attrs_file, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 3:
                attr_id = parts[0].strip()
                prefer = parts[1].strip()
                attr_name = parts[-1].strip()

                attr_map[attr_name] = attr_id
                attr_order.append(attr_id)
                attr_names.append(attr_name)
                attributes_list.append([attr_id, prefer, attr_name])

    # ------------------------------------------------------------
    # Step 3: Read rules
    # ------------------------------------------------------------
    list_of_conditions = []
    rules_conditions = []
    rhs_union_names = []

    with open(rules_file, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        # Remove everything after first semicolon
        if ";" in line:
            line = line.split(";", 1)[0].strip()

        if not line or "=>" not in line:
            continue

        rules_list.append(line)

        left_part, right_part = line.split("=>")

        # LHS conditions
        conditions = re.findall(r"\((.*?)\)", left_part)
        list_of_conditions.extend(conditions)
        rules_conditions.append(conditions)

        # RHS union condition
        match = re.search(r"\(([^()]+)\)", right_part)
        if not match:
            rhs_union_names.append(None)
            continue

        cond = match.group(1).strip()

        if rule_format == "jmaf":
            union_name = parse_rhs_jmaf(cond)
        else:
            union_name = parse_rhs_4emka2(cond)

        rhs_union_names.append(union_name)

    # ------------------------------------------------------------
    # Step 4: Unique elementary conditions
    # ------------------------------------------------------------
    unique_conditions = list(dict.fromkeys(list_of_conditions))
    elementary_conditions.extend(unique_conditions)

    # ------------------------------------------------------------
    # Step 5: Build conditions_list
    # ------------------------------------------------------------
    for idx, cond in enumerate(unique_conditions, start=1):

        if rule_format == "4emka2":
            m = re.match(r"(.+?)(<=|>=|=)(.+)", cond)
            if not m:
                raise ValueError(f"Cannot parse 4emka2 condition: {cond}")

            attr_name = m.group(1).strip()
            operator = m.group(2).strip()
            rhs = m.group(3).strip()

            # IMPORTANT: Do NOT strip A1_, A2_, etc.
            # attr_name must match attrs_list.txt exactly.

        else:
            parts = cond.split()
            if len(parts) != 3:
                raise ValueError(f"Cannot parse jMAF condition: {cond}")

            attr_name = parts[0]
            operator = parts[1]
            rhs = parts[2]

        # Validate attribute name
        if attr_name not in attr_map:
            raise KeyError(f"Attribute '{attr_name}' not found in attrs_list.txt")

        attr_id = attr_map[attr_name]
        conditions_list.append([str(idx), attr_id, operator, rhs])

    # ------------------------------------------------------------
    # Step 6: Unique union-class decisions
    # ------------------------------------------------------------
    unique_union_names = list(dict.fromkeys([u for u in rhs_union_names if u is not None]))
    decision_conditions.extend(unique_union_names)

    # ------------------------------------------------------------
    # Step 6.5: Build decisions_list (metadata for graph nodes)
    # ------------------------------------------------------------
    decisions_list.clear()
    for j, name in enumerate(unique_union_names):
        # decisions_list[j] = [id, label, rhs]
        decisions_list.append([str(j), name, ""])


    # ------------------------------------------------------------
    # Step 7: Build base incidence matrix
    # ------------------------------------------------------------
    matrix = []
    for conds in rules_conditions:
        row = [1 if uc in conds else 0 for uc in unique_conditions]
        matrix.append(row)

    # ------------------------------------------------------------
    # Step 8: Extend matrix with union-class columns
    # ------------------------------------------------------------
    extended_matrix = []

    for row_idx, base_row in enumerate(matrix):
        union_bits = [0] * len(unique_union_names)

        union_name = rhs_union_names[row_idx]

        if union_name is None:
            raise ValueError(f"Rule {row_idx+1} has NO decision class!")

        if union_name in unique_union_names:
            idx = unique_union_names.index(union_name)
            union_bits[idx] = 1
        else:
            raise ValueError(f"Unknown union class '{union_name}' in rule {row_idx+1}")

        extended_matrix.append(base_row + union_bits)

    # ------------------------------------------------------------
    # Step 9: Return ONLY the matrix (C++ style)
    # ------------------------------------------------------------
    #print("\n\n\n\nEXTENDED MATRIX SIZE:", len(extended_matrix), "x", len(extended_matrix[0]))

    return extended_matrix
