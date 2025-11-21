# Luồng Hoạt động Chuẩn cho Quản lý Mật khẩu và Xác minh Email

Tài liệu này mô tả chi tiết các luồng hoạt động tiêu chuẩn để triển khai các tính năng "Quên mật khẩu", "Đổi mật khẩu", và "Xác minh Email" trong một ứng dụng hiện đại, sử dụng JSON Web Tokens (JWT) để tạo các đường link an toàn.

## 1. Tổng quan

Các tính năng này rất quan trọng đối với trải nghiệm người dùng và bảo mật. Chúng đều dựa trên một nguyên tắc chung: tạo ra một **token tạm thời, an toàn, có mục đích sử dụng duy nhất** và gửi nó cho người dùng qua email. JWT là một lựa chọn tuyệt vời cho việc này.

**Thành phần cốt lõi:**
- **Tạo Token an toàn**: Sử dụng JWT để mã hóa thông tin định danh người dùng và mục đích của token.
- **Dịch vụ gửi Email**: Cần một dịch vụ để gửi email chứa link có gắn token cho người dùng.
- **Các Endpoint được bảo vệ**: Các API endpoint để xử lý token và thực hiện các hành động tương ứng.

---

## 2. Luồng 1: Xác minh Email (Sau khi đăng ký)

**Mục đích**: Đảm bảo email người dùng cung cấp khi đăng ký là có thật và họ sở hữu nó.

**Các bước thực hiện**:

1.  **Đăng ký (Sign-up)**:
    - Người dùng đăng ký tài khoản với `username`, `email`, `password`.
    - Backend tạo một record `User` mới trong database với `email_verified = False`. Bạn cũng có thể set `is_active = False` để ngăn người dùng đăng nhập cho đến khi họ xác minh email.

2.  **Tạo Token Xác minh (Verification Token)**:
    - Ngay sau khi tạo tài khoản, backend tạo một JWT đặc biệt (gọi là `verification_token`).
    - **Payload của JWT**:
        - `sub`: ID hoặc email của người dùng (ví dụ: `user.id`).
        - `scope`: Một trường để chỉ rõ mục đích của token, ví dụ: `{"scope": "email_verification"}`.
        - `exp`: Thời gian hết hạn của token. Nên đặt thời gian hợp lý (ví dụ: 1 đến 24 giờ).

3.  **Gửi Email Xác minh**:
    - Backend gọi một dịch vụ email để gửi thư đến địa chỉ email người dùng đã đăng ký.
    - Nội dung email chứa một đường link duy nhất, ví dụ: `https://your-frontend-app.com/verify-email?token=<verification_token>`.

4.  **Người dùng Xác minh**:
    - Người dùng mở email và nhấp vào đường link.
    - Frontend nhận được `token` từ URL và gửi nó đến một endpoint của backend, ví dụ: `POST /api/v1/auth/verify-email` với token trong body.

5.  **Backend Xử lý**:
    - Endpoint backend nhận token.
    - Nó giải mã và xác thực JWT: kiểm tra chữ ký, thời gian hết hạn (`exp`), và quan trọng nhất là `scope` phải là `"email_verification"`.
    - Nếu token hợp lệ, backend lấy `user.id` từ `sub` và cập nhật bản ghi người dùng trong database: `email_verified = True` và `is_active = True`.
    - Trả về thông báo thành công cho frontend.

---

## 3. Luồng 2: Quên Mật khẩu (Forgot Password)

**Mục đích**: Cho phép người dùng đã xác minh email có thể lấy lại quyền truy cập tài khoản khi họ quên mật khẩu.

**Các bước thực hiện**:

1.  **Yêu cầu Reset Mật khẩu**:
    - Người dùng vào trang "Quên mật khẩu" và nhập địa chỉ email của họ.
    - Frontend gửi email này đến backend qua `POST /api/v1/auth/forgot-password`.

2.  **Tạo Token Reset**:
    - Backend kiểm tra xem email có tồn tại trong database và đã được xác minh hay chưa.
    - Nếu có, nó tạo một JWT mới (gọi là `reset_token`).
    - **Payload của JWT**:
        - `sub`: `user.id` hoặc `email`.
        - `scope`: `{"scope": "password_reset"}`.
        - `exp`: **Thời gian hết hạn rất ngắn (ví dụ: 15-60 phút)** để tăng cường bảo mật.

3.  **Gửi Email Reset**:
    - Backend gửi email chứa link reset mật khẩu, ví dụ: `https://your-frontend-app.com/reset-password?token=<reset_token>`.

4.  **Người dùng Đặt lại Mật khẩu**:
    - Người dùng nhấp vào link và được chuyển đến trang đặt lại mật khẩu trên frontend.
    - Frontend hiển thị form nhập mật khẩu mới và xác nhận mật khẩu mới.
    - Sau khi người dùng điền xong, frontend gửi một request `POST /api/v1/auth/reset-password`, trong body chứa `token` (lấy từ URL) và `new_password`.

5.  **Backend Cập nhật Mật khẩu**:
    - Endpoint backend nhận `token` và `new_password`.
    - Nó giải mã và xác thực token (chữ ký, thời gian, và `scope` phải là `"password_reset"`).
    - Nếu hợp lệ, backend sẽ băm (hash) `new_password` và cập nhật trường `hashed_password` cho người dùng tương ứng trong database.

---

## 4. Luồng 3: Đổi Mật khẩu (Khi đã đăng nhập)

**Mục đích**: Cho phép người dùng đang đăng nhập có thể tự đổi mật khẩu của mình.

**Các bước thực hiện**:

1.  **Yêu cầu Đổi mật khẩu**:
    - Người dùng vào trang cài đặt tài khoản và điền vào form "Đổi mật khẩu" (gồm mật khẩu cũ, mật khẩu mới, xác nhận mật khẩu mới).

2.  **Gửi Request**:
    - Frontend gửi request `POST /api/v1/users/me/change-password` (hoặc một endpoint tương tự).
    - **Quan trọng**: Đây là một **endpoint được bảo vệ**, yêu cầu người dùng phải đăng nhập và gửi kèm `access_token` (JWT dùng để đăng nhập) trong header `Authorization`.

3.  **Backend Xử lý**:
    - Backend xác thực `access_token` để lấy thông tin người dùng hiện tại (`current_user`).
    - So sánh `old_password` mà người dùng gửi lên với `hashed_password` đang được lưu trong database của `current_user`.
    - Nếu mật khẩu cũ không khớp, trả về lỗi `400 Bad Request`.
    - Nếu khớp, backend sẽ băm (hash) `new_password` và cập nhật trường `hashed_password` trong database.

## 5. Thiết kế Token JWT cho các luồng này

- **Sử dụng `scope`**: Luôn dùng một trường `scope` trong payload để phân biệt rõ ràng mục đích của token (`email_verification`, `password_reset`, `login`). Điều này ngăn chặn việc dùng token reset mật khẩu để xác minh email và ngược lại.
- **Thời gian sống (Expiry `exp`)**: Đặt thời gian hết hạn ngắn và phù hợp cho từng loại token để giảm thiểu rủi ro nếu token bị lộ. Token đăng nhập có thể sống lâu hơn token reset mật khẩu.
- **Bí mật ký (Signing Secret)**: Có thể xem xét sử dụng một secret key khác (hoặc một thuật toán khác) để ký các token tạm thời này so với token đăng nhập chính, nhằm tăng cường bảo mật.