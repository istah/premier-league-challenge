from fastapi.testclient import TestClient

from plc.api import app

c = TestClient(app)


def test_play_and_coach_override():
    s = c.post("/match").json()
    mid = s["id"]
    tired = max((p for p in s["xi"] if p["position"] == "MID"), key=lambda p: p["rating"])["name"]
    for _ in range(14):
        r = c.post(f"/match/{mid}/tick").json()
    assert any(a["off"] == tired for a in r["alerts"])
    on = next(b["name"] for b in r["bench"] if b["position"] == "MID")
    # coach says someone else; AI's suggestion in the same request loses
    other = next(p["name"] for p in r["xi"] if p["position"] == "MID" and p["name"] != tired)
    out = c.post(f"/match/{mid}/decision", json={"off": tired, "on": on, "transcript": f"take off {other}, bring on {on}, go attacking"}).json()
    assert out["applied"]["source"] == "coach" and out["applied"]["off"] == other
    assert out["mentality"] == "attack"
    assert c.post("/match/nope/tick").status_code == 404


def test_index_served():
    assert "Coach Room" in c.get("/").text


def test_formation_by_dictation_and_button():
    s = c.post("/match").json()
    mid = s["id"]
    out = c.post(f"/match/{mid}/decision", json={"transcript": "switch to four four two"}).json()
    assert out["formation"] == "4-4-2" and sorted(out["lines"].values()).count("MID") == 4
    out = c.post(f"/match/{mid}/decision", json={"formation": "3-4-3"}).json()
    assert list(out["lines"].values()).count("FWD") == 3


def test_sliders_and_spoken_instructions():
    mid = c.post("/match").json()["id"]
    out = c.post(f"/match/{mid}/decision", json={"instructions": {"press": 80}}).json()
    assert out["instructions"]["press"] == 80 and out["mentality"] == "custom"
    out = c.post(f"/match/{mid}/decision", json={"transcript": "drop deeper"}).json()
    assert out["instructions"]["line"] == 30
    assert out["wellness"] and out["concerns"]
