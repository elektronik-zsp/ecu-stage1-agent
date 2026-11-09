from __future__ import annotations

from core.diffing import diff_bytes


def test_diff_flags_outside_declared_range() -> None:
    before = bytes(16)
    after = bytearray(before)
    after[3] = 4
    report = diff_bytes(before, bytes(after), ((0, 8),))
    assert report.total_changed_bytes == 1
    assert report.regions[0].critical is False
    assert diff_bytes(before, bytes(after)).critical_out_of_bounds


def test_length_change_is_critical() -> None:
    assert diff_bytes(bytes(4), bytes(5), ((0, 10),)).critical_out_of_bounds
