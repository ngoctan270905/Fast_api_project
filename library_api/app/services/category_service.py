from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status
from typing import List
from app.repositories.category_repository import CategoryRepository
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from typing import List, Optional


class CategoryService:
    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    # Lấy all category
    async def get_all_categories(self) -> List[CategoryResponse]:
        categories_list_dict = await self.category_repo.get_all_category()
        return [CategoryResponse(**cat) for cat in categories_list_dict]

    # lấy category theo id
    async def get_category(self, category_id: str) -> Optional[CategoryResponse]:
        category_dict = await self.category_repo.get_by_category_id(category_id)
        if not category_dict:
            return None
        return CategoryResponse(**category_dict)

    # thêm category
    async def create_category(self, category_create: CategoryCreate) -> CategoryResponse:
        existing_category = await self.category_repo.get_category_by_name(category_create.name)
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category '{category_create.name}' đã tồn tại"
            )

        new_category_dict = await self.category_repo.create_category(category_create)
        return CategoryResponse(**new_category_dict)

    # sửa category
    async def update_category(self, category_id: str, category_update: CategoryUpdate) -> Optional[CategoryResponse]:
        existing_category = await self.get_category(category_id)
        if not existing_category:
            return None
        updated_category_dict = await self.category_repo.update_category(category_id, category_update)

        return CategoryResponse(**updated_category_dict)

    # xóa
    async def delete_category(self, category_id: str) -> bool:
        deleted = await self.category_repo.delete(category_id)
        return deleted