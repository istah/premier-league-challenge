from statistics import mean

from plc.squad import make_squad
from plc.tracking import track_match
from plc.training import run_training


def test_training_moves_ratings_deterministically():
    a, b = make_squad(1), make_squad(1)
    before = [p.rating for p in a]
    assert run_training(a, seed=2) == run_training(b, seed=2)
    assert [p.rating for p in a] != before


def test_low_hrv_player_fades_late():
    squad = make_squad(1)
    tired = squad[5]
    snaps = track_match(squad[:11], {tired.name: 0.6})
    d = lambda lo, hi: mean(s.distance_m for s in snaps if s.player == tired.name and lo <= s.minute <= hi)
    assert d(75, 90) < d(5, 40) * 0.9
