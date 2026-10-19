from plc.engine import new_match
from plc.staff import briefing, gold_facts


def _played(minute):
    m, _ = new_match(7)
    while m.minute < minute:
        m.tick()
    return m


def test_opponent_style_matches_their_profile():
    f = gold_facts(_played(30))
    labels = [s["label"] for s in f["their_style"]]
    assert "high block" in labels and "high press" in labels  # seed-7 opponent presses at 80%
    assert f["their_formation"] == "4-3-3"


def test_style_shift_detected_when_opponent_leads_late():
    m = _played(40)
    m.score[1], m.score[0] = 2, 0  # they lead, so they drop deeper after 65'
    while m.minute < 90:
        m.tick()
    assert gold_facts(m)["their_shifts"] == ["moved from a high block to a mid block"]


def test_offline_briefing_cites_sources_and_waits_for_data():
    assert briefing(_played(0))["notes"] == []
    notes = briefing(_played(30))["notes"]
    assert notes and all(n["source"] for n in notes) and any(n["agent"] == "Formation Tactician" for n in notes)
