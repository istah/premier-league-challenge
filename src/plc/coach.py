"""Coach override: a dictated or typed instruction always beats the AI suggestion."""
import re
from dataclasses import dataclass
from difflib import get_close_matches

from .squad import Player

ON_WORDS = ("bring on", "put on", "send on", "with", "on")


@dataclass
class Decision:
    off: str
    on: str
    source: str  # "coach" or "ai"


def parse_command(transcript: str, squad: list[Player]) -> Decision | None:
    """'take off Vance, bring on Haas' / 'replace Vance with Haas' / 'bring on Haas for Vance'."""
    names = {p.name.lower(): p.name for p in squad}
    off = on = None
    prev: list[str] = []  # words since the last player name
    for w in re.findall(r"[\w-]+", transcript.lower()):
        m = get_close_matches(w, names, n=1, cutoff=0.8)
        if not m:
            prev.append(w)
            continue
        context = " ".join(prev)
        is_on = any(context.endswith(k) for k in ON_WORDS)
        if is_on and on is None:
            on = names[m[0]]
        elif off is None:
            off = names[m[0]]
        prev = []
    return Decision(off, on, "coach") if off and on else None


def decide(ai: Decision | None, transcript: str | None, squad: list[Player]) -> Decision | None:
    return (transcript and parse_command(transcript, squad)) or ai


DEEPER = {"deeper", "lower", "drop", "back", "deep"}
HIGHER = {"higher", "push", "forward"}
WIDER = {"wider", "wide", "out"}
NARROWER = {"narrower", "tuck", "inside"}


def parse_orders(transcript: str, xi: list[Player], step: int = 12) -> dict[str, dict[str, int]]:
    """'Haas drop wider', 'Moretti push higher and tuck in': direction words after a player's name apply to him."""
    names = {p.name.lower(): p.name for p in xi}
    out: dict[str, dict[str, int]] = {}
    who = None
    for w in re.findall(r"[\w-]+", transcript.lower()):
        m = get_close_matches(w, names, n=1, cutoff=0.8)
        if m:
            who = names[m[0]]
            continue
        if who and w in DEEPER | HIGHER | WIDER | NARROWER:
            o = out.setdefault(who, {})
            if w in DEEPER | HIGHER:
                o["depth"] = -step if w in DEEPER else step
            else:
                o["width"] = step if w in WIDER else -step
    return out
