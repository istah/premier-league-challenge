"""Late-match fatigue, shared by the live engine and the demo tracker.

The original formula (tracking.py, engine.py) had no upper bound: at low HRV or high pressing it returned more than 1, which turned
distance, strength and chance negative. The only change here is the cap: below F_MAX every value is identical to the original.
F_MAX = 0.5 keeps every pre-cap value for HRV ratios down to 0.84 at 90' under neutral instructions and keeps output at 50% or more.
"""
ONSET = 55  # minutes of play before fatigue starts
RAMP = 35  # minutes until the full effect, at neutral instructions
GAIN = 3  # effect per unit of HRV ratio below 1
THRESHOLD = 0.9  # ratios at or above this do not fade at all (a step of GAIN * 0.1 = 0.3 at the threshold, kept from the original)
F_MAX = 0.5  # largest share of output a player can lose


def fade(played: float, r: float) -> float:
    """Share of output lost, 0..F_MAX. `played` is effective minutes on the pitch, `r` the readiness ratio (HRV or wellness, 1 = baseline)."""
    if r >= THRESHOLD:
        return 0.0
    return min(F_MAX, max(0, played - ONSET) / RAMP * max(0, 1 - r) * GAIN)
