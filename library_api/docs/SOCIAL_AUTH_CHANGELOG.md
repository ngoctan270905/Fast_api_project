# Changelog: Triển Khai Xác Thực Xã Hội với Google

Đây là danh sách chi tiết tất cả các thay đổi đã được thực hiện ở phía backend để tích hợp chức năng "Đăng nhập với Google".

### 1. Cài đặt & Cấu hình

-   **`requirements.txt`**:
    -   Thêm thư viện `authlib` và các phụ thuộc của nó (`cryptography`, `cffi`, `pycparser`).

-   **`.env.example`**:
    -   Thêm các biến môi trường mẫu cho Google OAuth:
        ```
        GOOGLE_CLIENT_ID=your_google_client_id
        GOOGLE_CLIENT_SECRET=your_google_client_secret
        ```

-   **`.env`**:
    -   Thêm các biến môi trường trên với giá trị placeholder để ứng dụng có thể khởi chạy. **Đây là nơi bạn cần điền credentials thật.**

-   **`app/core/config.py`**:
    -   Thêm `GOOGLE_CLIENT_ID: str` và `GOOGLE_CLIENT_SECRET: str` vào class `Settings` để Pydantic đọc các biến môi trường từ file `.env`.

### 2. Cập nhật Cơ sở dữ liệu (Models & Migrations)

-   **`app/models/oauth_account.py` (File mới)**:
    -   Tạo model `OAuthAccount` để lưu trữ thông tin từ nhà cung cấp OAuth (provider, account_id, access_token) và liên kết nó với `User` model qua `user_id`.

-   **`app/models/users.py`**:
    -   Chỉnh sửa trường `hashed_password` thành `Optional[str]` (có thể `NULL`) để cho phép người dùng đăng ký qua mạng xã hội mà không cần mật khẩu.
    -   Thêm mối quan hệ `oauth_accounts: List["OAuthAccount"]` để liên kết ngược lại với bảng `oauth_accounts`.

-   **`alembic/versions/0c2096824ce0_add_oauth_accounts_table.py` (File mới)**:
    -   File migration được Alembic tự động tạo ra để:
        -   Tạo bảng `oauth_account` mới trong database.
        -   Chỉnh sửa cột `hashed_password` trong bảng `users` thành `NULLABLE`.

### 3. Logic & Tích hợp

-   **`app/core/oauth.py` (File mới)**:
    -   Khởi tạo và cấu hình `Authlib` OAuth client.
    -   Đăng ký client `google` với `client_id`, `client_secret` và các `scope` cần thiết (openid, email, profile).

-   **`app/main.py`**:
    -   Import hàm `register_oauth_clients` từ `app.core.oauth`.
    -   Gọi hàm `register_oauth_clients(app)` để khởi tạo OAuth client cùng với ứng dụng FastAPI.

-   **`app/repositories/user_repository.py`**:
    -   Thêm phương thức mới `find_or_create_by_oauth`.
    -   Logic của phương thức này:
        1.  Kiểm tra xem `OAuthAccount` đã tồn tại chưa.
        2.  Nếu chưa, kiểm tra xem `User` với email tương ứng đã tồn tại chưa.
        3.  Nếu cả hai đều chưa, tạo cả `User` và `OAuthAccount` mới.
        4.  Xử lý trường hợp `username` bị trùng bằng cách thêm số vào cuối.

-   **`app/services/auth_service.py`**:
    -   Thêm phương thức mới `handle_google_oauth(request)`.
    -   Phương thức này chứa toàn bộ logic nghiệp vụ:
        1.  Nhận callback từ Google.
        2.  Lấy token và thông tin người dùng.
        3.  Gọi `user_repository.find_or_create_by_oauth` để xử lý phía database.
        4.  Tạo một token JWT của hệ thống và trả về.

### 4. Endpoints & Routing

-   **`app/api/v1/endpoints/social_auth.py` (File mới)**:
    -   Tạo một router mới cho các endpoint xác thực xã hội.
    -   **`GET /login/google`**: Endpoint để chuyển hướng người dùng đến trang đăng nhập của Google.
    -   **`GET /auth/google/callback`**: Endpoint nhận callback từ Google, gọi `AuthService` để xử lý và cuối cùng chuyển hướng người dùng về frontend kèm theo JWT.

-   **`app/api/v1/router.py`**:
    -   Import router `social_auth` mới.
    -   Thêm `social_auth.router` vào `api_router` chính để các endpoint mới có thể được truy cập.
