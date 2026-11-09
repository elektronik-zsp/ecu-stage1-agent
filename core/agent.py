from __future__ import annotations

import re

from core.safety import SafetyViolation, reject_prohibited_request

SYSTEM_PROMPT = (
    "You are a constrained Stage 1 planning assistant. You may explain workflow and propose "
    "validation steps, but must never edit bytes directly. Do not assist with disabling, "
    "bypassing, or modifying emissions systems. Requests involving emissions defeat must be refused."
)


def plan_locally(prompt: str) -> str:
    """Safe offline stub; actual API/tool-use integration is intentionally not enabled yet."""
    try:
        reject_prohibited_request(prompt)
    except SafetyViolation:
        return "Request refused: emissions-system defeat or modification is outside the supported scope."
    if re.search(r"\b(?:write|flash|apply|modify|tune)\b", prompt, re.IGNORECASE):
        return ("I can help review a declared-map plan and safety checks. This prototype does not "
                "generate calibration values or write/flash ECU files.")
    return "I can explain the inspection workflow. No file was changed."
