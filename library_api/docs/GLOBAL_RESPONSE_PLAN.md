# Kế hoạch triển khai Global Response Model và Global Error Handling

Tài liệu này mô tả các bước cần thiết để chuẩn hóa tất cả các phản hồi API (cả thành công và lỗi) bằng cách sử dụng một cấu trúc chung.

## 1. Mục tiêu

-   **Phản hồi thành công (Success):** Tất cả các phản hồi thành công sẽ có cấu trúc `{ "status": "success", "data": ... }`.
-   **Phản hồi lỗi (Error):** Tất cả các lỗi (bao gồm lỗi xác thực, lỗi nghiệp vụ, và lỗi hệ thống) sẽ có cấu trúc `{ "status": "error", "message": "...", "detail": ... }`.
-   **Tăng tính nhất quán:** Giúp phía client dễ dàng xử lý các phản hồi từ API một cách đồng nhất.
-   **Bảo mật:** Ngăn chặn việc rò rỉ các thông tin chi tiết về lỗi hệ thống (stack traces) ra cho client.

## 2. Các bước triển khai

### Bước 1: Tạo Schema cho Response

Tạo một file mới tại `app/schemas/response.py` để định nghĩa `ResponseModel` chung và `ErrorResponse` cho các lỗi.

**Nội dung file `app/schemas/response.py`:**

```python
from typing import Generic, TypeVar, Optional, Any
from pydantic.generics import GenericModel
from pydantic import BaseModel, Field

T = TypeVar('T')

class ResponseModel(GenericModel, Generic[T]):
    """
    Schema chuẩn cho các phản hồi thành công.
    """
    status: str = Field("success", description="Trạng thái của request (luôn là 'success')")
    message: Optional[str] = Field(None, description="Thông điệp tùy chọn, ví dụ: 'Book created successfully'")
    data: Optional[T] = Field(None, description="Dữ liệu chính của phản hồi")

class ErrorResponse(BaseModel):
    """
    Schema chuẩn cho các phản hồi lỗi.
    """
    status: str = Field("error", description="Trạng thái của request (luôn là 'error')")
    message: str = Field(..., description="Mô tả lỗi chính, an toàn để hiển thị cho người dùng")
    detail: Optional[Any] = Field(None, description="Chi tiết kỹ thuật của lỗi (chỉ dùng trong môi trường dev)")
```

### Bước 2: Tách và tích hợp Global Exception Handlers một cách module hóa

Để giữ cho `app/main.py` gọn gàng và tập trung vào việc khởi tạo ứng dụng, chúng ta sẽ di chuyển các exception handler vào một module riêng biệt.

**Bước 2.1: Tạo file `app/exceptions/handlers.py`**

Tạo một file mới tại `app/exceptions/handlers.py` để chứa các hàm xử lý exception.

**Nội dung file `app/exceptions/handlers.py`:**

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException as StarletteHTTPException
from slowapi.errors import RateLimitExceeded
from app.schemas.response import ErrorResponse
import logging

logger = logging.getLogger(__name__)

async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    """
    Handler cho RateLimitExceeded (lỗi vượt quá giới hạn request).
    """
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=ErrorResponse(
            status="error",
            message="Too many requests",
            detail=f"Rate limit exceeded: {exc.detail}"
        ).model_dump()
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handler cho các lỗi HTTPException được ném ra chủ động từ code FastAPI.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            status="error",
            message=exc.detail,
        ).model_dump(),
        headers=exc.headers
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handler cho tất cả các lỗi không xác định (lỗi hệ thống không lường trước).
    """
    logger.error(f"Unhandled error occurred: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status="error",
            message="An unexpected internal server error occurred.",
        ).model_dump()
    )
```

**Bước 2.2: Tạo file `app/exceptions/__init__.py`**

File này sẽ chứa một hàm để đăng ký tất cả các handler vào ứng dụng FastAPI.

**Nội dung file `app/exceptions/__init__.py`:**

```python
from fastapi import FastAPI
from app.exceptions.handlers import (
    rate_limit_exception_handler,
    http_exception_handler,
    generic_exception_handler
)
from fastapi.exceptions import HTTPException as StarletteHTTPException
from slowapi.errors import RateLimitExceeded


def add_exception_handlers(app: FastAPI):
    """
    Đăng ký tất cả các exception handlers vào ứng dụng FastAPI.
    """
    app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
```

**Bước 2.3: Cập nhật `app/main.py`**

Bây giờ, `app/main.py` sẽ gọn gàng hơn nhiều, chỉ cần import và gọi hàm `add_exception_handlers`.

**Các thay đổi trong `app/main.py`:**

```python
# app/main.py (chỉ các phần chỉnh sửa/thêm vào)
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse # Có thể cần hoặc không tùy thuộc vào handler

from app.api.v1.router import api_router
from app.core.config import settings
from app.middleware.logging_middleware import LoggingMiddleware
from app.core.lifespan import lifespan

from app.core.rate_limiter import limiter
# Không cần import RateLimitExceeded nữa vì nó được handle trong exceptions module
# from slowapi.errors import RateLimitExceeded

# Import hàm đăng ký exception handlers
from app.exceptions import add_exception_handlers

logging.basicConfig(
    level=logging.INFO if settings.ENVIRONMENT == "development" else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Library API", lifespan=lifespan)

app.state.limiter = limiter

# --- Phần này sẽ được xóa hoặc thay thế bằng add_exception_handlers ---
# @app.exception_handler(RateLimitExceeded)
# async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
#     return JSONResponse(
#         status_code=429,
#         content={"Lỗi": f"Vượt quá giới hạn limit: {exc.detail}"},
#     )
# --- Kết thúc phần cần xóa ---

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

# Đăng ký tất cả các exception handlers
add_exception_handlers(app)

app.include_router(api_router, prefix="/api/v1")
```

### Bước 3: Cập nhật các API Endpoint

Sửa đổi các endpoint để sử dụng `ResponseModel` cho `response_model` và cấu trúc lại dữ liệu trả về.

**Ví dụ với `app/api/v1/endpoints/books.py`:**

```python
# import các model/schema cần thiết, bao gồm cả ResponseModel
from app.schemas.response import ResponseModel
from app.schemas.book import BookRead, BookCreate

router = APIRouter()

# --- Endpoint tạo sách ---
@router.post("/", response_model=ResponseModel[BookRead], status_code=status.HTTP_201_CREATED)
async def create_book(
    book_in: BookCreate,
    # ... các dependencies khác
):
    # ... logic tạo sách
    new_book = await book_service.create_book(db, book_in)
    # Bọc dữ liệu trả về trong ResponseModel
    return ResponseModel(data=new_book, message="Book created successfully.")

# --- Endpoint lấy sách theo ID ---
@router.get("/{book_id}", response_model=ResponseModel[BookRead])
async def read_book_by_id(
    book_id: int,
    # ... các dependencies khác
):
    book = await book_service.get_book_by_id(db, book_id)
    if not book:
        # Lỗi này sẽ được bắt bởi http_exception_handler và định dạng lại
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    
    # Bọc dữ liệu trả về trong ResponseModel
    return ResponseModel(data=book)

# --- Endpoint xóa sách ---
# Đối với các endpoint không trả về nội dung (204 No Content), không cần thay đổi
@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    # ... các dependencies khác
):
    # ... logic xóa
    return None # Giữ nguyên
```
