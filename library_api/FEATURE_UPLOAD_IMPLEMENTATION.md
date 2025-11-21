# Triển khai Chức năng Upload File cho Ảnh bìa sách

Tài liệu này ghi lại quá trình triển khai chức năng upload file từ đầu, bao gồm các bước thực hiện, sửa lỗi và giải thích các quyết định thiết kế.

## 1. Mục tiêu

Triển khai chức năng cho phép người dùng upload file ảnh bìa cho một cuốn sách (`Book`) đã tồn tại trong hệ thống. Đường dẫn của file ảnh sau khi upload sẽ được lưu vào database.

## 2. Các bước thực hiện

Quá trình được chia thành các bước logic như sau:

### Bước 1: Cập nhật Cấu trúc Database

Đây là bước đầu tiên để hệ thống có nơi lưu trữ thông tin về ảnh bìa.

1.  **Sửa Model**: Mở file `app/models/book.py` và thêm một trường mới vào class `Book` để lưu đường dẫn file ảnh.
    ```python
    cover_image_url: Optional[str] = Field(default=None, max_length=255, nullable=True)
    ```
2.  **Tạo Migration File**: Sử dụng Alembic để tự động phát hiện thay đổi trên model và tạo ra một script migration.
    ```bash
    alembic revision --autogenerate -m "Add cover_image_url to books table"
    ```
    Lệnh này đã tạo ra file `alembic/versions/006c91c7d290_add_cover_image_url_to_books_table.py`.

3.  **Áp dụng Migration**: Chạy script migration để cập nhật cấu trúc database thực tế.
    ```bash
    alembic upgrade head
    ```
    Lệnh này đã thêm cột `cover_image_url` vào bảng `book` trong database.

### Bước 2: Chuẩn bị Môi trường

1.  **Kiểm tra Thư viện**: Đảm bảo thư viện `python-multipart` đã được cài đặt, vì nó cần thiết cho FastAPI để xử lý dữ liệu form và file upload.
2.  **Tạo Thư mục Media**: Tạo một thư mục `media/` ở thư mục gốc của dự án. Đây là nơi các file vật lý sẽ được lưu trữ.
    ```bash
    mkdir media
    ```

### Bước 3: Mở rộng Logic ở các Tầng (Layers)

Để endpoint có thể tương tác với database, chúng ta cần cập nhật các tầng Repository và Service.

1.  **Repository Layer**: Thêm phương thức `update_book_cover_image_url` vào class `BookRepository` trong `app/repositories/book_repository.py`. Phương thức này chịu trách nhiệm tìm sách và cập nhật cột `cover_image_url`.
2.  **Service Layer**: Thêm phương thức `update_book_cover_image_url` vào class `BookService` trong `app/services/book_service.py`. Phương thức này chứa logic nghiệp vụ, kiểm tra xem sách có tồn tại không trước khi gọi xuống Repository.

### Bước 4: Cập nhật Schema Response

Để API có thể trả về thông tin đường dẫn ảnh, chúng ta cần cập nhật schema.

- **Sửa Schema**: Thêm trường `cover_image_url: Optional[str] = None` vào class `BookResponse` trong file `app/schemas/book.py`.

### Bước 5: Tạo và Tích hợp API Endpoint

Đây là bước tạo ra giao diện để client có thể tương tác.

1.  **Tạo file Endpoint**: Tạo một file mới `app/api/v1/endpoints/uploads.py` để chứa tất cả logic liên quan đến việc upload.
2.  **Tích hợp Router**: Import router từ `uploads.py` và thêm nó vào `api_router` chính trong file `app/api/v1/router.py` để API có thể được truy cập.

### Bước 6: Sửa lỗi và Hoàn thiện

Trong quá trình tích hợp, hai lỗi đã phát sinh và được khắc phục:

1.  **Lỗi `ImportError`**: Ban đầu, `uploads.py` đã cố gắng import `get_db` từ một vị trí sai.
    - **Nguyên nhân**: Sai tên và sai vị trí file của dependency cung cấp session database.
    - **Cách sửa**: Thay đổi import thành `from app.core.database import get_session` và sử dụng `Depends(get_session)`, giống hệt như các endpoint khác trong dự án.

2.  **Lỗi Dependency Injection của `BookService`**: Sau khi sửa lỗi trên, ứng dụng vẫn không khởi động được.
    - **Nguyên nhân**: Cố gắng inject `BookService` trực tiếp vào hàm endpoint (`Depends(BookService)`). FastAPI không biết cách tạo `BookService` vì nó cần một `db session`.
    - **Cách sửa**: Xóa `Depends(BookService)` khỏi chữ ký hàm. Thay vào đó, khởi tạo service thủ công bên trong endpoint: `book_service = BookService(db)`. Đây là convention đã được thiết lập trong toàn bộ dự án.

## 3. Luồng hoạt động của chức năng Upload

1.  Client gửi một request `POST` đến `http://.../api/v1/uploads/book-cover/{book_id}`. Trong body của request là dữ liệu file ảnh (`multipart/form-data`).
2.  Endpoint `upload_book_cover` trong `uploads.py` tiếp nhận request.
3.  Nó kiểm tra định dạng file (chỉ cho phép ảnh).
4.  File được lưu vào thư mục `/media` trên server với một tên an toàn (ví dụ: `book_1_cover.png`).
5.  Endpoint khởi tạo `BookService` và gọi phương thức `update_book_cover_image_url`, truyền vào `book_id` và đường dẫn file vừa lưu.
6.  `BookService` kiểm tra xem sách có tồn tại không.
7.  Nếu có, `BookService` gọi xuống `BookRepository`.
8.  `BookRepository` thực thi câu lệnh `UPDATE` trên database, lưu đường dẫn file ảnh vào cột `cover_image_url` của sách tương ứng.
9.  API trả về một response JSON xác nhận upload thành công, kèm theo thông tin của sách đã được cập nhật.

## 4. Tại sao không upload trực tiếp trong route tạo/sửa sách?

Đây là một câu hỏi rất hay về thiết kế API. Việc tách riêng endpoint upload ra khỏi các endpoint tạo/sửa (`POST /books`, `PUT /books/{id}`) là một quyết định có chủ đích dựa trên các nguyên tắc thiết kế phần mềm hiện đại:

1.  **Tách biệt Trách nhiệm (Separation of Concerns)**:
    - Các endpoint `POST /books` và `PUT /books/{id}` có trách nhiệm chính là xử lý **dữ liệu có cấu trúc** dạng JSON.
    - Endpoint `/uploads` có trách nhiệm xử lý **dữ liệu nhị phân** (binary data) của file.
    - Gộp chung cả hai (gửi JSON và file trong cùng một request `multipart/form-data`) làm cho logic ở backend trở nên phức tạp và client cũng khó gửi request hơn. Tách riêng giúp code sạch sẽ, dễ bảo trì hơn.

2.  **Tối ưu Trải nghiệm và Luồng làm việc (UX Flow)**:
    - Luồng làm việc tự nhiên thường là: người dùng **tạo cuốn sách trước**, sau đó mới **tải lên hoặc thay đổi ảnh bìa** cho nó.
    - Việc tách riêng cho phép người dùng thay đổi ảnh bìa nhiều lần mà không cần phải gửi lại toàn bộ thông tin của cuốn sách. Nếu gộp chung, mỗi lần muốn đổi ảnh, bạn lại phải `PUT` lại cả `title`, `author_ids`... rất bất tiện.

3.  **Linh hoạt và Tái sử dụng (Flexibility & Reusability)**:
    - Với một router `/uploads` riêng, bạn có thể dễ dàng mở rộng chức năng upload cho các đối tượng khác trong tương lai. Ví dụ, bạn có thể thêm endpoint `/uploads/author-avatar/{author_id}` để upload ảnh cho tác giả mà không làm ảnh hưởng đến router của `books` hay `authors`.

4.  **Hạn chế Kỹ thuật của `multipart/form-data`**:
    - Khi bạn dùng `multipart/form-data` để gửi cả file và dữ liệu JSON phức tạp, toàn bộ phần JSON đó phải được gửi dưới dạng một chuỗi văn bản (string).
    - Việc validate một đối tượng JSON lồng nhau (nested object) khi nó chỉ là một chuỗi trong form-data sẽ khó khăn và kém hiệu quả hơn nhiều so với việc nhận một body `application/json` chuẩn mà FastAPI/Pydantic đã tối ưu.

**Kết luận**: Tách riêng endpoint upload là một design pattern phổ biến và mạnh mẽ, giúp hệ thống API của bạn trở nên module hóa, linh hoạt và dễ bảo trì hơn trong dài hạn.