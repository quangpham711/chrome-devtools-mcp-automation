"""
AI Web Testing Hybrid Architecture - Core Package.
Combines Google Chrome DevTools MCP with a Spec-Driven Python Excel Reporter.
"""

from .models import ErrorCode, TestCase, TestResult, TestStatus

__all__ = [
    "ErrorCode",
    "TestStatus",
    "TestCase",
    "TestResult",
]
