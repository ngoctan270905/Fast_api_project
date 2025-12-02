from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.dependencies import DbSession
from app.core.database import get_session
from app.services.book_service import BookService
from app.schemas.book import BookResponse, BookListResponse, BookCreate, BookUpdate
from app.schemas.response import ResponseModel

router = APIRouter()

@router.get(
    "/",
    response_model=BookListResponse,
    summary="Lấy danh sách sách",
    description="Lấy danh sách sách với filter available, search và pagination"
)
async def get_books(
        available: Optional[bool] = Query(
            None,
            description="Filter theo trạng thái: true=sách available, false=sách không available, null=tất cả"
        ),
        search: Optional[str] = Query(
            None,
            description="Tìm kiếm theo tên sách (không phân biệt hoa thường)"
        ),
        page: int = Query(
            1,
            ge=1,
            description="Số trang (bắt đầu từ 1)"
        ),
        page_size: int = Query(
            10,
            ge=1,
            le=100,
            description="Số sách mỗi trang (tối đa 100)"
        ),
        db: AsyncSession = Depends(get_session)
):

    service = BookService(db)
    books, total, current_page = await service.get_books_list(
        available=available,
        search=search,
        page=page,
        page_size=page_size
    )

    return BookListResponse(
        total=total,
        page=current_page,
        page_size=page_size,
        books=books
    )


@router.get(
    "/{book_id}",
    response_model=BookResponse,
    summary="Lấy chi tiết sách",
    description="Lấy thông tin chi tiết 1 cuốn sách theo ID (bao gồm category và authors)"
)
async def get_book_detail(
        book_id: int,
        db: AsyncSession = Depends(get_session)
):
    """
    **Lấy chi tiết 1 cuốn sách theo ID**

    Response bao gồm:
    - Thông tin sách đầy đủ
    - Category (eager loaded - không có N+1 query)
    - Danh sách authors (eager loaded - không có N+1 query)

    **Ví dụ:**
    - `/api/v1/books/1` - Lấy sách có id=1

    **Lưu ý về hiệu suất:**
    - Authors và Category được load cùng lúc (sử dụng selectinload)
    - Chỉ có 2-3 SQL queries thay vì N+1 queries
    """
    service = BookService(db)
    book = await service.get_book_detail(book_id)  # ✅ await
    return book


# ============================================
# POST - Tạo sách mới
# ============================================

@router.post(
    "/",
    response_model=ResponseModel[BookResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Tạo sách mới",
    description="Tạo sách mới với category_id và danh sách author_ids"
)
async def create_book(
        book_data: BookCreate,
        db: AsyncSession = Depends(get_session)  # ✅ Async session
):
    """
    **Tạo sách mới**

    Request Body:
    ```json
    {
        "title": "Clean Code",
        "category_id": 1,
        "published_date": "2008-08-01",
        "is_available": true,
        "author_ids": [1, 2]
    }
    ```

    Validation:
    - `title`: Không được rỗng, tối đa 200 ký tự
    - `category_id`: Phải tồn tại trong database
    - `published_date`: Không được trong tương lai
    - `author_ids`:
        - Phải có ít nhất 1 tác giả
        - Tất cả IDs phải tồn tại trong database
        - Không được trùng lặp

    Response:
    - Thông tin sách vừa tạo (bao gồm category và authors)

    Error Responses:
    - `404`: Category hoặc Author không tồn tại
    - `422`: Validation error (title rỗng, ngày tương lai, v.v.)
    """
    service = BookService(db)
    new_book = await service.create_new_book(book_data)  # ✅ await
    # return new_book
    return ResponseModel(data=new_book, message="Book created successfully.")


# ============================================
# PUT/PATCH - Update sách
# ============================================

@router.put(
    "/{book_id}",
    response_model=BookResponse,
    summary="Update sách",
    description="Update thông tin sách (có thể update 1 hoặc nhiều field)"
)
async def update_book(
        book_id: int,
        book_data: BookUpdate,
        db: AsyncSession = Depends(get_session)  # ✅ Async session
):
    """
    **Update thông tin sách**

    Request Body (tất cả field đều optional):
    ```json
    {
        "title": "Clean Code - Updated",
        "category_id": 2,
        "published_date": "2009-01-01",
        "is_available": false,
        "author_ids": [1, 3]
    }
    ```

    Validation:
    - Tương tự như khi tạo sách
    - Chỉ validate các field được gửi lên

    **Ví dụ:**
    - Update chỉ title: `{"title": "New Title"}`
    - Update chỉ available: `{"is_available": false}`
    - Update nhiều field cùng lúc
    """
    service = BookService(db)
    updated_book = await service.update_book(book_id, book_data)  # ✅ await
    return updated_book


# ============================================
# DELETE - Xóa sách
# ============================================

@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa sách",
    description="Xóa sách khỏi database"
)
async def delete_book(
        book_id: int,
        db: AsyncSession = Depends(get_session)  # ✅ Async session
):
    """
    **Xóa sách khỏi database**

    **Ví dụ:**
    - `DELETE /api/v1/books/1` - Xóa sách có id=1

    Response:
    - `204 No Content`: Xóa thành công
    - `404 Not Found`: Không tìm thấy sách
    """
    service = BookService(db)
    await service.delete_book(book_id)  # ✅ await
    return None