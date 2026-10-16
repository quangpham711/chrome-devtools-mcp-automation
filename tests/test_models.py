"""
Unit tests for src/webtest/models.py (ErrorCode, TestStatus, TestCase, TestResult).
"""

import pytest

from src.webtest.models import ErrorCode, TestCase, TestResult, TestStatus


def test_testcase_valid_and_formatted_steps() -> None:
    tc = TestCase(
        id="TC_01",
        module="Authentication",
        feature="Đăng nhập",
        description="Kiểm tra đăng nhập thành công với tài khoản hợp lệ",
        steps=[
            "Mở trang đăng nhập",
            "2. Nhập email và mật khẩu",
            "Nhấn nút Đăng nhập",
        ],
        expected_result="Chuyển hướng vào trang Dashboard",
    )
    assert tc.id == "TC_01"
    assert tc.module == "Authentication"
    formatted = tc.formatted_steps()
    assert formatted == (
        "1. Mở trang đăng nhập\n"
        "2. Nhập email và mật khẩu\n"
        "3. Nhấn nút Đăng nhập"
    )
    data = tc.to_dict()
    assert data["id"] == "TC_01"
    assert len(data["steps"]) == 3


@pytest.mark.parametrize(
    "kwargs, match_msg",
    [
        (
            {
                "id": "   ",
                "module": "Auth",
                "feature": "Login",
                "description": "Desc",
                "steps": ["Step 1"],
                "expected_result": "OK",
            },
            "'id' must not be empty",
        ),
        (
            {
                "id": "TC_02",
                "module": "",
                "feature": "Login",
                "description": "Desc",
                "steps": ["Step 1"],
                "expected_result": "OK",
            },
            "'module' must not be empty",
        ),
        (
            {
                "id": "TC_02",
                "module": "Auth",
                "feature": "Login",
                "description": "Desc",
                "steps": [],
                "expected_result": "OK",
            },
            "'steps' must be a non-empty list",
        ),
        (
            {
                "id": "TC_02",
                "module": "Auth",
                "feature": "Login",
                "description": "Desc",
                "steps": ["   "],
                "expected_result": "OK",
            },
            "step #1 must not be empty",
        ),
    ],
)
def test_testcase_validation_errors(kwargs: dict, match_msg: str) -> None:
    with pytest.raises(ValueError, match=match_msg):
        TestCase(**kwargs)


def test_testresult_pass_normalization() -> None:
    tc = TestCase(
        id="TC_01",
        module="Dashboard",
        feature="Hiển thị KPI",
        description="Kiểm tra bảng KPI",
        steps=["Mở trang Dashboard"],
        expected_result="Hiển thị đầy đủ số liệu",
    )
    res = TestResult(
        test_case=tc,
        status="pass",
        actual_result="Hiển thị đúng số liệu",
        screenshot_path=r"reports\screenshots\TC_01.png",
    )
    assert res.is_passed is True
    assert res.is_failed is False
    assert res.status == TestStatus.PASS.value
    assert res.screenshot_path == "reports/screenshots/TC_01.png"
    assert res.error_code == ErrorCode.NONE


def test_testresult_fail_and_f12_root_cause_formatting() -> None:
    tc = TestCase(
        id="TC_02",
        module="Order",
        feature="Tạo đơn hàng",
        description="Kiểm tra nút Lưu đơn hàng",
        steps=["Điền thông tin đơn hàng", "Bấm nút Lưu"],
        expected_result="Lưu thành công và hiện thông báo",
    )
    res = TestResult(
        test_case=tc,
        status="FAIL",
        actual_result="Nút Lưu quay vòng vô hạn, không tạo được đơn",
        screenshot_path="reports/screenshots/TC_02.png",
        ui_error="Spinner không tắt sau khi bấm nút Lưu",
        console_errors=["Uncaught TypeError: Cannot read properties of null (reading 'orderId')"],
        network_errors=["POST https://api.example.com/v1/orders -> HTTP 500 Internal Server Error"],
    )
    assert res.is_failed is True
    assert res.error_code == ErrorCode.NETWORK_ERROR
    assert res.bug_status == "Chờ xác nhận"

    details = res.build_root_cause_details()
    assert "[Mã lỗi]: NETWORK_ERROR" in details
    assert "Spinner không tắt sau khi bấm nút Lưu" in details
    assert "Uncaught TypeError: Cannot read properties of null" in details
    assert "POST https://api.example.com/v1/orders -> HTTP 500 Internal Server Error" in details


def test_testresult_invalid_status_raises() -> None:
    tc = TestCase(
        id="TC_03",
        module="Auth",
        feature="Logout",
        description="Đăng xuất",
        steps=["Bấm nút Đăng xuất"],
        expected_result="Về màn hình đăng nhập",
    )
    with pytest.raises(ValueError, match="Invalid status"):
        TestResult(test_case=tc, status="BLOCKED", actual_result="Không bấm được")
