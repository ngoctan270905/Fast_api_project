# Ghi nhận việc sửa lỗi 500 khi lấy danh sách người dùng

## Mô tả lỗi

Khi người dùng có quyền admin thực hiện yêu cầu lấy danh sách tất cả người dùng (`GET /api/v1/users`), hệ thống trả về lỗi `500 Internal Server Error` thay vì danh sách người dùng.

## Nguyên nhân gốc rễ

Lỗi được xác định nằm trong file `app/services/user_service.py`, cụ thể là trong phương thức `get_all_users`. Nguyên nhân là do việc sử dụng một truy vấn SQLAlchemy không hợp lệ để đếm tổng số lượng người dùng trong cơ sở dữ liệu.

Đoạn mã gây lỗi đã cố gắng tạo một truy vấn con và đếm số lượng ID, nhưng cú pháp này không được SQLAlchemy 2.0 hỗ trợ và gây ra ngoại lệ (exception) ở tầng dịch vụ, dẫn đến lỗi 500.

## Chi tiết việc sửa lỗi

### File đã thay đổi

- `app/services/user_service.py`

### Đoạn mã trước khi sửa

```python
# app/services/user_service.py

from sqlalchemy import select
# ...

class UserService:
    # ...
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> (int, List[User]):
        """Lấy danh sách tất cả user với phân trang"""
        
        # Đếm tổng số user
        total_query = select(User)
        total_result = await self.db_session.execute(select(total_query.subquery().c.id).count())
        total = total_result.scalar_one()

        # Lấy user theo phân trang
        query = select(User).offset(skip).limit(limit)
        result = await self.db_session.execute(query)
        users = result.scalars().all()
        
        return total, users
    # ...
```

### Đoạn mã sau khi sửa

```python
# app/services/user_service.py

from sqlalchemy import select, func
# ...

class UserService:
    # ...
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> (int, List[User]):
        """Lấy danh sách tất cả user với phân trang"""
        
        # Đếm tổng số user
        total_query = select(func.count(User.id))
        total_result = await self.db_session.execute(total_query)
        total = total_result.scalar_one()

        # Lấy user theo phân trang
        query = select(User).offset(skip).limit(limit)
        result = await self.db_session.execute(query)
        users = result.scalars().all()
        
        return total, users
    # ...
```

### Giải thích thay đổi

1.  **Import `func` từ `sqlalchemy`**:
    -   `func` là một đối tượng của SQLAlchemy cho phép sử dụng các hàm SQL tiêu chuẩn (như `COUNT`, `SUM`, `AVG`, v.v.) một cách an toàn và tương thích với nhiều loại cơ sở dữ liệu.
    -   Dòng `from sqlalchemy import select` đã được thay đổi thành `from sqlalchemy import select, func`.

2.  **Sử dụng `func.count` để đếm**:
    -   Thay vì tạo một truy vấn con phức tạp và không chính xác, chúng tôi đã sử dụng trực tiếp `func.count(User.id)` để yêu cầu cơ sở dữ liệu đếm số lượng bản ghi trong bảng `User`.
    -   `select(func.count(User.id))` tạo ra một câu lệnh SQL tương đương `SELECT count(users.id) FROM users`, đây là cách hiệu quả và đúng đắn để lấy tổng số lượng.

Thay đổi này đã giải quyết được vấn đề, giúp truy vấn hoạt động chính xác và loại bỏ lỗi 500.
