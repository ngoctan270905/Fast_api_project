# Kế Hoạch Tích Hợp Đăng Nhập Bằng GitHub

Tài liệu này vạch ra các bước cần thiết để tích hợp chức năng đăng nhập bằng tài khoản GitHub vào hệ thống xác thực của dự án, bao gồm cả backend (FastAPI) và frontend (React).

## 📝 Tổng Quan

Mục tiêu là cho phép người dùng đăng nhập vào ứng dụng bằng tài khoản GitHub của họ, tương tự như chức năng đăng nhập bằng Google hiện có. Luồng xác thực sẽ tuân theo tiêu chuẩn OAuth 2.0.

### Luồng Hoạt Động (OAuth 2.0 Flow)

1.  **Người dùng** nhấp vào nút "Đăng nhập với GitHub" trên trang Login của frontend.
2.  **Frontend** chuyển hướng người dùng đến endpoint `/api/v1/auth/github/login` của backend.
3.  **Backend** tạo và chuyển hướng người dùng đến trang xác thực của GitHub, kèm theo `client_id` và các tham số cần thiết.
4.  **Người dùng** cấp quyền cho ứng dụng trên trang của GitHub.
5.  **GitHub** chuyển hướng người dùng trở lại endpoint `/api/v1/auth/github/callback` của backend, kèm theo một mã `code` tạm thời.
6.  **Backend** nhận `code`, gửi lại cho GitHub cùng với `client_id` và `client_secret` để đổi lấy `access_token`.
7.  **Backend** dùng `access_token` để lấy thông tin người dùng từ API của GitHub.
8.  **Backend** xử lý thông tin người dùng:
    *   Nếu người dùng GitHub đã tồn tại trong bảng `oauth_accounts`, tiến hành đăng nhập.
    *   Nếu chưa, kiểm tra email người dùng. Nếu email đã có trong bảng `users`, liên kết tài khoản GitHub này với tài khoản `users` có sẵn.
    *   Nếu email chưa tồn tại, tạo một tài khoản `users` mới và một bản ghi `oauth_accounts` tương ứng.
9.  **Backend** tạo một JWT (JSON Web Token) cho người dùng và chuyển hướng về trang callback của frontend (`/auth/callback`), đính kèm JWT này dưới dạng query parameter.
10. **Frontend** tại trang callback nhận JWT, lưu vào `localStorage`, cập nhật trạng thái xác thực và chuyển người dùng đến trang chính.

---

## 🛠️ Kế Hoạch Triển Khai

### Phần 1: Backend (FastAPI)

1.  **Cập nhật Cấu hình Môi trường:**
    *   Thêm các biến mới vào file `.env.example` và `.env`:
        ```env
        # ========================
        # GITHUB OAUTH SETTINGS
        # ========================
        GITHUB_CLIENT_ID=your_github_client_id
        GITHUB_CLIENT_SECRET=your_github_client_secret
        ```
    *   Vào `app/core/config.py`, cập nhật class `Settings` để nạp các biến môi trường trên.

2.  **Đăng ký GitHub OAuth Provider (trong `app/core/oauth.py`):**
    *   Dựa theo cách đăng ký của Google, thêm một provider mới cho GitHub sử dụng `Authlib`.
    *   Thông tin cần thiết cho việc đăng ký:
        *   `name`: 'github'
        *   `client_id`: `settings.GITHUB_CLIENT_ID`
        *   `client_secret`: `settings.GITHUB_CLIENT_SECRET`
        *   `authorize_url`: `https://github.com/login/oauth/authorize`
        *   `access_token_url`: `https://github.com/login/oauth/access_token`
        *   `api_base_url`: `https://api.github.com/`
        *   `client_kwargs`: `{'scope': 'user:email'}` (để yêu cầu quyền truy cập email người dùng).

3.  **Tạo API Endpoints:**
    *   Tạo một file router mới `app/api/v1/endpoints/social_auth.py` hoặc thêm vào router xác thực hiện có.
    *   **Endpoint 1: Login** (`/api/v1/auth/github/login`)
        *   Sử dụng `oauth.github.authorize_redirect(request, redirect_uri)` để chuyển hướng người dùng đến GitHub.
    *   **Endpoint 2: Callback** (`/api/v1/auth/github/callback`)
        *   Sử dụng `oauth.github.authorize_access_token(request)` để lấy token.
        *   Dùng `oauth.github.get('user', token=token)` để lấy thông tin người dùng.
        *   Triển khai logic kiểm tra/tạo người dùng như mô tả trong luồng hoạt động.
        *   Tạo JWT và redirect về `f"{settings.CLIENT_BASE_URL}/auth/callback?token={jwt_token}"`.

4.  **Cập nhật `UserService` và `UserRepository`:**
    *   Đảm bảo các hàm xử lý logic (tìm người dùng qua email, tạo người dùng, tạo tài khoản OAuth) đủ linh hoạt để tái sử dụng. Logic này có thể đã tồn tại từ việc tích hợp Google Login.

### Phần 2: Frontend (React)

1.  **Thêm Nút Đăng Nhập GitHub (trong `src/pages/LoginPage.tsx`):**
    *   Tạo một component `Button` hoặc một thẻ `<a>` mới có nội dung "Đăng nhập với GitHub".
    *   Thiết lập `href` cho nút này trỏ đến endpoint của backend: `http://127.0.0.1:8000/api/v1/auth/github/login`. (Nên lấy URL gốc từ biến môi trường `VITE_API_BASE_URL`).

2.  **Xử lý Callback (trong `src/pages/AuthCallbackPage.tsx`):**
    *   Trang này có nhiệm vụ lấy `token` từ URL query params.
    *   Lưu token vào `localStorage` hoặc `sessionStorage`.
    *   Cập nhật `AuthContext` để thông báo cho toàn bộ ứng dụng rằng người dùng đã đăng nhập.
    *   Chuyển hướng người dùng đến trang chủ hoặc trang trước đó.
    *   **Lưu ý:** Nếu trang này được thiết kế tốt, có thể sẽ không cần chỉnh sửa gì cả vì nó chỉ nhận token và không quan tâm đến phương thức đăng nhập là Google hay GitHub.

---

## ✅ Checklist Công Việc

-   [ ] **Backend**: Lấy `Client ID` và `Client Secret` từ trang cài đặt OAuth App trên GitHub.
-   [ ] **Backend**: Cập nhật file `.env` và `config.py`.
-   [ ] **Backend**: Cập nhật `oauth.py` để đăng ký GitHub provider.
-   [ ] **Backend**: Tạo các endpoint `/login` và `/callback` cho GitHub.
-   [ ] **Backend**: Hoàn thiện logic xử lý callback (lấy thông tin, tạo/liên kết tài khoản, tạo JWT).
-   [ ] **Frontend**: Thêm nút "Đăng nhập với GitHub" vào trang Login.
-   [ ] **Frontend**: Kiểm tra và đảm bảo `AuthCallbackPage.tsx` hoạt động đúng với luồng mới.
-   [ ] **Testing**: Kiểm thử toàn bộ luồng đăng nhập với một tài khoản GitHub.
