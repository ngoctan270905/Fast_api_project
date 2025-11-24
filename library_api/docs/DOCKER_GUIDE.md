# Hướng dẫn chi tiết развертывание dự án với Docker Compose

Chào bạn, đây là tài liệu hướng dẫn từng bước để bạn có thể chạy toàn bộ dự án (backend và frontend) bằng Docker. Docker sẽ giúp tạo ra một môi trường nhất quán, đóng gói ứng dụng và các dependencies của nó vào các "container", giúp việc chạy ứng dụng trở nên dễ dàng hơn trên mọi máy tính.

## Docker Compose là gì?

`docker-compose` là một công cụ cho phép định nghĩa và chạy các ứng dụng Docker đa container. Trong dự án của chúng ta, chúng ta có 3 container chính:
1.  `db`: Container chứa cơ sở dữ liệu MySQL.
2.  `backend`: Container chứa API backend viết bằng FastAPI.
3.  `frontend`: Container chứa giao diện người dùng viết bằng React, được phục vụ (serve) bởi Nginx.

File `docker-compose.yml` ở thư mục gốc của dự án là file cấu hình chính cho Docker Compose.

## Yêu cầu

Trước khi bắt đầu, hãy chắc chắn bạn đã cài đặt **Docker Desktop** trên máy tính của mình. Bạn có thể tải nó từ trang chủ của Docker: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)

## Các bước thực hiện

### Bước 1: Chuẩn bị file môi trường `.env` cho Backend

File `.env` chứa các biến môi trường cần thiết để backend có thể hoạt động, ví dụ như thông tin kết nối đến database, các khóa bí mật,...

1.  Đi đến thư mục `library_api`.
2.  Tạo một bản sao của file `.env.example` và đổi tên thành `.env`.
3.  Mở file `.env` và **chỉnh sửa lại cho phù hợp với cấu hình trong `docker-compose.yml`**.

Nội dung file `.env` của bạn cần được cập nhật như sau để kết nối với container `db` mà chúng ta đã định nghĩa trong `docker-compose.yml`:

```env
# ========================
# DATABASE SETTINGS
# Thay thế các giá trị này để khớp với dịch vụ 'db' trong docker-compose.yml
# ========================
DATABASE_URL="mysql+aiomysql://user:password@db:3306/library_db"
DATABASE_URL_SYNC="mysql+pymysql://user:password@db:3306/library_db"

# ========================
# JWT AUTHENTICATION
# Giữ nguyên hoặc thay đổi khóa bí mật nếu bạn muốn
# ========================
SECRET_KEY="your-super-secret-key-that-is-long-and-random"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ========================
# EMAIL SETTINGS (Tùy chọn)
# Cấu hình nếu bạn muốn dùng tính năng email, nếu không có thể để trống
# ========================
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-google-app-password
MAIL_FROM=your-email@gmail.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
MAIL_FROM_NAME="My Awesome App"

# ========================
# FRONTEND
# ========================
CLIENT_BASE_URL="http://localhost:3000"

# ========================
# OAUTH SETTINGS (Tùy chọn)
# Để trống nếu bạn không cấu hình đăng nhập qua mạng xã hội
# ========================
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
FACEBOOK_CLIENT_ID=
FACEBOOK_CLIENT_SECRET=
```

**Quan trọng:**
*   `user`, `password`, `library_db` phải khớp với các biến môi_trường `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` của dịch vụ `db` trong file `docker-compose.yml`.
*   `db` trong chuỗi kết nối (`@db:3306`) là tên của service database được định nghĩa trong `docker-compose.yml`. Docker Compose sẽ tự động phân giải tên này thành địa chỉ IP nội bộ của container `db`.
*   `CLIENT_BASE_URL` được đặt là `http://localhost:3000` vì đây là địa chỉ mà chúng ta sẽ truy cập frontend.

### Bước 2: Build và Chạy ứng dụng

Bây giờ bạn đã sẵn sàng để "build" các image và khởi chạy các container.

1.  Mở terminal hoặc command prompt.
2.  Di chuyển đến thư mục gốc của dự án (nơi chứa file `docker-compose.yml`).
3.  Chạy lệnh sau:

    ```bash
    docker-compose up --build -d
    ```

**Giải thích lệnh:**
*   `docker-compose up`: Khởi tạo và chạy các container được định nghĩa trong file `docker-compose.yml`.
*   `--build`: Yêu cầu Docker build lại các image từ `Dockerfile` trước khi khởi chạy container. Bạn nên dùng flag này trong lần chạy đầu tiên hoặc khi bạn có thay đổi trong code (ví dụ: `Dockerfile`, code backend, code frontend).
*   `-d` (detached mode): Chạy các container ở chế độ nền. Terminal của bạn sẽ không bị chiếm dụng và bạn có thể tiếp tục sử dụng nó.

Quá trình build có thể mất vài phút, đặc biệt là lần đầu tiên vì Docker cần tải các base images và cài đặt tất cả dependencies.

### Bước 3: Truy cập ứng dụng

Sau khi lệnh trên hoàn tất, các container của bạn sẽ chạy ở chế độ nền.

*   **Frontend (Giao diện người dùng)**: Mở trình duyệt và truy cập `http://localhost:3000`.
*   **Backend (API)**: API sẽ chạy tại `http://localhost:8000`. Bạn có thể kiểm tra các endpoint và tài liệu API tự động của FastAPI bằng cách truy cập `http://localhost:8000/docs`.
*   **Database**: Database đang chạy và có thể được truy cập từ bên trong mạng Docker trên cổng `3306`. Cổng này cũng được map ra máy host của bạn, nên bạn có thể kết nối tới nó bằng một công cụ quản lý DB (như DBeaver, TablePlus) với thông tin:
    *   Host: `localhost`
    *   Port: `3306`
    *   User: `user`
    *   Password: `password`
    *   Database: `library_db`

### Các lệnh Docker Compose hữu ích khác

*   **Xem logs của các container:**
    Để xem log (kết quả output) của tất cả các container đang chạy, dùng lệnh:
    ```bash
    docker-compose logs -f
    ```
    Nếu bạn chỉ muốn xem log của một service cụ thể (ví dụ `backend`):
    ```bash
    docker-compose logs -f backend
    ```

*   **Dừng các container:**
    Để dừng tất cả các container đang chạy mà không xóa chúng, dùng lệnh:
    ```bash
    docker-compose stop
    ```

*   **Dừng và xóa các container:**
    Lệnh này sẽ dừng các container và xóa chúng cùng với các network đã được tạo. Volume chứa dữ liệu database (`mysql_data`) sẽ không bị xóa.
    ```bash
    docker-compose down
    ```

*   **Chạy lệnh bên trong một container:**
    Đôi khi bạn muốn chạy một lệnh trực tiếp bên trong container đang chạy. Ví dụ, để mở một shell (bash) vào container backend:
    ```bash
    docker-compose exec backend bash
    ```
    Từ đó, bạn có thể thực thi các lệnh bên trong môi trường của container.

Chúc bạn thành công!
