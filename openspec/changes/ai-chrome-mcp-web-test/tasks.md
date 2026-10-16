## 1. Khởi tạo Git, GitHub Repository & Đặc tả OpenSpec

- [x] 1.1 Khởi tạo Git cục bộ (`git init`), tạo `.gitignore`, tạo GitHub Repository mới (`chrome-devtools-mcp-automation`) và push bản đầu tiên lên nhánh `main`
- [x] 1.2 Thiết lập cấu trúc OpenSpec (`openspec/config.yaml`, `proposal.md`, `design.md`, `specs/chrome-devtools-mcp/spec.md`, `specs/test-reporting/spec.md`, `tasks.md`), kiểm tra hợp lệ bằng `openspec validate ai-chrome-mcp-web-test` và commit/push lên GitHub

## 2. Thiết lập Cấu hình Môi trường & Cấu trúc Dự án Chuẩn

- [ ] 2.1 Tạo file `package.json` (cấu hình `chrome-devtools-mcp`), `requirements.txt` (`openpyxl`, `pyyaml`, `pytest`, `pillow`), `README.md` và khởi tạo khung thư mục dự án (`src/webtest/`, `tools/`, `test_cases/`, `reports/screenshots/`, `tests/`), sau đó commit/push lên GitHub

## 3. Xây dựng Mô hình Dữ liệu & Bộ nạp Kịch bản YAML

- [ ] 3.1 Cài đặt `src/webtest/__init__.py` và `src/webtest/models.py` (định nghĩa `ErrorCode`, `TestCase`, `TestResult` kèm đầy đủ thuộc tính Console F12 & Network API error) và viết unit test `tests/test_models.py`, chạy pytest pass và commit/push lên GitHub
- [ ] 3.2 Cài đặt `src/webtest/test_loader.py` (nạp và validate kịch bản kiểm thử từ file YAML) cùng bộ test case mẫu `test_cases/sample.yaml`, `test_cases/company_testcases.yaml` và unit test `tests/test_loader.py`, chạy pytest pass và commit/push lên GitHub

## 4. Xây dựng Python Excel Reporter Engine (3 Sheets) & CLI Tools

- [ ] 4.1 Cài đặt `src/webtest/reporter.py` (`ExcelReporter` xuất 3 Sheets: `Summary` KPI Dashboard, `TestResults` 11 cột kèm hyperlink tương đối & bảo toàn cột Phản hồi/FEEDBACK, `NoteBug` 10 cột kèm Root Cause F12 & nhúng ảnh thumbnail `200x112px` ở dòng cao `125pt`), viết unit test `tests/test_reporter.py`, chạy pytest pass và commit/push lên GitHub
- [ ] 4.2 Cài đặt CLI script `tools/log_to_excel.py` và `tools/take_screenshot.py` để AI Agent gọi trực tiếp trong quá trình thực thi kiểm thử, kiểm tra hoạt động end-to-end tạo file báo cáo mẫu trong `reports/`, sau đó commit/push lên GitHub
