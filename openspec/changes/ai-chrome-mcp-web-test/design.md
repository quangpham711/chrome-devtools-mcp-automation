## Context

Hệ thống Kiểm thử Web Tự động bằng AI được xây dựng theo kiến trúc **Hybrid Architecture**, kết hợp trực tiếp khả năng suy luận của AI Coding Agent ngay trong phiên làm việc IDE (không tốn chi phí API Key ngoài) với hai phân hệ cốt lõi:
1. **Google Chrome DevTools MCP (`ChromeDevTools/chrome-devtools-mcp`)**: Đóng vai trò là đôi mắt và bàn tay của AI Agent trên trình duyệt Google Chrome thật, đồng thời cung cấp quyền truy cập trực tiếp vào tầng DevTools F12 (Console & Network).
2. **Python Excel Reporter Engine (`src/webtest/`)**: Đóng vai trò chuẩn hóa dữ liệu đầu vào (YAML) và xuất báo cáo kiểm thử định dạng Excel `.xlsx` 3 Sheets theo đúng tiêu chuẩn QA doanh nghiệp.

## Goals / Non-Goals

**Goals:**
- Cho phép AI Agent tự động điều hướng, tương tác giao diện web (`click`, `fill`, `hover`, `press_key`, `wait_for`) qua Chrome DevTools MCP mà không cần viết script Python dò CSS selector cứng.
- Đảm bảo an toàn thông tin đăng nhập tuyệt đối bằng cơ chế **Chat Gate** (Headed Chrome + dừng chờ người dùng nhập tài khoản và xác nhận `"xong"`).
- Tự động thu thập bằng chứng lỗi toàn diện khi test case bị `FAIL`: ảnh chụp màn hình (`take_screenshot`), log lỗi Javascript (`list_console_messages`) và lỗi API HTTP 4xx/5xx (`list_network_requests`).
- Xuất báo cáo Excel 3 Sheets (`Summary`, `TestResults`, `NoteBug`) với định dạng chuẩn doanh nghiệp: công thức động trên `Summary`, hyperlink tương đối trên `TestResults` (11 cột), và nhúng ảnh thumbnail `200x112px` trên dòng cao `125pt` kèm phân tích Root Cause trên `NoteBug`.
- Đảm bảo kiểm soát tiến độ chặt chẽ: cập nhật `tasks.md`, commit và push lên GitHub sau mỗi bước hoàn thành.

**Non-Goals:**
- Không sử dụng Playwright hay Selenium để viết code tự động hóa dò selector cho từng trang web.
- Không gọi trả phí đến các dịch vụ LLM Cloud bên ngoài (OpenAI GPT-4o Vision API, Anthropic API).
- Không tự động lưu trữ, mã hóa hay tự điền thông tin mật khẩu của người dùng trong mã nguồn hoặc file cấu hình.

## Decisions

1. **Sử dụng `ChromeDevTools/chrome-devtools-mcp` thay vì Playwright script thuần**:
   - *Lý do*: Giúp AI tương tác theo thời gian thực như một QA Tester thực thụ và lấy được trực tiếp Console F12 (`list_console_messages`) cùng Network API (`list_network_requests`) mà không cần viết mã bắt sự kiện phức tạp.
2. **Tách biệt tầng Thực thi MCP và tầng Báo cáo Python (`tools/log_to_excel.py`)**:
   - *Lý do*: Việc tạo file Excel phức tạp (màu sắc, freeze panes, auto-filter, công thức, nhúng ảnh `openpyxl.drawing.image.Image`) cần sự chính xác tuyệt đối và khả năng tái sử dụng qua CLI script. Agent chỉ cần gọi lệnh CLI sau mỗi test case hoặc mỗi batch để ghi dữ liệu an toàn xuống ổ đĩa.
3. **Chia nhỏ chu trình thực thi theo Batching (2–3 test cases / batch)**:
   - *Lý do*: Tránh tràn bộ nhớ ngữ cảnh (context window) khi kiểm thử danh sách dài và đảm bảo kết quả được lưu vào Excel cũng như commit/push định kỳ.
4. **Cơ chế hiển thị ảnh khác biệt giữa `TestResults` và `NoteBug`**:
   - *Lý do*: Ở sheet `TestResults` (11 cột tổng hợp toàn bộ PASS/FAIL), chỉ gắn **hyperlink tương đối** (`reports/screenshots/{case_id}.png`) để bảng tính gọn nhẹ, dễ lọc. Ở sheet `NoteBug` (chỉ chứa các case `FAIL`), nhúng trực tiếp ảnh thumbnail kích thước `200x112px` vào cột H với chiều cao dòng `125pt` để QA/Dev nhìn thấy lỗi ngay khi mở sheet.

## Risks / Trade-offs

- **[Rủi ro] Tràn bộ nhớ ngữ cảnh khi chạy nhiều test case liên tiếp** $\rightarrow$ *Giảm thiểu*: Áp dụng quy tắc Batching (tối đa 2–3 test cases mỗi lượt), ghi kết quả ngay vào Excel qua `tools/log_to_excel.py` và khuyến nghị người dùng sử dụng `/compact` khi phiên làm việc kéo dài.
- **[Rủi ro] File ảnh chụp màn hình quá lớn làm nặng file Excel khi nhúng vào `NoteBug`** $\rightarrow$ *Giảm thiểu*: Sử dụng thư viện `Pillow` và `openpyxl.drawing.image.Image` để cố định kích thước hiển thị thumbnail ở mức `200px x 112px` và chiều cao dòng `125pt`.
- **[Rủi ro] Ghi đè làm mất phản hồi của QA/Dev trong file Excel đã tồn tại** $\rightarrow$ *Giảm thiểu*: Trong `ExcelReporter`, khi cập nhật test case đã có sẵn trong `TestResults`, bắt buộc đọc và bảo toàn giá trị hiện có của cột 10 (`Phản hồi`) và cột 11 (`FEEDBACK`).
