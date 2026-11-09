from __future__ import annotations

from html import escape
from typing import Any

NOCHK_WARNING = "Sumy kontrolne niepoprawione, plik wymaga programatora z automatyczną korekcją przy zapisie."


def build_markdown_report(identity: Any, warnings: list[str] | tuple[str, ...], changes: list[str] | None = None) -> str:
    lines = ["# ECU Stage 1 Agent — report", "", f"- File: `{identity.source_name}`",
             f"- Family: {identity.family}", f"- SW: {identity.sw_number or 'not found'}",
             f"- HW: {identity.hw_number or 'not found'}", f"- Size: {identity.size_bytes} bytes",
             f"- Original CRC32: `{identity.crc32}`", f"- Original SHA-256: `{identity.sha256}`", "", "## Warnings"]
    lines.extend(f"- {warning}" for warning in warnings) if warnings else lines.append("- None")
    lines.extend(["", "## Changes"])
    lines.extend(f"- {change}" for change in (changes or ["No changes recorded."]))
    lines.extend(["", "## Checksum notice", f"> {NOCHK_WARNING}"])
    return "\n".join(lines)


def build_html_report(markdown: str) -> str:
    return "<!doctype html><meta charset=\"utf-8\"><pre>" + escape(markdown) + "</pre>"
