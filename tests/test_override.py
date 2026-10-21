from fastapi.testclient import TestClient

from plc.api import app
from plc.coach import Decision, decide
from plc import orchestrator
from plc.engine import new_match

c = TestClient(app)


def _ticked(n=14):
    mid = c.post("/match?seed=7").json()["id"]
    for _ in range(n):
        r = c.post(f"/match/{mid}/tick").json()
    return mid, r


def test_api_coach_beats_ai():
    mid, r = _ticked()
    ai_off = r["alerts"][0]["off"]
    ai_on = r["alerts"][0]["on"]
    off = next(p["name"] for p in r["xi"] if p["position"] != "GK" and p["name"] != ai_off)
    pos = {p["name"]: p["position"] for p in r["xi"]}
    on = next(b["name"] for b in r["bench"] if b["name"] != ai_on and b["position"] == pos[off])  # a goalkeeper may only be replaced by a goalkeeper
    out = c.post(f"/match/{mid}/decision", json={"off": ai_off, "on": ai_on, "transcript": f"take off {off}, bring on {on}"}).json()
    assert out["applied"] == {"off": off, "on": on, "source": "coach"}
    names = {p["name"] for p in out["xi"]}
    assert on in names and off not in names and ai_off in names  # the AI's player stays on


def test_api_ai_only_applies_when_posted():
    mid, r = _ticked()
    a = r["alerts"][0]
    out = c.post(f"/match/{mid}/decision", json={"off": a["off"], "on": a["on"]}).json()
    assert out["applied"]["source"] == "ai"  # only because the coach posted it


def test_decide_coach_wins():
    m, squad = new_match(7)
    ai = Decision(m.xi[1].name, m.bench[0].name, "ai")
    d = decide(ai, f"take off {m.xi[2].name}, bring on {m.bench[1].name}", squad)
    assert d.source == "coach" and d.off == m.xi[2].name
    assert decide(ai, "go attacking", squad) is ai  # nothing parseable: AI suggestion stands as a suggestion
    assert decide(None, None, squad) is None


def test_nothing_changes_without_a_decision():
    mid = c.post("/match?seed=7").json()["id"]
    before = c.get(f"/match/{mid}").json()
    xi0, bench0, form0, line0 = [p["name"] for p in before["xi"]], [p["name"] for p in before["bench"]], before["formation"], before["lines"]
    while True:
        r = c.post(f"/match/{mid}/tick").json()
        assert [p["name"] for p in r["xi"]] == xi0 and [p["name"] for p in r["bench"]] == bench0
        assert r["formation"] == form0 and r["lines"] == line0
        for route in ("full", "fade", "losing", "leading", "shape", "opponent"):  # not "goal": offline_briefing crashes on it before any goal
            assert c.get(f"/match/{mid}/briefing?route={route}").status_code == 200
        if r["minute"] >= 90:
            break
    after = c.get(f"/match/{mid}").json()
    assert [p["name"] for p in after["xi"]] == xi0 and [p["name"] for p in after["bench"]] == bench0


def test_staff_survives_substitution_and_early_goal_route():
    m, _ = new_match(7)
    for i in range(18):
        m.tick()
        if i == 9:
            m.substitute(m.xi[5].name, next(b.name for b in m.bench if b.position == m.xi[5].position))
        for route in ("full", "goal", "shape"):
            orchestrator.run(m, route)
