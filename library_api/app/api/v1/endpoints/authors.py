from fastapi import APIRouter, status
from typing import List
from app.core.dependencies import DbSession
from app.services.author_service import AuthorService
from app.schemas.author import AuthorCreate, AuthorUpdate, AuthorResponse

router = APIRouter()

@router.get(
    "/",
    response_model=List[AuthorResponse],
    summary="Lấy danh sách tất cả tác giả"
)
# Lấy dữ liệu
async def get_authors(db: DbSession):
    service = AuthorService(db) # Khởi tạo instance
    authors = await service.get_all_authors() # gọi đến service
    return authors


@router.get(
    "/{author_id}",
    response_model=AuthorResponse,
    summary="Lấy chi tiết tác giả"
)
# Lấy chi tiết tác giả theo ID
async def get_author(author_id: int, db: DbSession):
    service = AuthorService(db) # Khởi tạo instance
    author = await service.get_author_detail(author_id) # Gọi services kèm ID client gửi lên
    return author


@router.post(
    "/",
    response_model=AuthorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo author mới"
)
async def create_author(author_data: AuthorCreate, db: DbSession):
    service = AuthorService(db)
    new_author = await service.create_new_author(author_data)
    return new_author


@router.put(
    "/{author_id}",
    response_model=AuthorResponse,
    summary="Cập nhật author"
)
async def update_author(
        author_id: int,
        author_data: AuthorUpdate,
        db: DbSession
):
    """
    Cập nhật thông tin author

    - Tất cả fields đều optional
    - Chỉ update các field được gửi lên
    """
    service = AuthorService(db)
    updated_author = await service.update_author(author_id, author_data)
    return updated_author


@router.delete(
    "/{author_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa author"
)
async def delete_author(author_id: int, db: DbSession):
    """
    Xóa author

    Note: Nếu author có books liên kết, cần xử lý trước khi xóa
    """
    service = AuthorService(db)
    await service.delete_author(author_id)