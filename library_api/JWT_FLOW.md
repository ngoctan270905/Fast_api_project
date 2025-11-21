# Luồng xử lý JWT trong dự án

Tài liệu này mô tả chi tiết luồng xử lý JSON Web Token (JWT) để xác thực và ủy quyền người dùng trong dự án.

## 1. Đăng nhập (Login)

Luồng xử lý bắt đầu khi người dùng gửi yêu cầu đăng nhập với `username` và `password`.

1.  **Endpoint:** Người dùng gửi một yêu cầu `POST` đến endpoint `/api/v1/auth/login`. Dữ liệu được gửi dưới dạng `OAuth2PasswordRequestForm`.
2.  **Service Layer:** `AuthService` (`app/services/auth_service.py`) nhận yêu cầu.
3.  **Xác thực người dùng:**
    *   Dịch vụ sử dụng `UserRepository` để tìm người dùng trong cơ sở dữ liệu dựa trên `username`.
    *   Nếu người dùng tồn tại, `AuthService` sử dụng hàm `verify_password` từ `app/core/security.py` để so sánh mật khẩu người dùng cung cấp với mật khẩu đã được hash trong CSDL.
4.  **Tạo Token:** Nếu xác thực thành công, `AuthService` sẽ gọi hàm `create_access_token` để tạo một JWT mới.

## 2. Tạo Token (Token Creation)

Hàm `create_access_token` trong `app/core/security.py` chịu trách nhiệm tạo JWT.

1.  **Payload:** Một "payload" (dữ liệu) được tạo cho token, chứa các thông tin (claims) quan trọng:
    *   `sub` (Subject): ID của người dùng.
    *   `exp` (Expiration Time): Thời gian hết hạn của token, được tính toán dựa trên cấu hình `ACCESS_TOKEN_EXPIRE_MINUTES` trong `app/core/config.py`.
2.  **Ký Token:** Payload được mã hóa và ký bằng cách sử dụng:
    *   `SECRET_KEY`: Một chuỗi bí mật.
    *   `ALGORITHM`: Thuật toán ký (ví dụ: HS256).
    Cả hai giá trị này đều được định nghĩa trong file cấu hình.
3.  **Trả về Token:** Token đã được ký (một chuỗi dài) được trả về cho client trong phản hồi của yêu cầu đăng nhập.

## 3. Bảo vệ Endpoint (Endpoint Protection)

Các endpoint yêu cầu xác thực sẽ được "bảo vệ" bằng cách sử dụng hệ thống Dependency Injection của FastAPI.

1.  **Dependency:** Endpoint được khai báo với một dependency, phổ biến nhất là `Depends(get_current_active_user)`.
2.  **File chứa Dependency:** Các dependency này được định nghĩa trong `app/core/dependencies.py`.

## 4. Xác thực Token (Token Validation)

Khi client gửi yêu cầu đến một endpoint được bảo vệ, họ phải đính kèm JWT vào header `Authorization` theo dạng `Bearer <token>`.

1.  **Trích xuất Token:** Dependency `oauth2_scheme` (một instance của `OAuth2PasswordBearer`) tự động trích xuất token từ header.
2.  **Giải mã và Xác thực:**
    *   Hàm `get_current_user` trong `app/core/dependencies.py` nhận token này.
    *   Nó gọi hàm `decode_access_token` từ `app/core/security.py` để xác thực chữ ký và kiểm tra xem token đã hết hạn hay chưa.
    *   Nếu token không hợp lệ (sai chữ ký, hết hạn), một `HTTPException` (thường là lỗi 401 Unauthorized) sẽ được ném ra.
3.  **Lấy thông tin người dùng:**
    *   Nếu token hợp lệ, ID người dùng được trích xuất từ claim `sub` trong payload.
    *   `UserRepository` được sử dụng để truy vấn người dùng từ CSDL bằng ID này.
    *   Nếu không tìm thấy người dùng, một lỗi 401 sẽ được ném ra.
4.  **Gắn vào Request:** Cuối cùng, đối tượng người dùng đã được xác thực sẽ được trả về bởi dependency và có thể được sử dụng bên trong logic của endpoint.

## Các thành phần chính (Key Components)

-   `app/api/v1/endpoints/auth.py`: Định nghĩa các API endpoint cho việc đăng nhập (`/login`) và lấy thông tin người dùng (`/me`).
-   `app/services/auth_service.py`: Chứa logic nghiệp vụ cốt lõi cho việc xác thực người dùng và gọi tạo token.
-   `app/core/security.py`: Trung tâm của việc xử lý JWT. Chứa các hàm để tạo, giải mã, và xác thực token, cũng như xử lý mật khẩu.
-   `app/core/dependencies.py`: Cung cấp các dependency cho FastAPI để bảo vệ endpoint và lấy thông tin người dùng hiện tại từ token.
-   `app/core/config.py`: Chứa các cấu hình quan trọng như `SECRET_KEY`, `ALGORITHM`, và thời gian hết hạn của token.
