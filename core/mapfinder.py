from __future__ import annotations

import struct
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MapCandidate:
    address: int
    rows: int
    cols: int
    confidence: float
    note: str = "Heuristic candidate; requires expert verification"


def _monotonic_score(values: list[int]) -> float:
    if len(values) < 2:
        return 0.0
    asc = sum(a <= b for a, b in zip(values, values[1:]))
    desc = sum(a >= b for a, b in zip(values, values[1:]))
    return max(asc, desc) / (len(values) - 1)


def find_candidates(data: bytes, endian: str = "little", max_candidates: int = 64) -> list[MapCandidate]:
    """Read-only heuristic scan for grid-shaped regions; never writes to the file."""
    if endian not in {"little", "big"}:
        raise ValueError("endian must be 'little' or 'big'")
    if max_candidates <= 0:
        return []
    fmt = "<H" if endian == "little" else ">H"
    found: list[MapCandidate] = []
    seen: set[tuple[int, int, int]] = set()
    for rows, cols in ((16, 16), (16, 10), (12, 10)):
        size = rows * cols * 2
        for address in range(0, len(data) - size + 1, 2):
            key = (address, rows, cols)
            if key in seen:
                continue
            values = list(struct.unpack_from(f"{fmt[0]}{rows * cols}H", data, address))
            # Score successive row and column boundaries rather than arbitrary byte runs.
            row_scores = [_monotonic_score(values[r * cols:(r + 1) * cols]) for r in range(rows)]
            col_scores = [_monotonic_score(values[c::cols]) for c in range(cols)]
            confidence = 0.5 * (sum(row_scores) / rows) + 0.5 * (sum(col_scores) / cols)
            if confidence >= 0.72:
                found.append(MapCandidate(address, rows, cols, round(confidence, 3)))
                seen.add(key)
                if len(found) >= max_candidates:
                    return found
    return found
