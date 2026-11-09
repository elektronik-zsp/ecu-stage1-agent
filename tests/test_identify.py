from __future__ import annotations

from core.identify import identify_dump


def test_identify_hashes_and_warnings() -> None:
    data = b"EDC17 1037123456 0281123456" + bytes(128)
    result = identify_dump(data, "sample.bin")
    assert result.family == "Bosch EDC17"
    assert result.sw_number == "1037123456"
    assert result.hw_number == "0281123456"
    assert result.size_bytes == len(data)
    assert len(result.sha256) == 64
    assert result.crc32
    assert result.warnings
