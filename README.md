# Automotive HMI GUI Agent (Vision-Based UI Navigation)

Dự án phát triển một AI Agent điều khiển và tương tác với giao diện hệ thống thông tin giải trí trên ô tô (HMI) dựa trên dữ liệu hình ảnh (Vision) và danh sách cấu trúc widget hiện tại. Agent sẽ tự động lập kế hoạch và thực thi chuỗi hành động để hoàn thành mục tiêu của người dùng.

---

## 🚀 Các Tính Năng Nổi Bật

1. **Phân tích hình ảnh tối ưu (Groq TPM Optimization)**:
   - Tự động nén ảnh chụp màn hình về kích thước `512x288 JPEG (70%)` kết hợp cấu hình hiển thị chất lượng thấp (`low-detail`).
   - Lọc bỏ các widget ẩn và nút bấm bàn phím ảo giúp giảm kích thước gói dữ liệu gửi đi tới **95%** (dưới 1000 tokens/request), hoàn toàn tránh lỗi giới hạn dung lượng `413 Payload Too Large` của Groq API.
2. **Chống treo ứng dụng (Non-Blocking GUI Event Loop)**:
   - Gửi yêu cầu API và xử lý mạng trên một luồng phụ ngầm (Background Thread) song song với việc duy trì vòng lặp sự kiện `QEventLoop` ở luồng chính. 
   - Đảm bảo cửa sổ giả lập PySide6 luôn hoạt động mượt mà, phản hồi tốt và **không bị đóng băng (Not Responding)** khi gặp tình trạng chờ API rate limit.
3. **Cơ chế Fallback thông minh chống lỗi API**:
   - Nếu API Groq bị lỗi mạng, dính giới hạn cuộc gọi (`429 Rate Limit`) hoặc hết dung lượng, hệ thống sẽ tự động chuyển sang chế độ phản hồi giả lập dựa trên luật để chạy mượt mà chuỗi hành động mong muốn, phục vụ tốt cho việc quay video demo MVP.
4. **Tương tác Widget nâng cao**:
   - Nhận diện và tự động thay đổi giá trị thanh trượt `QSlider` (như giới hạn sạc pin xe lên 100%) bằng cách click tọa độ hoặc nhận diện tỷ lệ phần trăm.
   - Nhập liệu và gửi yêu cầu tìm kiếm chuẩn xác thông qua bàn phím ảo tích hợp.

---

## 📁 Cấu Trúc Thư Mục Chính

- `main.py`: Điểm kích hoạt chương trình chính.
- `instruction.txt`: Lưu câu lệnh yêu cầu của Agent (Ví dụ: Tìm kiếm đường đi, chỉnh cài đặt xe,...).
- `src/`:
  - `planner_module.py`: Vòng lặp Agent 5 giai đoạn (STAGE 1-5), lưu lịch sử hành động và tạo báo cáo.
  - `vlm_backend.py`: Quản lý gọi API Groq (mô hình Qwen) và cơ chế tự động fallback.
  - `executor.py`: Chuyển đổi lệnh hành động (CLICK, TYPE, SWIPE) và tác động trực tiếp vào widget của ứng dụng PySide6.
  - `prompt.py`: Cấu hình Prompt hệ thống và Schema định dạng hành động JSON.
  - `config.py`: File cấu hình chung (thời gian nghỉ giữa các bước, token, model...).
- `ui_simulator/`: Chứa mã nguồn của bộ giả lập màn hình ô tô viết bằng PySide6.
- `screenshots/`: Lưu ảnh chụp màn hình ứng dụng sau mỗi bước.
- `outputs/`: Chứa nhật ký chi tiết hành động (`execution_log.json`) và báo cáo tổng quan (`summary_report.md`).

---

## 🛠️ Hướng Dẫn Cài Đặt

1. **Tạo môi trường ảo Python**:
   ```bash
   python -m venv venv
   ```
2. **Kích hoạt môi trường ảo**:
   - Trên Windows (PowerShell):
     ```powershell
     .\venv\Scripts\activate
     ```
   - Trên Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
3. **Cài đặt thư viện**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Thiết lập API Key**:
   Tạo file `.env` tại thư mục gốc của dự án và thêm key Groq của bạn:
   ```env
   GROQ_API_KEY=gsk_your_key_here
   ```

---

## 🎮 Cách Sử Dụng và Demo

1. **Cấu hình yêu cầu**:
   Mở file `instruction.txt` ở thư mục gốc và nhập yêu cầu của bạn, ví dụ:
   ```text
   Open Navigation and type HO CHI MINH CITY in the textbox. Go to Vehicle and Swipe Limit to 100%. Done
   ```
2. **Khởi chạy Agent**:
   ```bash
   python main.py
   ```
3. **Theo dõi kết quả**:
   - Khi khởi chạy, màn hình giao diện giả lập ô tô PySide6 (kích thước chuẩn `1024x576`) sẽ hiện ra.
   - Agent sẽ nghỉ 1.5 giây giữa mỗi hành động để tạo hiệu ứng chuyển màn hình tự nhiên hỗ trợ ghi hình video.
   - Khi hoàn thành, ứng dụng tự động đóng lại và xuất báo cáo kết quả hoàn thành 100% trong thư mục `outputs/`.
