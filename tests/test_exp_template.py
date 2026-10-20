from plc.experiments import template


def test_template_signals_have_evidence():
    sigs = template.run()
    assert sigs and all(0 <= s.value <= 1 and s.evidence for s in sigs)
