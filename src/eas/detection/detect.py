from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from eas.detection.extras import enrich_signals
from eas.detection.go_detect import detect_go
from eas.detection.java_detect import detect_gradle, detect_maven
from eas.detection.merge import merge_detection_results
from eas.detection.models import DetectionResult
from eas.detection.node_detect import detect_node
from eas.detection.python_detect import detect_python
from eas.detection.rust_detect import detect_rust

Detector = Callable[[Path, Path], DetectionResult | None]

# Order defines primary stack when multiple manifests exist at repo root (monorepo).
MANIFEST_DETECTORS: list[tuple[str, Detector]] = [
    ("pyproject.toml", detect_python),
    ("package.json", detect_node),
    ("go.mod", detect_go),
    ("Cargo.toml", detect_rust),
    ("pom.xml", detect_maven),
    ("build.gradle.kts", detect_gradle),
    ("build.gradle", detect_gradle),
]


def detect_project(root: Path) -> DetectionResult:
    """Detect stack from root-level manifests; merge signals when monorepo."""
    collected: list[tuple[str, DetectionResult]] = []

    for manifest_name, detector in MANIFEST_DETECTORS:
        path = root / manifest_name
        if not path.is_file():
            continue
        result = detector(root, path)
        if result is not None:
            collected.append((manifest_name, result))

    if not collected:
        result = DetectionResult(
            project_name=root.name,
            signals=["(no manifest matched — edit .ai/project.yaml manually)"],
        )
        return enrich_signals(root, result)

    merged = merge_detection_results(collected)
    return enrich_signals(root, merged)
