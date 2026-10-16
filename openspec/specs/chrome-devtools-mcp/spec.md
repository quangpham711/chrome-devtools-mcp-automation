# chrome-devtools-mcp Specification

## Purpose
Tích hợp máy chủ Google Chrome DevTools MCP để thực thi tương tác giao diện trực quan (Headed mode), bảo mật đăng nhập qua Chat Gate và trích xuất lỗi chuyên sâu từ F12 Console & Network API.

## Requirements

### Requirement: Cấu hình và Kết nối Google Chrome DevTools MCP
Hệ thống MUST tích hợp máy chủ `chrome-devtools-mcp` thông qua `npx -y chrome-devtools-mcp@latest` trên môi trường Node.js (v18+) và trình duyệt Google Chrome có giao diện trực quan (Headed mode), hoàn toàn không sử dụng API Key trả phí bên ngoài.

#### Scenario: Khởi chạy trình duyệt qua MCP
- **WHEN** AI Agent gọi công cụ `navigate_page` với URL mục tiêu của phiên kiểm thử
- **THEN** trình duyệt Google Chrome MUST mở lên ở chế độ có giao diện trực quan (Headed mode) và điều hướng tới đúng URL được yêu cầu

### Requirement: Cơ chế Bảo mật Chat Gate khi Đăng nhập
Khi phát hiện trang đăng nhập (URL chứa `/login` hoặc xuất hiện biểu mẫu yêu cầu tài khoản/mật khẩu), AI Agent MUST dừng toàn bộ thao tác tự động, tuyệt đối không tự điền mật khẩu và yêu cầu người dùng tự đăng nhập trên cửa sổ Chrome.

#### Scenario: Tạm dừng chờ người dùng đăng nhập tại Chat Gate
- **WHEN** `navigate_page` hoặc thao tác điều hướng dẫn tới màn hình đăng nhập
- **THEN** Agent MUST dừng lại ngay lập tức và gửi thông báo trong chat: *"Đã phát hiện màn hình đăng nhập. Vui lòng thao tác đăng nhập tài khoản trên cửa sổ Google Chrome đang mở. Sau khi đăng nhập xong, hãy nhắn 'xong' để Agent tiếp tục kiểm thử."*

#### Scenario: Tiếp tục kiểm thử sau khi người dùng xác nhận
- **WHEN** người dùng hoàn tất đăng nhập trên trình duyệt và nhắn `"xong"` vào khung chat
- **THEN** Agent MUST kiểm tra trạng thái trang hiện tại và tiếp tục thực thi các test case tiếp theo

### Requirement: Thực thi Tương tác Tự động theo Batching và Bắt Bug F12
AI Agent SHALL thực thi kiểm thử theo từng nhóm nhỏ (Batching từ 2 đến 3 test cases mỗi đợt) bằng các công cụ Input/Navigation của `chrome-devtools-mcp` (`click`, `fill`, `fill_form`, `hover`, `press_key`, `type_text`, `wait_for`) và tự động trích xuất log kỹ thuật F12 khi phát hiện lỗi.

#### Scenario: Thao tác kiểm thử thành công (PASS)
- **WHEN** Agent thực hiện các bước của một test case trên giao diện và kết quả thực tế khớp với Expected Result
- **THEN** Agent SHALL chụp ảnh màn hình bằng chứng (`take_screenshot`) lưu vào `reports/screenshots/{case_id}.png` và ghi nhận trạng thái `PASS` vào báo cáo Excel

#### Scenario: Phát hiện lỗi và thu thập Root Cause từ Console F12 & Network API (FAIL)
- **WHEN** một bước thao tác thất bại hoặc giao diện hiển thị không đúng với Expected Result
- **THEN** Agent MUST gọi `list_console_messages` để thu thập lỗi Javascript đỏ trên tab Console F12, gọi `list_network_requests` để thu thập các request API bị lỗi HTTP 4xx/5xx, gọi `take_screenshot` để lưu ảnh bằng chứng vào `reports/screenshots/{case_id}.png` và chuyển toàn bộ thông tin Root Cause sang bộ xuất báo cáo Excel
