# Hướng Dẫn Nâng Cấp Hệ Thống Phân Quyền (RBAC) Lên Permission-Based

Đúng vậy, để chuyển sang một hệ thống phân quyền chi tiết hơn, bạn **cần tạo thêm các bảng trong cơ sở dữ liệu** để quản lý vai trò (Roles), quyền hạn (Permissions), và mối quan hệ giữa chúng.

Để kiểm thử (test) hệ thống mới, chúng ta sẽ tạo một kịch bản thực tế: **Tạo ra một vai trò mới là `content_manager`**. Người có vai trò này chỉ có quyền quản lý sách (tạo, sửa, xóa), nhưng **không** có quyền quản lý người dùng.

Dưới đây là các bước chi tiết để triển khai.

---

## Kế Hoạch Triển Khai

### Bước 1: Cập Nhật Cấu Trúc Cơ Sở Dữ Liệu

Chúng ta sẽ bỏ cột `role` ở bảng `users` và thay thế bằng một cấu trúc quan hệ linh hoạt hơn.

1.  **Tạo Model `Permission`:**
    -   Tạo file `app/models/permission.py`.
    -   Định nghĩa model `Permission` với các trường: `id`, `name` (ví dụ: `user:create`, `user:read`, `book:create`), và `description`.

2.  **Tạo Model `Role`:**
    -   Tạo file `app/models/role.py`.
    -   Định nghĩa model `Role` với các trường: `id`, `name` (`admin`, `user`, `content_manager`), và `description`.

3.  **Tạo Bảng Liên Kết:**
    -   **`user_roles`:** Bảng trung gian để liên kết `User` và `Role` (một người dùng có thể có nhiều vai trò).
    -   **`role_permissions`:** Bảng trung gian để liên kết `Role` và `Permission` (một vai trò có thể có nhiều quyền hạn).
    -   Bạn có thể định nghĩa các bảng này trong các file model tương ứng (`app/models/user.py` và `app/models/role.py`) sử dụng `Table` và `relationship` của SQLAlchemy.

4.  **Cập nhật Model `User`:**
    -   Xóa cột `role: str` hiện tại.
    -   Thêm mối quan hệ `roles = relationship("Role", secondary="user_roles", back_populates="users")`.

5.  **Tạo Alembic Migration:**
    -   Chạy lệnh `alembic revision --autogenerate -m "create_rbac_tables_and_update_user_model"` để tạo file migration mới.
    -   Kiểm tra kỹ file migration vừa tạo để đảm bảo nó xóa cột `role` và tạo ra các bảng `roles`, `permissions`, `user_roles`, `role_permissions` chính xác.
    -   Chạy `alembic upgrade head` để áp dụng thay đổi vào database.

### Bước 2: Seeding Dữ Liệu Ban Đầu

Cập nhật script `scripts/seed_data.py` để tạo các vai trò và quyền hạn mặc định.

1.  **Tạo Permissions:**
    -   Tạo các quyền hạn cơ bản: `user:create`, `user:read`, `user:update`, `user:delete`, `book:create`, `book:read`, `book:update`, `book:delete`.

2.  **Tạo Roles:**
    -   `admin`: Gán tất cả các quyền hạn.
    -   `user`: Chỉ gán các quyền cơ bản (ví dụ: `book:read`).
    -   `content_manager`: Gán các quyền `book:create`, `book:read`, `book:update`, `book:delete`.

3.  **Gán Role cho User:**
    -   Khi tạo user `admin_user`, gán cho anh ta vai trò `admin`.
    -   Khi tạo user `normal_user`, gán cho anh ta vai trò `user`.
    -   Tạo một user mới, `content_manager_user`, và gán vai trò `content_manager`.

### Bước 3: Cập Nhật Logic Phân Quyền

Đây là phần cốt lõi. Chúng ta sẽ tạo một dependency mới để kiểm tra `permission` thay vì kiểm tra `role`.

1.  **Tạo Dependency `require_permission`:**
    -   Trong file `app/core/dependencies.py`, tạo một *function factory* (một hàm trả về một hàm dependency khác).
    -   Hàm này sẽ có dạng `def require_permission(permission_name: str) -> Callable:`.
    -   Bên trong, nó sẽ định nghĩa và trả về một dependency, ví dụ `def _permission_checker(current_user: User = Depends(get_current_active_user)) -> User:`.
    -   Logic của `_permission_checker`:
        -   Lấy tất cả các `roles` của `current_user`.
        -   Từ các `roles` đó, lấy tất cả các `permissions` liên quan.
        -   Kiểm tra xem `permission_name` được yêu cầu có nằm trong danh sách quyền hạn của người dùng không.
        -   Nếu không, raise `HTTPException(status_code=403, detail="Forbidden: You don't have the required permission")`.
        -   Nếu có, trả về `current_user`.

2.  **Xóa Dependency Cũ:**
    -   Xóa hàm `get_current_admin_user` vì nó đã lỗi thời.

### Bước 4: Áp Dụng Dependency Mới vào Endpoints

Cập nhật các API endpoints để sử dụng hệ thống phân quyền mới.

1.  **Ví dụ với User Endpoint:**
    -   `DELETE /api/v1/users/{user_id}`:
        -   Thay `Depends(get_current_admin_user)` bằng `Depends(require_permission("user:delete"))`.

2.  **Ví dụ với Book Endpoint (cho vai trò `content_manager`):**
    -   `POST /api/v1/books/`:
        -   Sử dụng `Depends(require_permission("book:create"))`.
    -   `DELETE /api/v1/books/{book_id}`:
        -   Sử dụng `Depends(require_permission("book:delete"))`.

### Bước 5: Kiểm Thử

Sau khi hoàn thành các bước trên, hãy dùng một công cụ như Postman hoặc Swagger UI để kiểm thử:

1.  **Login với `admin_user`:** Thử gọi endpoint xóa user (`DELETE /users/{id}`). Yêu cầu phải thành công.
2.  **Login với `content_manager_user`:**
    -   Thử gọi endpoint xóa user (`DELETE /users/{id}`). Yêu cầu phải thất bại với lỗi `403 Forbidden`.
    -   Thử gọi endpoint tạo sách (`POST /books/`). Yêu cầu phải thành công.
3.  **Login với `normal_user`:** Thử gọi cả hai endpoint trên. Cả hai đều phải thất bại với lỗi `403 Forbidden`.

---

Bằng cách làm theo các bước này, bạn sẽ xây dựng được một hệ thống phân quyền linh hoạt, dễ dàng mở rộng và phù hợp với các tiêu chuẩn của một ứng dụng chuyên nghiệp.
