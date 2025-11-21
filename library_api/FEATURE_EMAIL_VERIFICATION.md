# Ghi chú chi tiết: Triển khai luồng xác minh Email cho Backend

Tài liệu này giải thích chi tiết các thay đổi đã được thực hiện ở backend để xây dựng chức năng "Xác minh Email sau khi đăng ký".

## Mục tiêu

- Khi người dùng mới đăng ký, tài khoản của họ sẽ ở trạng thái không hoạt động (`is_active=False`).
- Hệ thống sẽ tự động gửi một email chứa đường link xác minh duy nhất.
- Người dùng phải nhấp vào link đó để kích hoạt tài khoản (`is_active=True`).
- Điều này đảm bảo rằng địa chỉ email người dùng cung cấp là có thật và họ sở hữu nó.

---

## Chi tiết các thay đổi và mục đích

### 1. Cấu hình & Dịch vụ Email

- **File thay đổi**: `app/core/config.py`, `.env.example`, và file mới `app/core/email.py`.
- **Cái này để làm gì?**:
    - **Mục đích**: Để cung cấp cho ứng dụng khả năng gửi email thật thông qua một nhà cung cấp SMTP (như Gmail). Đây là thành phần cốt lõi của chức năng.
    - **Đã làm gì?**:
        1.  **Cài đặt thư viện**: Cài đặt `fastapi-mail` để xử lý việc gửi email một cách chuyên nghiệp.
        2.  **Thêm cấu hình**: Các biến như `MAIL_USERNAME`, `MAIL_PASSWORD`... đã được thêm vào file `config.py` và `env.example`. Điều này giúp giữ an toàn cho thông tin đăng nhập và dễ dàng thay đổi cấu hình mà không cần sửa code.
        3.  **Tạo Email Service**: File `email.py` được tạo ra để thiết lập kết nối đến máy chủ email và đóng gói logic gửi mail. Nó sử dụng các template HTML (trong `app/templates/email/`) để nội dung email trông chuyên nghiệp và dễ quản lý hơn.

### 2. Tái cấu trúc Bảo mật Token

- **File thay đổi**: `app/core/security.py`.
- **Cái này để làm gì?**:
    - **Mục đích**: Để tạo ra một hệ thống token mạnh mẽ, linh hoạt và an toàn hơn, có khả năng phân biệt nhiều loại token khác nhau (token đăng nhập, token xác minh email, token reset mật khẩu...).
    - **Đã làm gì?**:
        1.  **Thêm "Scope" (Phạm vi)**: Khái niệm `scope` được thêm vào trong payload của JWT. Nó giống như một "nhãn" để ghi rõ mục đích của token. Ví dụ, token đăng nhập có `scope: "access_token"`, token xác minh email có `scope: "email_verification"`.
        2.  **Hàm `create_scoped_token`**: Một hàm mới được tạo ra để dễ dàng tạo các token có mục đích cụ thể với thời gian hết hạn tùy chỉnh.
        3.  **Hàm `verify_scoped_token`**: Hàm này thay thế các hàm cũ, chịu trách nhiệm giải mã token, kiểm tra chữ ký, kiểm tra hết hạn, và **quan trọng nhất là kiểm tra xem token có được dùng đúng mục đích (`scope`) hay không**. Nó sẽ báo lỗi nếu bạn cố dùng token xác minh email để đăng nhập và ngược lại.

### 3. Tái cấu trúc Dependencies

- **File thay đổi**: `app/core/dependencies.py`.
- **Cái này để làm gì?**:
    - **Mục đích**: Để áp dụng cơ chế xác thực token mới, đồng thời làm cho code sạch hơn, dễ hiểu hơn và sửa lỗi đã gây ra trước đó.
    - **Đã làm gì?**:
        1.  **Sử dụng `verify_scoped_token`**: Hàm `get_current_user` (dùng để lấy thông tin người dùng từ token đăng nhập) đã được cập nhật để sử dụng `verify_scoped_token`, đảm bảo chỉ token có `scope: "access_token"` mới hợp lệ.
        2.  **Tách biệt trách nhiệm**: Logic kiểm tra `is_active` đã được chuyển vào đúng hàm của nó là `get_current_active_user`. Điều này giúp `get_current_user` chỉ tập trung vào một việc duy nhất là xác thực token, còn `get_current_active_user` lo việc kiểm tra quyền (user có active không).
        3.  **Sửa lỗi**: Thêm lại dòng `DbSession = Annotated[...]` đã vô tình bị xóa, khắc phục lỗi `ImportError` khiến ứng dụng không thể khởi động.

### 4. Cập nhật Schemas

- **File thay đổi**: `app/schemas/auth.py`.
- **Cái này để làm gì?**:
    - **Mục đích**: Để định nghĩa cấu trúc dữ liệu cho các request và response mới của API, phù hợp với luồng xác minh email.
    - **Đã làm gì?**:
        1.  **Thêm `EmailVerificationRequest`**: Một schema mới để định nghĩa cấu trúc của request body cho endpoint xác minh email (chỉ chứa một trường `token`).
        2.  **Cập nhật `UserResponse`**: Thêm các trường `email_verified` và `updated_at` để API có thể trả về thông tin đầy đủ của người dùng.
        3.  **Xóa `UserWithToken`**: Xóa schema này vì luồng đăng ký mới không còn trả về token đăng nhập ngay lập tức.

### 5. Cập nhật Logic Đăng ký & Thêm Endpoint Xác minh

- **File thay đổi**: `app/services/auth_service.py` và `app/api/v1/endpoints/auth.py`.
- **Cái này để làm gì?**:
    - **Mục đích**: Đây là trung tâm của sự thay đổi, áp dụng tất cả các thành phần trên vào luồng đăng ký thực tế.
    - **Đã làm gì?**:
        1.  **Sửa `AuthService.register`**:
            - Khi tạo user mới, trường `is_active` được set là `False`.
            - Gọi `create_scoped_token` để tạo token xác minh.
            - Gọi `send_verification_email` để "gửi" email đi.
            - Thay đổi kiểu dữ liệu trả về, không còn trả về access token.
        2.  **Thêm `AuthService.verify_email`**: Thêm một phương thức mới để xử lý logic khi người dùng gửi token lên: tìm người dùng, kiểm tra token, và cập nhật `is_active=True`, `email_verified=True`.
        3.  **Cập nhật `endpoints/auth.py`**:
            - Sửa `response_model` của endpoint `/register` để phù hợp với dữ liệu trả về mới.
            - Thêm một endpoint hoàn toàn mới là `POST /verify-email` để tiếp nhận yêu cầu xác minh từ phía client.