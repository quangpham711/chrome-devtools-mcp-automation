# AI WEB TESTING BLUEPRINT: HYBRID ARCHITECTURE
## (Chrome DevTools MCP + Spec-Driven Python Excel Reporter)

Tài liệu này là **Kim chỉ nam thiết kế và triển khai (Master Blueprint)** dành cho AI Coding Agent (Antigravity / Cursor / Claude Code) và Lập trình viên để xây dựng hệ thống Kiểm thử Web Tự động bằng AI (AI Web Test Automation) thế hệ mới, tối ưu hóa toàn diện cho Google Chrome.

---

## 1. BỐI CẢNH & BÀI TOÁN THỰC TẾ

### 1.1. Kỳ vọng của Sếp và Doanh nghiệp
- **AI Agent kiểm thử tự động (True Agentic Testing)**: Người dùng chỉ cần cung cấp link website và ra lệnh bằng ngôn ngữ tự nhiên trong chat (ví dụ: *"Vào web test thử 10 tính năng chính xem có lỗi gì không"*). AI Agent tự mở web, tự dùng mắt nhìn giao diện, tự bấm thử các nút mà **con người KHÔNG CẦN phải ngồi code kịch bản chọn selector từng nút**.
- **Không tốn chi phí API Key ngoài (Zero External API Cost)**: Không bắt buộc công ty phải mua thêm thẻ tín dụng hay trả phí token định kỳ cho OpenAI / Anthropic API Key.
- **Bảo mật tuyệt đối (Manual Login qua Chat Gate)**: Khi gặp màn hình đăng nhập tài khoản công ty, trình duyệt phải bật lên có giao diện trực quan (**Headed mode**), Agent dừng lại chờ người dùng tự gõ thông tin bảo mật và nhắn `"xong"` trong chat mới tiếp tục. Tuyệt đối không tự động điền hay lưu trữ mật khẩu.
- **Báo cáo chuyên nghiệp 3 Sheets chuẩn Doanh nghiệp**:
  1. `Summary`: KPI Dashboard (Tổng test case, số Pass, số Fail, Tỷ lệ Pass Rate %, đánh giá tổng quan).
  2. `TestResults`: Chuẩn 11 cột mẫu công ty, có gắn **link siêu liên kết tương đối (hyperlink)** đến ảnh chụp bằng chứng màn hình trong thư mục `reports/screenshots/`.
  3. `NoteBug`: Tự động lọc riêng các test case bị `FAIL`, **chèn trực tiếp thumbnail ảnh chụp lỗi vào trong ô** (cột H) với chiều cao dòng tối ưu (125pt), đồng thời ghi lại **lỗi Console F12 và lỗi Network API** để QA/Dev mở file lên là nhìn thấy nguyên nhân gốc rễ (Root Cause) ngay lập tức.

### 1.2. Tại sao chọn Chrome DevTools MCP thay vì Playwright thông thường?
- Nếu dùng Playwright thuần Python: AI Agent phải đóng vai "Lập trình viên" đi soi mã HTML DOM, phát hiện iframe, viết file `.py` chọn từng CSS selector và fix lỗi code khi selector bị che khuất. Điều này biến quy trình thành **"tự code kịch bản tự động hóa"** chứ không phải **"AI tự vào test web"** như Sếp kỳ vọng.
- Nếu dùng `browser-use` nguyên bản: Bắt buộc phải có OpenAI API Key (GPT-4o Vision) chụp ảnh màn hình gửi liên tục lên cloud, ngốn chi phí token rất lớn.
- 👉 **Giải pháp tối ưu số 1**: Sử dụng **`ChromeDevTools/chrome-devtools-mcp`** (chính chủ Google Chrome DevTools team).
  - Tích hợp sẵn 10 tool Input + 6 tool Navigation để AI tự click, nhập liệu, chuyển trang mà không cần code selector.
  - Tích hợp sẵn công cụ **soi nội tạng F12** (`list_console_messages`, `list_network_requests`), giúp AI tự bắt được lỗi Javascript đỏ và lỗi API backend (HTTP 500/400) khi một tính năng bị hỏng.
  - **Hoàn toàn không cần API Key ngoài** (chạy cục bộ qua giao thức MCP).

---

## 2. KIẾN TRÚC TỔNG THỂ (HYBRID ARCHITECTURE)

```
                              ┌──────────────────────────────────┐
                              │     NGƯỜI DÙNG / QA TESTER       │
                              │   (Ra lệnh bằng ngôn ngữ tự nhiên)│
                              └─────────────────┬────────────────┘
                                                │
                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               AI CODING AGENT (Antigravity / IDE)                              │
│                                  (Bộ não suy luận duy nhất)                                    │
│                 - Không tốn tiền mua API Key ngoài (dùng phiên chat IDE có sẵn)                │
│                 - Quản lý ngữ cảnh bằng OpenSpec (Spec-Driven Development)                     │
└───────────────────────┬────────────────────────────────────────────────┬───────────────────────┘
                        │                                                │
         [1. Tự động thao tác & Soi F12]                         [2. Tự động ghi báo cáo]
                        │                                                │
                        ▼                                                ▼
┌─────────────────────────────────────────────────┐   ┌──────────────────────────────────────────┐
│           GOOGLE CHROME DEVTOOLS MCP            │   │          PYTHON REPORTING ENGINE         │
│          (ChromeDevTools/chrome-devtools-mcp)   │   │      (src/webtest/reporter.py)           │
├─────────────────────────────────────────────────┤   ├──────────────────────────────────────────┤
│ - Input Tools: click, fill, type, hover, drag   │   │ - Nhận dữ liệu Pass/Fail từ Agent        │
│ - Navigation Tools: navigate_page, wait_for     │   │ - Tính toán KPI Dashboard (Sheet 1)      │
│ - Debugging Tools: list_console_messages,       │   │ - Gắn hyperlink vào TestResults (Sheet 2)│
│   take_screenshot, evaluate_script              │   │ - Nhúng trực tiếp ảnh vào ô NoteBug (Sh3)│
│ - Network Tools: list_network_requests          │   │ - Ghi chi tiết Console / API error vào Sh3│
│ - TUYỆT ĐỐI KHÔNG CẦN VIẾT CODE DÒ SELECTOR     │   │ - Định dạng 11 cột, màu sắc chuẩn QA     │
└─────────────────────────────────────────────────┘   └──────────────────────────────────────────┘
```

---

## 3. YÊU CẦU BẮT BUỘC: ĐẶC TẢ BẰNG OPENSPEC (SPEC-DRIVEN)

Mọi thay đổi, thiết kế và triển khai cho dự án mới **BẮT BUỘC** phải tuân theo quy trình chuẩn của **OpenSpec** để đảm bảo AI Agent luôn có đầy đủ ngữ cảnh, không bị quên yêu cầu và không code tùy tiện.

### 3.1. Kích hoạt và Sử dụng Skill OpenSpec
Agent thực thi phải sử dụng các skill OpenSpec có sẵn trong hệ thống:
- `openspec-propose`: Đề xuất thay đổi kiến trúc hoặc tính năng mới.
- `openspec-apply-change`: Triển khai các nhiệm vụ (tasks) đã được duyệt.
- `openspec-explore`: Thảo luận, làm rõ yêu cầu thiết kế trước khi viết spec.
- `openspec-sync-specs` / `openspec-archive-change`: Cập nhật và lưu trữ đặc tả khi hoàn tất.

### 3.2. Cấu trúc thư mục OpenSpec chuẩn
Mọi đặc tả phải được lưu trong thư mục:
```text
openspec/
├── config.yaml
└── changes/
    └── <change-name>/
        ├── proposal.md   # Đặt vấn đề, giải pháp tổng quan và phạm vi
        ├── design.md     # Thiết kế kỹ thuật chi tiết (sơ đồ, hợp đồng tool, luồng dữ liệu)
        ├── specs/        # Các bản đặc tả chi tiết (Behavior Specifications)
        │   ├── chrome-devtools-mcp/spec.md # Đặc tả điều khiển trình duyệt qua Chrome DevTools MCP
        │   └── test-reporting/spec.md      # Đặc tả báo cáo Excel 3 sheet & nhúng ảnh
        └── tasks.md      # Danh sách việc cần làm (Checklist có thể kiểm chứng được)
```

### 3.3. Quy tắc cập nhật OpenSpec
- Không được code trước khi viết và phê duyệt `proposal.md`, `design.md` và `specs/`.
- Kiểm tra tính hợp lệ của đặc tả bằng lệnh CLI:
  ```bash
  openspec validate <change-name>
  ```
- Khi hoàn thành nhiệm vụ nào, phải cập nhật đánh dấu `[x]` ngay vào `tasks.md`.

### 3.4. Quy tắc Quản lý Mã nguồn với Git & GitHub
- **Khởi tạo Repository mới trước tiên**: Trước khi bắt đầu triển khai bất kỳ bước nào của dự án, bắt buộc phải khởi tạo Git cục bộ (`git init`), tạo file `.gitignore` chuẩn và **tạo một Repository mới trên GitHub** (qua GitHub CLI `gh repo create` hoặc gắn remote `git remote add origin <url>`), sau đó push bản khởi tạo đầu tiên (chứa tài liệu Blueprint) lên nhánh `main`.
- **Commit & Push sau mỗi bước thực hiện xong**: Sau khi hoàn thành bất kỳ bước thiết kế (OpenSpec), cài đặt cấu trúc, viết module code, viết unit test hay chạy kiểm thử nào, Agent bắt buộc phải đánh dấu `[x]` vào `tasks.md` và thực hiện tuần tự:
  ```bash
  git add .
  git commit -m "<mô tả rõ ràng bước vừa hoàn thành>"
  git push origin main
  ```
- Không được để dồn nhiều bước mới commit một lần nhằm đảm bảo lịch sử phiên bản (Git history) minh bạch và có thể khôi phục (rollback) bất cứ lúc nào.

---

## 4. ĐẶC TẢ CHI TIẾT TỪNG PHÂN HỆ

### 4.1. Phân hệ 1: Google Chrome DevTools MCP (`chrome-devtools-mcp`)
- **Vai trò**: Cung cấp bộ công cụ trực tiếp cho AI Agent để tương tác giao diện và trích xuất log kỹ thuật từ Google Chrome trong thời gian thực.
- **Cài đặt & Cấu hình**:
  - Yêu cầu môi trường máy có cài đặt **Node.js** (v18+) và trình duyệt **Google Chrome**.
  - Cấu hình server MCP trong file cấu hình của AI Agent / IDE (`mcp.json`):
    ```json
    {
      "mcpServers": {
        "chrome-devtools": {
          "command": "npx",
          "args": ["-y", "chrome-devtools-mcp@latest"]
        }
      }
    }
    ```
- **Các nhóm công cụ cốt lõi (Core Toolsets)**:
  1. **Input Automation**:
     - `click`: Click vào phần tử trên giao diện.
     - `fill` / `fill_form`: Nhập dữ liệu vào các ô input / form.
     - `hover`: Rê chuột để mở các menu xổ xuống.
     - `press_key` / `type_text`: Gõ phím hoặc gửi phím tắt (Enter, Tab, Esc).
  2. **Navigation Automation**:
     - `navigate_page`: Điều hướng đến URL mong muốn.
     - `wait_for`: Chờ phần tử xuất hiện hoặc chờ trang tải xong.
     - `list_pages` / `select_page`: Quản lý các tab đang mở.
  3. **Bắt Bug Kỹ thuật (Deep Debugging & Network - Điểm ăn tiền nhất)**:
     - `list_console_messages` / `get_console_message`: Lấy danh sách các dòng log đỏ, lỗi Javascript trên tab Console F12 khi thao tác bị lỗi.
     - `list_network_requests` / `get_network_request`: Kiểm tra các request API backend xem có endpoint nào bị lỗi HTTP 4xx hoặc 5xx không.
     - `take_screenshot`: Chụp ảnh màn hình lưu bằng chứng lỗi.
- **Cơ chế Chat Gate khi Đăng nhập**:
  - Khi `navigate_page` điều hướng vào URL chứa `/login` hoặc phát hiện form đăng nhập:
  - Agent **dừng lại ngay lập tức**, thông báo cho người dùng trong chat:
    > *"Đã phát hiện màn hình đăng nhập. Vui lòng thao tác đăng nhập tài khoản trên cửa sổ Google Chrome đang mở. Sau khi đăng nhập xong, hãy nhắn 'xong' để Agent tiếp tục kiểm thử."*
  - Khi người dùng nhắn `"xong"`, Agent tiếp tục chu trình kiểm thử tự động.

### 4.2. Phân hệ 2: Python Excel Reporter Engine
- **Vai trò**: Nhận kết quả và log lỗi từ Agent sau mỗi test case để xuất file Excel chuẩn doanh nghiệp.
- **Vị trí mã nguồn**: `src/webtest/reporter.py` và CLI script `tools/log_to_excel.py`.
- **Cấu trúc 3 Sheets bắt buộc**:

#### Sheet 1: `Summary` (KPI Dashboard)
- **Tiêu đề Banner**: `BÁO CÁO TỔNG QUAN KIỂM THỬ (AUTOMATION TEST SUMMARY)` (màu xanh navy `1F4E78`, chữ trắng).
- **Khối thông tin KPI**:
  - Tổng số Test Case (hàm Excel `=COUNTA(TestResults!A2:A100)`).
  - Số lượng PASS (hàm `=COUNTIF(TestResults!I2:I100, "PASS")`).
  - Số lượng FAIL (hàm `=COUNTIF(TestResults!I2:I100, "FAIL")`).
  - Tỷ lệ Pass Rate % (hàm `=C8/C7` định dạng `0.0%`).
  - Đánh giá chung: `PASSED` nếu 100% Pass, ngược lại là `FAILED`.
- **Khối phân loại theo Module**: Bảng thống kê số case Pass/Fail theo từng phân hệ.

#### Sheet 2: `TestResults` (Bảng chi tiết 11 cột chuẩn công ty)
- Cố định dòng 1 (*Freeze Panes A2*), bật bộ lọc (*Auto-Filter*).
- 11 Tiêu đề chuẩn in đậm:
  1. `Test Case ID`
  2. `Module`
  3. `Chức năng`
  4. `Mô tả`
  5. `Các bước thực hiện` (đánh số thứ tự 1., 2., có xuống dòng)
  6. `Expected Result`
  7. `Actual Result / Đánh giá`
  8. `Log/Screenshot/Video`
  9. `Status` (`PASS` nền xanh lá `C6EFCE`, chữ xanh đậm `006100`; `FAIL` nền đỏ `FFC7CE`, chữ đỏ đậm `9C0006`)
  10. `Phản hồi` (bảo toàn dữ liệu người dùng điền, không bị ghi đè)
  11. `FEEDBACK` (bảo toàn dữ liệu review)
- **Quy tắc hiển thị Cột 8 (Log/Screenshot/Video)**:
  - Giữ bảng tính sạch đẹp, **không chèn ảnh nổi tại sheet này**.
  - Chỉ hiển thị **đường link siêu liên kết tương đối** (ví dụ: `Xem ảnh: TC_01.png` có hyperlink trỏ vào `reports/screenshots/TC_01.png`), click vào là mở ảnh.

#### Sheet 3: `NoteBug` (Trang chuyên biệt quản lý lỗi & Phân tích Root Cause)
- Chỉ ghi nhận những test case có trạng thái là `FAIL`.
- 10 cột tiêu đề quản lý Bug:
  1. `Bug ID / Test Case ID`
  2. `Module`
  3. `Chức năng`
  4. `Các bước tái hiện`
  5. `Expected Result`
  6. `Actual Result`
  7. `Chi tiết lỗi (Root Cause)`: Ghi nhận đầy đủ thông tin:
     - Lỗi giao diện người dùng (nút không phản hồi, popup không mở).
     - **Lỗi Console F12** lấy từ `list_console_messages` của Chrome DevTools.
     - **Lỗi Network API** lấy từ `list_network_requests` (endpoint URL, mã HTTP status code).
  8. `Bằng chứng ảnh (Screenshot)`: **NHÚNG THẲNG ẢNH THUMBNAIL VÀO Ô** bằng thư viện `openpyxl.drawing.image.Image`, định dạng kích thước cân đối (rộng 200px, cao 112px).
  9. `Trạng thái xử lý` (Mặc định: *Chờ xác nhận*)
  10. `Dev Note / Phản hồi`
- **Chiều cao dòng (Row Height)**: Tự động set chiều cao dòng chứa ảnh lên **125pt** để ảnh hiển thị gọn gàng, vừa vặn hoàn hảo bên trong ô mà không bị tràn hay đè lên dòng khác.

---

## 5. CẤU TRÚC THƯ MỤC DỰ ÁN CHUẨN

Khi tạo dự án hoặc thư mục mới cho giải pháp này, Agent cần thiết lập đúng cấu trúc sau:

```text
chrome-devtools-mcp-automation/
├── .gitignore
├── README.md
├── AI_WEB_TESTING_BLUEPRINT.md    # Tài liệu này
├── package.json                   # Cấu hình Node.js (chrome-devtools-mcp)
├── requirements.txt               # openpyxl, pyyaml, pytest, pillow
├── openspec/                      # Toàn bộ đặc tả dự án theo chuẩn OpenSpec
│   ├── config.yaml
│   └── changes/
│       └── ai-chrome-mcp-web-test/
│           ├── proposal.md
│           ├── design.md
│           ├── specs/
│           │   ├── chrome-devtools-mcp/spec.md
│           │   └── test-reporting/spec.md
│           └── tasks.md
├── src/
│   └── webtest/
│       ├── __init__.py
│       ├── models.py              # Data classes: TestCase, TestResult, ErrorCode
│       ├── test_loader.py         # Nạp và validate kịch bản từ YAML
│       └── reporter.py            # ExcelReporter 3 sheet (Summary, TestResults, NoteBug)
├── tools/
│   ├── log_to_excel.py            # CLI script ghi kết quả vào Excel
│   └── take_screenshot.py         # CLI script chụp ảnh màn hình
├── test_cases/
│   ├── sample.yaml                # Bộ test case mẫu kiểm thử hệ thống
│   └── company_testcases.yaml     # Kịch bản kiểm thử website thực tế của công ty
├── reports/
│   ├── test_report_YYYYMMDD.xlsx  # File báo cáo Excel đầu ra
│   └── screenshots/               # Nơi lưu trữ tất cả ảnh bằng chứng
└── tests/
    ├── test_models.py             # Unit test cho models
    ├── test_loader.py             # Unit test nạp file YAML
    └── test_reporter.py           # Unit test tạo 3 sheet Excel, link & nhúng ảnh
```

---

## 6. QUY TRÌNH THỰC THI CHUẨN CHO AGENT (SOP RUNBOOK)

### 6.1. Quy trình Xây dựng & Phát triển Hệ thống
1. **Bước 0: Tạo GitHub Repository mới (Thực hiện đầu tiên)**:
   - Khởi tạo Git (`git init`), tạo `.gitignore`, tạo repo mới trên GitHub và push tài liệu Blueprint đầu tiên lên nhánh `main`.
2. **Triển khai từng bước & Commit/Push liên tục**:
   - Thiết lập OpenSpec (`proposal.md`, `design.md`, `specs/`, `tasks.md`) $\rightarrow$ `git commit` & `git push`.
   - Xây dựng từng thành phần (`models.py`, `test_loader.py`, `reporter.py`, CLI `tools/`, `tests/`) $\rightarrow$ Sau **mỗi bước hoàn thành**, cập nhật `[x]` vào `tasks.md`, chạy `git commit` và `git push` lên GitHub ngay lập tức.

### 6.2. Quy trình Thực thi Kiểm thử Web (5 Bước)
Khi người dùng yêu cầu kiểm thử một trang web mới, Agent thực hiện theo đúng 5 bước sau (và commit/push kết quả kịch bản sau mỗi bước quan trọng):

1. **Bước 1: Khởi tạo Phiên & Báo cáo**:
   - Nạp file `test_cases/*.yaml` qua `test_loader.py` (hoặc nhận kịch bản tự do từ lời nhắc của người dùng).
   - Khởi tạo file báo cáo Excel `reports/test_report_{timestamp}.xlsx` với đủ 3 sheets.
2. **Bước 2: Mở Google Chrome và Chat Gate**:
   - Gọi `navigate_page(url)` qua Chrome DevTools MCP để mở trình duyệt có giao diện trực quan trước mắt người dùng.
   - Nếu gặp màn hình Login: dừng lại, yêu cầu người dùng tự đăng nhập và đợi người dùng nhắn `"xong"`.
3. **Bước 3: Tự động tương tác & Bắt Bug F12 theo từng nhóm nhỏ (Batching 2–3 cases)**:
   - Thay vì chạy một mạch 20 case làm tràn bộ nhớ token, chia thành từng nhóm 2–3 test case.
   - Dùng các tool `click`, `fill`, `wait_for` của `chrome-devtools-mcp` để thao tác trực tiếp trên trang.
   - **Khi phát hiện lỗi hoặc nghi ngờ lỗi**:
     - Gọi `list_console_messages` để kiểm tra có lỗi Javascript đỏ không.
     - Gọi `list_network_requests` để kiểm tra có API backend nào bị lỗi 4xx/5xx không.
     - Gọi `take_screenshot` lưu ảnh bằng chứng vào `reports/screenshots/{case_id}.png`.
     - Gọi `python tools/log_to_excel.py` để ghi đầy đủ kết quả, mô tả lỗi F12 và đường dẫn ảnh vào Excel.
4. **Bước 4: Tổng kết ngắn gọn, Commit/Push & Bảo tồn Context**:
   - Sau mỗi batch hoặc bước hoàn thành, thông báo ngắn gọn: *"Đã hoàn thành Batch X (2/2 PASS). Dữ liệu đã lưu an toàn vào Excel."* và thực hiện commit/push tiến độ lên GitHub.
   - Khuyên người dùng dùng lệnh `/compact` nếu phiên làm việc kéo dài để giải phóng context window.
5. **Bước 5: Bàn giao Báo cáo hoàn chỉnh & Push lên GitHub**:
   - Cung cấp link markdown trực tiếp đến file báo cáo Excel.
   - Tóm tắt bảng KPI (Tổng số case, Pass, Fail, Pass Rate %).
   - Liệt kê các bug được phát hiện (kèm thông tin lỗi F12 Console / API backend) và hướng dẫn người dùng mở sheet `NoteBug` để xem ảnh nhúng trực tiếp.
   - Commit và push toàn bộ kịch bản test / báo cáo hoàn chỉnh lên GitHub.

---

## 7. ĐIỀU KHOẢN CAM KẾT (AGENT RULES)

1. **KHÔNG tự ý viết code Python giả lập thao tác web**: Dùng trực tiếp các tool của `chrome-devtools-mcp` (`click`, `fill`, `navigate_page`) để AI tự tương tác theo thời gian thực.
2. **KHÔNG tự động điền mật khẩu người dùng**: Luôn tuân thủ cơ chế Chat Gate bảo mật.
3. **LUÔN tận dụng công cụ Debugging của Chrome khi gặp lỗi**: Phải gọi `list_console_messages` và `list_network_requests` để ghi lại nguyên nhân gốc rễ (Root Cause) vào sheet `NoteBug`.
4. **KHÔNG chèn ảnh nổi vào sheet `TestResults`**: Cột 8 ở sheet `TestResults` chỉ chứa link hyperlink tương đối. Ảnh chỉ được nhúng trực tiếp ở sheet `NoteBug`.
5. **LUÔN duy trì tính toàn vẹn của OpenSpec**: Khi có bất kỳ thay đổi nào về thiết kế hay nghiệp vụ, phải cập nhật file đặc tả trong `openspec/` trước khi tiến hành viết code.
6. **LUÔN tạo Repo mới trước tiên và Commit & Push lên GitHub sau mỗi bước hoàn thành**: Bắt buộc khởi tạo Git và tạo Repository mới trên GitHub ngay từ đầu. Sau khi hoàn thành bất kỳ bước nào (viết spec, dựng cấu trúc, viết code từng module, chạy test), phải `git commit` và `git push` lên GitHub ngay lập tức.
