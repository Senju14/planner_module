# Automotive HMI GUI Agent (Trợ lý AI điều khiển giao diện xe hơi)

Dự án phát triển một AI Agent tự động điều khiển và tương tác với giao diện hệ thống thông tin giải trí trên ô tô (HMI) thông qua xử lý hình ảnh (Vision) và dữ liệu trạng thái UI. Sử dụng sức mạnh của các mô hình AI lớn (như `openai/gpt-4o-mini` qua OpenRouter), Agent có thể tự động lập kế hoạch và thực thi các thao tác để hoàn thành mục tiêu của người dùng.

---

## 🚀 Các Tính Năng Nổi Bật

1. **Tích hợp Mô hình Ngôn ngữ - Hình ảnh (VLM)**:
   - Tận dụng API OpenRouter để sử dụng các mô hình AI có khả năng đọc hiểu không gian hình ảnh UI.
   - Tự động chụp và nén màn hình theo thời gian thực để cung cấp bối cảnh cho AI một cách tiết kiệm token nhất.
2. **Thu thập Trạng thái UI Động**:
   - Tự động quét cấu trúc widget của PySide6 để ánh xạ các nút bấm, ô nhập liệu và thanh trượt mà không cần code cứng tọa độ (hardcode).
3. **Thực thi Hành động Chuẩn xác**:
   - Chuyển đổi trơn tru các lệnh từ AI (`CLICK`, `TYPE`, `SWIPE`) thành các thao tác chuột, bàn phím và kéo thả thực tế trên giao diện PySide6.
4. **Kiến trúc Non-Blocking (Không gây đơ UI)**:
   - Toàn bộ vòng lặp phân tích và gọi API của AI được chạy ngầm trên một luồng riêng (Background Thread), đảm bảo giao diện HMI luôn mượt mà và không bị treo.

---

## 📁 Cấu Trúc Thư Mục

- `main.py`: File khởi chạy cả giao diện UI và bộ não AI Agent.
- `instruction.txt`: Nơi chứa câu lệnh yêu cầu của người dùng.
- `src/`:
  - `planner_module.py`: Vòng lặp lõi của Agent (Quét màn hình -> Lập kế hoạch -> Chạy).
  - `vlm_backend.py`: Client kết nối API OpenRouter hỗ trợ hình ảnh và tự động ước tính số bước.
  - `executor.py`: Dịch các lệnh trừu tượng thành thao tác trên PySide6.
  - `prompt.py`: Prompt hệ thống cho AI và định dạng JSON.
  - `config.py`: File cấu hình môi trường.
- `ui_simulator/`: Mã nguồn giao diện mô phỏng HMI bằng PySide6.
- `screenshots/`: Nơi lưu ảnh chụp màn hình trong quá trình chạy.
- `outputs/`: Chứa file log và báo cáo kết quả markdown sau khi Agent chạy xong.

---

## 🛠️ Hướng Dẫn Cài Đặt

1. **Tạo và kích hoạt môi trường ảo (virtual environment)**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate   # Trên Windows
   # source venv/bin/activate # Trên Linux/Mac
   ```
2. **Cài đặt thư viện**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Cài đặt Biến môi trường**:
   Copy file `.env.example` thành `.env` và điền OpenRouter API Key của bạn vào:
   ```env
   OPENROUTER_API_KEY=sk-or-your_api_key_here
   OPENROUTER_MODEL=openai/gpt-4o-mini
   ```

---

## 🎮 Cách Sử Dụng

1. **Nhập câu lệnh yêu cầu**:
   Sửa nội dung file `instruction.txt` theo ý bạn, ví dụ:
   ```text
   Open Navigation and type HO CHI MINH CITY in the textbox. Go to Vehicle and Swipe Limit to 100%. Done.
   ```
2. **Khởi chạy chương trình**:
   ```bash
   python main.py
   ```
3. **Theo dõi kết quả**:
   - Giao diện mô phỏng HMI sẽ hiện lên.
   - Agent sẽ tự động chuyển hướng màn hình, click và gõ phím.
   - Khi chạy xong, kết quả tổng quát sẽ được xuất ra thư mục `outputs/`.
