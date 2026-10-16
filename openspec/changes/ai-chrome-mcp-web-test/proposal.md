## Why

Doanh nghiệp và đội ngũ QA cần một hệ thống **AI Agent kiểm thử web tự động (True Agentic Web Testing)** có khả năng tự mở trình duyệt Google Chrome, tự quan sát giao diện và tương tác theo ngôn ngữ tự nhiên mà **không cần lập trình viên phải viết kịch bản dò CSS/XPath selector cho từng nút**, đồng thời **không tốn chi phí mua OpenAI/Anthropic API Key ngoài**.

Bên cạnh đó, hệ thống bắt buộc phải đảm bảo an toàn bảo mật tuyệt đối khi đăng nhập tài khoản nội bộ công ty thông qua cơ chế **Chat Gate (Manual Login)** và xuất ra **Báo cáo Excel 3 Sheets chuẩn Doanh nghiệp** (`Summary`, `TestResults`, `NoteBug`), trong đó tự động thu thập lỗi kỹ thuật chuyên sâu từ **Console F12** và **Network API (HTTP 4xx/5xx)** kèm ảnh chụp màn hình nhúng trực tiếp vào ô báo cáo lỗi để Dev/QA xác định nguyên nhân gốc rễ (Root Cause) ngay lập tức.

## What Changes

- Thiết lập và tích hợp máy chủ **Google Chrome DevTools MCP** (`ChromeDevTools/chrome-devtools-mcp`) làm công cụ điều khiển trình duyệt trực quan (Headed mode) và trích xuất dữ liệu F12 (`list_console_messages`, `list_network_requests`, `take_screenshot`).
- Thiết lập quy trình bảo mật **Chat Gate** khi phát hiện màn hình đăng nhập (`/login` hoặc form password): Agent tạm dừng và chờ người dùng tự đăng nhập rồi nhắn `"xong"` trong khung chat trước khi tiếp tục kiểm thử theo từng nhóm nhỏ (Batching 2–3 test cases).
- Xây dựng **Python Reporting Engine** (`src/webtest/models.py`, `src/webtest/test_loader.py`, `src/webtest/reporter.py`) và bộ công cụ CLI (`tools/log_to_excel.py`, `tools/take_screenshot.py`) để nạp kịch bản YAML và xuất báo cáo Excel 3 Sheets:
  - Sheet `Summary`: Bảng điều khiển KPI tự động bằng công thức Excel (`COUNTA`, `COUNTIF`, tỷ lệ Pass Rate %) và thống kê theo từng Module.
  - Sheet `TestResults`: Bảng chi tiết 11 cột chuẩn công ty, cố định dòng tiêu đề (`Freeze Panes A2`), bật `Auto-Filter`, gắn link siêu liên kết tương đối (`reports/screenshots/...`) tại cột 8 (không chèn ảnh nổi) và bảo toàn dữ liệu các cột `Phản hồi` / `FEEDBACK`.
  - Sheet `NoteBug`: Tự động lọc riêng các test case `FAIL`, ghi nhận chi tiết Root Cause (UI + Console F12 + Network API) và **nhúng trực tiếp ảnh thumbnail (`200x112px`) vào ô cột H** với chiều cao dòng cố định `125pt`.
- Thiết lập bộ kịch bản mẫu (`test_cases/sample.yaml`, `test_cases/company_testcases.yaml`) và bộ Unit Test kiểm chứng toàn diện (`tests/test_models.py`, `tests/test_loader.py`, `tests/test_reporter.py`).

## Capabilities

### New Capabilities
- `chrome-devtools-mcp`: Điều khiển trình duyệt Google Chrome trực tiếp qua giao thức MCP (Input, Navigation), cơ chế bảo mật Chat Gate khi đăng nhập, thực thi theo Batching 2–3 cases và trích xuất lỗi kỹ thuật Console F12 / Network API / Screenshot.
- `test-reporting`: Hệ thống nạp kịch bản kiểm thử YAML (`test_loader.py`), mô hình dữ liệu (`models.py`), CLI ghi nhận kết quả (`log_to_excel.py`) và xuất báo cáo Excel 3 Sheets (`Summary`, `TestResults`, `NoteBug`) có gắn hyperlink và nhúng ảnh trực tiếp.

### Modified Capabilities
- Không có (dự án khởi tạo mới hoàn toàn).

## Impact

- **Cấu hình môi trường**: Thêm `package.json` và cấu hình MCP (`chrome-devtools-mcp@latest` trên Node.js v18+), thêm `requirements.txt` (`openpyxl`, `pyyaml`, `pillow`, `pytest`).
- **Mã nguồn dự án**: Tạo mới các module trong `src/webtest/`, `tools/`, `test_cases/`, `tests/` và thư mục đầu ra `reports/screenshots/`.
- **Quy trình vận hành & Quản lý mã nguồn**: Áp dụng quy trình SOP 5 bước kết hợp nguyên tắc **Commit & Push lên GitHub ngay sau mỗi bước hoàn thành**.

