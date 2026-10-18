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
