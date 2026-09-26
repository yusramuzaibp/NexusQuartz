def check_ranges(values, specs):
    """specs: list of (label, min, max) matched by position to `values`.
    Returns a list of human-readable warning strings for anything
    outside a plausible range (catches typos like BMI=250 or an
    extra/missing zero, without needing a real clinical bound check).
    """
    problems = []
    for val, (label, lo, hi) in zip(values, specs):
        if not (lo <= val <= hi):
            problems.append(
                f"- **{label}** = {val} looks out of the expected range "
                f"({lo}–{hi}). Please double-check this value."
            )
    return problems
