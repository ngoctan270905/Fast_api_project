# Phân tích Chức năng Xác thực & Phân quyền

Dưới đây là phân tích chi tiết về hệ thống xác thực và phân quyền trong dự án `library_api`.

## Tổng quan

Hệ thống được xây dựng dựa trên các tiêu chuẩn hiện đại, sử dụng FastAPI, OAuth2 (Password Bearer Flow) và JWT. Luồng hoạt động chính như sau:
1.  Người dùng gửi `username` và `password` đến endpoint `/api/v1/auth/login`.
2.  `AuthService` xác thực thông tin.
3.  `security.py` kiểm tra hash mật khẩu và tạo ra một JSON Web Token (JWT) nếu hợp lệ.
4.  JWT được trả về cho client.
5.  Với các yêu cầu cần xác thực sau đó, client gửi JWT trong header `Authorization`.
6.  Dependency `get_current_user` sẽ giải mã token, xác thực người dùng và "inject" thông tin người dùng vào route.

## Điểm mạnh

1.  **Cấu trúc Module tốt:** Logic được phân tách rõ ràng vào các module chuyên biệt:
    *   `app/core/security.py`: Xử lý băm mật khẩu và tạo/giải mã JWT.
    *   `app/core/dependencies.py`: Định nghĩa các dependency để bảo vệ route và kiểm tra vai trò.
    *   `app/services/auth_service.py`: Điều phối logic nghiệp vụ cho việc đăng ký và đăng nhập.
    *   `app/api/v1/endpoints/auth.py`: Cung cấp các API endpoint cho client.
    Cách tổ chức này giúp code dễ đọc, dễ bảo trì và mở rộng.

2.  **Sử dụng Thư viện Bảo mật Tiêu chuẩn:**
    *   **Passlib & Bcrypt:** Sử dụng `passlib` với thuật toán `bcrypt` để băm và lưu trữ mật khẩu một cách an toàn. Đây là một phương pháp mạnh mẽ và được khuyến nghị.
    *   **Python-jose:** Sử dụng `python-jose` để xử lý JWT, một thư viện đáng tin cậy cho các hoạt động liên quan đến token.

3.  **Phân quyền cơ bản (RBAC):** Hệ thống đã có một cơ chế phân quyền đơn giản nhưng hiệu quả thông qua dependency `get_current_admin_user`. Dependency này không chỉ xác thực người dùng mà còn kiểm tra xem trường `role` của người dùng có phải là "admin" hay không, giúp bảo vệ các endpoint dành riêng cho quản trị viên.

4.  **Sử dụng Dependency Injection:** Việc dùng `Depends(get_current_user)` của FastAPI là một cách tiếp cận rất tốt để tái sử dụng logic xác thực và đảm bảo các route được bảo vệ một cách nhất quán.

## Điểm yếu và Thiếu sót

1.  **Hệ thống Refresh Token bị lỗi nghiêm trọng:**
    *   **Vấn đề:** Endpoint `/refresh` hiện tại nhận vào một *access token* cũ và trả về một *access token* mới. Điều này hoàn toàn sai mục đích của refresh token. Access token vốn có đời sống ngắn để giảm thiểu rủi ro khi bị lộ. Nếu kẻ tấn công có được access token, họ có thể dùng nó để tạo ra token mới liên tục, vô hiệu hóa cơ chế hết hạn.
    *   **Cách hoạt động đúng:** Một hệ thống đúng cần có hai loại token: `access_token` (ngắn hạn) và `refresh_token` (dài hạn). Endpoint refresh sẽ nhận vào `refresh_token` để cấp `access_token` mới.

2.  **Không có Cơ chế Thu hồi Token (Token Revocation):**
    *   **Vấn đề:** Hệ thống hiện tại là "stateless". Một khi JWT được tạo ra, nó sẽ hợp lệ cho đến khi tự hết hạn. Không có cách nào để vô hiệu hóa một token ngay lập tức (ví dụ: khi người dùng logout, đổi mật khẩu, hoặc token bị nghi ngờ bị lộ). Endpoint `/logout` chỉ là một thao tác giả ở phía server và không thực sự vô hiệu hóa token.
    *   **Rủi ro:** Nếu một token bị đánh cắp, kẻ tấn công có thể sử dụng nó cho đến khi token hết hạn.

3.  **Không có Biện pháp chống Tấn công Brute-Force:**
    *   **Vấn đề:** Endpoint `/api/v1/auth/login` không được bảo vệ bởi cơ chế giới hạn số lần thử (rate limiting).
    *   **Rủi ro:** Kẻ tấn công có thể thực hiện tấn công brute-force bằng cách thử hàng loạt mật khẩu cho một username mà không bị ngăn chặn.

4.  **Thiếu Kiểm thử Tự động (Automated Tests):**
    *   **Vấn đề:** Dự án không có thư mục `tests`. Toàn bộ logic bảo mật quan trọng này không được kiểm thử tự động.
    *   **Rủi ro:** Việc thay đổi hoặc nâng cấp code trong tương lai có thể vô tình tạo ra lỗ hổng bảo mật mà không bị phát hiện.

## Đề xuất Cải thiện

1.  **Sửa lại Luồng Refresh Token:**
    *   Khi người dùng đăng nhập, cấp cho họ cả `access_token` và `refresh_token`.
    *   Lưu `refresh_token` (dưới dạng hash) vào database, liên kết với người dùng.
    *   Endpoint `/refresh` phải yêu cầu `refresh_token`. Khi nhận được, server sẽ xác thực nó với bản ghi trong database, đánh dấu nó là đã sử dụng (để chống tấn công phát lại - replay attack), và cấp một cặp `access_token` và `refresh_token` mới.

2.  **Triển khai Cơ chế Thu hồi Token:**
    *   Tạo một "blacklist" (danh sách đen) cho các token đã bị thu hồi. Có thể sử dụng một cơ sở dữ liệu nhanh như Redis để lưu trữ ID của các token bị vô hiệu hóa cho đến khi chúng hết hạn.
    *   Trong dependency `get_current_user`, sau khi giải mã token, kiểm tra xem ID của nó có nằm trong blacklist không. Nếu có, từ chối yêu cầu.
    *   Khi người dùng logout, thêm ID của token vào blacklist.

3.  **Thêm Rate Limiting:**
    *   Tích hợp một thư viện như `slowapi` vào FastAPI.
    *   Áp dụng rate limit cho endpoint `/login` và có thể cả các endpoint nhạy cảm khác để giới hạn số lượng yêu cầu từ một địa chỉ IP trong một khoảng thời gian nhất định.

4.  **Viết Bộ Kiểm thử Toàn diện:**
    *   Tạo thư mục `tests`.
    *   Sử dụng `pytest` và `HTTPX` để viết các bài kiểm thử cho toàn bộ luồng xác thực: đăng nhập thành công/thất bại, bảo vệ route, phân quyền admin, refresh token, và logout.

## API Key là gì?

API Key (Khóa API) là một đoạn mã định danh duy nhất (thường là một chuỗi ký tự dài, ngẫu nhiên) được sử dụng để xác thực một người dùng, một ứng dụng hoặc một dịch vụ khi truy cập vào một API. Nó giống như một mật khẩu bí mật mà ứng dụng hoặc dịch vụ cần cung cấp để chứng minh danh tính và được cấp quyền truy cập.

### Mục đích sử dụng

*   **Xác định nguồn gốc yêu cầu:** Cho phép nhà cung cấp API biết ai đang gửi yêu cầu.
*   **Kiểm soát truy cập:** Cấp hoặc từ chối quyền truy cập vào các tính năng API cụ thể.
*   **Giới hạn tỷ lệ (Rate Limiting):** Theo dõi và giới hạn số lượng yêu cầu mà một người dùng/ứng dụng có thể gửi trong một khoảng thời gian nhất định để tránh lạm dụng.
*   **Thống kê và phân tích:** Theo dõi việc sử dụng API để phân tích và tính phí.

### API Key khác JWT/OAuth2 như thế nào?

Mặc dù cả API Key và JWT (trong luồng OAuth2) đều dùng để xác thực, chúng phục vụ các mục đích hơi khác nhau và có các đặc điểm riêng:

| Đặc điểm          | API Key                                    | JWT (qua OAuth2)                                    |
| :---------------- | :----------------------------------------- | :-------------------------------------------------- |
| **Đối tượng xác thực**  | Ứng dụng, dịch vụ, hoặc người dùng tĩnh   | Người dùng cụ thể sau khi đăng nhập                 |
| **Cơ chế hoạt động**   | Chuỗi bí mật được gửi trong header hoặc query param | Token được ký số, gửi trong header `Authorization: Bearer <token>` |
| **Tính trạng thái**    | Có trạng thái (cần lưu trữ trong DB để xác thực) | Không trạng thái (Stateless), tự chứa thông tin xác thực |
| **Thời gian sống**      | Thường là dài hạn, có thể không hết hạn | Ngắn hạn (Access Token) hoặc dài hạn hơn (Refresh Token) |
| **Cơ chế thu hồi**    | Dễ dàng thu hồi (xóa khỏi DB)              | Cần cơ chế Blacklist/Revocation list cho Access Token |
| **Trường hợp sử dụng** | Gọi API giữa các server, ứng dụng mobile/web tĩnh | Ứng dụng tương tác với người dùng (web apps, SPAs, mobile apps) |

### Khi nào sử dụng API Key?

*   Khi bạn muốn cấp quyền truy cập cho một ứng dụng hoặc dịch vụ của bên thứ ba mà không cần người dùng cuối đăng nhập.
*   Để bảo vệ các API công khai nhưng cần kiểm soát lượng truy cập (ví dụ: API thời tiết, API bản đồ).
*   Khi bạn cần xác định một ứng dụng cụ thể chứ không phải một người dùng cụ thể.

### Cách triển khai cơ bản với FastAPI

Bạn có thể tạo một `Security` dependency để kiểm tra API Key từ header (ví dụ `X-API-Key`) và so sánh nó với một danh sách các API Key hợp lệ (lưu trữ trong biến môi trường hoặc database).

```python
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == "YOUR_SUPER_SECRET_API_KEY": # Thay bằng logic kiểm tra DB/config
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key",
    )

# Sau đó bạn có thể dùng nó trong router:
# @router.get("/protected-by-api-key", dependencies=[Depends(get_api_key)])
# async def some_api_route():
#    return {"message": "Access granted with API Key"}
```

Bổ sung thêm API Key vào hệ thống có thể giúp bạn mở rộng khả năng xác thực cho nhiều trường hợp sử dụng khác nhau.
