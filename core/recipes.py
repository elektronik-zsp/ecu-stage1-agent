from __future__ import annotations

from dataclasses import dataclass
from core.safety import EngineProfile, validate_value


@dataclass(frozen=True, slots=True)
class RecipeStep:
    map_name: str
    operation: str
    unit: str
    value: float
    profile_limit: float


def plan_step(profile: EngineProfile, map_name: str, unit: str, value: float,
              original_max: float | None = None) -> RecipeStep:
    """Validate and describe a single physical-unit value; no bytes are edited here."""
    validate_value(profile, map_name, value, unit, original_max)
    limit = profile.gearbox_limit_nm if unit.lower() == "nm" else (
        profile.max_rail_bar if map_name == "rail_pressure" else profile.max_boost_bar
    )
    return RecipeStep(map_name, "set", unit, value, limit)
