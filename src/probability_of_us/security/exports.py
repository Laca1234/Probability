"""Atomic, bounded, spreadsheet-safe export functions."""

from __future__ import annotations

import csv
import json
import os
import tempfile
from pathlib import Path
from typing import Any

MAX_EXPORT_BYTES = 20 * 1024 * 1024


def _atomic_write(path: str | Path, content: bytes) -> Path:
    destination = Path(path)
    if len(content) > MAX_EXPORT_BYTES:
        raise ValueError("Export exceeds the 20 MB limit.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".pou-", suffix=".tmp", dir=destination.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, destination)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise
    return destination


def safe_json_export(path: str | Path, data: dict[str, Any]) -> Path:
    body = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False).encode("utf-8")
    return _atomic_write(path, body)


def spreadsheet_safe_cell(value: Any) -> str:
    text = str(value)
    probe = text.lstrip("\ufeff\t\r\n ")
    if probe.startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


def safe_csv_export(path: str | Path, headers: list[str], rows: list[list[Any]]) -> Path:
    import io
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow([spreadsheet_safe_cell(value) for value in headers])
    for row in rows:
        writer.writerow([spreadsheet_safe_cell(value) for value in row])
    return _atomic_write(path, output.getvalue().encode("utf-8-sig"))


def safe_markdown_export(path: str | Path, text: str) -> Path:
    return _atomic_write(path, text.encode("utf-8"))

