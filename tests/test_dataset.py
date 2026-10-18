import csv
from datetime import date, timedelta

from plc.dataset import START, build


def rows(path, name):
    return list(csv.DictReader(open(path / f"{name}.csv")))


def test_deterministic(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    build(a, seed=3, days=30)
    build(b, seed=3, days=30)
    for name in ("wearable_daily", "injuries", "match_events"):
        assert (a / f"{name}.csv").read_text() == (b / f"{name}.csv").read_text()


def test_injured_players_only_rehab_and_never_start(tmp_path):
    build(tmp_path, seed=0, days=90)
    out = {}
    for i in rows(tmp_path, "injuries"):
        if i["context"] != "history":
            out.setdefault(i["player"], []).append((date.fromisoformat(i["date"]), date.fromisoformat(i["date"]) + timedelta(days=int(i["days_out"]))))
    inside = lambda p, d: any(s < date.fromisoformat(d) < e for s, e in out.get(p, []))
    assert all(s["type"] == "rehab" for s in rows(tmp_path, "training_sessions") if inside(s["player"], s["date"]))
    assert not any(inside(t["player"], t["date"]) for t in rows(tmp_path, "match_tracking"))
    assert all(r["ingest_ts"] for r in rows(tmp_path, "wearable_daily"))
