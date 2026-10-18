from plc.coach import Decision, decide, parse_command
from plc.squad import make_squad

squad = make_squad(1)
a, b = squad[0].name, squad[10].name


def test_dictation_variants():
    for t in (f"take off {a}, bring on {b}", f"replace {a} with {b}", f"bring on {b} for {a}"):
        d = parse_command(t, squad)
        assert (d.off, d.on) == (a, b)


def test_coach_overrides_ai():
    ai = Decision("x", "y", "ai")
    assert decide(ai, f"replace {a} with {b}", squad).source == "coach"
    assert decide(ai, "mumble", squad) is ai
