#!/usr/bin/env python3
"""
CLI Script for AI Coding Agent to initialize and log web test results into the 3-Sheet Excel Report:
- Sheet 1: Summary (KPI Dashboard)
- Sheet 2: TestResults (11 columns + relative hyperlinks)
- Sheet 3: NoteBug (FAIL cases + F12 Console & Network Root Cause + 200x112px embedded thumbnail)
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.webtest.models import ErrorCode, TestCase, TestResult  # noqa: E402
from src.webtest.reporter import ExcelReporter  # noqa: E402
from src.webtest.test_loader import get_test_case_by_id, load_test_suite  # noqa: E402


def _default_report_path() -> Path:
    date_str = datetime.now().strftime("%Y%m%d")
    return PROJECT_ROOT / "reports" / f"test_report_{date_str}.xlsx"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Log AI Web Test execution results and F12 diagnostics into a 3-Sheet Excel Report."
    )
    parser.add_argument(
        "--report",
        default=str(_default_report_path()),
        help="Path to target Excel report file (default: reports/test_report_YYYYMMDD.xlsx)",
    )
    parser.add_argument(
        "--yaml",
        default="",
        help="Optional path to YAML test suite file (e.g., test_cases/sample.yaml) to auto-fill test case metadata",
    )
    parser.add_argument(
        "--suite-name",
        default="",
        help="Suite name for Summary sheet header",
    )
    parser.add_argument(
        "--target-url",
        default="",
        help="Target website URL for Summary sheet metadata",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize an empty 3-sheet Excel report (or pre-load metadata from --yaml) and exit",
    )

    # Test Case identification & ad-hoc metadata
    parser.add_argument("--case-id", default="", help="Test Case ID (e.g., TC_01)")
    parser.add_argument("--module", default="", help="Module name (overrides YAML if provided)")
    parser.add_argument("--feature", default="", help="Feature name (overrides YAML if provided)")
    parser.add_argument("--description", default="", help="Test case description (overrides YAML if provided)")
    parser.add_argument(
        "--step",
        action="append",
        dest="steps",
        default=[],
        help="Test step (can be specified multiple times, or separated by '|' in --steps-text)",
    )
    parser.add_argument(
        "--steps-text",
        default="",
        help="Pipe-separated or newline-separated steps string if not using --step",
    )
    parser.add_argument("--expected", default="", help="Expected Result (overrides YAML if provided)")

    # Execution Result & F12 Deep Debugging inputs
    parser.add_argument("--status", default="", choices=["PASS", "FAIL", "pass", "fail", ""], help="PASS or FAIL")
    parser.add_argument("--actual", default="", help="Actual Result / Evaluation")
    parser.add_argument(
        "--screenshot",
        default="",
        help="Path to screenshot evidence (e.g., reports/screenshots/TC_01.png)",
    )
    parser.add_argument(
        "--error-code",
        default="NONE",
        help="Error classification code (NONE, UI_ERROR, CONSOLE_ERROR, NETWORK_ERROR, TIMEOUT_ERROR, ASSERTION_ERROR, AUTH_ERROR)",
    )
    parser.add_argument("--ui-error", default="", help="UI defect description if any")
    parser.add_argument(
        "--console-error",
        action="append",
        dest="console_errors",
        default=[],
        help="F12 Console error message from list_console_messages (can be passed multiple times)",
    )
    parser.add_argument(
        "--network-error",
        action="append",
        dest="network_errors",
        default=[],
        help="F12 Network API error from list_network_requests (can be passed multiple times)",
    )
    parser.add_argument("--root-cause", default="", help="Additional root cause analysis note")
    parser.add_argument("--bug-status", default="Chờ xác nhận", help="Bug status in NoteBug sheet")
    parser.add_argument("--response", default="", help="Column 10 'Phản hồi' / Dev Note")
    parser.add_argument("--feedback", default="", help="Column 11 'FEEDBACK'")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    suite_name = args.suite_name or "AI Web Testing Suite (Chrome DevTools MCP)"
    target_url = args.target_url

    if args.yaml:
        yaml_path = Path(args.yaml)
        if yaml_path.exists():
            suite_meta = load_test_suite(yaml_path)
            if not args.suite_name:
                suite_name = suite_meta["suite_name"]
            if not args.target_url:
                target_url = suite_meta["target_url"]

    reporter = ExcelReporter(
        report_path=args.report,
        suite_name=suite_name,
        target_url=target_url,
    )

    if args.init and not args.case_id:
        saved = reporter.save()
        print(f"[OK] Initialized 3-sheet Excel report at: {saved}")
        return 0

    if not args.case_id:
        parser.error("Either --init or --case-id (with --status and --actual) is required.")
    if not args.status:
        parser.error("--status (PASS or FAIL) is required when logging a test case.")
    if not args.actual:
        parser.error("--actual is required when logging a test case.")

    # Resolve TestCase from YAML if available, then apply any CLI overrides
    yaml_tc: TestCase | None = None
    if args.yaml:
        yaml_tc = get_test_case_by_id(args.yaml, args.case_id)

    steps_list: list[str] = list(args.steps or [])
    if not steps_list and args.steps_text:
        sep = "|" if "|" in args.steps_text else "\n"
        steps_list = [s.strip() for s in args.steps_text.split(sep) if s.strip()]

    if yaml_tc is not None:
        tc = TestCase(
            id=args.case_id,
            module=args.module or yaml_tc.module,
            feature=args.feature or yaml_tc.feature,
            description=args.description or yaml_tc.description,
            steps=steps_list or yaml_tc.steps,
            expected_result=args.expected or yaml_tc.expected_result,
        )
    else:
        tc = TestCase(
            id=args.case_id,
            module=args.module or "General",
            feature=args.feature or args.case_id,
            description=args.description or args.feature or f"Kiểm thử chức năng {args.case_id}",
            steps=steps_list or ["Thực hiện thao tác kiểm thử trên trình duyệt qua Chrome DevTools MCP"],
            expected_result=args.expected or "Chức năng hoạt động đúng, không có lỗi Console F12 hoặc Network API",
        )

    screenshot_path = args.screenshot
    if not screenshot_path:
        candidate = PROJECT_ROOT / "reports" / "screenshots" / f"{tc.id}.png"
        if candidate.exists():
            screenshot_path = f"reports/screenshots/{tc.id}.png"

    result = TestResult(
        test_case=tc,
        status=args.status.upper(),
        actual_result=args.actual,
        screenshot_path=screenshot_path,
        error_code=args.error_code or ErrorCode.NONE,
        ui_error=args.ui_error,
        console_errors=args.console_errors,
        network_errors=args.network_errors,
        root_cause=args.root_cause,
        bug_status=args.bug_status,
        response_note=args.response,
        feedback=args.feedback,
    )

    saved_path = reporter.log_result(result)
    print(f"[OK] Logged {tc.id} ({result.status}) -> {saved_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
