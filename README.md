# API Hệ Thống Quản Lý Thư Viện & Thi Trắc Nghiệm

Đây là hệ thống Backend API mạnh mẽ được xây dựng bằng **FastAPI** (Python). Dự án kết hợp giữa **Hệ thống Quản lý Thư viện** và **Hệ thống Thi trắc nghiệm trực tuyến**, được thiết kế để xử lý các mối quan hệ dữ liệu phức tạp, xác thực người dùng và các tác vụ nền sử dụng **MongoDB**.

## ✨ Tính năng chính

### 🔐 Xác thực & Người dùng
- **Xác thực bảo mật**: Đăng nhập, đăng ký và làm mới token dựa trên JWT.
- **Đăng nhập mạng xã hội**: Tích hợp OAuth2 (Google) qua `social_auth`.
- **Quản lý người dùng**: Cập nhật hồ sơ, đặt lại mật khẩu và phân quyền truy cập.
- **Xác minh Email**: Quy trình xác thực tài khoản tự động qua email.

### 📚 Quản lý Thư viện
- **Sách**: Các thao tác CRUD (Thêm, Đọc, Sửa, Xóa) với hỗ trợ ảnh bìa và siêu dữ liệu.
- **Tác giả**: Quản lý hồ sơ tác giả và liên kết với các đầu sách.
- **Danh mục**: Tổ chức nội dung theo hệ thống danh mục linh hoạt.

### 📝 Hệ thống Thi cử (Examination)
- **Kỳ thi (Exams)**: Tạo và quản lý các kỳ thi với cấu hình tùy chỉnh.
- **Ngân hàng câu hỏi**: Kho lưu trữ câu hỏi để tái sử dụng cho nhiều đề thi khác nhau.
- **Đề thi (Exam Papers)**: Tạo các đề thi cụ thể từ cấu trúc kỳ thi.
- **Phần thi (Sections)**: Chia đề thi thành các phần logic (ví dụ: Reading, Listening).

### 🛠 Điểm nhấn kỹ thuật
- **Cơ sở dữ liệu**: Sử dụng **MongoDB** (NoSQL) để lưu trữ tài liệu linh hoạt và hiệu suất cao.
- **Tác vụ nền**: Sử dụng **Celery** & **Redis** để xử lý các công việc bất đồng bộ (gửi email, xử lý dữ liệu nặng).
- **Giới hạn lưu lượng (Rate Limiting)**: Bảo vệ API khỏi các cuộc tấn công spam bằng `slowapi`.

## 🚀 Công nghệ sử dụng

- **Framework chính**: [FastAPI](https://fastapi.tiangolo.com/)
- **Ngôn ngữ**: Python 3.12+
- **Cơ sở dữ liệu**: MongoDB (thông qua driver `Motor`)
- **Quản lý tác vụ**: Celery
- **Message Broker**: Redis
- **Xác thực**: Python-JOSE, Authlib
- **Kiểm tra dữ liệu**: Pydantic

## 📋 Yêu cầu hệ thống

- [Python](https://www.python.org/downloads/) (v3.12+)
- [MongoDB](https://www.mongodb.com/try/download/community)
- [Redis](https://redis.io/)
- [Git](https://git-scm.com/)

## ⚙️ Cài đặt & Thiết lập

### 1. Tải mã nguồn
```bash
git clone <your-repo-url>
cd full_stack/library_api
```

### 2. Tạo môi trường ảo
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### 4. Cấu hình biến môi trường
Tạo file `.env` từ file mẫu:
```bash
# Windows
copy .env.example .env
# macOS/Linux
cp .env.example .env
```
*Mở file `.env` và cấu hình các thông tin kết nối MongoDB, Redis, và tài khoản SMTP gửi email.*

## ▶️ Khởi chạy ứng dụng

### Chạy API Server
```bash
uvicorn app.main:app --reload
```
- **Tài liệu Swagger UI**: `http://127.0.0.1:8000/docs`
- **Tài liệu ReDoc**: `http://127.0.0.1:8000/redoc`

### Chạy Celery Worker (Bắt buộc để gửi email/tác vụ nền)
```bash
# Windows (Yêu cầu gevent hoặc tương đương)
celery -A app.core.celery_app worker --loglevel=info --pool=solis

# Linux/macOS
celery -A app.core.celery_app worker --loglevel=info
```
