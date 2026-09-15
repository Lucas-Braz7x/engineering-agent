from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from eas.detection.models import DetectionResult


def _local_tag(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


def _framework_from_text(text: str) -> str | None:
    lower = text.lower()
    if "spring-boot" in lower or "springframework" in lower:
        return "spring-boot"
    if "quarkus" in lower:
        return "quarkus"
    if "micronaut" in lower:
        return "micronaut"
    return None


def _maven_artifact_id(root: Path, pom: Path) -> str:
    try:
        tree = ET.parse(pom)
    except (ET.ParseError, OSError):
        match = re.search(r"<artifactId>([^<]+)</artifactId>", pom.read_text(encoding="utf-8"))
        return match.group(1).strip() if match else root.name

    for elem in tree.getroot().iter():
        if _local_tag(elem.tag) == "artifactId" and elem.text:
            return elem.text.strip()
    return root.name


def detect_maven(root: Path, pom: Path) -> DetectionResult | None:
    try:
        text = pom.read_text(encoding="utf-8")
    except OSError:
        return None

    name = _maven_artifact_id(root, pom)
    framework = _framework_from_text(text)

    java_version = None
    props = re.search(
        r"<java\.version>([^<]+)</java\.version>|<maven\.compiler\.release>([^<]+)</maven\.compiler\.release>",
        text,
    )
    if props:
        java_version = (props.group(1) or props.group(2) or "").strip()

    signals = ["Java", "Maven"]
    if java_version:
        signals.append(f"Java {java_version}")
    if framework:
        signals.append(framework)
    signals.append("mvn test")

    return DetectionResult(
        project_name=name,
        language_name="java",
        language_version=java_version,
        framework_name=framework,
        package_manager_name="maven",
        testing_command="mvn test",
        build_command="mvn package",
        signals=signals,
    )


def detect_gradle(root: Path, gradle_file: Path) -> DetectionResult | None:
    try:
        text = gradle_file.read_text(encoding="utf-8")
    except OSError:
        return None

    framework = _framework_from_text(text)
    is_kotlin = "kotlin" in gradle_file.name or "org.jetbrains.kotlin" in text

    signals = ["Java", "Gradle"]
    if is_kotlin:
        signals.append("Kotlin")
    if framework:
        signals.append(framework)
    signals.append("gradle test")

    return DetectionResult(
        project_name=root.name,
        language_name="kotlin" if is_kotlin else "java",
        framework_name=framework,
        package_manager_name="gradle",
        testing_command="./gradlew test",
        build_command="./gradlew build",
        signals=signals,
    )
