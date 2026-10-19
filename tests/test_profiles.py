from plc.engine import new_match
from plc.profiles import archetype, fit, needs


def test_archetypes_are_deterministic_and_fit_follows_the_plan():
    m, squad = new_match(7)
    assert [archetype(p) for p in squad] == [archetype(p) for p in squad]
    fwd = next(p for p in m.xi if p.position == "FWD")
    counter = needs("4-4-2", {**m.instructions, "direct": 90}, m.profile)
    patient = needs("4-4-2", {**m.instructions, "direct": 10}, m.profile)
    assert any(n.attr == "pace" for n in counter["FWD"]) and not any(n.attr == "pace" for n in patient["FWD"])
    assert fit(fwd, "FWD", counter)[0] != fit(fwd, "FWD", patient)[0]
    assert fit(fwd, "DEF", counter)[0] < fit(fwd, "FWD", counter)[0]  # out of natural line costs
