# Kế hoạch Nâng cao Bảo mật cho API

Tài liệu này tổng hợp tình hình bảo mật hiện tại của dự án và đề ra kế hoạch chi tiết để triển khai các tính năng bảo mật nâng cao còn thiếu.

## 1. Tổng quan Tình hình Bảo mật Hiện tại

### Các tính năng đã có

- **Xác thực JWT**: Sử dụng JWT access token để bảo vệ các endpoint.
- **Băm mật khẩu (Password Hashing)**: Sử dụng `bcrypt` (thông qua `passlib`) để lưu trữ mật khẩu một cách an toàn.
- **Chống SQL Injection**: Sử dụng ORM (SQLAlchemy/SQLModel) giúp ngăn chặn các cuộc tấn công SQL injection bằng cách tham số hóa các truy vấn.
- **Chính sách CORS**: Có cấu hình Cross-Origin Resource Sharing để kiểm soát truy cập từ các domain khác.
- **Logging và Middleware Xác thực**: Đã có middleware để ghi log request và xác thực token tập trung.

### Các tính năng còn thiếu

- **Cơ chế Refresh Token**: Hiện tại chỉ sử dụng access token có thời gian sống ngắn. Người dùng phải đăng nhập lại sau khi token hết hạn.
- **Token Blacklist**: Không có cơ chế vô hiệu hóa token ngay lập tức (ví dụ: khi người dùng logout). Token vẫn hợp lệ cho đến khi hết hạn.
- **Giới hạn tần suất Request (Rate Limiting)**: Không có biện pháp nào để ngăn chặn các cuộc tấn công brute-force hoặc DoS bằng cách giới hạn số lượng request từ một client.
- **Làm sạch dữ liệu đầu vào (Input Sanitization)**: Chưa có cơ chế để làm sạch dữ liệu do người dùng cung cấp (ví dụ: tên sách, mô tả) để chống lại các cuộc tấn công Cross-Site Scripting (XSS).

---

## 2. Kế hoạch Nâng cao Bảo mật

Dưới đây là kế hoạch chi tiết để triển khai từng tính năng còn thiếu.

### 2.1. Triển khai Refresh Tokens (Lưu vào Database)

- **Mục tiêu**: Cho phép người dùng duy trì phiên đăng nhập lâu dài một cách an toàn. Việc lưu refresh token vào database cho phép chúng ta có thể thu hồi (revoke) chúng bất cứ lúc nào, tăng cường bảo mật so với refresh token không trạng thái (stateless).
- **Kế hoạch triển khai**:

    **Bước 1: Tạo Bảng `refresh_tokens` trong Database**
    1.  **Tạo Model**: Tạo file mới `library_api/app/models/refresh_token.py` với nội dung sau để định nghĩa cấu trúc bảng:
        ```python
        from datetime import datetime
        from typing import Optional, List
        from sqlmodel import Field, Relationship, SQLModel
        
        class RefreshToken(SQLModel, table=True):
            __tablename__ = "refresh_tokens"

            id: Optional[int] = Field(default=None, primary_key=True)
            token: str = Field(unique=True, index=True)
            user_id: int = Field(foreign_key="users.id")
            expires_at: datetime
            created_at: datetime = Field(default_factory=datetime.utcnow)
            revoked_at: Optional[datetime] = Field(default=None)

            user: "User" = Relationship(back_populates="refresh_tokens")
        ```
    2.  **Cập nhật Model `User`**: Trong file `library_api/app/models/users.py`, thêm mối quan hệ ngược lại vào class `User`:
        ```python
        # Thêm vào trong class User
        refresh_tokens: List["RefreshToken"] = Relationship(back_populates="user")
        ```
        Đừng quên import `List` và `RefreshToken` (dưới dạng string để tránh circular import).
    3.  **Tạo Migration**: Chạy các lệnh Alembic để tạo bảng trong database:
        ```sh
        alembic revision --autogenerate -m "create refresh_tokens table"
        alembic upgrade head
        ```

    **Bước 2: Cập nhật Logic Tạo và Quản lý Token**
    1.  **Tạo `TokenService`**: Tạo một service mới để quản lý logic của refresh token (tạo, xác thực, xoá).
    2.  **Hàm tạo Refresh Token**: Trong `TokenService`, tạo hàm `create_refresh_token(user_id: int)`. Hàm này sẽ:
        - Tạo một chuỗi token ngẫu nhiên, an toàn (ví dụ: `secrets.token_urlsafe(64)`).
        - Tính toán thời gian hết hạn (ví dụ: 30 ngày).
        - Lưu token này vào bảng `refresh_tokens` trong database cùng với `user_id` và `expires_at`.
        - Trả về chuỗi token vừa tạo.
    
    **Bước 3: Cập nhật Luồng Đăng nhập**
    1.  **Sửa `AuthService.login`**:
        - Sau khi xác thực người dùng thành công, gọi `TokenService.create_refresh_token` để tạo và lưu refresh token mới.
        - Trả về cả `access_token` (JWT, thời gian sống ngắn) và `refresh_token` (chuỗi ngẫu nhiên, thời gian sống dài) cho client.

    **Bước 4: Tạo Endpoint `/refresh`**
    1.  **Tạo endpoint mới**: Thêm `/api/v1/auth/refresh` vào `auth.py`.
    2.  **Nhận Refresh Token**: Endpoint này nhận refresh token từ client (ví dụ: trong request body).
    3.  **Xác thực Refresh Token**:
        - Sử dụng `TokenService`, viết hàm `verify_refresh_token(token: str)`.
        - Hàm này sẽ tìm token trong database, kiểm tra xem nó có tồn tại, chưa hết hạn, và chưa bị thu hồi (`revoked_at` is `None`) hay không.
        - Nếu không hợp lệ, `raise HTTPException`.
        - Nếu hợp lệ, nó sẽ trả về thông tin user tương ứng.
    4.  **Cấp Access Token mới**: Nếu refresh token hợp lệ, endpoint sẽ tạo một `access_token` mới và trả về cho client.
    5.  **(Nâng cao) Xoay vòng Refresh Token (Refresh Token Rotation)**: Để tăng bảo mật, sau khi xác thực thành công refresh token cũ, hãy thu hồi nó và tạo một refresh token hoàn toàn mới trả về cho client cùng với access token mới.

    **Bước 5: Cập nhật Luồng Đăng xuất**
    1.  **Sửa `AuthService.logout`**:
        - Endpoint logout sẽ nhận refresh token từ client.
        - Tìm refresh token này trong database và xoá nó (hoặc cập nhật trường `revoked_at` = `datetime.utcnow()`).
        - Điều này đảm bảo rằng refresh token không thể được sử dụng lại sau khi người dùng đã đăng xuất.
    2.  **(Tùy chọn) Blacklist Access Token**: Kết hợp với cơ chế blacklist access token ở mục 2.2 để vô hiệu hóa cả hai loại token khi logout.

### 2.2. Triển khai Token Blacklist

- **Mục tiêu**: Cho phép vô hiệu hóa access token ngay lập tức (ví dụ: khi người dùng logout), tăng cường bảo mật bằng cách ngăn chặn việc sử dụng lại token đã bị "thu hồi".
- **Kế hoạch triển khai (Sử dụng Redis)**:
    1.  **Tích hợp Redis**:
        - Thêm `redis` vào file `requirements.txt`.
        - Trong `app/core/config.py`, thêm các biến cấu hình cho Redis (host, port, db).
        - Tạo một file `app/core/redis.py` để quản lý kết nối đến Redis.
    2.  **Cập nhật cách tạo Token**:
        - Trong `app/core/security.py`, khi tạo access token, thêm một claim `jti` (JWT ID) duy nhất vào payload. Ví dụ: `to_encode["jti"] = str(uuid.uuid4())`.
    3.  **Tạo Blacklist Service**:
        - Tạo một service mới, ví dụ `blacklist_service.py`, chứa hàm `add_to_blacklist(jti: str, expires_in: timedelta)`. Hàm này sẽ lưu `jti` vào Redis với thời gian tự hủy bằng thời gian còn lại của token.
    4.  **Cập nhật Endpoint `/logout`**:
        - Trong `auth.py`, endpoint `/logout` sẽ lấy `jti` từ token của `current_user`, tính thời gian còn lại, và gọi `blacklist_service` để thêm `jti` vào danh sách đen.
    5.  **Cập nhật `AuthMiddleware`**:
        - Trong `auth_middleware.py`, sau khi giải mã token thành công, lấy ra `jti` và kiểm tra xem nó có tồn tại trong Redis hay không. Nếu có, `raise HTTPException(status.HTTP_401_UNAUTHORIZED)`.

### 2.3. Triển khai Rate Limiting

- **Mục tiêu**: Bảo vệ API khỏi các cuộc tấn công brute-force và DoS bằng cách giới hạn số lượng request mà một client có thể thực hiện trong một khoảng thời gian nhất định.
- **Kế hoạch triển khai**:
    1.  **Cài đặt thư viện**: Thêm `slowapi` vào `requirements.txt`.
    2.  **Cấu hình trong `main.py`**:
        - Import các thành phần cần thiết từ `slowapi`.
        - Tạo một `Limiter` instance, cấu hình để nhận dạng client dựa trên địa chỉ IP.
        - Gắn `SlowAPIMiddleware` vào ứng dụng.
        ```python
        # Trong main.py
        from slowapi import Limiter, _rate_limit_exceeded_handler
        from slowapi.util import get_remote_address
        from slowapi.errors import RateLimitExceeded

        limiter = Limiter(key_func=get_remote_address)
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        ```
    3.  **Áp dụng Rate Limit**:
        - Sử dụng decorator `@limiter.limit` cho các endpoint nhạy cảm.
        - Ví dụ, trong `auth.py`:
        ```python
        # auth.py
        from fastapi import Request

        @router.post("/login")
        @limiter.limit("5/minute") # Giới hạn 5 request mỗi phút
        async def login(request: Request, ...):
            # ...
        ```
        - Có thể áp dụng cho các endpoint: `/login`, `/register`, `/forgot-password`, `/refresh`.

### 2.4. Triển khai Input Sanitization (Chống XSS)

- **Mục tiêu**: Ngăn chặn các cuộc tấn công Cross-Site Scripting (XSS) bằng cách làm sạch các đoạn mã HTML/JavaScript độc hại từ dữ liệu do người dùng nhập vào.
- **Kế hoạch triển khai**:
    1.  **Cài đặt thư viện**: Thêm `bleach` vào `requirements.txt`.
    2.  **Tạo hàm làm sạch**:
        - Tạo một hàm tiện ích, ví dụ trong `app/utils/security_utils.py`:
        ```python
        import bleach

        def sanitize_html(input_string: str) -> str:
            """Cleans user input to prevent XSS."""
            if not input_string:
                return input_string
            # Cho phép một số tag an toàn nếu cần, hoặc xóa tất cả
            return bleach.clean(input_string, tags=[], strip=True)
        ```
    3.  **Tích hợp vào Pydantic Schemas**:
        - Cách tiếp cận tốt nhất là tự động làm sạch dữ liệu ngay khi nó được đưa vào hệ thống thông qua các schema Pydantic.
        - Sử dụng `@validator` trong các schema (`BookCreate`, `UserUpdate`, etc.) cho các trường string.
        ```python
        # ví dụ trong app/schemas/book.py
        from pydantic import validator
        from app.utils.security_utils import sanitize_html

        class BookCreate(BaseModel):
            title: str
            # ...

            _sanitize_title = validator('title', allow_reuse=True)(sanitize_html)
        ```
        - Áp dụng validator này cho tất cả các trường string mà người dùng có thể nhập vào.
