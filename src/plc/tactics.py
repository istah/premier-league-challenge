"""Tactical read: how a formation fits the opponent's style, and what each line should do.

Deterministic rules over the opponent's press / aerial / set-piece profile; the agents explain this, they don't invent it.
The weights are a modelling assumption for the demo, not fitted to real data.
"""
from dataclasses import dataclass

from .fixtures import Opponent

FORMATIONS = {"4-3-3": (4, 3, 3), "4-4-2": (4, 4, 2), "3-5-2": (3, 5, 2), "3-4-3": (3, 4, 3), "5-3-2": (5, 3, 2)}  # DEF, MID, FWD
HIGH = 0.65
LOW = 0.4


@dataclass
class Assessment:
    formation: str
    fit: float  # about -0.2..+0.2; the engine turns it into a chance multiplier
    verdict: str
    reasons: list[str]
    movements: dict[str, str]


def _fit(formation: str, o: Opponent) -> tuple[float, list[str]]:
    d, m, f = FORMATIONS[formation]
    fit, why = 0.0, []
    if o.press >= HIGH:
        fit += 0.06 * (m - 3)
        why.append(f"{o.name} press hard ({o.press:.0%}): {m} midfielders give passing triangles to play through" if m > 3
                   else f"{o.name} press hard ({o.press:.0%}): only {m} midfielders, expect to be pressed into long balls")
    elif o.press <= LOW:
        fit += 0.05 * (f - 3)
        why.append(f"{o.name} press little ({o.press:.0%}): safe to commit {f} forwards")
    threat = (o.aerial + o.set_piece_threat) / 2
    if threat >= HIGH:
        fit += 0.07 * (d - 4)
        why.append(f"{o.name} are dangerous in the air and on set pieces ({threat:.0%}): {d} defenders {'help' if d > 4 else 'leave us thin'}")
    if not why:
        why.append(f"{o.name} show no extreme tendency; shape matters little")
    return round(fit, 3), why


def why_switch(current: str, new: str, o: Opponent) -> list[str]:
    """Why `new` fits this opponent better than `current`: one reason per fit term that improves, with the same numbers as _fit."""
    dc, mc, fc = FORMATIONS[current]
    dn, mn, fn = FORMATIONS[new]
    out = []
    if o.press >= HIGH and mn > mc:
        out.append(f"{mn} midfielders give passing triangles against their hard press ({o.press:.0%})")
    if o.press <= LOW and fn > fc:
        out.append(f"it is safe to commit {fn} forwards because they press little ({o.press:.0%})")
    threat = (o.aerial + o.set_piece_threat) / 2
    if threat >= HIGH and dn > dc:
        out.append(f"{dn} defenders help against their aerial and set-piece threat ({threat:.0%})")
    return out or ["it scores higher on tactical fit against their profile"]


def _movements(formation: str, o: Opponent) -> dict[str, str]:
    d, m, f = FORMATIONS[formation]
    high_press, threat = o.press >= HIGH, (o.aerial + o.set_piece_threat) / 2 >= HIGH
    return {
        "GK": "Short distribution to the centre-backs, long only when the press is bypassed" if high_press else "Quick restarts to the full-backs",
        "DEF": (f"Back {d}: " + ("wide centre-backs step into midfield when we have the ball" if d == 3 else "full-backs overlap only when a midfielder covers" if d == 4 else "wing-backs stay deep, centre-backs mark tight"))
               + ("; zonal marking on corners, no needless fouls near the box" if threat else ""),
        "MID": f"Midfield {m}: " + ("hold a triangle, one drops between the centre-backs to receive under pressure" if high_press else "push up to support the forwards, press their first pass"),
        "FWD": f"Attack {f}: " + ("run in behind when they press, the space is there" if high_press else "front line presses their centre-backs to force mistakes"),
    }


def assess(formation: str, o: Opponent) -> Assessment:
    fit, why = _fit(formation, o)
    best = max(_fit(f, o)[0] for f in FORMATIONS)
    verdict = "Best fit" if fit == best else "Good fit" if fit >= best - 0.05 else "Risky"
    return Assessment(formation, fit, verdict, why, _movements(formation, o))


def recommend(o: Opponent) -> str:
    return max(FORMATIONS, key=lambda f: _fit(f, o)[0])


def their_formation(o: Opponent) -> str:
    """Derived from the opponent's style traits (a modelling assumption), so the Opponent Analyst has a shape to talk about."""
    return "4-3-3" if o.press >= HIGH else "5-3-2" if o.aerial >= HIGH else "4-4-2" if o.press <= LOW else "3-5-2"
