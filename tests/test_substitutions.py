import pytest

from plc.engine import IllegalSubstitution, Match, SubRules, new_match
from plc.staff import gold_facts, offline_briefing


def _match(minute=10, seed=7):
    m, _ = new_match(seed)
    while m.minute < minute:
        m.tick()
    return m


def _swap(m, k=0, pos=None):
    out = [p for p in m.xi if pos is None or p.position == pos][k]
    inn = next(b for b in m.bench if b.position == out.position and b.name not in m.subbed_off)
    m.substitute(out.name, inn.name)
    return out.name, inn.name


def _cand(m, off):
    pos = next(p.position for p in m.xi if p.name == off)
    return next(b.name for b in m.bench if b.position == pos and b.name not in m.subbed_off)


def _any(m):
    for p in m.xi:
        if p.position != "GK":
            c = [b.name for b in m.bench if b.position == p.position and b.name not in m.subbed_off]
            if c:
                return p.name, c[0]
    raise AssertionError("no legal pair left")


def _code(m, off, on):
    with pytest.raises(IllegalSubstitution) as e:
        m.substitute(off, on)
    return e.value.code


def _unique(m):
    names = [p.name for p in m.xi]
    return len(names) == len(set(names)) == 11 and not set(names) & {b.name for b in m.bench}


def test_valid_substitution_updates_every_piece_of_state():
    m = _match()
    off, on = _swap(m, 1, "MID")
    assert on in [p.name for p in m.xi] and off in [b.name for b in m.bench] and m.entered[on] == 10
    assert m.subs_used == 1 and m.windows_used == 1 and off in m.subbed_off and _unique(m)
    assert on in m.last_frame and off not in m.last_frame and off not in m.orders


def test_identities_are_checked_and_nothing_changes_on_rejection():
    m = _match()
    xi, bench = [p.name for p in m.xi], [b.name for b in m.bench]
    assert _code(m, "Nobody", bench[0]) == "not_on_pitch"
    assert _code(m, xi[0], "Nobody") == "not_on_bench"
    assert _code(m, xi[0], xi[1]) == "not_on_bench"  # a player already on the pitch cannot come on
    assert _code(m, bench[0], bench[1]) == "not_on_pitch"
    assert [p.name for p in m.xi] == xi and [b.name for b in m.bench] == bench and m.subs_used == 0


def test_no_reentry():
    m = _match()
    off, on = _swap(m, 1, "MID")
    assert _code(m, on, off) == "reentry_not_allowed"
    assert m.subs_used == 1


def test_at_most_five_substitutions():
    m = _match(5)
    for pos in ("DEF", "MID", "FWD"):  # three in one window
        _swap(m, 0, pos)
    while m.minute < 15:
        m.tick()
    _swap(m, 1, "DEF")
    _swap(m, 1, "MID")
    assert m.subs_used == 5 and m.windows_used == 2
    xi = [p.name for p in m.xi]
    assert _code(m, xi[1], _cand(m, xi[1])) == "substitution_limit_reached"
    assert m.subs_used == 5 and _unique(m)


def test_three_in_play_windows_and_a_free_halftime_window():
    m = _match(10)
    _swap(m, 0, "DEF")
    _swap(m, 0, "MID")  # same minute: still one window
    assert m.windows_used == 1
    while m.minute < 20:
        m.tick()
    _swap(m, 1, "DEF")
    while m.minute < 30:
        m.tick()
    m.rules = SubRules(max_subs=9)  # isolate the window rule from the count rule
    _swap(m, 1, "MID")
    assert m.windows_used == 3
    while m.minute < 40:
        m.tick()
    xi, on = _any(m)
    assert _code(m, xi, on) == "no_substitution_window"
    while m.minute < 45:
        m.tick()
    m.substitute(xi, on)  # half-time is a separate opportunity
    assert m.windows_used == 3 and m.subs_used == 5 and m.sub_log[-1]["half_time"]
    while m.minute < 55:
        m.tick()
    assert _code(m, *_any(m)) == "no_substitution_window"


def test_kickoff_team_selection_is_not_a_substitution():
    m = _match(0)
    off, on = _swap(m, 1, "MID")
    assert m.subs_used == 0 and off not in m.subbed_off
    m.substitute(on, off)  # the original starter can still be restored before kick-off
    assert _unique(m)


def test_rules_are_configurable():
    m = _match(10)
    m.rules = SubRules(max_subs=None, max_windows=None, allow_reentry=True)
    off, on = _swap(m, 1, "MID")
    m.substitute(on, off)
    assert m.subs_used == 2 and _unique(m)


def test_briefing_survives_a_substitution_that_changes_the_positions_in_use():
    # Regression: staff.shape_issues read last_frame[player] for every starter, but a substitute who came on after the last tick had no entry (KeyError, HTTP 500).
    m = _match(10)
    fwd = sorted((p for p in m.xi if m.line[p.name] == "FWD"), key=lambda p: p.name)
    last = {p.name: [10.0, 10.0] for p in m.xi}
    last[fwd[0].name] = [10.0, 50.0]  # the forward closest to the middle is the one the staff would pull back
    last.update({f"{m.opponent} #{k}": [50.0, 50.0] for k in (2, 3, 4)})  # three opponents in the central zone, none of ours
    m.last_frame = last
    assert any(i["kind"] == "central_overload" and i["player"] == fwd[0].name for i in gold_facts(m)["shape_issues"])
    on = next(b.name for b in m.bench if b.position == "FWD")
    m.substitute(fwd[0].name, on)
    facts = gold_facts(m)  # was KeyError before the fix
    assert any(i["kind"] == "central_overload" and i["player"] == on for i in facts["shape_issues"])
    assert offline_briefing(facts, "shape")


def test_briefing_stays_available_after_many_substitutions():
    m = _match(10)
    for minute in (10, 25, 40):
        while m.minute < minute:
            m.tick()
        for pos in ("FWD", "MID"):
            if m.subs_used < 5:
                _swap(m, 0, pos)
        for route in ("full", "shape", "fade", "opponent", "readiness"):
            offline_briefing(gold_facts(m), route)
    assert m.subs_used == 5 and _unique(m)


def test_gold_facts_work_when_our_back_line_is_high():
    # Regression: shape_issues indexed Style dataclasses like dicts once our block was high (line >= 45), so /tick returned HTTP 500 for any high-line plan.
    m = _match(0)
    m.set_instructions(line=100)
    for _ in range(4):
        m.tick()
    facts = gold_facts(m)
    assert any(s["label"] == "high block" for s in facts["our_style"])
    assert isinstance(facts["shape_issues"], list)


def test_staff_never_suggest_a_player_who_cannot_come_on():
    from plc.live import live_alerts
    m = _match(10)
    off, on = _swap(m, 1, "MID")
    assert on not in {b.name for b in m.eligible_bench} and off not in {b.name for b in m.eligible_bench}
    while m.minute < 70:
        m.tick()
        for a in live_alerts(m.minute, m.snaps, m.xi, m.eligible_bench, m.hrv):
            assert a.on == "none available" or a.on not in m.subbed_off
    assert all(b.name not in m.subbed_off for b in m.eligible_bench)
    m.rules = SubRules(max_subs=m.subs_used)  # all substitutions used: nothing is eligible, so nothing is suggested
    assert m.eligible_bench == []
    m2 = _match(10)
    m2.rules = SubRules(max_subs=9)  # isolate the window rule from the count rule
    for pos in ("DEF", "MID", "FWD"):
        _swap(m2, 0, pos)
    while m2.minute < 20:
        m2.tick()
    _swap(m2, 1, "DEF")
    while m2.minute < 30:
        m2.tick()
    _swap(m2, 1, "MID")
    while m2.minute < 40:
        m2.tick()
    assert m2.windows_used == 3 and m2.eligible_bench == []  # a fourth window is not available, half-time is the next chance
    while m2.minute < 45:
        m2.tick()
