# Ghi chú chi tiết: Luồng hoạt động Backend cho chức năng "Quên Mật khẩu"

Tài liệu này giải thích chi tiết luồng hoạt động và vai trò của từng file trong backend khi triển khai chức năng "Quên Mật khẩu".

## Mục tiêu

Xây dựng một quy trình an toàn cho phép người dùng đặt lại mật khẩu của họ khi họ không thể đăng nhập. Luồng này bao gồm hai giai đoạn chính:
1.  **Yêu cầu Reset**: Người dùng cung cấp email để nhận link reset.
2.  **Thực hiện Reset**: Người dùng sử dụng link để đặt mật khẩu mới.

---

## Giai đoạn 1: Yêu cầu Reset Mật khẩu

Đây là luồng hoạt động khi người dùng nhấn vào nút "Quên mật khẩu" và gửi email của họ.

**Endpoint**: `POST /api/v1/auth/forgot-password`

### 1. `app/schemas/auth.py`

- **Cái gì?**: Schema `ForgotPasswordRequest` được sử dụng.
    ```python
    class ForgotPasswordRequest(BaseModel):
        email: EmailStr
    ```
- **Để làm gì?**: Để xác thực (validate) dữ liệu đầu vào từ client. Nó đảm bảo rằng client phải gửi lên một trường `email` và giá trị đó phải có định dạng của một email hợp lệ.

### 2. `app/api/v1/endpoints/auth.py`

- **Cái gì?**: Endpoint `POST /forgot-password` được định nghĩa ở đây.
- **Để làm gì?**: Đây là "cổng vào" của API. Nó tiếp nhận request từ client, sử dụng `ForgotPasswordRequest` để validate body của request, và sau đó chuyển giao nhiệm vụ xử lý logic cho tầng Service.
- **Chi tiết**:
    ```python
    @router.post("/forgot-password", ...)
    async def forgot_password(
        request: ForgotPasswordRequest,
        auth_service: ...
    ):
        return await auth_service.forgot_password(request.email)
    ```

### 3. `app/services/auth_service.py`

- **Cái gì?**: Phương thức `forgot_password(self, email: str)` chứa logic nghiệp vụ cốt lõi.
- **Để làm gì?**: Để xử lý yêu cầu một cách an toàn và bắt đầu quá trình gửi email.
- **Chi tiết luồng hoạt động**:
    1.  Nhận `email` từ endpoint.
    2.  Sử dụng `user_repo.get_by_email(email)` để tìm kiếm xem có người dùng nào khớp với email này trong database không.
    3.  **Điểm bảo mật quan trọng**: Nếu **không tìm thấy** người dùng, phương thức sẽ **không báo lỗi**. Nó sẽ âm thầm kết thúc và vẫn trả về thông báo thành công chung chung. Điều này nhằm ngăn chặn kỹ thuật tấn công "Email Enumeration" (kẻ xấu có thể dò xem email nào đã tồn tại trong hệ thống của bạn).
    4.  Nếu **tìm thấy** người dùng, nó sẽ:
        a. Gọi hàm `create_scoped_token` (từ `security.py`) để tạo một JWT đặc biệt với `scope="password_reset"` và thời gian hết hạn rất ngắn (15 phút) để tăng tính bảo mật.
        b. Gọi hàm `send_password_reset_email` (từ `email.py`), truyền vào email của người dùng và token vừa tạo.
    5.  Cuối cùng, trả về một thông báo thành công chung cho client.

### 4. `app/core/security.py` & `app/core/email.py`

- **Cái gì?**: Các hàm hỗ trợ `create_scoped_token` và `send_password_reset_email` được gọi.
- **Để làm gì?**:
    - `create_scoped_token`: Tạo ra một token an toàn, chỉ dùng một lần, và có thời gian sống ngắn.
    - `send_password_reset_email`: Sử dụng template `password_reset.html` và thư viện `fastapi-mail` để tạo và gửi email chứa đường link reset (ví dụ: `http://localhost:5173/reset-password?token=...`).

---

## Giai đoạn 2: Thực hiện Reset Mật khẩu

Đây là luồng hoạt động khi người dùng nhấp vào link trong email và gửi mật khẩu mới.

**Endpoint**: `POST /api/v1/auth/reset-password`

### 1. `app/schemas/auth.py`

- **Cái gì?**: Schema `ResetPasswordRequest` được sử dụng.
    ```python
    class ResetPasswordRequest(BaseModel):
        token: str
        new_password: str = Field(..., min_length=6, ...)
    ```
- **Để làm gì?**: Để validate request từ client, đảm bảo nó phải chứa `token` (lấy từ URL) và `new_password` (phải đủ dài theo yêu cầu).

### 2. `app/api/v1/endpoints/auth.py`

- **Cái gì?**: Endpoint `POST /reset-password` được định nghĩa.
- **Để làm gì?**: Tiếp nhận `token` và `new_password`, sau đó chuyển cho `AuthService` để xử lý.
- **Chi tiết**:
    ```python
    @router.post("/reset-password", ...)
    async def reset_password(
        request: ResetPasswordRequest,
        auth_service: ...
    ):
        return await auth_service.reset_password(request.token, request.new_password)
    ```

### 3. `app/services/auth_service.py`

- **Cái gì?**: Phương thức `reset_password(self, token: str, new_password: str)` chứa logic nghiệp vụ chính.
- **Để làm gì?**: Để hoàn tất quá trình một cách an toàn: xác thực token và cập nhật mật khẩu mới.
- **Chi tiết luồng hoạt động**:
    1.  Nhận `token` và `new_password` từ endpoint.
    2.  Gọi hàm `verify_scoped_token(token, required_scope="password_reset")` (từ `security.py`).
        - Hàm này sẽ giải mã token, kiểm tra chữ ký, kiểm tra xem token đã hết hạn chưa, và quan trọng nhất là **kiểm tra xem `scope` có phải là `"password_reset"` hay không**.
        - Nếu có bất kỳ vấn đề gì, hàm này sẽ tự động trả về một lỗi `HTTPException` (401 Unauthorized) và luồng sẽ dừng lại.
        - Nếu token hợp lệ, hàm sẽ trả về `subject` của token (chính là `email` của người dùng).
    3.  Sử dụng `email` vừa lấy được để tìm người dùng trong database.
    4.  Nếu tìm thấy người dùng, gọi hàm `hash_password` (từ `security.py`) để băm `new_password`.
    5.  Cập nhật trường `hashed_password` của người dùng bằng mật khẩu đã băm.
    6.  Lưu thay đổi vào database.
    7.  Trả về thông tin người dùng đã được cập nhật (dưới dạng `UserResponse`) để xác nhận thành công.