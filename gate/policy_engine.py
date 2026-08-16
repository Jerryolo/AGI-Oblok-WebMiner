"""Deterministic policy layer; rules are deliberately reviewable and fail closed."""
from dataclasses import dataclass
from enum import Enum


class Verdict(str, Enum):
    ACT = "ACT NOW"
    WAIT = "WAIT"
    SILENCE = "SILENCE"
    REJECT = "REJECT"


@dataclass(frozen=True)
class Decision:
    verdict: Verdict
    reason: str


def evaluate(text: str, operation: str = "CHAT", risk: str = "low") -> Decision:
    normalized = text.lower()
    if operation not in {"CHAT", "TRANSACT"} or risk not in {"low", "medium", "high", "critical"}:
        return Decision(Verdict.REJECT, "invalid policy attributes")
    if any(term in normalized for term in ("exfiltrate", "bypass audit", "steal key", "disable safety")):
        return Decision(Verdict.REJECT, "adversarial or prohibited intent")
    if risk == "critical":
        return Decision(Verdict.SILENCE, "critical risk requires isolation and human review")
    if risk == "high" or any(term in normalized for term in ("credential", "personal data", "secret")):
        return Decision(Verdict.WAIT, "elevated risk requires human review")
    return Decision(Verdict.ACT, "policy checks passed")
