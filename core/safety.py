from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Iterable, Sequence


class SafetyViolation(ValueError):
    """Raised when a requested edit violates a hard safety invariant."""


# Deliberately use token matching instead of broad substrings (e.g. 'scr' in 'description').
_BLOCKED_TERMS = re.compile(
    r"\b(?:dpf|egr|scr|adblue|urea|catalyst|catalytic|lambda|oxygen\s+sensor|emissions?)\b",
    re.IGNORECASE,
)
_ALLOWED_MAPS = {
    "torque_limiter", "driver_wish", "fuel_dose", "smoke_limiter",
    "boost_target", "boost_limiter", "rail_pressure", "soi", "speed_limiter",
}


@dataclass(frozen=True, slots=True)
class EngineProfile:
    max_torque_nm: float = 400.0
    max_boost_bar: float = 2.5
    max_rail_bar: float = 1800.0
    max_percent_increase: float = 15.0
    gearbox_limit_nm: float = 380.0


def reject_prohibited_request(text: str) -> None:
    if _BLOCKED_TERMS.search(text):
        raise SafetyViolation("Request rejected: emissions-system defeat or modification is outside scope.")


def validate_map_name(name: str) -> None:
    reject_prohibited_request(name)
    if name not in _ALLOWED_MAPS:
        raise SafetyViolation("Map is not in the explicitly allowed Stage 1 map set.")


def validate_profile(profile: EngineProfile) -> None:
    fields = (profile.max_torque_nm, profile.max_boost_bar, profile.max_rail_bar,
              profile.max_percent_increase, profile.gearbox_limit_nm)
    if any(not math.isfinite(v) or v <= 0 for v in fields):
        raise SafetyViolation("Profile limits must be finite positive numbers.")
    if profile.max_percent_increase > 20:
        raise SafetyViolation("Profile increase cap cannot exceed the 20% hard limit.")
    if profile.max_torque_nm > profile.gearbox_limit_nm:
        raise SafetyViolation("Torque cap cannot exceed the gearbox limit.")


def validate_value(profile: EngineProfile, map_name: str, value: float, unit: str,
                   original_max: float | None = None) -> None:
    validate_map_name(map_name)
    validate_profile(profile)
    if not math.isfinite(value):
        raise SafetyViolation("Value must be finite.")
    limits = {
        "nm": min(profile.max_torque_nm, profile.gearbox_limit_nm),
        "bar": profile.max_boost_bar,
        "rail_bar": profile.max_rail_bar,
    }
    key = "rail_bar" if map_name == "rail_pressure" else unit.strip().lower()
    if key in limits and value > limits[key]:
        raise SafetyViolation(f"Requested value exceeds profile limit ({limits[key]} {unit}).")
    if original_max is not None:
        if not math.isfinite(original_max) or original_max < 0:
            raise SafetyViolation("Invalid original map maximum.")
        ceiling = original_max * (1 + profile.max_percent_increase / 100)
        if value > ceiling:
            raise SafetyViolation("Requested value exceeds the profile percentage-increase cap.")


def validate_axis(values: Iterable[float]) -> None:
    sequence = list(values)
    if any(not math.isfinite(value) for value in sequence):
        raise SafetyViolation("Axis values must be finite.")
    if len(sequence) > 1 and not (all(a <= b for a, b in zip(sequence, sequence[1:])) or
                                  all(a >= b for a, b in zip(sequence, sequence[1:]))):
        raise SafetyViolation("Axis must be monotonic.")


def validate_declared_changes(changed_addresses: Iterable[int], ranges: Sequence[tuple[int, int]]) -> None:
    """Ranges are half-open [start, end); every changed byte must be covered."""
    for address in changed_addresses:
        if address < 0 or not any(start <= address < end for start, end in ranges):
            raise SafetyViolation(f"Changed byte outside declared maps at 0x{address:X}.")
