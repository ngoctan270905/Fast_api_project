from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status
from typing import List
from app.repositories.category_repository import CategoryRepository
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.repository = CategoryRepository(db)

    async def get_all_categories(self) -> List[Category]:
        """Lấy tất cả categories"""
        return await self.repository.get_all_categories()

    async def get_category_detail(self, category_id: int) -> Category:
        """Lấy chi tiết 1 category, raise 404 nếu không tìm thấy"""
        category = await self.repository.get_category_by_id(category_id)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy category với id={category_id}"
            )

        return category

    async def create_new_category(self, category_data: CategoryCreate) -> Category:
        existing = await self.repository.get_category_by_name(category_data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category '{category_data.name}' đã tồn tại"
            )

        new_category = Category(name=category_data.name)
        created_category = await self.repository.create_category(new_category)

        return created_category

    async def update_category(
            self,
            category_id: int,
            category_data: CategoryUpdate
    ) -> Category:
        """Update category"""
        category = await self.repository.get_category_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy category với id={category_id}"
            )

        # Update fields
        if category_data.name is not None:
            category.name = category_data.name

        updated_category = await self.repository.update_category(category)
        return updated_category

    async def delete_category(self, category_id: int) -> None:
        """Xóa category"""
        category = await self.repository.get_category_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy category với id={category_id}"
            )

        await self.repository.delete_category(category)