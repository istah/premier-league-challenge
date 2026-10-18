"""Fast yes/no scoring. Heuristic backend for now; swap `p_substitute` for a Microsoft-Decision-1 call in Foundry."""


def p_substitute(drop_pct: float, hr_over_pct: float, hrv_ratio: float) -> float:
    """Probability a substitution is warranted, 0-1, from output drop, heart-rate elevation and morning HRV."""
    z = 6 * drop_pct + 3 * hr_over_pct + 2 * max(0, 0.9 - hrv_ratio) - 0.9
    return round(max(0.0, min(1.0, 0.5 + z)), 2)
