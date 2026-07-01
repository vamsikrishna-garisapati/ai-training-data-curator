#!/usr/bin/env python3
"""Validate .actor/ config files against official Apify JSON schemas.

Run before push to catch the same errors Apify Cloud build reports:
  python scripts/validate_apify.py
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver

ROOT = Path(__file__).resolve().parents[1]
ACTOR_DIR = ROOT / ".actor"

SCHEMA_VERSION = "0.7"
SCHEMA_BASE = f"https://apify-projects.github.io/actor-json-schemas"


def _fetch_schema(name: str) -> dict:
    url = f"{SCHEMA_BASE}/{name}?v={SCHEMA_VERSION}"
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.load(response)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _collect_errors(validator: Draft202012Validator, data: dict, label: str) -> list[str]:
    messages: list[str] = []
    for error in sorted(validator.iter_errors(data), key=lambda item: list(item.path)):
        path = "/".join(str(part) for part in error.path) or "(root)"
        messages.append(f"{label}: {path}: {error.message}")
    return messages


def main() -> int:
    errors: list[str] = []

    actor_schema = _fetch_schema("actor.json")
    input_schema = _fetch_schema("input.json")
    input_ide_schema = _fetch_schema("input.ide.json")
    output_schema = _fetch_schema("output.json")
    dataset_schema = _fetch_schema("dataset.json")

    resolver = RefResolver.from_schema(
        actor_schema,
        store={
            "https://apify.com/schemas/v1/output.json": output_schema,
            "https://apify.com/schemas/v1/dataset.json": dataset_schema,
        },
    )

    actor_path = ACTOR_DIR / "actor.json"
    input_path = ACTOR_DIR / "input_schema.json"
    output_path = ACTOR_DIR / "output_schema.json"
    readme_path = ACTOR_DIR / "README.md"
    dockerfile_path = ROOT / "Dockerfile"

    for path in (actor_path, input_path, output_path, readme_path, dockerfile_path):
        if not path.exists():
            errors.append(f"Missing required file: {path.relative_to(ROOT)}")

    if errors:
        for message in errors:
            print(message, file=sys.stderr)
        return 1

    actor = _load_json(actor_path)
    actor_input = _load_json(input_path)
    actor_output = _load_json(output_path)

    errors.extend(_collect_errors(Draft202012Validator(actor_schema, resolver=resolver), actor, "actor.json"))
    errors.extend(_collect_errors(Draft202012Validator(input_schema), actor_input, "input_schema.json"))
    errors.extend(_collect_errors(Draft202012Validator(input_ide_schema), actor_input, "input_schema.json (IDE)"))
    errors.extend(_collect_errors(Draft202012Validator(output_schema), actor_output, "output_schema.json"))

    dataset = actor.get("storages", {}).get("dataset")
    if isinstance(dataset, dict):
        errors.extend(
            _collect_errors(
                Draft202012Validator(dataset_schema, resolver=resolver),
                dataset,
                "actor.json storages.dataset",
            )
        )

    dockerfile_ref = actor.get("dockerfile", "../Dockerfile")
    dockerfile_resolved = (ACTOR_DIR / dockerfile_ref).resolve()
    if not dockerfile_resolved.exists():
        errors.append(f"actor.json dockerfile not found: {dockerfile_ref}")

    readme_ref = actor.get("readme")
    if readme_ref:
        readme_resolved = ACTOR_DIR / readme_ref
        if not readme_resolved.exists():
            errors.append(f"actor.json readme not found: {readme_ref}")

    version = actor.get("version", "")
    parts = str(version).split(".")
    if len(parts) != 2 or not all(part.isdigit() for part in parts):
        errors.append(f"actor.json: version must be [Number].[Number], got {version!r}")

    for name, props in actor_input.get("properties", {}).items():
        if not props.get("description"):
            errors.append(f"input_schema.json: properties.{name}.description is required")

    for name, props in actor_output.get("properties", {}).items():
        for field in ("type", "template", "title"):
            if field not in props:
                errors.append(f"output_schema.json: properties.{name}.{field} is required")

    if errors:
        print("Apify validation failed:", file=sys.stderr)
        for message in errors:
            print(f"  - {message}", file=sys.stderr)
        return 1

    print("Apify validation passed (actor.json, input_schema.json, output_schema.json, dataset schema)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
