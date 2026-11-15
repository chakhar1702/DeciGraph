# DeciGraph User Manual

Version for the code in the `chakhar1702/DeciGraph` repository.
Companion paper: Chakhar S., Panaro S., Greco S., Ishizaka A., Siraj S. (2027), *A novel decision graph model to visualise dominance based if-then decision rules*, Omega 146, 103687.

## Contents

1. [Introduction](#1-introduction)
2. [Background](#2-background)
3. [Installation](#3-installation)
4. [Input files](#4-input-files)
5. [Running the tool](#5-running-the-tool)
6. [Transformation strategies](#6-transformation-strategies)
7. [Reading the output](#7-reading-the-output)
8. [Drawing the graph with Graphviz](#8-drawing-the-graph-with-graphviz)
9. [Classifying objects and aggregating decisions](#9-classifying-objects-and-aggregating-decisions)
10. [Worked example](#10-worked-example)
11. [Troubleshooting](#11-troubleshooting)
12. [Code reference](#13-code-reference)
13. [Citation and contact](#14-citation-and-contact)

---

## 1. Introduction

DeciGraph helps decision makers read large sets of DRSA (Dominance-based Rough Set Approach) if-then rules. It converts the rules into a **decision graph**:

- **Nodes** are elementary conditions (for example `Costs_of_Intervention >= 500000`) or decisions (for example `at_most_Low`).
- **Edges** link a root to a first condition, a condition to the next condition in a rule, and the last condition to the decision.
- **Each path** from the root to a decision node is one decision rule.

The tool does four things:

1. Builds the graph from the rules.
2. Prints Graphviz code so the graph can be drawn.
3. **Linearises** the graph, listing every rule it contains, so you can check it against your input.
4. **Classifies** new objects by walking the graph and aggregating the rules they satisfy.

## 2. Background

In DRSA, a decision table has objects described by preference-ordered condition attributes and an ordered set of decision classes `Cl1 < Cl2 < ... < Clk`. Rules are induced for **unions of classes**:

- *at least* rules: `... then x belongs to Cl_t or better`
- *at most* rules: `... then x belongs to Cl_t or worse`

A rule has the form `C1 & C2 & ... & Cn -> K`, where each `Cj` is an elementary condition such as `attribute >= value`.

**Why a transformation is needed.** If two rules share a condition and you draw it as one node, the graph may contain paths that mix parts of different rules. These paths are *nonexistent rules*. For example, from `R1: C1 & C3 -> K1` and `R3: C3 & C4 -> K2`, a single shared `C3` node would also create `C3 -> K1` and `C1 & C3 & C4 -> K2`. To avoid this, the rules are first written as a binary matrix (rows are rules, columns are conditions and decisions) and then transformed, by splitting shared conditions into several nodes and/or ordering the columns.

## 3. Installation

1. Install Python 3.
2. Download or clone the repository:
   ```bash
   git clone https://github.com/chakhar1702/DeciGraph.git
   cd DeciGraph
   ```
3. (Recommended) Install Graphviz from https://graphviz.org/download/ and check that `dot -V` works in your terminal.

The code files reviewed for this manual use only the Python standard library, so no `pip install` is needed.

## 4. Input files

All input files live in the `data/` folder next to the scripts. The folder is found relative to the scripts, so you can run the tool from any directory.

### 4.1 `list_of_rules.txt`: the rules

One rule per line, exactly as exported by 4eMka2: conditions in parentheses joined by `&`, then `=>`, then the decision in parentheses. Example (from the Salerno case study):

```
Rule 1. (A1_Date_of_Construction>=18) & (A8_Economic_Self_Sustainability<=No) & (A4_Costs_of_Intervention>=500000.000000) => (Overall_Satisfaction at most Low);   [2, 100.00%]
Rule 2. (A8_Economic_Self_Sustainability<=No) & (A3_Current_Condition>=Partially_restored) => (Overall_Satisfaction at most Moderate);   [4, 80.00%]
Rule 8. (A8_Economic_Self_Sustainability>=Yes) => (Overall_Satisfaction at least High);   [9, 81.82%]
```

The `Rule N.` prefix and the `[support, strength]` text after the semicolon are ignored by the parser, so you can paste the 4eMka2 output without editing it.

Rules for the parser:

- Conditions use `<=`, `>=` or `=` **written without spaces** around the operator. 4eMka2 exports these as plain ASCII characters, also for ordinal attributes (for example `A3_Current_Condition>=Partially_restored`). The symbols `⪰` and `⪯` in the paper are only typesetting and are not accepted by the parser.
- Numeric values may carry decimals (`500000.000000`). Ordinal values are written as labels (`Partially_restored`, `Yes`, `No`) with underscores instead of spaces.
- Class labels in the decision part use underscores too, for example `Very_High`, and must be written the same way in `decision_classes.txt`.
- The decision has the form `(Attribute at most Label)` or `(Attribute at least Label)`.
- Everything after the first `;` on a line is ignored (for example a strength value).
- Lines without `=>` are skipped silently.
- Attribute names must **exactly** match a name in `attrs_list.txt`, including prefixes such as `A1_`.
- Every rule must have a decision, or the tool stops with an error.

A jMAF-style format (`Attr >= value` with spaces, and `(Attr >= Label)` as the decision) is implemented in `read_data.py`. To use it, change `read_data_for_graph("4emka2")` to `read_data_for_graph("jmaf")` in `deciGraph_main.py`.

### 4.2 `attrs_list.txt`: the attributes

One attribute per line with three whitespace-separated fields: the attribute **id**, the **preference** and the attribute **name**. Example (Salerno case study):

```
1  -1  A1_Date_of_Construction
2   1  A2_Area_Covered
3  -1  A3_Current_Condition
4  -1  A4_Costs_of_Intervention
5   1  A8_Economic_Self_Sustainability
```

- **Id:** use 1, 2, 3, ... in file order. The classification code finds attributes by position (`id - 1`), and objects in `unseen_data.txt` are matched to ids by column position. A number inside the name (such as the `8` in `A8_...`) is only part of the name and need not equal the id.
- **Preference:** `1` for a gain criterion (higher is better) and `-1` for a cost criterion (lower is better). The tool reads this column but does not use it in the graph construction or classification. The direction of each condition comes from the operator written in the rules.
- **Name:** must match the attribute names in `list_of_rules.txt` exactly, including the `A1_` style prefix. Trailing spaces in the file are ignored.

### 4.3 `decision_classes.txt`: the class order

One class per line: an order number and a label, from the worst class (1) to the best. Example (Salerno case study):

```
1  Low
2  Moderate
3  High
4  Very_High
```

The labels must be spelled exactly as in the decision part of the rules, including the underscore in `Very_High`, because the rule text `(Overall_Satisfaction at least Very_High)` is matched against this file. The order numbers define the class order used for aggregation and for the admissible interval, and the file must list every class, even classes that no rule mentions.

### 4.4 `unseen_data.txt`: the objects to classify

One object per line, values separated by spaces (commas are also accepted). There is no header line and no project name. The values follow the attribute ids in `attrs_list.txt`: column 1 is attribute 1, column 2 is attribute 2, and so on. For the Salerno data the order is date of construction, area covered, current condition, costs of intervention, economic self-sustainability.

Example: the four new projects of the case study (Table 14 of the paper). Extra spaces between values are fine:

```
9  4500  To_be_restored  9900000.00  Yes
13  8500  To_be_restored  18700000.00  Yes
16  3900  To_be_restored  8580000.00  Yes
14  2500  To_be_restored  5500000.00  Yes
```

Notes:

- Numbers use a decimal point (`42335.30`). Ordinal values are the same labels as in the rules (`Restored`, `Partially_restored`, `Restoration_on_going`, `To_be_restored`, `Yes`, `No`).
- A `?` means the value is missing. A missing value never satisfies a condition.
- You can add the known class as an extra last value to check the results, as in the learning set below. The classifier ignores this extra value, but it is printed with the object so you can compare it with the final decision.

```
15 3000 Restored 1550000.00 Yes Very_High
20 1000 Partially_restored 42335.30 Yes High
11 1465.31 Restoration_on_going ? Yes High
```

Reclassifying the learning set with this file is a good test. The paper reports a 100% match with the original classes (Table 13), and High for all four new projects (Table 15).

## 5. Running the tool

```bash
python deciGraph_main.py
```

To keep the output:

```bash
python deciGraph_main.py > output.txt
```

The settings are edited directly in the code:

| Setting | Where | Default |
|---|---|---|
| Rule format | `read_data_for_graph("4emka2")` in `deciGraph_main.py` | `4emka2` |
| Transformation strategy | `version = ...` in `deciGraph_main.py` | 2 |
| Aggregation operator | `aggregate_decisions(..., strategy="max")` in `deciGraph_main.py` | `max` (optimistic). Other options: `min` (pessimistic) and `median` |
| Node and edge labels | `label_on_nodes`, `label_on_edges` in `config.py` | 0 and 1 |
| Root label | `root_label` in `config.py` | `r` |

**Important:** the default `version = 2` (ordering only) can create nonexistent rules. Change it to 1 or 4 for real work (see section 6).

## 6. Transformation strategies

| `version` | Name | File | Result |
|---|---|---|---|
| 0 | None | | Use only if no condition appears in more than one rule. The tool also skips preprocessing automatically when this is the case. |
| 1 | Column splitting (duplication) | `column_duplication_vers.py` | Every condition that appears in several rules gets one node per occurrence. Always removes nonexistent rules. Largest graph. |
| 2 | Column ordering | `column_ordering_vers.py` | Orders conditions by how often they occur. Smaller graph, **but can create nonexistent rules.** |
| 3 | Mixed | `mixed_vers.py` | Orders columns and splits one fixed column (position 1). Built for the Salerno case study, **not general.** |
| 4 | Optimised mixed | `optimised_mixed_version.py` | Finds a maximum chain of conditions whose rule sets are nested (S_j is a subset of S_k), keeps these once and orders them, and splits all other conditions. Aims for a smaller graph than strategy 1. |

Recommendations:

- Start with **strategy 1**. It is the safest.
- Try **strategy 4** if the graph is too large.
- Always run the linearisation (section 7.5) and compare the listed rules with your input. If extra rules appear, switch to strategy 1.
- Strategy 4 also writes `poset.dot` to the working directory. It shows the inclusion relations between conditions and can be drawn with Graphviz.

## 7. Reading the output

The tool prints the following blocks in order.

1. **Parsed input summary.** Attributes, decision unions, rules and unique elementary conditions. Check this first to confirm your files were read correctly.
2. **Initial binary matrix.** Rows are rules. Columns are the unique conditions followed by the decision unions. A `1` means the condition is in the rule, or the rule leads to that decision.
3. **Strategy banner and final binary matrix.** The matrix after transformation, with the number of split or reordered condition columns. A `|` separates conditions from decisions.
4. **Graphviz code.** A block starting with `digraph preferenceGraph{`. See section 8.
5. **Linearisation.** For each decision node, every rule found in the graph, written as `If (Attr op value) and (...) then decision`.
6. **Batch exploitation.** For each unseen object: its values, the rules it satisfies, the decisions extracted, the admissible interval and the final aggregated decision.
7. **Summary table.** Object number and final decision.

### 7.5 Validating the graph

The linearised rules should be the same as the input rules. Conditions may appear in a different order within a rule, and rules may appear in a different order, because all conditions are combined with "and". Any rule in the linearised list that is not in your input is a nonexistent rule.

## 8. Drawing the graph with Graphviz

The tool prints DOT code to the console and does not save an image. To draw it:

1. Run `python deciGraph_main.py > output.txt`.
2. Copy everything from `digraph preferenceGraph{` to the closing `}` into a new file called `graph.dot`.
3. Render it:
   ```bash
   dot -Tpng graph.dot -o graph.png
   dot -Tsvg graph.dot -o graph.svg
   ```

The root is node `0`. Condition nodes are numbered `1..N`, followed by the decision nodes. Edges from the root are drawn in green.

## 9. Classifying objects and aggregating decisions

For each object in `unseen_data.txt`, the tool starts at the root and follows an edge into a condition node only if the object satisfies that condition. Each decision node it reaches is a rule the object satisfies. The result is the set of decisions suggested by those rules.

Missing values (`?` or empty) never satisfy a condition.

### Aggregation

Decisions are written as `at_most_<Label>` or `at_least_<Label>`. The label must match a label in `decision_classes.txt` exactly (case-sensitive), and its position in that file gives the class index (1 is the worst class).

- **Only *at most* rules cover the object.** The final class is the lowest class among them.
- **Only *at least* rules cover the object.** The final class is the highest class among them.
- **Both types cover the object.** The tool computes an admissible interval `[l(x), u(x)]`:
  - `l(x)` is the lowest class given by the *at least* rules (or the first class if there are none).
  - `u(x)` is the highest class given by the *at most* rules (or the last class if there are none).

  If `l(x) = u(x)`, that class is the answer. Otherwise the aggregation operator chooses one class from the interval:

  | `strategy` | Choice | Meaning |
  |---|---|---|
  | `"max"` (default) | `u(x)` | Optimistic, as in DOMLEM. Suits cases where underestimating an object is the costlier mistake. |
  | `"min"` | `l(x)` | Pessimistic. Suits risk-sensitive cases. |
  | `"median"` | `(l(x) + u(x)) // 2` | The midpoint of the interval, rounded down. For an interval of two adjacent classes this equals the lower class. |

  Any other value for `strategy` raises an error. The strategy only matters when the interval contains more than one class.
- **No rule covers the object.** The tool prints `No rules satisfied`, the interval from the first to the last class, and `Final decision: None`. This differs slightly from the paper, which assigns the object to all classes.

## 10. Worked example

A small illustrative rule set (not from the paper's data):

```
(C1) & (C3) => K1
(C2) => K1
(C3) & (C4) => K2
(C5) => K2
```

`C3` appears in two rules.

- With **no preprocessing** (version 0), the single `C3` node creates two nonexistent rules: `If C3 then K1` and `If C1 and C3 and C4 then K2`.
- With **column splitting** (version 1), `C3` becomes two nodes (`C3` and `C3'`), the graph has one more edge, and the linearisation returns exactly the four original rules.

To reproduce this in the tool, write the rules in `list_of_rules.txt` using real attribute names and operators, list the attributes in `attrs_list.txt` and the classes in `decision_classes.txt`, set `version = 1`, and run the script. Compare the linearisation block with your input.

### The Salerno rules

The paper's Salerno case study (Section 6) uses 12 rules from 4eMka2 (the full list is in Table 6 of the paper). Reading them gives:

- 17 unique elementary conditions and 6 decision unions (`at_most_Low`, `at_most_Moderate`, `at_most_High`, `at_least_Moderate`, `at_least_High`, `at_least_Very_High`), so the initial binary matrix has 12 rows and 23 columns.
- Two conditions shared by several rules: `A1_Date_of_Construction>=18` (rules 1 and 5) and `A8_Economic_Self_Sustainability<=No` (rules 1 and 2).

Expected result with `version = 1` (column splitting): the two shared conditions are split, giving 19 condition nodes, 6 decision nodes and the root, so **26 nodes and 31 edges**, as reported in the paper. You can use this as a quick check that your installation works. The linearisation block should list the same 12 rules as the input.

The paper reports 25 nodes and 30 edges for the mixed strategy (splitting only the `A8_Economic_Self_Sustainability` condition). Strategy 3 in the code splits a fixed column position, so it may not reproduce that figure.

By my reading of the code, `version = 2` (ordering only, the current default) leaves these two shared conditions as single nodes and creates paths that are not rules, such as a path from `A1_Date_of_Construction>=18` through `A4_Costs_of_Intervention>=500000` to `at_most_Low`. Check the linearisation output to see this for yourself.

## 11. Troubleshooting

| Message or symptom | Likely cause and fix |
|---|---|
| `KeyError: Attribute 'X' not found in attrs_list.txt` | The attribute name in a rule does not match `attrs_list.txt`. Names must match exactly, including prefixes. |
| `ValueError: Cannot parse 4emka2 condition` | A condition does not look like `Attr<=value`, `Attr>=value` or `Attr=value`. Remove spaces around the operator and replace `⪰`/`⪯`. |
| `ValueError: Rule N has NO decision class` | The part after `=>` is missing or not in the `(Attr at most/least Label)` form. |
| `FileNotFoundError` for a `data/` file | A required file is missing, or `data/` is not next to the scripts. |
| No rules found, empty matrix | Lines do not contain `=>`, so they were skipped. |
| Extra rules in the linearisation | Nonexistent rules. Use strategy 1 (or 4). |
| An object is classified wrongly for an ordinal attribute | See section 12, item 2. |
| `RecursionError` on very large graphs | The traversal is recursive. Raise the limit with `sys.setrecursionlimit`. |

## 12. Code reference

| File | Role | Paper |
|---|---|---|
| `deciGraph_main.py` | Runs the pipeline: read, transform, build graph, print DOT, linearise, classify, aggregate | Fig. 4 |
| `config.py` | Global state and display settings | |
| `read_data.py` | Parses the four input files and builds the initial binary matrix (`read_data_for_graph`, `load_unseen_objects`) | Section 4.1 |
| `column_duplication_vers.py` | `column_duplication_vers` | Algorithm 1 |
| `column_ordering_vers.py` | `column_ordering_vers`, `get_ordered_cols` | Eq. (14) |
| `mixed_vers.py` | `mixed_vers` | Section 6.3.1 |
| `optimised_mixed_version.py` | `optimised_mixed_version` (co-occurrence sets, maximum chain, splitting) | Section 4.3 |
| `main` (graph building) | Root-to-condition and condition-to-condition edges | Algorithm 3 |
| `printAllRulesasPaths.py` | `GraphPaths.printAllPaths` | Algorithm 4 (BFSL) |
| `exploitation.py` | `ExploitationGraph.classify`, `path_to_rule`, `eval_condition` | Algorithm 5 (BFSE) |
| `aggregate_decision.py` | `parse_decision`, `compute_interval`, `aggregate_decisions` | Algorithm 6 |
| `print_on_screen_routines.py` | Matrix printing, Graphviz code, poset export | |
| `utils.py` | Edge helpers and the parsed input summary | |
| `distance_funcs.py` | Experimental pairwise condition distances | |
| `bfs_algorithm.py` | Legacy draft of a breadth-first path search. Imported by `deciGraph_main.py` but never used, and `BFSAllPaths` does not run as written | Algorithms 4 and 5 (draft) |

### Using the pieces as a library

The functions rely on shared state in `config`. Before calling a strategy function, call `read_data_for_graph(...)` and set `config.nb_elem_conditions` and `config.nb_decisions`, as `main()` does. The strategy functions then set `config.nb_final_elem_conditions` and `config.final_conditions_list`.

## 12. Citation and contact

Please cite:

> Chakhar S., Panaro S., Greco S., Ishizaka A., Siraj S. (2027). A novel decision graph model to visualise dominance based if-then decision rules. *Omega* 146, 103687. https://doi.org/10.1016/j.omega.2026.103687

Contact: Dr Salem Chakhar, University of Portsmouth, salem.chakhar [at] port.ac.uk

The case study was part of the Horizon 2020 project CLIC (grant agreement No. 776758).
