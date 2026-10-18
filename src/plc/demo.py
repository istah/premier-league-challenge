"""End-to-end offline demo: training -> readiness -> XI -> live alerts -> coach override -> opponent memory."""
from dataclasses import asdict

from .coach import Decision, decide
from .events import generate_match
from .live import live_alerts
from .opponent import analyse, recall, remember
from .readiness import concerns, match_day_hrv, pick_xi
from .squad import CLUB, make_squad
from .tracking import track_match
from .training import run_training

OPPONENT = "Harbour Rovers"


def run(seed: int = 7, dictation: str | None = None):
    squad = make_squad(seed)
    pre = {p.name: p.rating for p in squad}
    run_training(squad, seed=seed)
    print(f"== Training: biggest rating moves")
    for p in sorted(squad, key=lambda p: -abs(p.rating - pre[p.name]))[:3]:
        print(f"  {p.name} ({p.position}): {pre[p.name]} -> {p.rating}")

    tired = sorted((p for p in squad if p.position == "MID"), key=lambda p: -p.rating)[0].name
    hrv = match_day_hrv(squad, seed, tired)
    xi, bench = pick_xi(squad, hrv)
    print(f"\n== Suggested XI vs {OPPONENT} (4-3-3): " + ", ".join(p.name for p in xi))
    for c in concerns(xi, hrv):
        print("  concern ->", c)
    if tired not in [p.name for p in xi]:
        t = next(p for p in squad if p.name == tired)
        weakest = min((p for p in xi if p.position == "MID"), key=lambda p: p.rating)
        xi[xi.index(weakest)] = t
        bench[:] = [b for b in bench if b.name != tired] + [weakest]
        print(f"  AI had {tired} resting (HRV {hrv[tired]:.0%}); COACH overrides and starts him over {weakest.name}")

    print(f"\n== Previously on {OPPONENT}: {recall(OPPONENT) or 'nothing stored'}")
    snaps = track_match(xi, hrv, seed)
    events = generate_match(seed, CLUB, OPPONENT, home_players=[p.name for p in xi])
    shown = set()
    for minute in range(50, 95, 5):
        for a in live_alerts(minute, snaps, xi, bench, hrv):
            if a.off in shown:
                continue
            shown.add(a.off)
            print(f"\n[{a.minute}'] AI suggests: {a.off} off, {a.on} on (p={a.probability}) because {a.evidence}")
            d = decide(Decision(a.off, a.on, "ai"), dictation, squad)
            print(f"  FINAL ({d.source}): {d.off} off, {d.on} on")
            dictation = None  # one dictated command per demo run
            out, inn = next(p for p in xi if p.name == d.off), next(p for p in bench if p.name == d.on)
            xi[xi.index(out)], bench[bench.index(inn)] = inn, out
    remember(OPPONENT, analyse(events, OPPONENT))
    print("\n== Stored opponent insight:", recall(OPPONENT)[-1])
