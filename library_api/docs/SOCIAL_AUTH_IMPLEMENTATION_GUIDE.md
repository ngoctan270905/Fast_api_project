# Hướng Dẫn Triển Khai Xác Thực Xã Hội (Social Authentication) với Google

Đây là kế hoạch chi tiết để tích hợp chức năng "Đăng nhập với Google" sử dụng OAuth2 vào dự án của bạn. Chúng ta sẽ sử dụng thư viện `Authlib` vì tính linh hoạt và mạnh mẽ của nó.

Và đúng vậy, chúng ta **cần cập nhật cơ sở dữ liệu** để hỗ trợ liên kết tài khoản mạng xã hội với tài khoản người dùng trong hệ thống.

---

## Kế Hoạch Triển Khai

### Bước 1: Cấu Hình Google Cloud và Lấy Credentials

1.  **Truy cập Google Cloud Console:**
    -   Tới [Google Cloud Console](https://console.cloud.google.com/).
    -   Tạo một dự án mới (nếu chưa có).
2.  **Tạo OAuth 2.0 Client ID:**
    -   Vào mục "APIs & Services" -> "Credentials".
    -   Nhấn "Create Credentials" -> "OAuth client ID".
    -   Chọn "Web application".
    -   Trong "Authorized redirect URIs", thêm URL callback của bạn. Đối với môi trường local, nó sẽ là:
        -   `http://127.0.0.1:8000/api/v1/auth/google/callback`
3.  **Lấy Client ID và Client Secret:**
    -   Sau khi tạo, Google sẽ cung cấp cho bạn `Client ID` và `Client Secret`. Hãy lưu lại cẩn thận.

### Bước 2: Cập Nhật Cấu Hình và Cài Đặt Thư Viện

1.  **Cài đặt `Authlib`:**
    ```bash
    pip install Authlib
    ```
    -   Đừng quên thêm `Authlib` vào file `requirements.txt`.

2.  **Thêm Cấu Hình vào `.env`:**
    -   Mở file `.env` (hoặc `.env.example` để làm mẫu) và thêm vào các biến môi trường:
    ```
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret
    ```

3.  **Cập nhật `app/core/config.py`:**
    -   Thêm các biến `GOOGLE_CLIENT_ID` và `GOOGLE_CLIENT_SECRET` vào class `Settings`.

### Bước 3: Cập Nhật Cấu Trúc Cơ Sở Dữ Liệu

Chúng ta cần một bảng mới để lưu thông tin tài khoản OAuth và cập nhật bảng `users`.

1.  **Tạo Model `OAuthAccount`:**
    -   Tạo file mới `app/models/oauth_account.py`.
    -   Model này sẽ liên kết với `User` và lưu trữ thông tin nhà cung cấp (Google, Facebook, etc.).
    -   **Nội dung `app/models/oauth_account.py` (dự kiến):**
        ```python
        from sqlmodel import Field, SQLModel, Relationship
        from app.models.users import User

        class OAuthAccount(SQLModel, table=True):
            id: int | None = Field(default=None, primary_key=True)
            provider: str
            account_id: str
            access_token: str
            
            user_id: int = Field(foreign_key="users.id")
            user: "User" = Relationship(back_populates="oauth_accounts")
        ```
        -   **Lưu ý:** `account_id` là ID duy nhất mà Google cung cấp cho người dùng (`sub`).

2.  **Cập Nhật Model `User` (`app/models/users.py`):**
    -   **Quan trọng:** Cho phép `hashed_password` có thể là `None` (`Optional[str]`), vì người dùng đăng ký qua Google sẽ không có mật khẩu.
    -   Thêm mối quan hệ ngược lại với `OAuthAccount`:
        ```python
        oauth_accounts: list["OAuthAccount"] = Relationship(back_populates="user")
        ```

3.  **Tạo và Áp Dụng Migration:**
    -   Chạy `alembic revision --autogenerate -m "add_oauth_accounts_table"`
    -   Kiểm tra lại file migration và chạy `alembic upgrade head`.

### Bước 4: Tích Hợp `Authlib` và Logic Xử Lý

1.  **Cấu hình `Authlib`:**
    -   Trong `app/services/auth_service.py` (hoặc tạo file mới `app/core/oauth.py`), khởi tạo `OAuth` object từ `Authlib`.
    ```python
    from authlib.integrations.starlette_client import OAuth
    from app.core.config import settings

    oauth = OAuth()
    oauth.register(
        name='google',
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )
    ```

2.  **Cập nhật `UserRepository`:**
    -   Thêm một phương thức để tìm hoặc tạo người dùng dựa trên thông tin từ Google. Logic sẽ như sau:
        -   Kiểm tra xem có `OAuthAccount` nào với `provider='google'` và `account_id` tương ứng không. Nếu có, trả về user liên quan.
        -   Nếu không, kiểm tra xem có user nào với `email` tương ứng không. Nếu có, tạo `OAuthAccount` mới và liên kết với user đó.
        -   Nếu không có cả hai, tạo một `User` mới và một `OAuthAccount` mới.

### Bước 5: Tạo API Endpoints

Thêm các endpoint sau vào một file router mới (ví dụ: `app/api/v1/endpoints/social_auth.py`).

1.  **Endpoint `/login/google` (GET):**
    -   **Chức năng:** Chuyển hướng người dùng đến trang đăng nhập của Google.
    -   **Logic:**
        -   Lấy `redirect_uri` bằng `request.url_for('auth_callback', provider='google')`.
        -   Gọi `await oauth.google.authorize_redirect(request, redirect_uri)`.

2.  **Endpoint `/auth/google/callback` (GET):**
    -   **Chức năng:** Xử lý callback từ Google sau khi người dùng xác thực.
    -   **Logic:**
        -   Dùng `await oauth.google.authorize_access_token(request)` để lấy `token`.
        -   Lấy thông tin người dùng từ Google: `user_info = await oauth.google.parse_id_token(request, token)`.
        -   Sử dụng `UserRepository` để tìm hoặc tạo người dùng (`find_or_create_by_oauth`).
        -   Tạo một token JWT của hệ thống cho người dùng này.
        -   Trả về token JWT cho client, hoàn tất quá trình đăng nhập.

### Bước 6: Tích Hợp Router

-   Thêm router `social_auth` vừa tạo vào `app/api/v1/router.py`.

---

Sau khi hoàn thành các bước trên, bạn có thể truy cập `/api/v1/login/google` trên trình duyệt. Hệ thống sẽ tự động chuyển hướng bạn qua Google, và sau khi đăng nhập thành công, bạn sẽ được trả về ứng dụng với một token JWT hợp lệ.

---

## Ghi Chú Sửa Lỗi (Troubleshooting Notes)

Trong quá trình triển khai, chúng ta đã gặp và sửa một số lỗi sau:

1.  **Lỗi `pydantic.ValidationError` khi khởi động:**
    -   **Nguyên nhân:** Ứng dụng không tìm thấy `GOOGLE_CLIENT_ID` và `GOOGLE_CLIENT_SECRET` trong file `.env` khi khởi tạo `Settings`.
    -   **Giải pháp:** Thêm các biến này vào file `.env` với giá trị placeholder, và sau đó người dùng sẽ thay thế bằng credentials thật.

2.  **Lỗi `ModuleNotFoundError: No module named 'app.api.v1.deps'`:**
    -   **Nguyên nhân:** Viết sai đường dẫn import trong file `app/api/v1/endpoints/social_auth.py`. File chứa dependencies đúng là `app/api/deps.py`.
    -   **Giải pháp:** Sửa dòng `from app.api.v1.deps import ...` thành `from app.api.deps import ...`.

3.  **Lỗi `AttributeError: 'OAuth' object has no attribute 'init_app'`:**
    -   **Nguyên nhân:** Sử dụng sai phương thức `init_app` cho thư viện `Authlib` trong môi trường Starlette/FastAPI. Phương thức này dành cho các framework khác như Flask.
    -   **Giải pháp:** Xóa bỏ hàm `register_oauth_clients` và lời gọi `oauth.init_app(app)`. Việc đăng ký client (`oauth.register(...)`) được thực hiện trực tiếp ở cấp module trong `app/core/oauth.py` là đủ.