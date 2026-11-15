# distance_function.py

from config import distance_binary_matrix


# ------------------------------------------------------------
# Global arrays (same structure as C++)
# ------------------------------------------------------------
inters = 0
uniona = 0
ors = 0
xors = 0

# 50×50 matrices, initialized to 0
dista   = [[0.0 for _ in range(50)] for _ in range(50)]
interss = [[0.0 for _ in range(50)] for _ in range(50)]
unionas = [[0.0 for _ in range(50)] for _ in range(50)]
orss    = [[0.0 for _ in range(50)] for _ in range(50)]
xorss   = [[0.0 for _ in range(50)] for _ in range(50)]


def dista_func(the_matrix):
    """
    Python translation of dista_func().
    Computes pairwise distances between columns of distance_binary_matrix.

    NOTE:
    - nb_of_cols is hardcoded to 23 in the C++ version.
    - distance_binary_matrix must be filled BEFORE calling this.
    """

    global inters, uniona, ors, xors
    global dista, interss, unionas, orss, xorss

    nb_of_cols = 23  # same as C++

    # ------------------------------------------------------------
    # Compute distances
    # ------------------------------------------------------------
    for i in range(nb_of_cols):
        for j in range(nb_of_cols):

            inters = 0
            uniona = 0
            ors = 0
            xors = 0

            for k in range(nb_of_cols):

                a = distance_binary_matrix[k][i]
                b = distance_binary_matrix[k][j]

                if a == 1 and b == 1:
                    inters += 1
                if a == 1 or b == 1:
                    uniona += 1
                if a == 0 and b == 0:
                    ors += 1
                if (not a) != (not b):
                    xors += 1

            interss[i][j] = inters
            unionas[i][j] = uniona
            orss[i][j] = ors
            xorss[i][j] = xors

            if uniona > 0:
                dista[i][j] = inters / uniona
            else:
                dista[i][j] = 0.0

    # ------------------------------------------------------------
    # Print results (same as C++)
    # ------------------------------------------------------------
    print("\n===================================matrix========================================\n")

    print("i j  inters ors xors  union dist")
    for i in range(nb_of_cols):
        for j in range(nb_of_cols):
            if i < j and dista[i][j] != 0:
                print(
                    f"{i+1} {j+1}  | "
                    f"{interss[i][j]} "
                    f"{orss[i][j]} "
                    f"{xorss[i][j]} "
                    f"{unionas[i][j]}  | "
                    f"{17 if dista[i][j] == 0 else 1 - dista[i][j]}"
                )

    print("\n=================================================================================\n")
