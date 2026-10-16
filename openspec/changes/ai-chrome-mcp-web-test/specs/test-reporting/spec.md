## ADDED Requirements

### Requirement: Quản lý Mô hình Dữ liệu và Nạp Kịch bản Kiểm thử YAML
Hệ thống MUST cung cấp các cấu trúc dữ liệu chuẩn (`TestCase`, `TestResult`, `ErrorCode` trong `src/webtest/models.py`) và bộ nạp kịch bản (`src/webtest/test_loader.py`) để đọc và kiểm tra tính hợp lệ của các file kịch bản `.yaml` trong thư mục `test_cases/`.

#### Scenario: Nạp file YAML hợp lệ
- **WHEN** `test_loader.py` đọc một file kịch bản YAML chứa đầy đủ các trường bắt buộc (`id`, `module`, `feature`, `description`, `steps`, `expected_result`)
- **THEN** hệ thống SHALL trả về danh sách các đối tượng `TestCase` đã được chuẩn hóa để phục vụ thực thi và báo cáo

#### Scenario: Phát hiện file YAML thiếu trường bắt buộc hoặc sai định dạng
- **WHEN** `test_loader.py` đọc một file YAML bị lỗi cú pháp hoặc thiếu trường bắt buộc
- **THEN** hệ thống MUST phát sinh ngoại lệ (exception) với thông báo lỗi rõ ràng chỉ ra vị trí hoặc trường dữ liệu bị thiếu

### Requirement: Báo cáo Excel Sheet 1 - Summary (KPI Dashboard)
Bộ xuất báo cáo `ExcelReporter` (`src/webtest/reporter.py`) MUST tạo Sheet đầu tiên có tên `Summary` đóng vai trò bảng điều khiển KPI tổng quan của toàn bộ phiên kiểm thử.

#### Scenario: Khởi tạo và tính toán KPI trên Sheet Summary
- **WHEN** `ExcelReporter` xuất hoặc cập nhật file báo cáo Excel
- **THEN** Sheet `Summary` MUST có Banner tiêu đề `BÁO CÁO TỔNG QUAN KIỂM THỬ (AUTOMATION TEST SUMMARY)` (nền xanh navy `1F4E78`, chữ trắng), bảng KPI sử dụng công thức Excel động (`=COUNTA(TestResults!A2:A100)` cho Tổng số Test Case, `=COUNTIF(TestResults!I2:I100, "PASS")` cho Số lượng PASS, `=COUNTIF(TestResults!I2:I100, "FAIL")` cho Số lượng FAIL, `=C8/C7` định dạng `0.0%` cho Pass Rate %, đánh giá chung `PASSED`/`FAILED`) và bảng thống kê số lượng Pass/Fail phân loại theo từng Module

### Requirement: Báo cáo Excel Sheet 2 - TestResults (Bảng 11 cột chuẩn công ty)
Bộ xuất báo cáo `ExcelReporter` MUST tạo Sheet thứ hai có tên `TestResults` gồm đúng 11 cột tiêu chuẩn công ty, cố định dòng tiêu đề (`Freeze Panes A2`), bật bộ lọc (`Auto-Filter`), gắn hyperlink tương đối cho ảnh chụp màn hình và bảo toàn dữ liệu phản hồi của người dùng.

#### Scenario: Ghi kết quả kiểm thử và gắn Hyperlink tương đối tại cột 8
- **WHEN** một `TestResult` được ghi vào Sheet `TestResults` kèm đường dẫn ảnh chụp màn hình
- **THEN** hệ thống MUST điền đúng 11 cột (`Test Case ID`, `Module`, `Chức năng`, `Mô tả`, `Các bước thực hiện`, `Expected Result`, `Actual Result / Đánh giá`, `Log/Screenshot/Video`, `Status`, `Phản hồi`, `FEEDBACK`), tô màu cột `Status` (`PASS` nền `C6EFCE` chữ `006100`; `FAIL` nền `FFC7CE` chữ `9C0006`), tuyệt đối không chèn ảnh nổi mà chỉ tạo hyperlink tương đối (ví dụ `Xem ảnh: TC_01.png` trỏ tới `reports/screenshots/TC_01.png`) tại cột 8, đồng thời giữ nguyên dữ liệu cũ ở cột 10 (`Phản hồi`) và cột 11 (`FEEDBACK`) nếu dòng test case đó được cập nhật lại

### Requirement: Báo cáo Excel Sheet 3 - NoteBug (Quản lý lỗi, Root Cause F12 & Nhúng ảnh Thumbnail)
Bộ xuất báo cáo `ExcelReporter` MUST tạo Sheet thứ ba có tên `NoteBug` chỉ lưu trữ các test case có trạng thái `FAIL` với 10 cột quản lý lỗi, bao gồm thông tin Root Cause (UI + Console F12 + Network API) và ảnh chụp màn hình được nhúng trực tiếp vào ô.

#### Scenario: Ghi nhận test case FAIL và nhúng ảnh trực tiếp vào Sheet NoteBug
- **WHEN** một `TestResult` có trạng thái `FAIL` được ghi vào báo cáo Excel
- **THEN** hệ thống MUST thêm dòng tương ứng vào Sheet `NoteBug` với đủ 10 cột (`Bug ID / Test Case ID`, `Module`, `Chức năng`, `Các bước tái hiện`, `Expected Result`, `Actual Result`, `Chi tiết lỗi (Root Cause)`, `Bằng chứng ảnh (Screenshot)`, `Trạng thái xử lý` mặc định là `Chờ xác nhận`, `Dev Note / Phản hồi`), ghi đầy đủ lỗi Console F12 và Network API vào cột 7, nhúng trực tiếp ảnh thumbnail kích thước `200px x 112px` vào ô cột 8 (cột H) bằng `openpyxl.drawing.image.Image` và tự động đặt chiều cao dòng đó lên `125pt`
