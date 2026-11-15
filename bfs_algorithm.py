# bfs_algorithm.py

from collections import deque

from config import (
    decisions_list,
    node_data_id,
    node_id,
    nb_final_elem_conditions,
    final_conditions_list,
    conditions_list,
    obj_descrip
)


class Graph:
    def __init__(self, V):
        self.V = V
        self.graph = [[] for _ in range(V)]   # adjacency list

    def addEdge(self, u, v):
        self.graph[u].append(v)

    def printAllPaths(self, s, d):
        visited = [False] * self.V
        path = []
        self._printAllPathsUtil(s, d, visited, path)

    def _printAllPathsUtil(self, u, d, visited, path):
        visited[u] = True
        path.append(u)

        if u == d:
            print(" -> ".join(str(x) for x in path))
        else:
            for v in self.graph[u]:
                if not visited[v]:
                    self._printAllPathsUtil(v, d, visited, path)

        path.pop()
        visited[u] = False

    def printPath(self, path):
        """Print a path (list of node indices)."""
        print(" ".join(str(n) for n in path))

    def BFSAllPaths(self, source, destination):
        """
        Enumerate all paths from source to destination using BFS.
        Replicates the C++ logic exactly.
        """

        q = deque()
        q.append([source])

        while q:
            path = q.popleft()
            node = path[-1]

            # ------------------------------------------------------------
            # Destination reached → print path + decision class
            # ------------------------------------------------------------
            if node == destination:
                self.printPath(path)

                # C++:
                # cl(x)= decisions_list[node_data_id[node]-1][1] decisions_list[node_data_id[node]-1][2]
                dec = decisions_list[node_data_id[node] - 1]
                print(f" ->cl(x)= {dec[1]} {dec[2]}")
                continue

            # ------------------------------------------------------------
            # Explore neighbors
            # ------------------------------------------------------------
            for adjNode in self.adj[node]:

                # Debug output (optional)
                print(f"\n-adjNode: {adjNode} u{node_id[adjNode - 1]}", end="")

                if node_id[adjNode - 1] == 0:
                    print("...root", end="")
                elif 0 < node_id[adjNode - 1] < nb_final_elem_conditions:
                    print("...condition", end="")
                else:
                    print("...decision", end="")

                # --------------------------------------------------------
                # Case 1: root or decision node → always allowed
                # --------------------------------------------------------
                if node_id[adjNode - 1] == 0 or node_id[adjNode - 1] >= nb_final_elem_conditions:
                    newPath = path + [adjNode]
                    q.append(newPath)
                    continue

                # --------------------------------------------------------
                # Case 2: condition node → evaluate condition
                # --------------------------------------------------------
                elmc_id = int(final_conditions_list[node_id[adjNode - 1] - 1][0])
                elmc_attr = int(final_conditions_list[node_id[adjNode - 1] - 1][1])
                attr_id = elmc_attr

                elmc_opr = conditions_list[attr_id][2]
                elmc_rhs = float(conditions_list[attr_id][3])

                print(f" >>elmc_id: {elmc_id}", end="")
                print(f" >>elmc_attr: {elmc_attr}", end="")
                print(f" >>elmc_ope: {elmc_opr}", end="")
                print(f" >>elmc_rhs: {elmc_rhs}")

                # --------------------------------------------------------
                # Evaluate condition: obj_descrip[attr_id] >= rhs
                # --------------------------------------------------------
                if obj_descrip[attr_id] >= elmc_rhs:
                    newPath = path + [adjNode]
                    q.append(newPath)
