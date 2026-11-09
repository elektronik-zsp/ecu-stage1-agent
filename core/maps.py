from __future__ import annotations

import json
import math
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence


@dataclass(frozen=True, slots=True)
class MapSpec:
    name: str
    address: int
    rows: int
    cols: int
    factor: float
    offset: float
    unit: str
    endian: str = "little"

    @property
    def end(self) -> int:
        return self.address + self.rows * self.cols * 2

    @property
    def size(self) -> int:
        return self.rows * self.cols * 2


def validate_spec(spec: MapSpec, file_size: int | None = None) -> None:
    if not spec.name.strip() or spec.address < 0 or spec.rows <= 0 or spec.cols <= 0:
        raise ValueError("Invalid map name, address, or dimensions")
    if not math.isfinite(spec.factor) or spec.factor <= 0 or not math.isfinite(spec.offset):
        raise ValueError("Map factor must be positive and factor/offset finite")
    if spec.endian not in {"little", "big"}:
        raise ValueError("Endian must be 'little' or 'big'")
    if file_size is not None and spec.end > file_size:
        raise ValueError("Map region extends beyond file")


def read_map(data: bytes, spec: MapSpec) -> list[list[float]]:
    validate_spec(spec, len(data))
    fmt = "<H" if spec.endian == "little" else ">H"
    result: list[list[float]] = []
    for row in range(spec.rows):
        values = []
        for col in range(spec.cols):
            pos = spec.address + 2 * (row * spec.cols + col)
            raw = struct.unpack_from(fmt, data, pos)[0]
            values.append(raw * spec.factor + spec.offset)
        result.append(values)
    return result


def encode_map(data: bytes, spec: MapSpec, matrix: Sequence[Sequence[float]]) -> bytes:
    """Return a modified copy; input bytes remain untouched."""
    validate_spec(spec, len(data))
    if len(matrix) != spec.rows or any(len(row) != spec.cols for row in matrix):
        raise ValueError("Matrix shape does not match map dimensions")
    output = bytearray(data)
    fmt = "<H" if spec.endian == "little" else ">H"
    for row in range(spec.rows):
        for col in range(spec.cols):
            value = float(matrix[row][col])
            if not math.isfinite(value):
                raise ValueError("Map values must be finite")
            raw = round((value - spec.offset) / spec.factor)
            if not 0 <= raw <= 65535:
                raise ValueError("Value does not fit uint16 after conversion")
            struct.pack_into(fmt, output, spec.address + 2 * (row * spec.cols + col), raw)
    return bytes(output)


def load_sw_database(directory: str | Path) -> dict[str, dict[str, Any]]:
    """Load SW JSON documents. No real-world map definitions are bundled."""
    result: dict[str, dict[str, Any]] = {}
    for path in sorted(Path(directory).glob("*.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            raise ValueError(f"Expected a JSON object in {path}")
        result.update(document)
    return result
