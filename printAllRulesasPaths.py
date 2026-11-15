import config

def get_operator_by_code_ascii(code):
    if code == "EQL":
        return "="
    elif code == "LEQ":
        return "<="
    elif code == "GEQ":
        return ">="
    return code  # already ASCII


class GraphPaths:
    def __init__(self, V):
        self.V = V
        self.adj = [[] for _ in range(V)]

    def addEdge(self, u, v):
        self.adj[u].append(v)

    def printAllPaths(self, s, d):
        visited = [False] * self.V
        path = [0] * self.V
        self._printAllPathsUntil(s, d, visited, path, 0)

    def _printAllPathsUntil(self, u, d, visited, path, idx):
        visited[u] = True
        path[idx] = u
        idx += 1

        if u == d:
            self._print_rule_path(path, idx)
        else:
            for nxt in self.adj[u]:
                if not visited[nxt]:
                    self._printAllPathsUntil(nxt, d, visited, path, idx)

        visited[u] = False

    def _print_rule_path(self, path, length):
        adding_and = 0

        for i in range(length):
            node = path[i]

            if i == 0:
                print(" If ", end="")
                continue

            # CONDITION NODE
            if node < config.nb_final_elem_conditions + 1:

                if adding_and == 0:
                    print(" (", end="")
                    adding_and = 1
                else:
                    print(" and (", end="")

                cond_index = int(config.final_conditions_list[node - 1][1])
               # attr_id = int(config.conditions_list[cond_index][1])

                # attribute name
               # print(config.attributes_list[attr_id - 1][1], end="")

                # Attribute code from conditions_list (e.g., "A3")
                attr_code = config.conditions_list[cond_index][1]

                # Find matching attribute in attributes_list
                attr_name = None
                for attr in config.attributes_list:
                    if attr[0] == attr_code:  # attr[0] = "A3"
                        attr_name = attr[2]  # attr[2] = "Current_Condition"
                        break

                if attr_name is None:
                    attr_name = attr_code  # fallback

                print(attr_name, end="")


                # operator
                op = config.conditions_list[cond_index][2]
                print(get_operator_by_code_ascii(op), end="")

                # RHS
                rhs = config.conditions_list[cond_index][3]
                print(rhs, end="")

                print(")", end="")

            # DECISION NODE
            else:
                dec_index = node - config.nb_final_elem_conditions - 1
                print(" then ", end="")
                print(config.decisions_list[dec_index][1], end=" ")
                print(config.decisions_list[dec_index][2], end="")

        print()
