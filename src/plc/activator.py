"""Activator rules: data-driven conditions on bus events that trigger the orchestrator.

Rules are plain data so the same definitions can be created as Fabric Activator rules on the Eventstream
(see docs/ARCHITECTURE.md). Like Activator, a rule fires on a change (a new key), not on every event that satisfies it.
"""
from dataclasses import dataclass, field

RULES = [
    {"name": "player_fading", "field": "alerts", "op": "nonempty", "key": "alerts", "route": "fade"},
    {"name": "opponent_changed_shape", "field": "their_shifts", "op": "nonempty", "key": "their_shifts", "route": "opponent"},
    {"name": "goal", "field": "goals", "op": "gt", "value": 0, "key": "minute", "route": "goal"},
    {"name": "readiness_concern", "field": "concerns", "op": "nonempty", "key": "concerns", "route": "readiness"},
    {"name": "shape_issue", "field": "shape_issues", "op": "nonempty", "key": "shape_issues", "route": "shape"},
    {"name": "losing_late", "field": "late_deficit", "op": "gt", "value": 0, "key": "score", "route": "losing"},
    {"name": "leading_late", "field": "late_lead", "op": "gt", "value": 0, "key": "score", "route": "leading"},
    {"name": "half_time", "field": "minute", "op": "eq", "value": 45, "key": "minute", "route": "full"},
]
OPS = {"nonempty": lambda v, _: bool(v), "gt": lambda v, x: v > x, "eq": lambda v, x: v == x}


@dataclass
class Activator:
    rules: list = field(default_factory=lambda: RULES)
    seen: set = field(default_factory=set)

    def evaluate(self, payload: dict) -> list[dict]:
        fired = []
        for r in self.rules:
            if not OPS[r["op"]](payload.get(r["field"]), r.get("value")):
                continue
            key = (r["name"], repr(payload.get(r["key"])))
            if key not in self.seen:  # state change only
                self.seen.add(key)
                fired.append({"rule": r["name"], "route": r["route"], "minute": payload["minute"]})
        return fired
