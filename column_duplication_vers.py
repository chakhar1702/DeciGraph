import config

def update_final_conditions_list_dup(sum_over_cols):
    config.final_conditions_list.clear()
    elm_cond_id = 0

    for j in range(config.nb_elem_conditions):
        dup_count = sum_over_cols[j]
        if dup_count == 0:
            dup_count = 1

        for _ in range(dup_count):
            config.final_conditions_list.append([str(elm_cond_id), str(j)])
            elm_cond_id += 1


def column_duplication_vers(ini_bin_matrix):
    n_rules = len(ini_bin_matrix)

    # -----------------------------------------
    # 1. Count 1s per column
    # -----------------------------------------
    sum_over_cols = []
    config.nb_final_elem_conditions = 0

    for j in range(config.nb_elem_conditions):
        col_sum = sum(ini_bin_matrix[i][j] for i in range(n_rules))
        sum_over_cols.append(col_sum)
        config.nb_final_elem_conditions += (col_sum if col_sum > 0 else 1)

    # -----------------------------------------
    # 2. PASS 1 — Build structure
    # -----------------------------------------
    dup_final = []

    for i in range(n_rules):
        row = []
        for j in range(config.nb_elem_conditions):
            if sum_over_cols[j] == 1:
                row.append(ini_bin_matrix[i][j])
            else:
                for _ in range(sum_over_cols[j] if sum_over_cols[j] > 0 else 1):
                    row.append(0)
        # append decision columns
        for j in range(config.nb_decisions):
            row.append(ini_bin_matrix[i][config.nb_elem_conditions + j])
        dup_final.append(row)

    # -----------------------------------------
    # 3. PASS 2 — Fill 1s in correct order
    # -----------------------------------------
    k = 0
    for j in range(config.nb_elem_conditions):
        dup_count = sum_over_cols[j] if sum_over_cols[j] > 0 else 1
        for i in range(n_rules):
            if ini_bin_matrix[i][j] == 1:
                dup_final[i][k] = 1
                k += 1
        if sum_over_cols[j] == 0:
            k += 1

    # -----------------------------------------
    # 4. Build mapping list
    # -----------------------------------------
    update_final_conditions_list_dup(sum_over_cols)

    return dup_final
