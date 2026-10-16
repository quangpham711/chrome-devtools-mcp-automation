"""
AI Web Testing Hybrid Architecture - Core Package.
Combines Google Chrome DevTools MCP with a Spec-Driven Python Excel Reporter.
"""

from .models import ErrorCode, TestCase, TestResult, TestStatus
from .test_loader import get_test_case_by_id, load_test_cases, load_test_suite

__all__ = [
    "ErrorCode",
    "TestStatus",
    "TestCase",
    "TestResult",
    "load_test_suite",
    "load_test_cases",
    "get_test_case_by_id",
]
