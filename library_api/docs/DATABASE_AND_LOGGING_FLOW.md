# Phân tích Luồng Kết nối Database và Ghi Log

Tài liệu này giải thích chi tiết về cách ứng dụng FastAPI kết nối với cơ sở dữ liệu và cách ghi log (ghi nhật ký) một cách hiệu quả để gỡ lỗi (debug).

## 1. Luồng Kết nối Database của Ứng dụng Chính (FastAPI)

Luồng kết nối của ứng dụng rất chuẩn và tập trung, giúp việc quản lý trở nên dễ dàng.

1.  **Tải Cấu hình từ `.env`**:
    *   Khi ứng dụng khởi động, file `library_api/app/core/database.py` được thực thi.
    *   Nó sử dụng thư viện `dotenv` để đọc các biến môi trường từ file `.env` của bạn. Biến quan trọng nhất ở đây là `DATABASE_URL`. Đây là "nguồn chân lý" (source of truth) cho kết nối database của ứng dụng.

2.  **Tạo "Engine"**:
    *   Dựa trên chuỗi `DATABASE_URL` đọc được, một đối tượng `engine` của thư viện SQLAlchemy được tạo ra.
    *   `engine` quản lý các kết nối ở mức độ thấp tới database. Bạn có thể coi nó như một "nhà máy" chuyên sản xuất các kết nối.

3.  **Tạo "Session" cho mỗi Request**:
    *   File `database.py` cũng định nghĩa một hàm là `get_session`. Đây là một "dependency" của FastAPI.
    *   Mỗi khi có một request từ người dùng đến một API endpoint cần truy cập database, FastAPI sẽ tự động gọi hàm `get_session` này.

4.  **Thực thi và Tự động Đóng**:
    *   Hàm `get_session` sẽ tạo ra một `session` (phiên làm việc) riêng biệt cho chỉ request đó, "đưa" nó vào trong hàm xử lý endpoint của bạn để bạn sử dụng.
    *   Khi request xử lý xong (dù thành công hay thất bại), `session` đó sẽ được tự động đóng lại để giải phóng tài nguyên.

**Tóm lại:** Luồng của ứng dụng chính rất gọn gàng và dễ theo dõi: **File `.env` -> `database.py` (tạo engine) -> `get_session` (cung cấp session) -> Endpoint (sử dụng session)**.

---

## 2. Điểm Kết nối Thứ hai: Công cụ Migration (Alembic)

Ngoài ứng dụng chính, project còn một nơi khác cũng định nghĩa kết nối database.

*   **File cấu hình riêng**: Công cụ migration **Alembic** đọc cấu hình từ file `library_api/alembic.ini`.
*   **Kết nối Hardcode**: Bên trong file này, chuỗi kết nối đang bị ghi cứng (hardcoded):
    ```ini
    sqlalchemy.url = mysql+pymysql://root:1@localhost:3308/library_db
    ```
*   **Rủi ro**: Việc này tạo ra sự không nhất quán. Khi chạy trong Docker, cấu hình này sẽ gây lỗi vì `localhost` bên trong container `backend` không phải là container `db`. Lệnh `alembic upgrade head` trong `Dockerfile` sẽ thất bại vì lý do này.

**Khuyến nghị**: Nên sửa file `alembic.ini` và `alembic/env.py` để nó cũng đọc chuỗi kết nối từ biến môi trường, thống nhất với ứng dụng chính.

---

## 3. Ghi Log và Debug (Tại sao `print` không hoạt động?)

Đây là một vấn đề thường gặp khi làm việc với Docker và các web server chuyên dụng như Uvicorn.

### Nguyên nhân

1.  **Cơ chế Đệm (Buffering)**: Theo mặc định, Python không `print` ngay lập tức ra màn hình. Nó sẽ giữ lại output trong một bộ đệm (buffer) và chỉ "xả" (flush) ra khi bộ đệm đầy hoặc khi chương trình kết thúc. Vì web server là một tiến trình chạy mãi mãi, output của bạn có thể bị "kẹt" lại trong bộ đệm.

2.  **Uvicorn Quản lý Output**: `uvicorn` (server chạy app FastAPI của bạn) sẽ "bắt" toàn bộ output của ứng dụng (bao gồm cả `print`) và đưa nó qua hệ thống logging của riêng mình. Nó được thiết kế để làm việc với module `logging` của Python, do đó `print` không phải là công cụ phù hợp để ghi log trong môi trường này.

### Cách xem log debug hiệu quả

*   **Cách 1: Sửa nhanh để dùng `print` (Quick Fix)**
    Bạn có thể buộc Python không sử dụng bộ đệm bằng cách thêm một biến môi trường vào service `backend` trong file `docker-compose.yml`:

    ```yaml
    services:
      backend:
        # ... các cấu hình khác
        environment:
          - PYTHONUNBUFFERED=1 # Thêm dòng này
    ```
    Sau khi thêm, hãy chạy lại `docker-compose up`. Các câu lệnh `print` của bạn sẽ xuất hiện ngay lập tức trong `docker-compose logs backend`.

*   **Cách 2: Cách làm Đúng chuẩn (dùng `logging`)**
    Cách làm chuyên nghiệp và đáng tin cậy nhất là sử dụng module `logging` có sẵn của Python.

    **Ví dụ:**
    ```python
    import logging

    # ...bên trong một hàm xử lý endpoint...
    logging.info("Bắt đầu xử lý request của user.")
    try:
        # ... làm gì đó ...
        logging.info("Xử lý thành công!")
    except Exception as e:
        logging.error(f"Đã xảy ra lỗi: {e}")
    ```
    Những log này được Uvicorn xử lý đúng cách và sẽ luôn luôn hiển thị một cách đáng tin cậy trong `docker-compose logs`.
