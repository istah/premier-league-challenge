"""Bronze dataset: ~90 days of wearables, training, injuries and 15 matches for a 32-player squad, written as CSVs.
Raw and append-only by convention; every row carries `date` and `ingest_ts`."""
import csv
import json
import math
import random
from dataclasses import asdict
from datetime import date, timedelta
from pathlib import Path
from statistics import mean

from .events import generate_match
from .fixtures import make_fixtures, make_opponent
from .medical import injury_history, make_profile, sample_injury
from .readiness import pick_xi
from .squad import CLUB, make_squad
from .tracking import track_match
from .training import ALPHA, Session

START, DAYS = date(2026, 7, 20), 90
INTENSITY = {"full": (0.65, 90), "prep": (0.55, 60), "recovery": (0.40, 40), "rehab": (0.30, 30)}
BASE_INJURY_P = 0.0055
MATCH_RISK = 8


def clip(x, lo, hi):
    return max(lo, min(hi, x))


def hr_series(rng, rest, hr_max, kind):
    mean_frac, dur = INTENSITY[kind]
    phase = rng.uniform(0, 6)
    fracs = [clip(mean_frac * min(1, t / 10) * min(1, (dur - t) / 8) * (1 + 0.25 * math.sin(t / 6 + phase)) + rng.gauss(0, 0.04), 0.1, 1)
             for t in range(0, dur, 2)]
    return dur, fracs, [round(rest + (hr_max - rest) * f) for f in fracs]


def write(out: Path, name: str, rows: list[dict]):
    for r in rows:
        r["ingest_ts"] = f"{r['date']}T23:59:00Z"
    with open(out / f"{name}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def build(out: Path, seed: int = 0, days: int = DAYS) -> dict[str, int]:
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    squad = make_squad(seed, depth=True)
    prof = {p.name: make_profile(p.name, p.position, rng) for p in squad}
    pos = {p.name: p.position for p in squad}
    trend = {p.name: rng.uniform(-1, 1) for p in squad}
    base_rating = {p.name: p.rating for p in squad}
    loads = {p.name: [] for p in squad}
    out_until = {p.name: START for p in squad}
    played_yesterday: set[str] = set()
    injuries = [r for p in squad for r in injury_history(p.name, START, rng)]
    past_areas = {p.name: {r["area"] for r in injuries if r["player"] == p.name} for p in squad}
    fixtures = {f.date: f for f in make_fixtures(START.year) if f.date < START + timedelta(days=days)}
    opps = {f.opponent: make_opponent(f.opponent, seed) for f in fixtures.values()}
    wear, sessions, hr_rows, ev_rows, trk_rows, results = [], [], [], [], [], []

    for d in range(days):
        day = START + timedelta(days=d)
        iso = day.isoformat()
        fx, tomorrow = fixtures.get(day), fixtures.get(day + timedelta(days=1))
        injured = {n for n in out_until if out_until[n] > day}
        morning = {}
        for p in squad:
            n, pf = p.name, prof[p.name]
            prev = loads[n][-1] if loads[n] else 6
            bad = rng.random() < 0.06  # illness, travel or a bad night
            sleep = round(clip(rng.gauss(5.8 if bad else 7.6, 0.9), 4.5, 10), 1)
            hrv = round(p.base_hrv * clip(0.7 + 0.05 * sleep, 0.8, 1.1) * (1 - 0.012 * prev) * rng.uniform(0.92, 1.08) * (0.78 if bad else 1), 1)
            rhr = round(pf.resting_hr_base * (1 + (1 - hrv / p.base_hrv) * 0.25 + (0.05 if n in injured else 0)) + rng.gauss(0, 1))
            awake = rng.randint(15, 60)
            deep, rem = (round(0.18 * sleep * 60 * rng.uniform(0.8, 1.2)), round(0.22 * sleep * 60 * rng.uniform(0.8, 1.2)))
            morning[n] = dict(date=iso, player=n, sleep_h=sleep, sleep_efficiency=round(1 - awake / (sleep * 60 + awake), 3),
                              deep_min=deep, rem_min=rem, light_min=round(sleep * 60 - deep - rem), awake_min=awake, resting_hr=rhr, hrv_rmssd=hrv,
                              hrv_vs_baseline=round(hrv / p.base_hrv, 2), respiratory_rate=round(rng.gauss(14.5, 0.8), 1),
                              skin_temp_delta=round(rng.gauss(0, 0.25), 2), spo2=round(min(100, rng.gauss(97, 0.8)), 1),
                              recovery_score=round(100 * clip(0.45 * min(1, hrv / p.base_hrv) + 0.3 * sleep / 8.5 + 0.25 * pf.resting_hr_base / rhr, 0, 1)))
        hrv_ratio = {n: m["hrv_vs_baseline"] for n, m in morning.items()}

        starters: set[str] = set()
        if fx:
            xi, _ = pick_xi([p for p in squad if p.name not in injured], hrv_ratio)
            starters = {p.name for p in xi}
            opp = opps[fx.opponent]
            home, away = (CLUB, fx.opponent) if fx.home else (fx.opponent, CLUB)
            names = [p.name for p in xi]
            theirs = [q.name for q in opp.squad]
            evs = generate_match(seed * 1000 + d, home, away, 140, *((names, theirs) if fx.home else (theirs, names)))
            ev_rows += [dict(match_id=fx.match_id, date=iso, minute=e.minute, team=e.team, player=e.player, kind=e.kind, x=e.x, y=e.y,
                             detail=json.dumps(e.detail)) for e in evs]
            goals = lambda t: sum(e.kind == "shot" and e.team == t and e.detail["goal"] for e in evs)
            results.append(dict(match_id=fx.match_id, date=iso, competition=fx.competition, opponent=fx.opponent, home=int(fx.home),
                                goals_for=goals(CLUB), goals_against=goals(fx.opponent)))
            trk_rows += [dict(match_id=fx.match_id, date=iso, **asdict(s)) for s in track_match(xi, hrv_ratio, seed * 1000 + d)]

        for p in squad:
            n, pf, m = p.name, prof[p.name], morning[p.name]
            kind = None
            if n in injured:
                kind = "rehab"
            elif fx:
                kind = None
            elif n in played_yesterday:
                kind = "recovery"
            elif tomorrow:
                kind = "prep"
            elif day.weekday() != 6:
                kind = "full"
            load = 0.0
            if kind:
                hr_max = 205 - pf.age // 2
                dur, fracs, series = hr_series(rng, m["resting_hr"], hr_max, kind)
                load = round(clip(mean(fracs) * dur / 5, 0, 21), 1)
                score = clip(base_rating[n] + trend[n] * 8 + (m["hrv_vs_baseline"] - 1) * 20 + rng.gauss(0, 4), 0, 100)
                sessions.append(dict(asdict(Session(d + 1, n, round(mean(series)), max(series), load, m["hrv_rmssd"], m["sleep_h"], round(score, 1))),
                                     date=iso, type=kind, duration_min=dur))
                hr_rows += [dict(date=iso, player=n, type=kind, minute=2 * i, hr=h) for i, h in enumerate(series)]
                if kind in ("full", "prep"):
                    p.rating = round((1 - ALPHA) * p.rating + ALPHA * score, 1)
            elif fx and n in starters:
                load = round(clip(rng.gauss(14.5, 1.5), 8, 21), 1)
            elif fx and n not in injured:
                load = 3.0
            loads[n].append(load)
            trend[n] = clip(trend[n] + rng.gauss(0, 0.05), -1, 1)
            wear.append({**m, "day_strain": load})

            if n not in injured and (kind in ("full", "prep") or n in starters):
                acute, chronic = mean(loads[n][-7:]), mean(loads[n][-28:])
                acwr = acute / chronic if len(loads[n]) >= 14 and chronic else 1
                risk = BASE_INJURY_P * (1 + 2.5 * max(0, acwr - 1.3)) * (1 + 2 * (m["hrv_vs_baseline"] < 0.8)) * (1.5 if pf.age > 31 else 1)
                if rng.random() < risk * (MATCH_RISK if n in starters else 1):
                    kind_i, area, sev, days_out = sample_injury(rng)
                    recur = area in past_areas[n]
                    days_out = round(days_out * (1.3 if recur else 1))
                    out_until[n] = day + timedelta(days=days_out)
                    past_areas[n].add(area)
                    injuries.append(dict(player=n, date=iso, type=kind_i, area=area, severity=sev, days_out=days_out,
                                         context="match" if n in starters else "training", minute=rng.randint(5, 90) if n in starters else "", recurrence=int(recur)))
        played_yesterday = starters

    end = START + timedelta(days=days)
    status = [dict(date=end.isoformat(), player=p.name, position=pos[p.name], rating=p.rating,
                   status="injured" if out_until[p.name] > end else "available",
                   return_date=out_until[p.name].isoformat() if out_until[p.name] > end else "",
                   injuries_in_window=sum(1 for r in injuries if r["player"] == p.name and r["context"] != "history"),
                   injuries_history=sum(1 for r in injuries if r["player"] == p.name and r["context"] == "history")) for p in squad]
    profile_rows = [dict(date=START.isoformat(), position=pos[n], **asdict(pf)) for n, pf in prof.items()]
    opp_rows = [dict(date=START.isoformat(), team=o.name, position=q_pos, **asdict(q)) for o in opps.values() for q, q_pos in zip(o.squad, o.positions)]
    team_rows = [dict(date=START.isoformat(), team=o.name, press=o.press, aerial=o.aerial, set_piece_threat=o.set_piece_threat,
                      avg_height_cm=round(mean(q.height_cm for q in o.squad), 1), avg_weight_kg=round(mean(q.weight_kg for q in o.squad), 1)) for o in opps.values()]
    fx_rows = [dict(match_id=f.match_id, date=f.date.isoformat(), competition=f.competition, opponent=f.opponent, home=int(f.home)) for f in fixtures.values()]
    tables = dict(players=profile_rows, opponent_players=opp_rows, opponents=team_rows, fixtures=fx_rows, wearable_daily=wear,
                  training_sessions=sessions, training_hr=hr_rows, injuries=sorted(injuries, key=lambda r: r["date"]), player_status=status,
                  match_results=results, match_events=ev_rows, match_tracking=trk_rows)
    for name, rows in tables.items():
        write(out, name, rows)
    return {k: len(v) for k, v in tables.items()}
