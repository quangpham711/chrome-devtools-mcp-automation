# AI Web Testing Automation — Hybrid Architecture
**(Google Chrome DevTools MCP + Spec-Driven Python Excel Reporter)**

Hệ thống kiểm thử Web tự động bằng AI thế hệ mới dành cho QA/Doanh nghiệp:
- **True Agentic Testing**: AI Agent tự mở Google Chrome, tự quan sát giao diện và thao tác trực tiếp qua `chrome-devtools-mcp` mà không cần viết code dò CSS/XPath selector cứng.
- **Zero External API Cost**: Không tốn chi phí mua OpenAI / Anthropic API Key ngoài.
- **Bảo mật tuyệt đối (Manual Login qua Chat Gate)**: Khi gặp màn hình đăng nhập, trình duyệt mở ở chế độ Headed để người dùng tự nhập mật khẩu và nhắn `"xong"` trong chat.
- **Bắt Bug Kỹ thuật F12 (Deep Debugging)**: Tự động trích xuất lỗi Javascript đỏ (`list_console_messages`) và lỗi API HTTP 4xx/5xx (`list_network_requests`).
- **Báo cáo Excel 3 Sheets chuẩn Doanh nghiệp**:
  1. `Summary`: KPI Dashboard tự động tính Tổng case, PASS, FAIL, Pass Rate % và thống kê theo Module.
  2. `TestResults`: Bảng 11 cột chuẩn công ty, Freeze Panes, Auto-Filter, gắn hyperlink tương đối tới ảnh chụp màn hình và bảo toàn cột `Phản hồi` / `FEEDBACK`.
  3. `NoteBug`: Tự động lọc các case `FAIL`, ghi chi tiết Root Cause (UI + Console F12 + Network API) và **nhúng trực tiếp ảnh thumbnail (`200x112px`) vào ô cột H** với chiều cao dòng `125pt`.

---

## 1. Cấu trúc Thư mục Dự án

```text
chrome-devtools-mcp-automation/
├── .gitignore
├── README.md
├── AI_WEB_TESTING_BLUEPRINT.md    # Tài liệu Kim chỉ nam thiết kế & vận hành
├── package.json                   # Cấu hình Node.js (chrome-devtools-mcp)
├── mcp.json                       # Cấu hình MCP Server cho IDE / AI Agent
├── requirements.txt               # openpyxl, pyyaml, pytest, pillow
├── openspec/                      # Đặc tả dự án theo chuẩn OpenSpec (Spec-Driven)
│   ├── config.yaml
│   └── changes/
│       └── ai-chrome-mcp-web-test/
├── src/
│   └── webtest/
│       ├── __init__.py
│       ├── models.py              # Data classes: TestCase, TestResult, ErrorCode
│       ├── test_loader.py         # Nạp và validate kịch bản từ YAML
│       └── reporter.py            # ExcelReporter 3 sheets (Summary, TestResults, NoteBug)
├── tools/
│   ├── log_to_excel.py            # CLI script ghi kết quả vào Excel
│   └── take_screenshot.py         # CLI script quản lý/chuẩn hóa ảnh chụp màn hình
├── test_cases/
│   ├── sample.yaml                # Bộ test case mẫu kiểm thử hệ thống
│   └── company_testcases.yaml     # Kịch bản kiểm thử website thực tế của công ty
├── reports/
│   └── screenshots/               # Nơi lưu trữ tất cả ảnh bằng chứng
└── tests/
    ├── test_models.py             # Unit test cho models
    ├── test_loader.py             # Unit test nạp file YAML
    └── test_reporter.py           # Unit test tạo 3 sheets Excel, link & nhúng ảnh
```

---

## 2. Cài đặt Môi trường

### Yêu cầu hệ thống
- **Node.js**: v18+ và trình duyệt **Google Chrome**.
- **Python**: v3.10+

### Cài đặt thư viện Python
```bash
pip install -r requirements.txt
```

### Kiểm tra đặc tả OpenSpec & chạy Unit Tests
```bash
openspec validate ai-chrome-mcp-web-test
pytest tests/ -v
```
