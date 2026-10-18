"""Experiments read the bronze CSVs and return Signals the Tactician agent can use as tools."""
from dataclasses import dataclass


@dataclass
class Signal:
    name: str      # e.g. "set_piece_vulnerability"
    subject: str   # player or team the signal is about
    value: float   # 0-1 where possible, higher = stronger
    evidence: str  # one sentence quoting the numbers behind it, so the Fact-checker can verify it
