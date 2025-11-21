# Cấu Hình GitHub OAuth App

Để tích hợp chức năng đăng nhập bằng GitHub, bạn cần đăng ký một ứng dụng OAuth mới trên GitHub. Dưới đây là hướng dẫn chi tiết về cách điền các thông tin trong quá trình đăng ký:

## Các Bước Đăng Ký Ứng Dụng OAuth trên GitHub

1.  Truy cập trang [GitHub Developer Settings](https://github.com/settings/developers).
2.  Chọn **OAuth Apps** ở thanh bên trái.
3.  Nhấp vào nút **New OAuth App**.

## Thông Tin Cần Điền

| Trường Form                  | Giải Thích                                                                                                                                                                                                                           | Giá Trị Đề Xuất (Môi trường phát triển)                                       |
| :--------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------- |
| **Application name**         | Tên ứng dụng của bạn mà người dùng sẽ thấy khi cấp quyền. Nên là một cái tên dễ nhận biết và đáng tin cậy.                                                                                                                           | `FullStack FastAPI React App` hoặc `Library Management`                       |
| **Homepage URL**             | URL trang chủ của ứng dụng của bạn. Đây là nơi GitHub sẽ chuyển hướng người dùng nếu họ nhấp vào tên ứng dụng trong màn hình cấp quyền hoặc nếu họ cần thêm thông tin về ứng dụng của bạn.                                               | `http://localhost:5173` (URL của frontend trong môi trường phát triển)         |
| **Application description**  | Mô tả ngắn gọn về ứng dụng của bạn. Đây là tùy chọn nhưng nên được điền để cung cấp thêm thông tin cho người dùng.                                                                                                                | `A full-stack application for library management with user authentication.` |
| **Authorization callback URL** | **Rất quan trọng.** Đây là URL mà GitHub sẽ chuyển hướng người dùng sau khi họ cấp quyền (hoặc từ chối) cho ứng dụng của bạn. URL này phải trỏ đến endpoint xử lý callback của backend của bạn. | `http://127.0.0.1:8000/api/v1/auth/github/callback` (URL của backend trong môi trường phát triển) |
| **Enable Device Flow**       | Tùy chọn này cho phép ứng dụng của bạn xác thực người dùng thông qua luồng Device Flow (thường dùng cho các thiết bị không có trình duyệt hoặc CLI). **Không cần thiết cho dự án này.**                                                | Để trống (Không chọn)                                                        |

### Lưu ý Quan Trọng:

*   **Môi trường Phát triển vs. Sản phẩm (Production):** Các giá trị `Homepage URL` và `Authorization callback URL` trên đây là dành cho môi trường phát triển cục bộ của bạn. Khi triển khai ứng dụng lên môi trường production, bạn sẽ cần tạo một GitHub OAuth App khác hoặc cập nhật các URL này thành các URL public của ứng dụng đã được triển khai (ví dụ: `https://your-frontend-domain.com` và `https://api.your-backend-domain.com/api/v1/auth/github/callback`).
*   Sau khi đăng ký thành công, bạn sẽ nhận được **`Client ID`** và **`Client Secret`**. Hãy lưu trữ chúng cẩn thận, bạn sẽ cần các giá trị này để cấu hình biến môi trường cho backend của mình.
