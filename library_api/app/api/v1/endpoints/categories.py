from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import DbSession
from app.core.database import get_session
from app.services.category_service import CategoryService
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse

router = APIRouter()


# GET tất cả categories
@router.get(
    "/",
    response_model=List[CategoryResponse],
    summary="Lấy danh sách categories"
)
async def get_categories(db: DbSession):
    """Lấy tất cả categories"""
    service = CategoryService(db)
    categories = await service.get_all_categories()
    return categories


# GET category theo ID
@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Lấy chi tiết category"
)
async def get_category(
    category_id: int,
    db: DbSession
):
    """Lấy chi tiết 1 category theo ID"""
    service = CategoryService(db)
    category = await service.get_category_detail(category_id)
    return category


# POST tạo category mới
@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo category mới"
)
async def create_category(
    category_data: CategoryCreate,
    db: DbSession
):

    service = CategoryService(db)
    new_category = await service.create_new_category(category_data)
    return new_category


# PUT update category
@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Cập nhật category"
)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: DbSession
):

    service = CategoryService(db)
    updated_category = await service.update_category(category_id, category_data)
    return updated_category


# DELETE category
@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa category"
)
async def delete_category(
    category_id: int,
    db: DbSession
):
    """Xóa category"""
    service = CategoryService(db)
    await service.delete_category(category_id)