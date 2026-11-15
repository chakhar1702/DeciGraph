import config
from column_ordering_vers import get_ordered_cols


def mixed_vers(ini_bin_matrix):
    """
    Mixed version:
        1. Column ordering
        2. Selective duplication (hardcoded: column 1 duplicated)
        3. Build final mixed matrix
        4. Update config.final_conditions_list and config.nb_final_elem_conditions
    """

    # ------------------------------------------------------------
    # Step 1: Compute ordered columns
    # ------------------------------------------------------------
    ordered_cols = get_ordered_cols(ini_bin_matrix)

    # ------------------------------------------------------------
    # Step 2: Select which columns to duplicate
    # ------------------------------------------------------------
    cols_to_duplica = [0] * config.nb_elem_conditions

    # Hardcoded C++ behavior: duplicate column 1
    if config.nb_elem_conditions > 1:
        cols_to_duplica[1] = 1

    # ------------------------------------------------------------
    # Step 3: Build ordered binary matrix
    # ------------------------------------------------------------
    ord_binary_matrix = []

    for i in range(len(ini_bin_matrix)):
        row_out = []

        # Ordered condition columns
        for j in range(config.nb_elem_conditions):
            original_col = ordered_cols[j][1]
            row_out.append(ini_bin_matrix[i][original_col])

        # Decision columns unchanged
        for j in range(config.nb_elem_conditions,
                       config.nb_elem_conditions + config.nb_decisions):
            row_out.append(ini_bin_matrix[i][j])

        ord_binary_matrix.append(row_out)

    # ------------------------------------------------------------
    # Step 4: Build mixed matrix with duplicated columns
    # ------------------------------------------------------------
    mixed_binary_matrix = []

    for i in range(len(ord_binary_matrix)):
        row_out = []

        for j in range(config.nb_elem_conditions):
            if cols_to_duplica[j] == 0:
                row_out.append(ord_binary_matrix[i][j])
            else:
                # Duplicate column ordered_cols[j][0] times
                for _ in range(ordered_cols[j][0]):
                    row_out.append(0)

        # Append decision columns
        for j in range(config.nb_elem_conditions,
                       config.nb_elem_conditions + config.nb_decisions):
            row_out.append(ord_binary_matrix[i][j])

        mixed_binary_matrix.append(row_out)

    # ------------------------------------------------------------
    # Step 5: Fill duplicated columns with 1s
    # ------------------------------------------------------------
    curr_col = 0

    for j in range(config.nb_elem_conditions):

        if cols_to_duplica[j] == 1:

            k = 0
            for i in range(len(ord_binary_matrix)):
                if ord_binary_matrix[i][j] == 1:
                    mixed_binary_matrix[i][curr_col + k] = 1
                    k += 1

            curr_col += k

        else:
            curr_col += 1

    # ------------------------------------------------------------
    # Step 6: Compute nb_final_elem_conditions
    # ------------------------------------------------------------
    total_cols = 0

    for j in range(config.nb_elem_conditions):
        if cols_to_duplica[j] == 1:
            total_cols += ordered_cols[j][0]
        else:
            total_cols += 1

    config.nb_final_elem_conditions = total_cols

    # ------------------------------------------------------------
    # Step 7: Build final_conditions_list
    # ------------------------------------------------------------
    config.final_conditions_list.clear()

    itr_cols = 0

    for j in range(config.nb_elem_conditions):

        if cols_to_duplica[j] == 1:
            for _ in range(ordered_cols[j][0]):
                config.final_conditions_list.append([
                    str(itr_cols),
                    str(ordered_cols[j][1])
                ])
                itr_cols += 1

        else:
            config.final_conditions_list.append([
                str(itr_cols),
                str(ordered_cols[j][1])
            ])
            itr_cols += 1

    return mixed_binary_matrix
