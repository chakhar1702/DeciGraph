# config.py
# ============================
# Global variables (mirroring C++ globals)
# ============================

# Filled by read_data_for_graph()
attributes_list = []
conditions_list = []
decisions_list = []
elementary_conditions = []
decision_conditions = []
rules_list = []

# Global counters
nb_elem_conditions = 0
nb_decisions = 0
nb_attributes = 0
nb_final_elem_conditions = 0

order_class_map = {}

# Final duplicated conditions list
final_conditions_list = []

# Graph structures
edges = []
obj_descrip = []

node_id = []
node_data_id = []

node_label = []
edge_label = []

# Matrices
initial_binary_matrix = []
final_binary_matrix = []
distance_binary_matrix = []

# Graphviz settings
root_label = "r"
deci_node_shape = "box"

# Display settings
# 0: only attribute name
# 1: attribute name + operator + rhs
label_on_nodes = 0

# 0: nothing
# 1: operator + rhs
label_on_edges = 1
