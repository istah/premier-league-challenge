"""Regression tests for the playtest findings (issues #6-#35): goalkeeper rules, alerts, staff advice, API strictness and full-time handling."""
from fastapi.testclient import TestClient

from plc import orchestrator
from plc.api import app
from plc.engine import IllegalSubstitution, new_match
from plc.events import Event
from plc.live import live_alerts
from plc.readiness import NOT_READY, concerns
from plc.staff import gold_facts, offline_briefing
from plc.tactics import FORMATIONS, why_switch

c = TestClient(app)


def _play(m, minute):
    while m.minute < minute:
        m.tick()
    return m


# ---------------- goalkeepers (#6, #10)
def test_goalkeeper_only_for_goalkeeper():
    m = _play(new_match(7)[0], 10)
    gk = next(p for p in m.xi if p.position == "GK").name
    mid = next(p for p in m.xi if p.position == "MID").name
    bench_gk = next(b.name for b in m.bench if b.position == "GK")
    bench_mid = next(b.name for b in m.bench if b.position == "MID")
    for off, on in ((mid, bench_gk), (gk, bench_mid)):
        try:
            m.substitute(off, on)
            raise AssertionError("accepted")
        except IllegalSubstitution as e:
            assert e.code == "goalkeeper_swap"
    m.set_formation("4-4-2")  # the XI is untouched, so a formation change still works
    m.substitute(gk, bench_gk)
    m.set_formation("3-5-2")
    assert sorted(m.line.values()).count("GK") == 1


def test_api_goalkeeper_swap_is_422_and_formation_still_changes():
    mid = c.post("/match?seed=7").json()["id"]
    for _ in range(3):
        s = c.post(f"/match/{mid}/tick").json()
    outfield = next(p["name"] for p in s["xi"] if p["position"] == "MID")
    keeper = next(b["name"] for b in s["bench"] if b["position"] == "GK")
    r = c.post(f"/match/{mid}/decision", json={"off": outfield, "on": keeper})
    assert r.status_code == 422 and r.json()["code"] == "goalkeeper_swap"
    assert c.post(f"/match/{mid}/decision", json={"formation": "4-4-2"}).status_code == 200


def test_alerts_never_name_a_goalkeeper_or_an_unready_replacement_and_say_down_when_hr_falls():
    seen = 0
    for seed in range(0, 25):
        m, _ = new_match(seed)
        pos = {p.name: p.position for p in m.xi + m.bench}
        while not m.finished:
            m.tick()
            alerts = live_alerts(m.minute, m.snaps, m.xi, m.eligible_bench, m.hrv)
            for a in alerts:
                seen += 1
                assert pos[a.off] != "GK" and "up -" not in a.evidence
                assert a.on == "none available" or m.hrv[a.on] >= NOT_READY
                assert a.strength in ("strong", "moderate", "watch") and 0 <= a.drop <= 0.6
            assert [a.probability for a in alerts] == sorted((a.probability for a in alerts), reverse=True)
    assert seen > 100  # the checks above were exercised


# ---------------- full time and strict input (#11, #12, #13)
def _finished():
    mid = c.post("/match?seed=7").json()["id"]
    for _ in range(18):
        last = c.post(f"/match/{mid}/tick").json()
    return mid, last


def test_nothing_is_recommended_or_accepted_after_full_time():
    mid, last = _finished()
    assert last["finished"] and last["alerts"] == []
    xi = [p for p in last["xi"] if p["position"] == "DEF"][0]["name"]
    on = next(b["name"] for b in last["bench"] if b["position"] == "DEF")
    r = c.post(f"/match/{mid}/decision", json={"off": xi, "on": on})
    assert r.status_code == 409 and r.json()["code"] == "match_finished"
    assert c.post(f"/match/{mid}/decision", json={"formation": "4-4-2"}).status_code == 409
    for route in orchestrator.ROUTES:
        b = c.get(f"/match/{mid}/briefing?route={route}")
        assert b.status_code == 200 and not any(n.get("actions") for n in b.json()["notes"])


def test_unknown_route_limit_empty_body_and_booleans_are_rejected():
    mid = c.post("/match?seed=7").json()["id"]
    r = c.get(f"/match/{mid}/briefing?route=nonsense")
    assert r.status_code == 422 and r.json()["code"] == "invalid_route" and "full" in r.json()["detail"]
    assert c.get("/events?limit=-1").status_code == 422 and c.get("/events?limit=0").status_code == 200
    assert c.post(f"/match/{mid}/decision", json={}).status_code == 422
    assert c.post(f"/match/{mid}/decision", json={"off": "", "on": "X"}).status_code == 422
    assert c.post(f"/match/{mid}/decision", json={"instructions": {"press": True}}).status_code == 422
    assert c.post(f"/match/{mid}/decision", json={"instructions": {"press": "80"}}).status_code == 422
    assert c.post(f"/match/{mid}/decision", json={"instructions": {"press": 80}}).status_code == 200


def test_state_tells_the_screen_what_it_needs():
    s = c.post("/match?seed=7&formation=5-3-2").json()
    assert s["opponent"] == "Harbour Rovers" and s["finished"] is False and s["formation"] == "5-3-2"
    assert set(s["eligible"]) <= {b["name"] for b in s["bench"]} and s["substitutions"]["left"] == 5


# ---------------- staff advice (#9, #15, #16, #17, #23, #26)
def _facts_at(seed, minute, score=None, mentality=None, formation=None):
    m, _ = new_match(seed)
    _play(m, minute)
    if score:
        m.score[:] = score
    if mentality:
        m.set_mentality(mentality)
    if formation:
        m.set_formation(formation)
    return m


def _all_routes(m):
    f = gold_facts(m)
    return {r: offline_briefing(f, r) for r in orchestrator.ROUTES}


def test_no_note_offers_the_plan_or_formation_that_is_already_on():
    for seed in range(0, 12):
        for minute in (25, 45, 70, 85):
            for mentality in ("balanced", "attack", "defend"):
                m = _facts_at(seed, minute, mentality=mentality)
                for notes in _all_routes(m).values():
                    for n in notes:
                        for a in n.get("actions", []):
                            assert not (a["type"] == "plan" and a["value"] == m.mentality) and not (a["type"] == "formation" and a["value"] == m.formation)


def test_every_route_in_one_state_offers_at_most_one_plan_and_advice_matches_it():
    for seed in range(0, 12):
        for minute, score in ((30, [0, 0]), (45, [0, 1]), (70, [1, 3]), (70, [3, 1]), (85, [2, 2])):
            m = _facts_at(seed, minute, score=score)
            plans, forms = set(), []
            lead = m.score[0] - m.score[1]
            for route, notes in _all_routes(m).items():
                if (route == "losing" and not (lead < 0 and minute >= 60)) or (route == "leading" and not (lead > 0 and minute >= 60)):
                    continue  # the Activator only fires these routes in those states
                for n in notes:
                    for a in n.get("actions", []):
                        if a["type"] == "plan":
                            plans.add(a["value"])
                        if a["type"] == "formation":
                            forms.append(a["value"])
            assert len(plans) <= 1, (seed, minute, score, plans)
            if plans == {"defend"}:
                assert all(FORMATIONS[f][2] <= FORMATIONS[m.formation][2] for f in forms)
            if plans == {"attack"}:
                assert all(FORMATIONS[f][2] >= FORMATIONS[m.formation][2] for f in forms)


def test_formation_advice_is_only_given_for_a_risky_shape_and_explains_the_new_shape():
    for seed in range(0, 15):
        m = _facts_at(seed, 45)
        f = gold_facts(m)
        advice = [n for n in offline_briefing(f, "full") if any(a["type"] == "formation" for a in n.get("actions", []))]
        if f["tactical_read"]["verdict"] != "Risky":
            assert not advice
        for n in advice:
            assert f["recommended_formation"] in n["claim"] and all(r in n["claim"] for r in f["switch_reasons"])
            assert "only 3 midfielders" not in n["claim"]  # the old contradiction: Risky because of 3 midfielders, advice has 3 midfielders
    m, _ = new_match(7)
    assert why_switch("4-3-3", "5-3-2", m.profile)


def _goal_note(minute, score, mine=False):
    m = _facts_at(7, minute, score=score)
    m.events.append(Event(minute, "Redmoor FC" if mine else m.opponent, "Someone", "shot", 90.0, 50.0, {"xg": 0.3, "goal": True}))
    return " ".join(n["claim"] for n in offline_briefing(gold_facts(m), "goal") if n["agent"].endswith("Analyst"))


def test_goal_advice_follows_the_score_and_the_minute():
    assert "chase" not in _goal_note(65, [4, 3])  # still leading
    assert "Do not chase yet" in _goal_note(30, [0, 1])
    assert "behind" in _goal_note(75, [0, 2]) and "Do not chase yet" not in _goal_note(75, [0, 2])
    assert "Level again" in _goal_note(50, [2, 2])
    assert "the current settings" in _goal_note(40, [2, 0], mine=True) or "the plan that worked" in _goal_note(40, [2, 0], mine=True)
    m = _facts_at(7, 40, score=[2, 0])
    m.set_instructions(press=60)  # moving a slider turns the plan into "custom"
    m.events.append(Event(40, "Redmoor FC", "Someone", "shot", 90.0, 50.0, {"xg": 0.3, "goal": True}))
    note = next(n["claim"] for n in offline_briefing(gold_facts(m), "goal") if n["agent"] == "Own-Style Analyst")
    assert "custom" not in note and "current settings" in note


def test_repeated_advice_is_suppressed_until_the_situation_changes():
    m = _facts_at(7, 45)
    first = orchestrator.run(m, "full")["notes"]
    assert any(a["type"] == "formation" for n in first for a in n.get("actions", []))
    assert orchestrator.run(m, "full")["notes"] == first  # the same request in the same minute is repeatable
    assert not any(a["type"] == "formation" for n in orchestrator.run(m, "goal")["notes"] for a in n.get("actions", []))  # another route in that minute does not repeat it
    _play(m, 60)
    assert not any(a["type"] == "formation" for n in orchestrator.run(m, "full")["notes"] for a in n.get("actions", []))
    m.score[:] = [1, 0]  # the situation changed: advice may come back
    assert any(a["type"] == "formation" for n in orchestrator.run(m, "full")["notes"] for a in n.get("actions", []))


def test_readiness_notes_explain_the_hooper_scale():
    m, _ = new_match(7)
    out = concerns(m.xi, m.hrv, m.wellness)
    assert out and all("4 is best, 28 is worst" in c for c in out) and any("HRV alone would miss this" in c for c in out)
