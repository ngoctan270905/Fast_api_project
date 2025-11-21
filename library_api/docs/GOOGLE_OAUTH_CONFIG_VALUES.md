# Cấu Hình Google OAuth trong Google Cloud Console

Để tích hợp thành công "Đăng nhập với Google", bạn cần cấu hình các thông số sau trong Google Cloud Console khi tạo hoặc chỉnh sửa "OAuth 2.0 Client ID":

---

### 1. JavaScript origins (Nguồn gốc JavaScript)

Trường này dùng để khai báo các URL mà từ đó frontend của bạn sẽ gửi yêu cầu xác thực.
Dựa trên cấu hình hiện tại của dự án cho môi trường phát triển cục bộ, giá trị cần điền là:

-   `http://localhost:5173`

    *(Lưu ý: `http://localhost:5173` là cổng mặc định của Vite, đã được khai báo trong `CLIENT_BASE_URL` của `.env` và `app/core/config.py`.)*

### 2. Allowed redirect URIs (URI chuyển hướng được phép)

Trường này dùng để khai báo URL callback mà Google sẽ chuyển hướng người dùng về sau khi họ xác thực thành công. Đây là endpoint backend của bạn.
Dựa trên cách triển khai backend hiện tại, giá trị cần điền là:

-   `http://127.0.0.1:8000/api/v1/auth/google/callback`

    *(Giải thích chi tiết:
    -   `http://127.0.0.1:8000`: Địa chỉ và cổng của server backend FastAPI.
    -   `/api/v1`: Prefix của `api_router` chính.
    -   `/auth/google/callback`: Đường dẫn của endpoint callback trong `app/api/v1/endpoints/social_auth.py`.)*

---

**Quan trọng:** Các giá trị trên chỉ dành cho môi trường phát triển cục bộ. Khi triển khai lên môi trường Production, bạn sẽ cần thay thế `http://localhost:5173` và `http://127.0.0.1:8000` bằng các domain và URL thật của ứng dụng frontend và backend của bạn.
