from __future__ import annotations

import pytest
from core.safety import EngineProfile, SafetyViolation, validate_axis, validate_map_name, validate_value


def test_allowed_map_and_profile_caps() -> None:
    profile = EngineProfile(max_torque_nm=350, max_boost_bar=2.2, max_rail_bar=1600,
                            max_percent_increase=15, gearbox_limit_nm=350)
    validate_value(profile, "torque_limiter", 330, "Nm", original_max=300)
    with pytest.raises(SafetyViolation):
        validate_value(profile, "torque_limiter", 400, "Nm")


def test_prohibited_request_rejected_without_false_positive() -> None:
    validate_map_name("torque_limiter")
    with pytest.raises(SafetyViolation):
        validate_map_name("dpf_control")
    with pytest.raises(SafetyViolation):
        validate_map_name("lambda")


def test_axis_must_be_monotonic() -> None:
    validate_axis([1, 2, 3])
    with pytest.raises(SafetyViolation):
        validate_axis([1, 3, 2])
