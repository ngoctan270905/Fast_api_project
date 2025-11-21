# Ghi chú chi tiết: Luồng hoạt động Backend cho chức năng "Đổi Mật khẩu"

Tài liệu này giải thích chi tiết luồng hoạt động và vai trò của từng file trong backend khi triển khai chức năng "Đổi Mật khẩu" cho một người dùng đã đăng nhập.

## Mục tiêu

Xây dựng một quy trình an toàn cho phép người dùng đã được xác thực (đang đăng nhập) có thể tự thay đổi mật khẩu của chính họ.

---

## Chi tiết Luồng hoạt động (Backend)

Luồng này bắt đầu khi một người dùng đã đăng nhập gửi yêu cầu thay đổi mật khẩu của họ.

**Endpoint**: `POST /api/v1/users/me/change-password`

### 1. Schema (`app/schemas/user.py`)

- **Cái gì?**: Schema `UserChangePasswordRequest` được sử dụng.
    ```python
    class UserChangePasswordRequest(BaseModel):
        old_password: str
        new_password: str = Field(..., min_length=6, max_length=100)
    ```
- **Để làm gì?**: Để xác thực (validate) body của request gửi từ client. Nó đảm bảo rằng request phải chứa hai trường là `old_password` và `new_password`, đồng thời `new_password` phải có độ dài tối thiểu là 6 ký tự.

### 2. Endpoint & Dependency (`app/api/v1/endpoints/users.py`)

- **Cái gì?**: Endpoint `POST /me/change-password` được định nghĩa và được bảo vệ bởi dependency `Depends(get_current_active_user)`.
    ```python
    @router.post("/me/change-password", response_model=UserResponse)
    async def change_current_user_password(
        password_data: UserChangePasswordRequest,
        user_service: ...,
        current_user: Annotated[User, Depends(get_current_active_user)]
    ):
        # ... call service ...
    ```
- **Để làm gì?**:
    - **`Depends(get_current_active_user)`**: Đây là lớp bảo vệ đầu tiên và quan trọng nhất. Dependency này sẽ tự động thực hiện các việc sau:
        1.  Yêu cầu client phải gửi `access_token` hợp lệ trong `Authorization` header.
        2.  Sử dụng `verify_scoped_token` (trong `security.py`) để giải mã và xác thực token, đảm bảo token hợp lệ, chưa hết hạn và có `scope="access_token"`.
        3.  Lấy `user_id` từ token và truy vấn người dùng tương ứng từ database.
        4.  Kiểm tra xem người dùng đó có `is_active` hay không.
        5.  Nếu tất cả các bước trên thành công, nó sẽ "inject" (tiêm) toàn bộ object `User` đã được xác thực vào biến `current_user` của hàm endpoint. Nếu thất bại ở bất kỳ bước nào, nó sẽ tự động trả về lỗi `401 Unauthorized` hoặc `400 Bad Request`.
    - **Endpoint**: Sau khi có được `current_user`, endpoint sẽ nhận `password_data` từ body của request và gọi phương thức `user_service.change_user_password` để xử lý logic chính.

### 3. Service (`app/services/user_service.py`)

- **Cái gì?**: Phương thức `change_user_password(self, current_user: User, old_password: str, new_password: str)` chứa logic nghiệp vụ cốt lõi.
- **Để làm gì?**: Để thực hiện việc thay đổi mật khẩu một cách an toàn sau khi đã xác thực người dùng.
- **Chi tiết luồng hoạt động**:
    1.  Nhận object `current_user` (đã được xác thực đầy đủ) từ endpoint.
    2.  Gọi hàm `verify_password(old_password, current_user.hashed_password)` (từ `security.py`).
        - **Mục đích**: So sánh `old_password` mà người dùng nhập với `hashed_password` đang được lưu trong database của chính người dùng đó.
    3.  Nếu `verify_password` trả về `False` (mật khẩu cũ không khớp), service sẽ trả về một lỗi `HTTPException 400 Bad Request` với thông báo "Incorrect old password".
    4.  Nếu mật khẩu cũ khớp, service sẽ gọi hàm `hash_password(new_password)` (từ `security.py`) để băm mật khẩu mới.
    5.  Cập nhật trường `current_user.hashed_password` bằng giá trị mật khẩu mới đã được băm.
    6.  Gọi phương thức `user_repo.update(current_user)` để lưu thông tin người dùng đã được cập nhật vào database.
    7.  Trả về object người dùng đã được cập nhật.

### 4. Response

- **Cái gì?**: API trả về một JSON chứa thông tin người dùng đã được cập nhật (theo schema `UserResponse`, không bao gồm mật khẩu) và status code `200 OK`.
- **Để làm gì?**: Để xác nhận với client rằng việc thay đổi mật khẩu đã thành công.