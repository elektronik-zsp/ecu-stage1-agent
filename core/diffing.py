from __future__ import annotations

import hashlib
import zlib
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DiffRegion:
    start: int
    length: int
    original: bytes
    modified: bytes
    critical: bool


@dataclass(frozen=True, slots=True)
class DiffReport:
    regions: tuple[DiffRegion, ...]
    total_changed_bytes: int
    critical_out_of_bounds: bool


def diff_bytes(original: bytes, modified: bytes,
               declared_ranges: tuple[tuple[int, int], ...] = ()) -> DiffReport:
    if len(original) != len(modified):
        return DiffReport((DiffRegion(min(len(original), len(modified)), abs(len(original)-len(modified)),
                                      original[min(len(original),len(modified)):],
                                      modified[min(len(original),len(modified)):], True),),
                          abs(len(original)-len(modified)), True)
    changed = [i for i, (a, b) in enumerate(zip(original, modified)) if a != b]
    regions: list[DiffRegion] = []
    if not changed:
        return DiffReport((), 0, False)
    start = previous = changed[0]
    for address in changed[1:] + [len(original) + 1]:
        if address != previous + 1:
            end = previous + 1
            critical = any(not any(lo <= i < hi for lo, hi in declared_ranges) for i in range(start, end))
            regions.append(DiffRegion(start, end-start, original[start:end], modified[start:end], critical))
            start = address
        previous = address
    return DiffReport(tuple(regions), len(changed), any(region.critical for region in regions))


def checksums(data: bytes) -> tuple[str, str]:
    return f"{zlib.crc32(data) & 0xFFFFFFFF:08X}", hashlib.sha256(data).hexdigest()
