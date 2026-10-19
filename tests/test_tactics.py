from plc.engine import new_match
from plc.tactics import FORMATIONS, assess, recommend


def test_recommendation_is_best_fit_and_reasons_quote_the_profile():
    o = new_match(7)[0].profile  # high press, strong in the air, dangerous set pieces
    best = recommend(o)
    assert assess(best, o).verdict == "Best fit"
    assert "%" in assess("4-4-2", o).reasons[0]
    assert assess("5-3-2", o).fit != assess("3-4-3", o).fit


def test_worst_formation_is_risky():
    o = new_match(7)[0].profile
    assert any(assess(f, o).verdict == "Risky" for f in FORMATIONS)
