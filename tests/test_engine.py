from plc.engine import Match
from plc.live import live_alerts
from plc.readiness import match_day_hrv, pick_xi
from plc.squad import make_squad
from plc.training import run_training


def _match(seed=7):
    squad = make_squad(seed)
    run_training(squad, seed=seed)
    tired = max((p for p in squad if p.position == "MID"), key=lambda p: p.rating).name
    hrv = match_day_hrv(squad, seed, tired)
    xi, bench = pick_xi(squad, hrv)
    if tired not in [p.name for p in xi]:  # coach starts him against the AI's advice
        t = next(p for p in squad if p.name == tired)
        weak = min((p for p in xi if p.position == "MID"), key=lambda p: p.rating)
        xi[xi.index(weak)] = t
        bench[:] = [b for b in bench if b.name != tired] + [weak]
    return Match(xi, bench, hrv, seed=seed), tired


def _to(minute, m):
    while m.minute < minute:
        m.tick()
    return m


def test_deterministic():
    (a, _), (b, _) = _match(), _match()
    assert _to(90, a).snaps == _to(90, b).snaps


def test_tired_player_fades_and_ai_flags_him():
    m, tired = _match()
    _to(70, m)
    assert any(a.off == tired for a in live_alerts(70, m.snaps, m.xi, m.bench, m.hrv))


def test_substitution_restores_strength():
    stay, tired = _match()
    swap, _ = _match()
    _to(70, stay), _to(70, swap)
    on = max((b for b in swap.bench if b.position == "MID"), key=lambda b: b.rating).name
    swap.substitute(tired, on)
    assert swap.strength() > stay.strength()
    assert tired not in [p.name for p in swap.xi] and on in [p.name for p in swap.xi]
