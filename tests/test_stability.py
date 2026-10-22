import csv
import itertools
import random
from pathlib import Path

import pytest

from plc import fatigue
from plc.dataset import build
from plc.engine import PRESETS, Match, new_match, probability
from plc.squad import make_squad
from plc.tracking import track_match


def legacy(played, r):  # the unbounded formula that tracking.py and engine.py carried before fatigue.py
    return max(0, played - 55) / 35 * max(0, 1 - r) * 3 if r < 0.9 else 0


GRID = [(p, r / 100) for p in range(0, 160, 5) for r in range(55, 121, 5)]


def test_fade_stays_within_bounds():
    assert all(0 <= fatigue.fade(p, r) <= fatigue.F_MAX < 1 for p, r in GRID)


def test_fade_equals_the_original_wherever_the_original_was_valid():
    assert all(fatigue.fade(p, r) == pytest.approx(legacy(p, r)) for p, r in GRID if legacy(p, r) <= fatigue.F_MAX)
    assert all(fatigue.fade(p, r) == fatigue.F_MAX for p, r in GRID if legacy(p, r) > fatigue.F_MAX)  # and is only capped where it was not


def test_fade_grows_with_time_and_with_lower_readiness():
    assert all(fatigue.fade(p, r) <= fatigue.fade(p + 5, r) for p, r in GRID)
    assert all(fatigue.fade(p, r) >= fatigue.fade(p, r + 0.05) for p, r in GRID)


def test_fade_has_no_new_discontinuity():
    # The original step at the HRV threshold is kept on purpose (GAIN * 0.1 = 0.3 at full ramp). Nothing else may jump.
    assert fatigue.fade(90, 0.9) == 0 and fatigue.fade(90, 0.8999) == pytest.approx(0.3, abs=1e-3)
    others = [abs(fatigue.fade(p, r / 1000) - fatigue.fade(p, r / 1000 + 0.001)) for p in range(0, 160, 5) for r in range(600, 1100) if r != 899]
    assert max(others) < 0.01 * 3  # slope is at most GAIN per unit of ratio
    assert all(abs(fatigue.fade(p, 0.8) - fatigue.fade(p + 0.1, 0.8)) < 0.01 for p in range(0, 160))


def test_probability_is_clamped():
    assert probability(-2.0) == 0.0 and probability(0.4) == 0.4 and probability(1.7) == 1.0


def _corner_matches():
    keys = list(PRESETS["balanced"])
    for combo in itertools.islice(itertools.product((0, 100), repeat=len(keys)), 0, 128, 7):
        for hrv in (0.6, 1.0):
            m, _ = new_match(1)
            for p in m.xi:
                m.hrv[p.name] = hrv
            m.wellness = {}
            m.set_instructions(**dict(zip(keys, combo)))
            yield m


def test_engine_outputs_stay_physical_at_extreme_sliders_and_hrv():
    for m in _corner_matches():
        while not m.finished:
            m.tick()
            assert m.strength() >= 0 and all(0 <= m.fade(p) <= fatigue.F_MAX for p in m.xi)
        assert all(s.distance_m >= 0 and s.sprints >= 0 and s.hr <= 205 for s in m.snaps)


def test_default_scenario_has_no_negative_values_over_many_seeds():
    for seed in range(40):
        m, _ = new_match(seed)
        while not m.finished:
            m.tick()
        assert min(s.distance_m for s in m.snaps) >= 0 and m.strength() > 0


def test_bounded_tracker_never_goes_negative_but_default_stays_legacy():
    squad = make_squad(1)
    hrv = {squad[5].name: 0.6}
    old, new = track_match(squad[:11], hrv, 0), track_match(squad[:11], hrv, 0, bounded=True)
    assert min(s.distance_m for s in old) < 0 <= min(s.distance_m for s in new)
    assert [s.distance_m for s in old if s.minute <= 55] == [s.distance_m for s in new if s.minute <= 55]  # before onset nothing differs


def test_bronze_seed0_still_regenerates_byte_for_byte(tmp_path):
    build(tmp_path, seed=0)
    committed = Path(__file__).parent.parent / "data" / "bronze"
    assert sorted(p.name for p in tmp_path.glob("*.csv")) == sorted(p.name for p in committed.glob("*.csv"))
    for f in committed.glob("*.csv"):
        assert (tmp_path / f.name).read_bytes() == f.read_bytes(), f.name


def test_match_is_still_deterministic_after_the_patch():
    a, _ = new_match(11)
    b, _ = new_match(11)
    while not a.finished:
        a.tick(), b.tick()
    assert a.snaps == b.snaps and a.score == b.score
