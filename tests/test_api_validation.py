import pytest
from fastapi.testclient import TestClient

from plc.api import app

c = TestClient(app)


def _new(seed=7):
    s = c.post(f"/match?seed={seed}").json()
    return s["id"], s


def _decide(mid, body):
    return c.post(f"/match/{mid}/decision", json=body)


def _same_state(a, b):
    keys = ("formation", "mentality", "instructions", "orders", "lines", "substitutions")
    return all(a[k] == b[k] for k in keys) and [p["name"] for p in a["xi"]] == [p["name"] for p in b["xi"]]


@pytest.mark.parametrize("body,field", [
    ({"formation": "9-9-9"}, "formation"),
    ({"mentality": "banana"}, "mentality"),
    ({"instructions": {"press": 101}}, "instructions"),
    ({"instructions": {"tempo": -1}}, "instructions"),
    ({"instructions": {"vo2max": 50}}, "instructions"),
    ({"instructions": {"line": "high"}}, "instructions"),
    ({"orders": {"Nobody": {"depth": 1}}}, None),
    ({"orders": {"x": {"depth": 500}}}, "orders"),
    ({"orders": {"x": {"height": 5}}}, "orders"),
    ({"off": "Ferreira"}, None),
    ({"formaton": "4-4-2"}, "formaton"),
])
def test_invalid_input_is_rejected_and_changes_nothing(body, field):
    mid, s = _new()
    r = _decide(mid, body)
    j = r.json()
    assert r.status_code == 422 and isinstance(j["detail"], str) and j["code"] in ("invalid_input", "unknown_player")
    if field:
        assert any(e["field"].startswith(field) for e in j["errors"])
    assert _same_state(c.get(f"/match/{mid}").json(), s)


def test_valid_bodies_the_coach_screen_sends_are_still_accepted():
    mid, s = _new()
    xi = [p["name"] for p in s["xi"]]
    for body in ({"mentality": "attack"}, {"formation": "4-4-2"}, {"instructions": {"line": 30}}, {"instructions": {"press": 0, "box": 100}},
                 {"orders": {xi[5]: {"depth": 12, "width": 0}}}, {"orders": {xi[5]: {"depth": 36, "width": 0}}}, {"orders": {xi[5]: {"depth": 0, "width": 0}}},
                 {"transcript": "press higher"}, {"transcript": "gibberish that matches nothing"}):
        assert _decide(mid, body).status_code == 200, body
    assert c.get(f"/match/{mid}").json()["orders"] == {}


def test_order_is_clamped_by_the_engine_and_reported_back():
    mid, s = _new()
    name = s["xi"][5]["name"]
    assert _decide(mid, {"orders": {name: {"depth": 90}}}).json()["orders"][name]["depth"] == 30


def test_start_rejects_unknown_formation():
    r = c.post("/match?formation=1-1-8")
    assert r.status_code == 422 and r.json()["code"] == "invalid_input"
    assert c.post("/match?formation=5-3-2").json()["formation"] == "5-3-2"
    assert c.post("/match?seed=abc").status_code == 422


def test_substitution_errors_are_structured_and_leave_the_match_untouched():
    mid, s = _new()
    for _ in range(2):
        c.post(f"/match/{mid}/tick")
    state = c.get(f"/match/{mid}").json()
    xi, bench = [p["name"] for p in s["xi"]], [p["name"] for p in s["bench"]]
    r = _decide(mid, {"off": "Nobody", "on": bench[0]})
    assert r.status_code == 422 and r.json()["code"] == "not_on_pitch" and "Nobody" in r.json()["detail"] and r.json()["subs_left"] == 5
    assert _decide(mid, {"off": xi[1], "on": xi[2]}).json()["code"] == "not_on_bench"
    assert _same_state(c.get(f"/match/{mid}").json(), state)


def test_five_substitutions_no_return_and_the_window_rule_through_the_api():
    mid, s = _new()
    xi = {p["position"]: [q["name"] for q in s["xi"] if q["position"] == p["position"]] for p in s["xi"]}
    bench = {p["position"]: [q["name"] for q in s["bench"] if q["position"] == p["position"]] for p in s["bench"]}
    c.post(f"/match/{mid}/tick")  # 5'
    r = _decide(mid, {"off": xi["DEF"][0], "on": bench["DEF"][0]})
    assert r.status_code == 200 and r.json()["substitutions"]["used"] == 1
    back = _decide(mid, {"off": bench["DEF"][0], "on": xi["DEF"][0]})
    assert back.status_code == 422 and back.json()["code"] == "reentry_not_allowed"
    for minute_ticks, pos, k in ((1, "MID", 0), (1, "FWD", 0)):  # windows at 10' and 15'
        for _ in range(minute_ticks):
            c.post(f"/match/{mid}/tick")
        assert _decide(mid, {"off": xi[pos][k], "on": bench[pos][k]}).status_code == 200
    c.post(f"/match/{mid}/tick")  # 20': a fourth window
    r = _decide(mid, {"off": xi["MID"][1], "on": bench["MID"][1]})
    assert r.status_code == 422 and r.json()["code"] == "no_substitution_window" and r.json()["windows_left"] == 0
    for _ in range(5):
        c.post(f"/match/{mid}/tick")  # 45': half-time, a separate opportunity
    assert _decide(mid, {"off": xi["MID"][1], "on": bench["MID"][1]}).status_code == 200
    assert _decide(mid, {"off": xi["DEF"][1], "on": bench["DEF"][1]}).status_code == 200  # same window, fifth substitution
    r = _decide(mid, {"off": xi["DEF"][2], "on": bench["MID"][2]})
    assert r.status_code == 422 and r.json()["code"] == "substitution_limit_reached"
    assert c.get(f"/match/{mid}").json()["substitutions"]["left"] == 0


def test_briefing_never_fails_after_substitutions():
    mid, s = _new()
    xi = {p["position"]: [q["name"] for q in s["xi"] if q["position"] == p["position"]] for p in s["xi"]}
    bench = {p["position"]: [q["name"] for q in s["bench"] if q["position"] == p["position"]] for p in s["bench"]}
    plan = iter([("FWD", 0), ("MID", 0), ("DEF", 0), ("FWD", 1), ("MID", 1)])
    for tick in range(18):
        r = c.post(f"/match/{mid}/tick").json()
        if tick in (2, 5, 8, 11, 12):
            pos, k = next(plan)
            c.post(f"/match/{mid}/decision", json={"off": xi[pos][k], "on": bench[pos][k]})
        for route in ("full", "shape", "fade", "opponent", "readiness", "goal", "losing", "leading"):
            assert c.get(f"/match/{mid}/briefing?route={route}").status_code == 200
