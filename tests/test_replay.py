from plc.replay import ARMS, compare, play


def test_replay_deterministic():
    assert [play(3, a) for a in ARMS] == [play(3, a) for a in ARMS]
    assert compare([0, 1, 2]) == compare([0, 1, 2])


def test_replay_arms():
    r = compare(list(range(6)))
    assert r["seeds"] == 6 and r["arms"]["none"]["interventions"] == 0
    assert r["arms"]["accept_all"]["interventions"] > 0 and r["arms"]["coach"]["interventions"] > 0
    assert set(r["paired_vs_none"]) == {"accept_all.gd", "accept_all.xgd", "coach.gd", "coach.xgd"}
