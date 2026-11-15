import config

from print_on_screen_routines import (
    debug_print_chain_and_duplications,
    debug_visualise_poset
)


# ============================================================
# 1. Compute co-occurrence sets S_j
# ============================================================

def compute_cooccurrence_sets(matrix, n_cond):
    """
    Returns a list S where S[j] is the set of rule indices i
    such that matrix[i][j] == 1.
    """
    S = []
    n_rules = len(matrix)

    for j in range(n_cond):
        S_j = {i for i in range(n_rules) if matrix[i][j] == 1}
        S.append(S_j)

    return S


# ============================================================
# 2. Build partial order: S_j ⊆ S_k
# ============================================================

def build_partial_order(S):
    """
    Returns adjacency list for the poset:
    j -> list of k such that S[j] ⊆ S[k]
    """
    n = len(S)
    order = [[] for _ in range(n)]

    for j in range(n):
        for k in range(n):
            if j != k and S[j].issubset(S[k]):
                order[j].append(k)

    return order


# ============================================================
# 3. Find maximum chain in the poset
# ============================================================

def find_max_chain(S):
    """
    Returns the indices of columns forming a maximum chain
    under the subset relation.
    """
    n = len(S)

    # Sort columns by |S_j| ascending (helps chain extraction)
    sorted_cols = sorted(range(n), key=lambda j: len(S[j]))

    # DP: longest chain ending at column j
    dp = [1] * n
    parent = [-1] * n

    for idx_j in range(n):
        j = sorted_cols[idx_j]
        for idx_k in range(idx_j):
            k = sorted_cols[idx_k]
            if S[k].issubset(S[j]):
                if dp[k] + 1 > dp[j]:
                    dp[j] = dp[k] + 1
                    parent[j] = k

    # Find end of longest chain
    end = max(range(n), key=lambda j: dp[j])

    # Reconstruct chain
    chain = []
    while end != -1:
        chain.append(end)
        end = parent[end]

    chain.reverse()
    return chain


# ============================================================
# 4. Build transformed matrix (ordering + duplication)
# ============================================================

def build_transformed_matrix(matrix, ordered_cols, duplicated_cols):
    """
    ordered_cols: list of column indices forming the safe chain
    duplicated_cols: list of column indices NOT in the chain
    """
    n_rules = len(matrix)
    n_cond = config.nb_elem_conditions
    n_dec = config.nb_decisions

    # --------------------------------------------------------
    # Step 1: Build ordered matrix (safe columns first)
    # --------------------------------------------------------
    ordered_matrix = []

    for i in range(n_rules):
        row = []

        # Add ordered columns in chain order
        for j in ordered_cols:
            row.append(matrix[i][j])

        # Add duplicated columns (original order)
        for j in duplicated_cols:
            row.append(matrix[i][j])

        # Add decision columns unchanged
        for j in range(n_cond, n_cond + n_dec):
            row.append(matrix[i][j])

        ordered_matrix.append(row)

    # --------------------------------------------------------
    # Step 2: Duplicate unsafe columns
    # --------------------------------------------------------
    # For each duplicated column j, count number of 1s
    dup_counts = []
    for j in duplicated_cols:
        col_sum = sum(matrix[i][j] for i in range(n_rules))
        dup_counts.append(col_sum if col_sum > 0 else 1)

    # Build final matrix with duplication
    final_matrix = []

    for i in range(n_rules):
        row = []

        # Ordered columns (1 copy each)
        for j in ordered_cols:
            row.append(matrix[i][j])

        # Duplicated columns
        for idx, j in enumerate(duplicated_cols):
            count = dup_counts[idx]
            if count == 1:
                row.append(matrix[i][j])
            else:
                # Insert count zeros; fill later
                row.extend([0] * count)

        # Decision columns
        for j in range(n_cond, n_cond + n_dec):
            row.append(matrix[i][j])

        final_matrix.append(row)

    # --------------------------------------------------------
    # Step 3: Fill duplicated columns with 1s
    # --------------------------------------------------------
    # Offset: number of ordered columns
    offset = len(ordered_cols)

    for idx, j in enumerate(duplicated_cols):
        count = dup_counts[idx]
        if count == 1:
            offset += 1
            continue

        k = 0
        for i in range(n_rules):
            if matrix[i][j] == 1:
                final_matrix[i][offset + k] = 1
                k += 1

        offset += count

    return final_matrix, dup_counts


# ============================================================
# 5. Update config.final_conditions_list
# ============================================================

def update_final_conditions_list_opt(ordered_cols, duplicated_cols, dup_counts):
    config.final_conditions_list.clear()

    elm_id = 0

    # Ordered columns: 1 copy each
    for j in ordered_cols:
        config.final_conditions_list.append([str(elm_id), str(j)])
        elm_id += 1

    # Duplicated columns
    for idx, j in enumerate(duplicated_cols):
        count = dup_counts[idx]
        for _ in range(count):
            config.final_conditions_list.append([str(elm_id), str(j)])
            elm_id += 1

    config.nb_final_elem_conditions = elm_id


# ============================================================
# 6. Main function: optimised_mixed_version
# ============================================================

def optimised_mixed_version(ini_bin_matrix):
    n_cond = config.nb_elem_conditions

    # Step 1: Compute co-occurrence sets
    S = compute_cooccurrence_sets(ini_bin_matrix, n_cond)

    # Step 2: Find maximum chain (safe ordered columns)
    ordered_cols = find_max_chain(S)

    from print_on_screen_routines import export_poset_to_dot

    # After computing S:
    export_poset_to_dot(S, filename="poset.dot")

    # Step 3: Remaining columns must be duplicated
    duplicated_cols = [j for j in range(n_cond) if j not in ordered_cols]

    # >>> DEBUG PRINTS <<<
    debug_print_chain_and_duplications(ordered_cols, duplicated_cols, S)
    debug_visualise_poset(S)
    # >>> END DEBUG <<<

    # Step 4: Build transformed matrix
    final_matrix, dup_counts = build_transformed_matrix(
        ini_bin_matrix, ordered_cols, duplicated_cols
    )

    # Step 5: Update config
    update_final_conditions_list_opt(ordered_cols, duplicated_cols, dup_counts)

    return final_matrix
