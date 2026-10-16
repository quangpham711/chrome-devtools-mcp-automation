"""
Unit tests for src/webtest/test_loader.py (loading and validating YAML test cases).
"""

from pathlib import Path

import pytest

from src.webtest.test_loader import get_test_case_by_id, load_test_cases, load_test_suite

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_load_sample_yaml_suite() -> None:
    sample_path = PROJECT_ROOT / "test_cases" / "sample.yaml"
    suite = load_test_suite(sample_path)

    assert suite["suite_name"] == "Bộ kịch bản kiểm thử mẫu (Sample Web Test Suite)"
    assert suite["target_url"] == "https://the-internet.herokuapp.com"
    assert suite["requires_chat_gate_login"] is False
    assert len(suite["test_cases"]) == 3
    assert suite["test_cases"][0].id == "TC_01"
    assert suite["test_cases"][0].module == "Authentication"


def test_load_company_testcases_yaml_and_lookup() -> None:
    company_path = PROJECT_ROOT / "test_cases" / "company_testcases.yaml"
    cases = load_test_cases(company_path)
    assert len(cases) == 4

    tc = get_test_case_by_id(company_path, "COMP_TC_03")
    assert tc is not None
    assert tc.module == "Customer Management"

    missing = get_test_case_by_id(company_path, "NON_EXISTENT")
    assert missing is None


def test_load_top_level_list_yaml(tmp_path: Path) -> None:
    yaml_file = tmp_path / "list_only.yaml"
    yaml_file.write_text(
        """
- id: "TC_10"
  module: "Search"
  feature: "Tìm kiếm nhanh"
  description: "Kiểm tra ô tìm kiếm"
  steps:
    - "Nhập từ khóa"
    - "Nhấn Enter"
  expected_result: "Hiển thị kết quả"
""",
        encoding="utf-8",
    )
    cases = load_test_cases(yaml_file)
    assert len(cases) == 1
    assert cases[0].id == "TC_10"


def test_loader_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="not found"):
        load_test_cases(tmp_path / "does_not_exist.yaml")


def test_loader_invalid_yaml_syntax_raises(tmp_path: Path) -> None:
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("test_cases:\n  - id: [unclosed_bracket\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid YAML syntax"):
        load_test_cases(bad_yaml)


def test_loader_missing_required_field_raises(tmp_path: Path) -> None:
    missing_field_yaml = tmp_path / "missing.yaml"
    missing_field_yaml.write_text(
        """
test_cases:
  - id: "TC_ERR"
    module: "Auth"
    feature: "Login"
    description: "Thiếu steps và expected_result"
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="missing required field\\(s\\): steps, expected_result"):
        load_test_cases(missing_field_yaml)


def test_loader_duplicate_id_raises(tmp_path: Path) -> None:
    dup_yaml = tmp_path / "dup.yaml"
    dup_yaml.write_text(
        """
test_cases:
  - id: "TC_DUP"
    module: "M1"
    feature: "F1"
    description: "D1"
    steps: ["S1"]
    expected_result: "E1"
  - id: "TC_DUP"
    module: "M2"
    feature: "F2"
    description: "D2"
    steps: ["S2"]
    expected_result: "E2"
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Duplicate TestCase id 'TC_DUP'"):
        load_test_cases(dup_yaml)
