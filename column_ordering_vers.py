# column_ordering_vers.py

import config


def update_final_conditions_list_ord12(sum_over_cols):
    """
    Direct translation of update_final_conditions_list_ord12().
    (NOTE: This function is NOT used by column_ordering_vers,
           but included for completeness.)
    """

    global final_conditions_list, nb_elem_conditions

    final_conditions_list.clear()
    elm_cond_id = 0

    for j in range(nb_elem_conditions):

        if sum_over_cols[j] == 0:
            final_conditions_list.append([
                str(elm_cond_id),
                str(j)
            ])
            elm_cond_id += 1

        else:
            for _ in range(sum_over_cols[j]):
                final_conditions_list.append([
                    str(elm_cond_id),
                    str(j)
                ])
                elm_cond_id += 1


def sortbyCond(a, b):
    """
    C++ comparator:
        if (a.first != b.first) return a.first < b.first
        else return a.second > b.second
    Python equivalent for sorting with key.
    """
    # We will not use this directly; Python sorting uses key functions.
    pass


def get_ordered_cols(ini_bin_matrix):
    """
    Returns a list of [sum_of_column, original_column_id].
    Sorted by:
        - sum_of_column DESC
        - original_column_id DESC
    """

    sum_over_cols = []
    cols_ids = []

    # Compute number of 1s per column
    for j in range(config.nb_elem_conditions):
        col_sum = sum(ini_bin_matrix[i][j] for i in range(len(ini_bin_matrix)))
        sum_over_cols.append(col_sum)

        # C++: cols_ids.push_back(std::stoi(conditions_list[j][0]) - 1);
        cond_id = int(config.conditions_list[j][0]) - 1
        cols_ids.append(cond_id)

    vect = list(zip(sum_over_cols, cols_ids))

    # primary: sum DESC, secondary: col_id DESC
    vect.sort(key=lambda x: (x[0], x[1]), reverse=True)

    ordered_cols = [[v[0], v[1]] for v in vect]
    return ordered_cols


def column_ordering_vers(ini_bin_matrix):
    """
    Reorders columns by number of 1s (descending), then by condition ID.
    Updates config.final_conditions_list and config.nb_final_elem_conditions.
    """

    ordered_cols = get_ordered_cols(ini_bin_matrix)

    ord_final_binary_matrix = []

    for i in range(len(ini_bin_matrix)):
        row_out = []

        # Reordered condition columns
        for j in range(config.nb_elem_conditions):
            original_col = ordered_cols[j][1]
            row_out.append(ini_bin_matrix[i][original_col])

        # Append decision columns unchanged
        for j in range(config.nb_elem_conditions,
                       config.nb_elem_conditions + config.nb_decisions):
            row_out.append(ini_bin_matrix[i][j])

        ord_final_binary_matrix.append(row_out)

    # Update final_conditions_list in config
    config.final_conditions_list.clear()
    for j in range(config.nb_elem_conditions):
        config.final_conditions_list.append([
            str(j),                   # new column index
            str(ordered_cols[j][1])   # original column index
        ])

    # Update number of final conditions in config
    config.nb_final_elem_conditions = config.nb_elem_conditions

    return ord_final_binary_matrix
