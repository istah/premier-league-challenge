from plc.events import generate_match


def test_deterministic_and_ordered():
    a, b = generate_match(seed=1), generate_match(seed=1)
    assert a == b
    assert [e.minute for e in a] == sorted(e.minute for e in a)
