"""Play-style classifier: turns recent team shapes into labels with the numbers behind them. Pure code, no LLM."""
from dataclasses import dataclass
from statistics import mean

from .engine import Shape


@dataclass
class Style:
    label: str
    evidence: str


def _avg(shapes: list[Shape]) -> dict[str, float]:
    return {k: round(mean(getattr(s, k) for s in shapes), 1) for k in Shape.__dataclass_fields__}


def block(line: float) -> str:
    return "high block" if line >= 45 else "low block" if line <= 33 else "mid block"


def classify(shapes: list[Shape]) -> list[Style]:
    a, out = _avg(shapes), []
    out.append(Style(block(a["def_line"]), f"back line averages {a['def_line']} (0 own goal, 100 theirs)"))
    if a["ppda"] <= 8:
        out.append(Style("high press", f"opponents get only {a['ppda']} passes per defensive action"))
    elif a["ppda"] >= 13:
        out.append(Style("passive press", f"opponents get {a['ppda']} passes per defensive action"))
    if a["possession"] >= 54 and a["fwd_pct"] < 40:
        out.append(Style("midfield dominance", f"{a['possession']}% possession with patient build-up ({a['fwd_pct']}% forward passes)"))
    if a["lateral_pct"] >= 33:
        out.append(Style("lateral play", f"{a['lateral_pct']}% of passes go sideways"))
    if a["fwd_pct"] >= 45:
        out.append(Style("direct play", f"{a['fwd_pct']}% of passes go forward"))
    if a["def_line"] <= 36 and a["fwd_pct"] >= 44:
        out.append(Style("counter-attacking", f"deep block ({a['def_line']}) with {a['fwd_pct']}% forward passes and {a['possession']}% possession"))
    if a["cross_pct"] >= 60:
        out.append(Style("cross-heavy", f"{a['cross_pct']}% of box entries are crosses"))
    elif a["cross_pct"] <= 35:
        out.append(Style("inside combinations", f"only {a['cross_pct']}% of box entries are crosses; the rest cutbacks and inside passes"))
    if a["box_players"] >= 3.5:
        out.append(Style("crowds the box", f"{a['box_players']} players in the box when chances are created"))
    if a["wide_pct"] >= 50:
        out.append(Style("wing play", f"{a['wide_pct']}% of attacks use the wide channels"))
    return out


def shifts(history: list[dict[str, Shape]], side: str) -> list[str]:
    """Compare the first 40 minutes with the last 20 and report a change of block."""
    early, late = [h[side] for h in history[:8]], [h[side] for h in history[-4:]]
    if len(history) < 12:
        return []
    b0, b1 = block(_avg(early)["def_line"]), block(_avg(late)["def_line"])
    return [f"moved from a {b0} to a {b1}"] if b0 != b1 else []
