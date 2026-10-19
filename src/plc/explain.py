"""Plain-language meaning of each instruction slider, with the numbers it currently produces (same formulas as engine.py)."""

DOES = {
    "press": "How early and hard we hunt the ball. Higher: we win it further up the pitch (shaded zone) and allow fewer passes per defensive action, but players tire sooner.",
    "line": "How high our back line stands. Higher: squeezes their space and keeps play near their goal, but a ball over the top finds space behind.",
    "width": "How far apart our players stand. Wider: stretches their block and frees overlapping runs. Narrower: compact centre, harder to play through.",
    "tempo": "How fast we play and move. Higher: more chances, more energy spent.",
    "direct": "How quickly we go forward after winning the ball. Higher: one or two passes to the final third, best when we let them have the ball (counter-attack). Lower: patient circulation.",
    "cross": "How we enter the box. Higher: crosses from wide areas (more shots, lower quality, needs aerial forwards). Lower: cutbacks and inside passes through the half-spaces (fewer, better shots).",
    "box": "How many players we commit into the box: near post, penalty spot, far post, edge. More targets, but fewer players back against the counter.",
}


def _pct(v: float) -> str:
    return f"{v:+.0f}%"


def explain(i: dict) -> dict[str, dict[str, str]]:
    cost = max(0.5, 1 + 0.008 * (i["press"] - 50) + 0.006 * (i["tempo"] - 50))
    now = {
        "press": f"Press zone starts at {25 + i['press'] * 0.5:.0f}% of the pitch. Passes allowed per defensive action about {12 - (i['press'] - 50) * 0.1:.1f}. "
                 f"Our chances {_pct(0.4 * (i['press'] - 50))}, theirs {_pct(-0.3 * (i['press'] - 50))}. Tired players fade from about minute {55 / cost:.0f}.",
        "line": f"Back line about {38 + (i['line'] - 50) / 2:.0f}% up the pitch. Our chances {_pct(0.2 * (i['line'] - 50))}, theirs {_pct(0.4 * (i['line'] - 50))}.",
        "width": f"About {35 + (i['width'] - 50) * 0.3:.0f}% of our attacks use the wide channels.",
        "tempo": f"Our chances {_pct(0.3 * (i['tempo'] - 50))}. Tired players fade from about minute {55 / cost:.0f}.",
        "direct": f"About {40 + (i['direct'] - 50) * 0.25:.0f}% of passes go forward. " + ("Counter-attack bonus when we have under half the ball." if i["direct"] > 50 else "No counter-attack bonus."),
        "cross": f"About {50 + (i['cross'] - 50) * 0.8:.0f}% of box entries are crosses. Shot volume {_pct(0.2 * (i['cross'] - 50))}, best-case shot quality capped at {0.5 - 0.003 * (i['cross'] - 50):.2f} xG.",
        "box": f"About {1 + i['box'] / 100 * 3:.1f} players in the box when we create a chance.",
    }
    return {k: {"does": DOES[k], "now": now[k]} for k in DOES}
