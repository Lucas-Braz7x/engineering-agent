from __future__ import annotations

from pathlib import Path


def bundled_root() -> Path:
    return Path(__file__).resolve().parent / "bundled"
