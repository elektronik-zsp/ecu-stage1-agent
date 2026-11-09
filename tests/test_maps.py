from __future__ import annotations

import pytest
from core.maps import MapSpec, encode_map, read_map


def test_round_trip_leaves_original_unchanged() -> None:
    original = bytes(16)
    spec = MapSpec("torque_limiter", 2, 2, 2, 0.5, 0, "Nm")
    changed = encode_map(original, spec, [[10.0, 20.0], [30.0, 40.0]])
    assert original == bytes(16)
    assert read_map(changed, spec) == [[10.0, 20.0], [30.0, 40.0]]


def test_out_of_bounds_and_uint16_rejected() -> None:
    with pytest.raises(ValueError):
        read_map(bytes(2), MapSpec("x", 0, 2, 2, 1, 0, "Nm"))
    with pytest.raises(ValueError):
        encode_map(bytes(8), MapSpec("x", 0, 1, 1, 0.01, 0, "Nm"), [[700]])
