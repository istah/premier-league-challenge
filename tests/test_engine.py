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


def test_formation_change_moves_players_along_the_chain():
    m, _ = _match()
    m.set_formation("5-3-2")  # one more defender, one fewer forward: a midfielder drops back and a forward drops into midfield
    assert sorted(m.moves().values()) == ["FWD->MID", "MID->DEF"]
    assert m.strength() < _match()[0].strength()
    m.set_formation("4-3-3")
    assert m.moves() == {}  # back to natural roles, nothing accumulates


def test_pressing_hard_creates_more_but_tires_players_sooner():
    calm, _ = _match()
    hard, _ = _match()
    hard.set_instructions(press=90, tempo=80)
    _to(75, calm), _to(75, hard)
    p = hard.xi[5]
    assert hard.fade(p) >= calm.fade(p) and hard.mentality == "custom"
    assert hard.snaps[-1].distance_m <= calm.snaps[-1].distance_m * 1.1  # fatigue shows up in the data, not just a flag
    assert hard.shapes[-1]["us"].ppda < calm.shapes[-1]["us"].ppda  # and the press is visible in the style stats


def test_wellness_exposes_a_player_hrv_would_miss():
    from plc.readiness import concerns
    m, _ = _match()
    out = concerns(m.xi, m.hrv, m.wellness)
    assert any("HRV alone would miss this" in c for c in out)
    assert not any("HRV alone" in c for c in concerns(m.xi, m.hrv))  # without the check-in he looks fine


def _frames_for(plan, minutes=90, formation="4-4-2"):
    m, _ = _match()
    m.set_formation(formation)
    m.set_mentality(plan)
    out = []
    while m.minute < minutes:
        out.append((m.tick(), m))
    return out


def test_counter_plan_sits_deep_goes_direct_and_is_labelled():
    from plc.style import classify
    shapes = [t.shapes["us"] for t, _ in _frames_for("counter")[-4:]]
    labels = [s.label for s in classify(shapes)]
    assert "low block" in labels and "counter-attacking" in labels
    assert "counter-attacking" not in [s.label for s in classify([t.shapes["us"] for t, _ in _frames_for("possession")[-4:]])]


def test_wings_plan_overlaps_fullbacks_and_box_slider_fills_the_box():
    def stats(plan, box=None):
        run, overlaps, in_box = _frames_for(plan), 0, 0
        for t, m in run:
            overlaps += sum(r == "overlaps" for r in t.roles.values())
            for f in t.frames:
                if f["ball"][0] > 68:
                    in_box = max(in_box, sum(f[p.name][0] >= 78 for p in m.xi))
        return overlaps, in_box
    wings, inside = stats("wings"), stats("inside")
    assert wings[0] > inside[0] == 0  # only the wide plan produces overlapping runs
    assert wings[1] >= inside[1]
