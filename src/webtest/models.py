"""
Data models for AI Web Testing Hybrid Architecture.
Defines ErrorCode, TestStatus, TestCase, and TestResult with F12 Console & Network Root Cause formatting.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ErrorCode(str, Enum):
    """Standard error classification codes for failed web test cases."""

    NONE = "NONE"
    UI_ERROR = "UI_ERROR"
    CONSOLE_ERROR = "CONSOLE_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    ASSERTION_ERROR = "ASSERTION_ERROR"
    AUTH_ERROR = "AUTH_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class TestStatus(str, Enum):
    """Execution status of a test case."""

    __test__ = False

    PASS = "PASS"
    FAIL = "FAIL"


_NUMBERED_STEP_PATTERN = re.compile(r"^\s*\d+[\.\)]\s+")


@dataclass
class TestCase:
    """Represents a structured QA test case loaded from YAML or natural language prompt."""

    __test__ = False

    id: str
    module: str
    feature: str
    description: str
    steps: list[str]
    expected_result: str

    def __post_init__(self) -> None:
        self.id = str(self.id).strip()
        self.module = str(self.module).strip()
        self.feature = str(self.feature).strip()
        self.description = str(self.description).strip()
        self.expected_result = str(self.expected_result).strip()

        if not self.id:
            raise ValueError("TestCase 'id' must not be empty.")
        if not self.module:
            raise ValueError(f"TestCase '{self.id}': 'module' must not be empty.")
        if not self.feature:
            raise ValueError(f"TestCase '{self.id}': 'feature' must not be empty.")
        if not self.description:
            raise ValueError(f"TestCase '{self.id}': 'description' must not be empty.")
        if not self.expected_result:
            raise ValueError(f"TestCase '{self.id}': 'expected_result' must not be empty.")

        if not isinstance(self.steps, list) or len(self.steps) == 0:
            raise ValueError(f"TestCase '{self.id}': 'steps' must be a non-empty list of strings.")

        cleaned_steps: list[str] = []
        for idx, step in enumerate(self.steps, start=1):
            step_str = str(step).strip()
            if not step_str:
                raise ValueError(f"TestCase '{self.id}': step #{idx} must not be empty.")
            cleaned_steps.append(step_str)
        self.steps = cleaned_steps

    def formatted_steps(self) -> str:
        """
        Format steps as a numbered multiline string:
        1. Step one
        2. Step two
        """
        lines: list[str] = []
        for idx, step in enumerate(self.steps, start=1):
            if _NUMBERED_STEP_PATTERN.match(step):
                lines.append(step)
            else:
                lines.append(f"{idx}. {step}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert TestCase to a serializable dictionary."""
        return {
            "id": self.id,
            "module": self.module,
            "feature": self.feature,
            "description": self.description,
            "steps": list(self.steps),
            "expected_result": self.expected_result,
        }


@dataclass
class TestResult:
    """
    Represents the execution result of a TestCase, including F12 Console & Network API diagnostics
    captured via Google Chrome DevTools MCP.
    """

    __test__ = False

    test_case: TestCase
    status: str | TestStatus
    actual_result: str
    screenshot_path: str = ""
    error_code: ErrorCode | str = ErrorCode.NONE
    ui_error: str = ""
    console_errors: list[str] = field(default_factory=list)
    network_errors: list[str] = field(default_factory=list)
    root_cause: str = ""
    bug_status: str = "Chờ xác nhận"
    response_note: str = ""
    feedback: str = ""
    executed_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def __post_init__(self) -> None:
        if not isinstance(self.test_case, TestCase):
            raise TypeError("'test_case' must be an instance of TestCase.")

        status_str = (
            self.status.value if isinstance(self.status, TestStatus) else str(self.status).strip().upper()
        )
        if status_str not in (TestStatus.PASS.value, TestStatus.FAIL.value):
            raise ValueError(f"Invalid status '{self.status}'. Must be 'PASS' or 'FAIL'.")
        self.status = status_str

        self.actual_result = str(self.actual_result).strip()
        if not self.actual_result:
            raise ValueError("TestResult 'actual_result' must not be empty.")

        self.screenshot_path = str(self.screenshot_path).strip().replace("\\", "/")

        if isinstance(self.error_code, str):
            code_upper = self.error_code.strip().upper() or "NONE"
            try:
                self.error_code = ErrorCode(code_upper)
            except ValueError:
                self.error_code = ErrorCode.UNKNOWN_ERROR

        self.ui_error = str(self.ui_error).strip()
        self.console_errors = [str(item).strip() for item in (self.console_errors or []) if str(item).strip()]
        self.network_errors = [str(item).strip() for item in (self.network_errors or []) if str(item).strip()]
        self.root_cause = str(self.root_cause).strip()
        self.bug_status = str(self.bug_status).strip() or "Chờ xác nhận"
        self.response_note = str(self.response_note).strip()
        self.feedback = str(self.feedback).strip()

        # Automatically infer error code on FAIL if left as NONE
        if self.is_failed and self.error_code == ErrorCode.NONE:
            if self.network_errors:
                self.error_code = ErrorCode.NETWORK_ERROR
            elif self.console_errors:
                self.error_code = ErrorCode.CONSOLE_ERROR
            elif self.ui_error:
                self.error_code = ErrorCode.UI_ERROR
            else:
                self.error_code = ErrorCode.ASSERTION_ERROR

    @property
    def is_passed(self) -> bool:
        """Return True if the test case passed."""
        return self.status == TestStatus.PASS.value

    @property
    def is_failed(self) -> bool:
        """Return True if the test case failed."""
        return self.status == TestStatus.FAIL.value

    def build_root_cause_details(self) -> str:
        """
        Format comprehensive Root Cause string for Column 7 of Sheet 'NoteBug', combining:
        - UI Error / Summary Root Cause
        - Chrome DevTools F12 Console Errors
        - Chrome DevTools F12 Network API Errors (HTTP 4xx/5xx)
        """
        sections: list[str] = []

        if self.error_code != ErrorCode.NONE:
            sections.append(f"[Mã lỗi]: {self.error_code.value}")

        ui_summary = self.ui_error or self.root_cause or self.actual_result
        if ui_summary:
            sections.append(f"[Lỗi Giao diện / Thực tế]: {ui_summary}")

        if self.console_errors:
            console_block = "\n  - ".join(self.console_errors)
            sections.append(f"[Console F12]:\n  - {console_block}")
        else:
            sections.append("[Console F12]: Không phát hiện lỗi Javascript đỏ.")

        if self.network_errors:
            network_block = "\n  - ".join(self.network_errors)
            sections.append(f"[Network API]:\n  - {network_block}")
        else:
            sections.append("[Network API]: Không phát hiện request lỗi HTTP 4xx/5xx.")

        return "\n".join(sections)
