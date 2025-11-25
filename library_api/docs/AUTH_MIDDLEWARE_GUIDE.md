# Hướng dẫn Xây dựng Middleware Xác thực Tùy chỉnh (Custom Authentication Middleware)

Tài liệu này phác thảo kế hoạch và luồng hoạt động để xây dựng một middleware xác thực tùy chỉnh cho ứng dụng FastAPI.

## 1. Mục tiêu

Mục tiêu của middleware này là tự động kiểm tra và xác thực token JWT cho mọi request gửi đến các endpoint được bảo vệ. Nếu token hợp lệ, thông tin người dùng sẽ được lấy và "gắn" vào context của request, giúp các endpoint có thể truy cập dễ dàng mà không cần lặp lại logic xác thực ở mỗi nơi.

Điều này giúp thay thế việc phải thêm `Depends(get_current_user)` vào từng endpoint cần bảo vệ, làm cho code gọn gàng và tập trung hơn.

## 2. Luồng hoạt động của Middleware

Middleware sẽ hoạt động như một "người gác cổng" cho mỗi request. Luồng xử lý chuẩn sẽ như sau:

1.  **Chặn mọi Request**: Middleware sẽ được kích hoạt cho mọi request đi vào ứng dụng.

2.  **Phân loại Route**:
    *   Middleware sẽ kiểm tra xem request có đang nhắm đến các route công khai (public) hay không. Các route này cần được định nghĩa trước (ví dụ: `/api/v1/auth/login`, `/api/v1/auth/register`, `/docs`, `/openapi.json`).
    *   Nếu là route công khai, middleware sẽ bỏ qua việc xác thực và chuyển request đi tiếp.

3.  **Kiểm tra `Authorization` Header**:
    *   Nếu route không phải là công khai (tức là cần được bảo vệ), middleware sẽ tìm header `Authorization` trong request.
    *   Nó sẽ kiểm tra xem header có tuân thủ định dạng `Bearer <token>` hay không.

4.  **Xử lý Token**:
    *   **Thiếu Token**: Nếu không có header `Authorization` hoặc định dạng sai, middleware sẽ ngay lập tức trả về lỗi `401 Unauthorized`.
    *   **Có Token**: Nếu có token, middleware sẽ sử dụng logic đã có trong `app/core/security.py` (hàm `verify_scoped_token` hoặc một phiên bản tương tự) để:
        *   Kiểm tra chữ ký của token.
        *   Kiểm tra xem token đã hết hạn chưa.
        *   Kiểm tra "scope" của token để chắc chắn đó là `access_token`.

5.  **Lấy thông tin User**:
    *   Nếu token hợp lệ, middleware sẽ giải mã payload để lấy ra `sub` (chính là `user.id`).
    *   Sử dụng `UserRepository`, middleware sẽ truy vấn database để lấy đối tượng `User` tương ứng.
    *   Nếu không tìm thấy user (ví dụ: user đã bị xóa sau khi token được cấp), middleware sẽ trả về lỗi `401 Unauthorized`.

6.  **Gắn User vào Context của Request**:
    *   Nếu tìm thấy user, đối tượng `User` sẽ được gắn vào `request.state`. Đây là cách chuẩn của FastAPI để truyền dữ liệu từ middleware đến các route handler. Ví dụ: `request.state.user = db_user`.

7.  **Chuyển tiếp Request**: Middleware gọi hàm `call_next(request)` để chuyển request đã được "bổ sung" thông tin user đến các xử lý tiếp theo (middleware khác hoặc route handler).

## 3. Các bước triển khai (Kế hoạch hành động)

Đây là các file cần được tạo mới hoặc chỉnh sửa để triển khai chức năng này.

### Bước 1: Tạo file Middleware
*   **Tạo file mới**: `library_api/app/middleware/auth_middleware.py`.
*   **Nội dung**:
    *   Định nghĩa một class `AuthMiddleware` kế thừa từ `BaseHTTPMiddleware` của Starlette.
    *   Triển khai logic của "Luồng hoạt động" (đã mô tả ở trên) bên trong phương thức `async def dispatch(self, request: Request, call_next)`.
    *   Trong `dispatch`, cần khởi tạo một `UserRepository` để có thể truy vấn database.

### Bước 2: Đăng ký Middleware
*   **Chỉnh sửa file**: `library_api/app/main.py`.
*   **Hành động**:
    *   Import `AuthMiddleware` vừa tạo.
    *   Đăng ký middleware với ứng dụng FastAPI bằng `app.add_middleware(AuthMiddleware)`.
    *   **Lưu ý**: Thứ tự của middleware rất quan trọng. Middleware này nên được đặt sau `CORSMiddleware` và `SessionMiddleware`.

### Bước 3: (Khuyến khích) Tạo Dependency `get_current_user` đơn giản
*   **Chỉnh sửa file**: `library_api/app/api/deps.py`.
*   **Hành động**:
    *   Tạo một dependency mới, ví dụ `get_current_active_user`, để lấy thông tin user từ `request.state`.
    *   Hàm này sẽ rất đơn giản, chỉ cần truy cập `request.state.user`. Nó cũng có thể kiểm tra xem user có `is_active` không.

    ```python
    # Ví dụ về dependency mới trong deps.py
    from fastapi import Request, Depends, HTTPException, status
    from app.models.users import User

    async def get_current_active_user(request: Request) -> User:
        user = getattr(request.state, "user", None)
        if not user:
            # Middleware nên xử lý việc này, nhưng đây là một lớp bảo vệ an toàn
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return user
    ```

### Bước 4: Cập nhật các Endpoint được bảo vệ
*   **Chỉnh sửa các file**: Các file trong `library_api/app/api/v1/endpoints/`.
*   **Hành động**:
    *   Thay thế các dependency xác thực phức tạp hiện có (nếu có) bằng `Depends(get_current_active_user)` đã tạo ở Bước 3.
    *   Bây giờ, các hàm xử lý endpoint có thể nhận đối tượng `User` đã được xác thực một cách gọn gàng.
