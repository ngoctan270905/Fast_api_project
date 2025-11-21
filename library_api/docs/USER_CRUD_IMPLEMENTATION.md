# Tổng kết chức năng CRUD cho User (Admin-Only)

Tài liệu này tóm tắt các bước đã thực hiện để xây dựng API quản lý người dùng (CRUD), với quyền truy cập được giới hạn chỉ cho những người dùng có vai trò là "admin".

## 1. Các file đã được tạo và chỉnh sửa

Để hoàn thiện chức năng này, các file sau đã được tạo mới hoặc cập nhật:

### `app/schemas/user.py` (Mới)

- **Mục đích:** Định nghĩa các schema (mô hình dữ liệu) Pydantic để xác thực và định dạng dữ liệu đầu vào và đầu ra cho API.
- **Các schema chính:**
    - `UserCreate`: Dùng khi admin tạo người dùng mới (yêu cầu `password`).
    - `UserUpdate`: Dùng khi cập nhật thông tin người dùng (tất cả các trường đều không bắt buộc).
    - `UserResponse`: Dùng để trả về thông tin người dùng trong API response (không chứa `hashed_password`).
    - `UserListResponse`: Dùng để trả về danh sách người dùng có phân trang.

### `app/services/user_service.py` (Mới)

- **Mục đích:** Chứa toàn bộ logic nghiệp vụ (business logic) để xử lý các hoạt động CRUD. Service này đóng vai trò trung gian giữa API endpoint và tầng repository.
- **Các phương thức chính:**
    - `get_all_users`: Lấy danh sách người dùng với phân trang.
    - `get_user_by_id`: Lấy một người dùng cụ thể.
    - `create_user`: Tạo người dùng mới, bao gồm cả việc kiểm tra username/email trùng lặp và hash mật khẩu.
    - `update_user`: Cập nhật thông tin người dùng.
    - `delete_user`: Xóa người dùng.

### `app/core/dependencies.py` (Cập nhật)

- **Mục đích:** Cung cấp các dependency injection cho FastAPI, đặc biệt là để xác thực quyền truy cập.
- **Thay đổi:**
    - Sử dụng dependency `get_current_admin_user` đã có sẵn. Dependency này gọi `get_current_user` để lấy thông tin người dùng từ JWT token, sau đó kiểm tra trường `role` của người dùng. Nếu `role` không phải là `"admin"`, nó sẽ trả về lỗi `403 Forbidden`.
    - Thêm `get_user_service` để inject `UserService` vào các endpoint.

### `app/api/v1/endpoints/users.py` (Mới)

- **Mục đích:** Định nghĩa các API endpoint cho chức năng CRUD của User.
- **Các endpoint:**
    - `GET /users/`: Lấy danh sách người dùng.
    - `POST /users/`: Tạo người dùng mới.
    - `GET /users/{user_id}`: Lấy thông tin một người dùng.
    - `PUT /users/{user_id}`: Cập nhật người dùng.
    - `DELETE /users/{user_id}`: Xóa người dùng.
- **Bảo mật:** Tất cả các endpoint trong file này đều được bảo vệ bởi `Depends(get_current_admin_user)`, đảm bảo chỉ admin mới có thể truy cập.

### `app/api/v1/router.py` (Cập nhật)

- **Mục đích:** Tích hợp các endpoint mới vào hệ thống API chính.
- **Thay đổi:** Thêm router từ `users.py` vào `api_router` với prefix là `/users` và tag là `Users (Admin)`.

### `scripts/seed_data.py` (Cập nhật)

- **Mục đích:** Tạo dữ liệu mẫu để kiểm thử.
- **Thay đổi:** Thêm logic để tạo sẵn hai người dùng khi chạy script:
    - **Admin:** `username: admin`, `password: admin123`, `role: "admin"`
    - **User:** `username: user`, `password: user123`, `role: "user"`

## 2. Hướng dẫn kiểm tra

1.  **Chạy Seed Script:** Mở terminal và chạy lệnh sau để tạo dữ liệu mẫu, bao gồm cả admin và user.
    ```bash
    python scripts/seed_data.py
    ```
2.  **Khởi động Server:** Chạy ứng dụng FastAPI của bạn.
    ```bash
    uvicorn app.main:app --reload
    ```
3.  **Lấy Token của Admin:**
    - Truy cập Swagger UI tại `http://127.0.0.1:8000/docs`.
    - Mở endpoint `POST /api/v1/auth/login`.
    - Nhấn "Try it out" và nhập `username` là `admin` và `password` là `admin123`.
    - Execute và sao chép `access_token` từ response.
4.  **Kiểm tra API User:**
    - Ở góc trên bên phải của Swagger UI, nhấn nút "Authorize".
    - Dán token vừa sao chép vào ô "Value" theo định dạng `Bearer <your_token>`.
    - Bây giờ bạn có thể truy cập và thử các endpoint trong mục `Users (Admin)`.
5.  **(Tùy chọn) Kiểm tra quyền truy cập của User thường:**
    - Lặp lại bước 3 để lấy token cho `username: user` và `password: user123`.
    - Dùng token này để "Authorize" và thử gọi một endpoint trong `Users (Admin)`. Bạn sẽ nhận được lỗi `403 Forbidden`.
