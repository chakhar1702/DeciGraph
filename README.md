# DeciGraph
DeciGraph is a novel decision graph model for visualising dominance based if-then decision rules. The construction of a decision graph  begins with a preprocessing phase to extract a binary decision matrix from the descriptions of decision rules. To prevent the creation of nonexistent rules, the generated binary decision matrix may require some transformation using either column duplication, column ordering, or a combination of both strategies. The transformed  binary decision matrix is then used to construct a directed acyclic decision graph, where nodes represent elementary conditions and decisions, and edges denote relationships between conditions and decisions. Each path from the root to a decision node in this graph corresponds to a decision rule. This tool offers a collection of algorithms for the construction, linearisation, and exploitation of decision graphs. 

## Why use it

Large DRSA rule sets are hard to read as text or tables. A decision graph shares conditions between rules, so the whole rule set can be read at a glance. Experts in the paper's cultural-heritage case study found the graphs easier to interpret.

## Features

- Reads DRSA rules exported from jMAF-style rules (4eMka2-style rules are also supported in the parser).
- Builds the binary decision matrix and transforms it so the graph contains no nonexistent rules. Four strategies are available (see below).
- Prints Graphviz (DOT) code for the decision graph.
- Linearises the graph back into if-then rules, which is useful for validation.
- Classifies unseen objects and aggregates the matching rules into one final class (optimistic `max` by default, with `min` and `median` also available).

## Requirements

- Python 3 (with the standard library).
- [Graphviz](https://graphviz.org/download/) to render the DOT output into images (optional but recommended).

## Quick start

```bash
git clone https://github.com/chakhar1702/DeciGraph.git
cd DeciGraph
python deciGraph_main.py
```

The script reads its inputs from the `data/` folder (see the [User Manual](USER_MANUAL.md#4-input-files)). To save the output and render the graph:

```bash
python deciGraph_main.py > output.txt
# copy the "digraph preferenceGraph{ ... }" block from output.txt into graph.dot, then:
dot -Tpng graph.dot -o graph.png
```

## Choosing a transformation strategy

Edit the line `version = ...` in `deciGraph_main.py`:

```bash
| `version` | Strategy | Avoids nonexistent rules? |
|---|---|---|
| 0 | No preprocessing | Only if no condition is shared between rules |
| 1 | Column splitting | Yes, but gives the largest graph |
| 2 | Column ordering only | No, can create nonexistent rules |
| 3 | Mixed (case-study version) | Not guaranteed, hardcoded for one dataset |
| 4 | Optimised mixed (maximum chain + splitting) | Intended, gives smaller graphs |

Use 1 when correctness matters most and 4 for smaller graphs. In either case, check the linearised rules against your input rules. Avoid 2 and 3 for new data.

## Input files (`data/`)

| File | Content |
|---|---|
| `list_of_rules.txt` | 4eMka2 rules, one per line, e.g. `Rule 8. (A8_Economic_Self_Sustainability>=Yes) => (Overall_Satisfaction at least High);   [9, 81.82%]` |
| `attrs_list.txt` | Attribute id, preference and name |
| `decision_classes.txt` | Class order and label, e.g. `1 Low` |
| `unseen_data.txt` | Objects to classify, one per line |
```
Details and examples are in the [User Manual](USER_MANUAL.md).

## Repository structure
```bash
deciGraph_main.py            Entry point: runs the whole pipeline
config.py                    Shared state and display settings
read_data.py                 Reads rules, attributes, classes, unseen objects
column_duplication_vers.py   Strategy 1: column splitting
column_ordering_vers.py      Strategy 2: column ordering
mixed_vers.py                Strategy 3: mixed (case-study version)
optimised_mixed_version.py   Strategy 4: maximum chain + splitting
printAllRulesasPaths.py      Linearisation (graph -> rules)
exploitation.py              Classification of objects
aggregate_decision.py        Aggregation of decisions
print_on_screen_routines.py  Console output and Graphviz code
utils.py                     Edge helpers and input summary
distance_funcs.py            Experimental co-occurrence distances (not used by main)
bfs_algorithm.py             Legacy breadth-first draft (not used, does not run)
data/                        Input files
```


## Contact

Dr Salem Chakhar, University of Portsmouth: salem.chakhar@port.ac.uk
