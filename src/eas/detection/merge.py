from __future__ import annotations

from dataclasses import replace

from eas.detection.models import DetectionResult


def merge_detection_results(
    collected: list[tuple[str, DetectionResult]],
) -> DetectionResult:
    """Pick primary stack by manifest priority; merge stdout signals from all manifests."""
    if not collected:
        raise ValueError("collected must not be empty")

    manifests = [name for name, _ in collected]
    primary = collected[0][1]

    merged_signals: list[str] = []
    for _, result in collected:
        merged_signals.extend(result.signals)
    merged_signals = list(dict.fromkeys(merged_signals))

    database_name = primary.database_name
    for _, result in collected:
        if result.database_name and not database_name:
            database_name = result.database_name

    return replace(
        primary,
        database_name=database_name,
        signals=merged_signals,
        manifests=manifests,
        monorepo=len(manifests) > 1,
    )
