from plc import orchestrator
from plc.activator import Activator
from plc.engine import new_match
from plc.judge import judge
from plc.staff import gold_facts


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


def test_orchestrator_waits_for_data_then_routes_by_trigger():
    assert orchestrator.run(_played(0))["notes"] == []
    m = _played(70)
    fade = orchestrator.run(m, "fade")
    assert fade["agents"] == ["Formation Tactician", "Own-Style Analyst"]
    assert any(a["type"] == "sub" for n in fade["notes"] for a in n.get("actions", [])) and fade["judge"]["grounded"]
    assert {n["agent"] for n in orchestrator.run(m, "opponent")["notes"]} <= {"Opponent Analyst", "Formation Tactician"}
    m.score[:] = [0, 1]
    assert "Behind 0-1" in orchestrator.run(m, "losing")["notes"][0]["claim"]


def test_every_offline_note_is_grounded_and_cites_sources_for_every_route():
    m = _played(70)
    for route in orchestrator.ROUTES:
        out = orchestrator.run(m, route)
        assert out["judge"]["grounded"], (route, out["judge"]["unsupported"])
        assert all(n["source"] for n in out["notes"])


def test_judge_catches_invented_numbers_and_styles():
    m = _played(40)
    f = gold_facts(m)
    good = {"agent": "Opponent Analyst", "claim": f"{f['opponent']} play a {f['their_formation']}.", "source": "x"}
    fake_num = {"agent": "Opponent Analyst", "claim": "Their press wins the ball 17 times per half.", "source": "x"}
    fake_style = {"agent": "Opponent Analyst", "claim": "They sit in a low block and wing play.", "source": "x"}
    assert judge([good], f)["grounded"]
    assert not judge([fake_num], f)["grounded"] and not judge([fake_style], f)["grounded"]


def test_activator_fires_on_change_not_on_every_event():
    a = Activator()
    p = {"minute": 55, "alerts": [{"off": "X"}], "fading": ["X"], "goals": 0, "their_shifts": [], "concerns": [], "score": (0, 0), "late_deficit": 0, "late_lead": 0}
    assert [r["route"] for r in a.evaluate(p)] == ["fade"]
    assert a.evaluate(p) == []  # same state, no re-fire
    assert [r["route"] for r in a.evaluate({**p, "alerts": [{"off": "Y"}], "fading": ["Y"]})] == ["fade"]


def test_benchmark_judge_catches_every_corruption_and_flags_no_real_note(tmp_path):
    from plc.bench import run
    r = run(seeds=(7,), plans=("balanced", "counter"), out=tmp_path)
    assert r["judge_catch_rate"] == 1.0 and r["judge_false_positive_rate"] == 0.0 and r["grounded_rate"] == 1.0
    assert (tmp_path / "eval.jsonl").read_text().strip()


def test_judge_citations_and_calibration(tmp_path):
    from plc.bench import calibration
    from plc.judge import judge

    facts = {"possession_pct": 61.5, "xg": {"us": 1.2}, "their_style": [{"label": "high block"}]}
    note = {"agent": "Opponent Analyst", "claim": "We hold 61.5% and they play a high block, xg 9.9."}
    j = judge([note], facts)
    keys = {c["key"] for c in j["citations"]}
    assert "gold_facts['possession_pct']" in keys and "gold_facts['their_style'][0]['label']" in keys
    assert all(c["layer"] == "gold" for c in j["citations"])
    assert j["notes"][0]["searched"] == ["number 9.9 in gold_facts"] and not j["grounded"]
    path = tmp_path / "labels.csv"
    path.write_text("note_id,label,reason\na,ungrounded,bad xg\nb,grounded,ok\n")
    ok = {"agent": "Opponent Analyst", "claim": "We hold 61.5%."}
    r = calibration({"a": (note, facts), "b": (ok, facts)}, path)
    assert r["accuracy"] == 1.0 and r["tp"] == 1 and r["tn"] == 1
    assert calibration({}, tmp_path / "none.csv") is None


def test_fact_checker_flag_blocks_a_live_note(monkeypatch):
    from plc import orchestrator
    from plc.engine import new_match

    m, _ = new_match(7)
    for _ in range(13):
        m.tick()
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "x")
    monkeypatch.setenv("FOUNDRY_MODEL", "x")
    live = [{"agent": "Formation Tactician", "claim": "Change shape.", "source": "agent"}, {"agent": "Fact-checker", "claim": "Check: invented movement", "source": "facts"}]
    monkeypatch.setattr(orchestrator, "agent_briefing", lambda *a: _coro(live))
    monkeypatch.setattr(orchestrator, "judge", lambda notes, facts, llm=False: {"grounded": True, "unsupported": [], "score": 1.0})
    r = orchestrator.run(m, "fade", live=True)
    assert r["mode"] == "agents" and r["judge"]["grounded"] is False and "invented movement" in r["judge"]["unsupported"][0]


async def _coro(x):
    return x
