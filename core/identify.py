from __future__ import annotations

import hashlib
import re
import zlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class FileIdentity:
    source_name: str
    family: str
    sw_number: str
    hw_number: str
    size_bytes: int
    dump_type: str
    crc32: str
    sha256: str
    warnings: tuple[str, ...]


def identify_dump(data: bytes, source_name: str = "") -> FileIdentity:
    """Identify basic file metadata without modifying the input bytes."""
    if not isinstance(data, bytes):
        raise TypeError("data must be immutable bytes")
    ascii_text = data.decode("ascii", errors="ignore")
    sw = _find_number(ascii_text, r"1037\d{6}")
    hw = _find_number(ascii_text, r"0281\d{6}")
    family = "unknown"
    text = ascii_text[:4096].lower()
    if "edc16" in text:
        family = "Bosch EDC16"
    elif "edc17" in text:
        family = "Bosch EDC17"
    elif len(data) >= 512 * 1024:
        family = "Bosch EDC17-like"
    elif len(data) >= 128 * 1024:
        family = "Bosch EDC16-like"
    warnings: list[str] = []
    if len(data) < 64 * 1024:
        warnings.append("Small file; it may be partial or truncated.")
    if not sw:
        warnings.append("No supported software number was found in the byte stream.")
    if not hw:
        warnings.append("No supported hardware number was found in the byte stream.")
    if family == "unknown":
        warnings.append("ECU family could not be inferred from size or text markers.")
    return FileIdentity(
        source_name=Path(source_name).name if source_name else "",
        family=family,
        sw_number=sw,
        hw_number=hw,
        size_bytes=len(data),
        dump_type="partial/unknown" if len(data) < 64 * 1024 else "binary dump (unverified)",
        crc32=f"{zlib.crc32(data) & 0xFFFFFFFF:08X}",
        sha256=hashlib.sha256(data).hexdigest(),
        warnings=tuple(warnings),
    )


def _find_number(text: str, pattern: str) -> str:
    match = re.search(pattern, text)
    return match.group(0) if match else ""
