from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import DbSession
from app.core.database import get_session
from app.services.category_service import CategoryService
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.api.deps import get_category_service

router = APIRouter()

# GET tất cả categories
@router.get(
    "/",
    response_model=List[CategoryResponse],
    summary="Lấy danh sách categories"
)
async def get_categories(service: CategoryService = Depends(get_category_service)):
    categories = await service.get_all_categories()
    return categories


# GET category theo ID:
@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Lấy chi tiết category"
)
async def get_category(
    category_id: str,
    service: CategoryService = Depends(get_category_service)
):
    category = await service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


# tạo category
@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo category mới"
)
async def create_category(
    category_data: CategoryCreate,
    # --- THAY ĐỔI QUAN TRỌNG ---
    # Thay vì inject `DbSession`, chúng ta inject `CategoryService`
    # thông qua hàm provider `get_category_service`.
    service: CategoryService = Depends(get_category_service)
):
    # Dòng `service = CategoryService(db)` đã được loại bỏ.
    # FastAPI đã tự động tạo và cung cấp cho chúng ta một instance 'service' sẵn sàng để sử dụng.
    new_category = await service.create_category(category_data)
    return new_category


# update category:
@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Cập nhật category"
)
async def update_category(
    category_id: str,
    category_data: CategoryUpdate,
    service: CategoryService = Depends(get_category_service)
):
    updated_category = await service.update_category(category_id, category_data)
    if not updated_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return updated_category

# xóa
@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa category"
)
async def delete_category(
    category_id: str,
    service: CategoryService = Depends(get_category_service)
):

    deleted = await service.delete_category(category_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")