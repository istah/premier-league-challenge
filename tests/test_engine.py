from plc.engine import new_match
from plc.live import live_alerts


def _match(seed=7):
    m, _ = new_match(seed)
    return m, max((p for p in m.xi if p.position == "MID"), key=lambda p: p.rating).name


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


def test_formation_trades_attack_for_defence_and_costs_out_of_position():
    m, _ = _match()
    base = m.strength()
    m.set_formation("3-4-3")
    assert list(m.line.values()).count("FWD") == 3 and m.strength() < base  # a defender now plays midfield


def test_frames_place_22_players_and_ball_in_bounds_and_high_block_sits_high():
    m, _ = _match()
    t = m.tick()
    assert len(t.frames) == 5 and all(len(f) == 23 for f in t.frames)
    assert all(0 <= v <= 100 for f in t.frames for xy in f.values() for v in xy)
    opp_defenders = [t.frames[0][f"{m.opponent} #{i}"][0] for i in range(2, 6)]
    assert max(opp_defenders) < 60  # a pressing side defends near the halfway line, not on its own box
