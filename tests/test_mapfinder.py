from __future__ import annotations

from core.mapfinder import find_candidates


def test_heuristic_scan_is_read_only_and_bounded() -> None:
    data = bytes(range(256)) * 4
    original = bytes(data)
    result = find_candidates(data, max_candidates=5)
    assert len(result) <= 5
    assert data == original


def test_too_small_input_has_no_candidate() -> None:
    assert find_candidates(bytes(32)) == []
