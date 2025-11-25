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

## 4. So sánh hiệu quả và tối ưu

Việc chuyển từ xác thực bằng dependency ở từng endpoint sang sử dụng một middleware tập trung mang lại nhiều lợi ích đáng kể về hiệu suất, bảo trì và sự gọn gàng của code.

### Trước khi có Middleware (Xác thực bằng `Depends`)

- **Lặp lại logic**: Mỗi endpoint được bảo vệ phải gọi `Depends(get_current_user)`. Bên trong dependency này, toàn bộ quy trình xác thực được thực thi lặp lại mỗi lần:
    1.  Đọc và phân tích `Authorization` header.
    2.  Xác thực chữ ký, thời gian hết hạn và scope của JWT.
    3.  Giải mã token để lấy `user_id`.
    4.  Thực hiện một truy vấn đến database (`SELECT * FROM users WHERE id = ...`) để lấy thông tin người dùng.
- **Tốn kém tài nguyên**: Mỗi request đến endpoint được bảo vệ đều tốn một lượt tính toán giải mã token và một lượt truy vấn database. Điều này tạo ra gánh nặng không cần thiết, đặc biệt khi hệ thống có nhiều endpoint được bảo vệ hoặc lưu lượng truy cập cao.
- **Khó bảo trì**: Nếu logic xác thực cần thay đổi (ví dụ: thêm một kiểu token mới, thay đổi cách kiểm tra), bạn phải sửa đổi logic ở dependency cốt lõi, có thể ảnh hưởng đến nhiều nơi.

### Sau khi có Middleware (Xác thực tập trung)

- **Logic tập trung (DRY - Don't Repeat Yourself)**: Toàn bộ logic xác thực (đọc header, giải mã token, truy vấn DB) chỉ nằm ở một nơi duy nhất: `AuthMiddleware`.
- **Thực thi một lần**: Middleware chỉ chạy một lần cho mỗi request. Nó xác thực người dùng và **gắn kết quả (đối tượng `User`) vào `request.state`**.
- **Dependency gọn nhẹ**: Các endpoint giờ đây sử dụng một dependency mới, `Depends(get_current_active_user)`, được định nghĩa trong `app/api/deps.py`. Dependency này cực kỳ nhanh và hiệu quả vì nó chỉ làm một việc:
    - **Đọc đối tượng `User` trực tiếp từ `request.state.user`**.
    - Nó không cần giải mã token, không cần truy vấn lại database.
- **Tối ưu hiệu suất**: Bằng cách loại bỏ việc giải mã token và truy vấn database lặp đi lặp lại ở mỗi endpoint, chúng ta đã giảm đáng kể độ trễ của request và tải cho database. Hiệu suất hệ thống được cải thiện rõ rệt.
- **Dễ bảo trì và mở rộng**: Khi cần thay đổi logic xác thực, bạn chỉ cần chỉnh sửa file `auth_middleware.py`. Các endpoint và dependency `get_current_active_user` không cần thay đổi.

Tóm lại, việc sử dụng middleware đã giúp **tách biệt luồng xác thực khỏi luồng xử lý business**, làm cho code sạch hơn, hiệu quả hơn và dễ quản lý hơn rất nhiều.

## 5. Luồng Request Chi Tiết (Sau khi có Middleware)

Để hiểu rõ hơn về cách hệ thống hoạt động, dưới đây là luồng xử lý từng bước của một request đến một endpoint được bảo vệ, ví dụ `POST /api/v1/users/me/change-password`.

1.  **Client gửi Request**: Người dùng gửi một request từ trình duyệt hoặc client, kèm theo token trong header:
    ```
    POST /api/v1/users/me/change-password HTTP/1.1
    Host: localhost:8000
    Authorization: Bearer <your_jwt_token>
    Content-Type: application/json

    {
      "old_password": "...",
      "new_password": "..."
    }
    ```

2.  **Middleware chặn Request**: `AuthMiddleware` được đăng ký với app FastAPI sẽ là "người gác cổng". Nó nhận request này đầu tiên.

3.  **Kiểm tra Route công khai**: Middleware kiểm tra xem đường dẫn `/api/v1/users/me/change-password` có trong danh sách các route được bỏ qua (public routes) hay không. Vì đây là endpoint cần bảo vệ, nó không có trong danh sách.

4.  **Trích xuất và xác thực Token**:
    *   Middleware đọc header `Authorization`.
    *   Nó trích xuất token và dùng hàm `verify_scoped_token` để kiểm tra chữ ký, thời gian hết hạn, và "scope" của token.
    *   Nếu token không hợp lệ, middleware sẽ trả về lỗi `401 Unauthorized` ngay lập tức và luồng xử lý dừng lại.

5.  **Truy vấn Database**:
    *   Nếu token hợp lệ, middleware lấy `user_id` từ payload của token.
    *   Nó thực hiện **một truy vấn duy nhất** đến database để lấy thông tin chi tiết của người dùng: `SELECT * FROM users WHERE id = <user_id>`.
    *   Nếu không tìm thấy người dùng, nó cũng trả về lỗi `401 Unauthorized`.

6.  **Gắn User vào `request.state`**:
    *   Sau khi lấy được đối tượng `User` từ database, middleware sẽ gắn đối tượng này vào `request.state`:
    ```python
    # Bên trong middleware
    request.state.user = db_user 
    ```

7.  **Chuyển tiếp Request**: Middleware gọi `await call_next(request)`. Request object lúc này đã chứa thông tin người dùng và được chuyển đến tầng tiếp theo là bộ định tuyến (router) của FastAPI.

8.  **FastAPI Routing**: FastAPI xác định rằng request này khớp với endpoint `change_current_user_password`.

9.  **Thực thi Dependency gọn nhẹ**:
    *   Endpoint này có một dependency: `current_user: Annotated[User, Depends(get_current_active_user)]`.
    *   FastAPI thực thi hàm `get_current_active_user` từ `app/api/deps.py`.
    *   Hàm này **không làm gì phức tạp**. Nó chỉ đơn giản là đọc thông tin user đã được middleware chuẩn bị sẵn:
        ```python
        # Bên trong get_current_active_user
        user = getattr(request.state, "user", None)
        # (và kiểm tra user is_active)
        return user
        ```
    *   Không có việc giải mã token hay truy vấn database lần thứ hai ở đây.

10. **Thực thi Logic của Endpoint**:
    *   Hàm `change_current_user_password` nhận được đối tượng `current_user` từ dependency.
    *   Nó tiếp tục thực hiện logic business của mình là thay đổi mật khẩu.

11. **Trả về Response**: Endpoint hoàn thành và trả về response cho client.

Luồng xử lý này đảm bảo rằng logic xác thực nặng nề chỉ được thực hiện một lần duy nhất ở "cổng vào", giúp các endpoint bên trong hoạt động nhanh chóng và chỉ tập trung vào nhiệm vụ của chúng.
