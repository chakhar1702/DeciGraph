def parse_decision(dec_str, classes_list):
    """
    dec_str examples: 'at_most_low', 'at_least_high'
    Returns: (type, class_index) with class_index 1-based.
    """

    if dec_str.startswith("at_most_"):
        t = "at_most"
        label = dec_str[len("at_most_"):]
    elif dec_str.startswith("at_least_"):
        t = "at_least"
        label = dec_str[len("at_least_"):]
    else:
        raise ValueError(f"Unknown decision format: {dec_str}")

    try:
        idx = classes_list.index(label) + 1
    except ValueError:
        raise ValueError(f"Unknown class label '{label}' in decision '{dec_str}'")

    return t, idx


def compute_interval(decisions, classes_list):
    """
    DRSA semantics:

    l(x) = min cl(ρ) over at_least rules that cover x, else Cl1
    u(x) = max cl(ρ) over at_most rules that cover x, else Cl_{|Ω|}
    """

    n = len(classes_list)

    lower_candidates = []   # from at_least
    upper_candidates = []   # from at_most

    for dec in decisions:
        t, idx = parse_decision(dec, classes_list)

        if t == "at_least":
            lower_candidates.append(idx)
        elif t == "at_most":
            upper_candidates.append(idx)

    # l(x)
    lx = min(lower_candidates) if lower_candidates else 1

    # u(x)
    ux = max(upper_candidates) if upper_candidates else n

    return lx, ux


def aggregate_decisions(decisions, classes_list, strategy="max"):
    """
    DRSA exploitation logic:

    1. If only at_most rules → pick lowest class
    2. If only at_least rules → pick highest class
    3. If both → use interval + aggregation strategy
    """

    at_least = []
    at_most = []

    # Separate decisions
    for dec in decisions:
        t, idx = parse_decision(dec, classes_list)
        if t == "at_least":
            at_least.append(idx)
        else:
            at_most.append(idx)

    # ------------------------------------------------------------
    # CASE 1: Only at_most rules → pick the lowest class
    # ------------------------------------------------------------
    if at_most and not at_least:
        final_idx = min(at_most)
        return classes_list[final_idx - 1]

    # ------------------------------------------------------------
    # CASE 2: Only at_least rules → pick the highest class
    # ------------------------------------------------------------
    if at_least and not at_most:
        final_idx = max(at_least)
        return classes_list[final_idx - 1]

    # ------------------------------------------------------------
    # CASE 3: Both types → interval + aggregation
    # ------------------------------------------------------------
    lx, ux = compute_interval(decisions, classes_list)

    if lx == ux:
        final_idx = lx
    else:
        if strategy == "min":
            final_idx = lx
        elif strategy == "max":
            final_idx = ux
        elif strategy == "median":
            final_idx = (lx + ux) // 2
        else:
            raise ValueError(f"Unknown aggregation strategy: {strategy}")

    return classes_list[final_idx - 1]
