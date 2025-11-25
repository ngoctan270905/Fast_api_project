# Hướng dẫn Triển khai Logging Middleware

Tài liệu này giải thích mục đích, cách hoạt động và kế hoạch triển khai một middleware chuyên dụng để ghi log cho mọi request và response trong ứng dụng FastAPI.

## 1. Mục tiêu

Mục tiêu chính là xây dựng một hệ thống ghi log (logging) tập trung và tự động. Việc này cực kỳ quan trọng cho các công việc sau:
- **Debugging**: Dễ dàng truy vết lỗi bằng cách xem lại lịch sử các request đã dẫn đến sự cố.
- **Monitoring**: Theo dõi tình hình hoạt động của hệ thống, xem các endpoint nào được gọi nhiều, endpoint nào chậm.
- **Security Auditing**: Ghi lại dấu vết về các truy cập vào hệ thống, phát hiện các hành vi bất thường.

## 2. Các chức năng cần có

Middleware cần ghi lại các thông tin hữu ích sau cho mỗi request:

- **Thông tin Request**:
    - `request_id`: Một mã định danh duy nhất cho mỗi request để dễ dàng tìm kiếm và gom nhóm log.
    - Phương thức HTTP (ví dụ: `GET`, `POST`).
    - Đường dẫn URL (ví dụ: `/api/v1/books/1`).
    - Địa chỉ IP của client.
    - User-Agent của client.
- **Thông tin Response**:
    - Status code (ví dụ: `200 OK`, `404 Not Found`, `500 Internal Server Error`).
- **Thông tin hiệu suất**:
    - Thời gian xử lý request (tính bằng mili giây).

## 3. Luồng hoạt động của Middleware

Middleware hoạt động như một "lớp vỏ" bao bọc quanh toàn bộ quá trình xử lý của ứng dụng.

1.  **Bắt đầu Request**: Ngay khi một request đến, middleware sẽ là một trong những thành phần đầu tiên xử lý nó.
2.  **Tạo `request_id`**: Middleware tạo một mã định danh duy nhất (ví dụ, sử dụng `uuid.uuid4()`) cho request này.
3.  **Ghi log Request đến**: Middleware ghi lại các thông tin của request (phương thức, URL, IP) kèm với `request_id`.
4.  **Bắt đầu đếm giờ**: Middleware ghi lại thời điểm bắt đầu xử lý request.
5.  **Chuyển tiếp xử lý**: Middleware gọi `response = await call_next(request)` để cho phép FastAPI và các endpoint thực hiện công việc của chúng.
6.  **Kết thúc Request**: Sau khi endpoint đã xử lý xong và trả về một response, middleware sẽ nhận lại response này.
7.  **Dừng đếm giờ**: Middleware lấy thời điểm hiện tại và tính toán tổng thời gian xử lý đã trôi qua.
8.  **Ghi log Response đi**: Middleware ghi lại các thông tin của response (status code) và thời gian xử lý, cũng kèm với `request_id` đã tạo ở bước 2.
9.  **Trả response về cho client**: Middleware trả đối tượng response về cho client.

## 4. Kế hoạch triển khai

### Bước 1: Cấu hình hệ thống Logging của Python

Chúng ta sẽ sử dụng thư viện `logging` có sẵn của Python.

- **File cần sửa**: `library_api/app/main.py`
- **Hành động**: Thêm đoạn code cấu hình logging cơ bản vào đầu file.

```python
# Thêm vào đầu file main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
```

### Bước 2: Tạo file `logging_middleware.py`

Chúng ta sẽ tạo một file middleware mới để chứa logic ghi log.

- **Tạo file mới**: `library_api/app/middleware/logging_middleware.py`
- **Nội dung file**:

```python
import logging
import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Lấy logger
logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Gán một ID duy nhất cho mỗi request
        request_id = str(uuid.uuid4())
        
        # Lấy thông tin request
        method = request.method
        path = request.url.path
        client_ip = request.client.host
        
        # Ghi log trước khi xử lý
        logger.info(f"Request ID: {request_id} | Bắt đầu: {method} {path} | IP: {client_ip}")
        
        # Bắt đầu đếm thời gian
        start_time = time.time()
        
        # Chuyển request đi xử lý
        response = await call_next(request)
        
        # Kết thúc đếm thời gian và tính toán
        process_time = (time.time() - start_time) * 1000  # ms
        
        # Ghi log sau khi xử lý xong
        status_code = response.status_code
        logger.info(f"Request ID: {request_id} | Kết thúc: {method} {path} | Status: {status_code} | Thời gian: {process_time:.2f}ms")
        
        return response

```

### Bước 3: Đăng ký Middleware với ứng dụng FastAPI

Cuối cùng, chúng ta cần nói cho FastAPI biết để sử dụng middleware này.

- **File cần sửa**: `library_api/app/main.py`
- **Hành động**: Import và thêm `LoggingMiddleware`.

```python
# Trong file main.py

# ... các import khác
from app.middleware.logging_middleware import LoggingMiddleware # <--- Import mới

# ... (khởi tạo app = FastAPI())

# Thêm Middleware
# Lưu ý: LoggingMiddleware nên được thêm vào trước AuthMiddleware
# để nó có thể ghi log cho cả các request bị lỗi xác thực.
app.add_middleware(LoggingMiddleware)
# app.add_middleware(AuthMiddleware) # Middleware xác thực đã có

# ... (các phần còn lại của file)
```

Với 3 bước trên, hệ thống sẽ tự động ghi lại thông tin của mọi request đi qua nó, giúp việc quản lý và gỡ lỗi trở nên đơn giản hơn rất nhiều.

## 5. Luồng hoạt động chi tiết của Logging Middleware

Để hiểu rõ hơn về cách Logging Middleware hoạt động trong chu trình request/response của FastAPI, dưới đây là mô tả chi tiết từng bước:

1.  **Request đến ứng dụng**:
    *   Một client (ví dụ: trình duyệt web, Postman) gửi một HTTP request tới ứng dụng FastAPI của bạn.

2.  **Middleware chặn Request**:
    *   Do `LoggingMiddleware` được đăng ký rất sớm trong chuỗi middleware (trước `AuthMiddleware`), nó sẽ là một trong những thành phần đầu tiên đón nhận request này.

3.  **Tạo `request_id` duy nhất**:
    *   Trong phương thức `dispatch` của `LoggingMiddleware`, một mã định danh duy nhất (`request_id`) được tạo ra cho mỗi request. Mã này giúp bạn dễ dàng theo dõi toàn bộ vòng đời của một request trong các file log.
    *   Ví dụ: `request_id = str(uuid.uuid4())`

4.  **Trích xuất thông tin Request**:
    *   Middleware truy cập vào đối tượng `request` để lấy các thông tin cần thiết:
        *   `request.method` (ví dụ: "GET", "POST", "PUT")
        *   `request.url.path` (ví dụ: "/api/v1/users/me")
        *   `request.client.host` (địa chỉ IP của client gửi request)

5.  **Ghi log Request đến**:
    *   Trước khi request được xử lý sâu hơn, một dòng log được ghi lại, chứa `request_id` và các thông tin cơ bản về request đến.
    *   Ví dụ: `logger.info(f"Request ID: {request_id} | Bắt đầu: {method} {path} | IP: {client_ip}")`

6.  **Bắt đầu đo thời gian**:
    *   Thời điểm hiện tại được ghi lại (`start_time = time.time()`) để tính toán thời gian xử lý toàn bộ request.

7.  **Chuyển tiếp Request**:
    *   Middleware gọi `response = await call_next(request)`. Điều này cho phép request tiếp tục đi qua các middleware khác (ví dụ: `AuthMiddleware`) và cuối cùng đến được hàm xử lý (route handler) tương ứng trong FastAPI.
    *   `call_next` đợi cho đến khi hàm xử lý và tất cả các middleware còn lại hoàn tất công việc và trả về một đối tượng `response`.

8.  **Ứng dụng xử lý Request**:
    *   Trong khi `call_next(request)` đang chạy, request được xử lý bởi ứng dụng:
        *   Nếu là request đến endpoint được bảo vệ, `AuthMiddleware` sẽ xác thực token và gắn thông tin user vào `request.state`.
        *   FastAPI tìm và gọi hàm handler cho endpoint đó.
        *   Logic nghiệp vụ của bạn (ví dụ: truy vấn database, tính toán) được thực thi.
        *   Hàm handler trả về một đối tượng `response`.

9.  **Nhận lại Response**:
    *   Sau khi ứng dụng hoàn tất và trả về response, `LoggingMiddleware` sẽ nhận lại đối tượng `response` này.

10. **Dừng đo thời gian và tính toán**:
    *   Thời điểm hiện tại được ghi lại lần nữa (`end_time = time.time()`).
    *   Thời gian xử lý `process_time` được tính toán: `(end_time - start_time) * 1000` (để có mili giây).

11. **Trích xuất thông tin Response**:
    *   Middleware lấy `status_code` từ đối tượng `response` (ví dụ: `response.status_code`).

12. **Ghi log Response đi**:
    *   Một dòng log khác được ghi lại, chứa `request_id`, thông tin request ban đầu, `status_code` của response và `process_time`.
    *   Ví dụ: `logger.info(f"Request ID: {request_id} | Kết thúc: {method} {path} | Status: {status_code} | Thời gian: {process_time:.2f}ms")`

13. **Trả Response về Client**:
    *   Cuối cùng, `LoggingMiddleware` trả đối tượng `response` về cho client, hoàn tất chu trình.

Thông qua luồng này, mọi request đi qua ứng dụng đều được ghi lại một cách có hệ thống, cung cấp cái nhìn toàn diện về hoạt động của API, hiệu suất và giúp ích rất nhiều cho việc gỡ lỗi.
