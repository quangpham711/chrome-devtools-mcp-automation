"""
YAML Test Case Loader and Validator for AI Web Testing Hybrid Architecture.
Supports loading and validating test suites from test_cases/*.yaml.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import TestCase

REQUIRED_FIELDS = ("id", "module", "feature", "description", "steps", "expected_result")


def _parse_test_case_dict(raw: Any, index: int, source_name: str) -> TestCase:
    """Validate and convert a raw dictionary from YAML into a TestCase instance."""
    if not isinstance(raw, dict):
        raise ValueError(
            f"Invalid test case entry #{index} in '{source_name}': expected a mapping/dict, got {type(raw).__name__}."
        )

    missing = [field for field in REQUIRED_FIELDS if field not in raw or raw[field] is None]
    if missing:
        case_label = raw.get("id", f"#{index}")
        raise ValueError(
            f"Test case '{case_label}' in '{source_name}' is missing required field(s): {', '.join(missing)}."
        )

    steps_raw = raw["steps"]
    if not isinstance(steps_raw, list):
        raise ValueError(
            f"Test case '{raw.get('id', f'#{index}')}' in '{source_name}': 'steps' must be a YAML list."
        )

    try:
        return TestCase(
            id=str(raw["id"]),
            module=str(raw["module"]),
            feature=str(raw["feature"]),
            description=str(raw["description"]),
            steps=[str(s) for s in steps_raw],
            expected_result=str(raw["expected_result"]),
        )
    except ValueError as exc:
        raise ValueError(f"Validation error in '{source_name}' (entry #{index}): {exc}") from exc


def load_test_suite(yaml_path: str | Path) -> dict[str, Any]:
    """
    Load full test suite metadata and validated TestCase objects from a YAML file.

    Returns a dict with:
    - suite_name: str
    - target_url: str
    - requires_chat_gate_login: bool
    - test_cases: list[TestCase]
    """
    path = Path(yaml_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"YAML test case file not found: '{path}'")

    try:
        content = path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML syntax in '{path.name}': {exc}") from exc

    if data is None:
        raise ValueError(f"YAML file '{path.name}' is empty.")

    suite_name = path.stem
    target_url = ""
    requires_chat_gate_login = False

    if isinstance(data, list):
        raw_cases = data
    elif isinstance(data, dict):
        suite_name = str(data.get("suite_name", path.stem)).strip()
        target_url = str(data.get("target_url", "")).strip()
        requires_chat_gate_login = bool(data.get("requires_chat_gate_login", False))
        if "test_cases" not in data:
            raise ValueError(
                f"YAML file '{path.name}' must contain a 'test_cases' list key or be a top-level list of test cases."
            )
        raw_cases = data["test_cases"]
    else:
        raise ValueError(
            f"YAML file '{path.name}' root must be a dict or list, got {type(data).__name__}."
        )

    if not isinstance(raw_cases, list) or len(raw_cases) == 0:
        raise ValueError(f"YAML file '{path.name}' must contain at least one test case in 'test_cases'.")

    cases: list[TestCase] = []
    seen_ids: set[str] = set()

    for idx, item in enumerate(raw_cases, start=1):
        tc = _parse_test_case_dict(item, index=idx, source_name=path.name)
        if tc.id in seen_ids:
            raise ValueError(f"Duplicate TestCase id '{tc.id}' found in '{path.name}'.")
        seen_ids.add(tc.id)
        cases.append(tc)

    return {
        "suite_name": suite_name,
        "target_url": target_url,
        "requires_chat_gate_login": requires_chat_gate_login,
        "test_cases": cases,
    }


def load_test_cases(yaml_path: str | Path) -> list[TestCase]:
    """Load and validate a list of TestCase objects from a YAML file."""
    suite = load_test_suite(yaml_path)
    return suite["test_cases"]


def get_test_case_by_id(yaml_path: str | Path, case_id: str) -> TestCase | None:
    """Look up a specific TestCase by its ID from a YAML file."""
    target = case_id.strip()
    for tc in load_test_cases(yaml_path):
        if tc.id == target:
            return tc
    return None
