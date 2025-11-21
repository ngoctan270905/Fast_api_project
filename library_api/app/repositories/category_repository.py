from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.category import Category
from typing import List, Optional
from sqlmodel import select


class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Lấy tất cả category
    async def get_all_categories(self) -> List[Category]:
        result = await self.db.execute(select(Category))
        return result.scalars().all()

    # Lấy category theo id
    async def get_category_by_id(self, category_id: int) -> Optional[Category]:
        result = await self.db.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    async def get_category_by_name(self, name: str) -> Category | None:
        """Tìm category theo tên"""
        result = await self.db.execute(
            select(Category).where(Category.name == name)
        )
        return result.scalar_one_or_none()

    # Tạo category mới
    async def create_category(self, category: Category) -> Category:
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    # Update category
    async def update_category(self, category: Category) -> Category:
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    # Delete category
    async def delete_category(self, category: Category):
        await self.db.delete(category)
        await self.db.commit()
