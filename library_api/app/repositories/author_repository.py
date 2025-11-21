from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.models.author import Author

class AuthorRepository:
    # Hàm khởi tạo
    def __init__(self, db: AsyncSession):
        self.db = db

    # Lấy danh sách author
    async def get_all_authors(self) -> List[Author]:
        result = await self.db.execute(select(Author))
        return list(result.scalars().all())

    # Lấy danh sách theo id
    async def get_author_by_id(self, author_id: int) -> Author | None: # Nếu tìm thấy trả về oj ko thì None
        # Thực hiện truy vấn SQL bất đồng bộ
        result = await self.db.execute(
            select(Author).where(Author.id == author_id)
        )
        # Dùng scalar_one_or_none() chắc chắn sẽ chỉ nhận đc 1 OJ
        return result.scalar_one_or_none()

    # Kiểm tra trùng tên
    async def get_author_by_name(self, name: str) -> Author | None: # Nếu tìm thấy trả về oj ko thì None
        # Thực hiện truy vấn SQL bất đồng bộ
        result = await self.db.execute(
            select(Author).where(Author.name == name)
        )
        # Dùng scalar_one_or_none() chắc chắn sẽ chỉ nhận đc 1 OJ
        return result.scalar_one_or_none()

    async def create_author(self, author: Author) -> Author:
        """Tạo author mới"""
        self.db.add(author)
        await self.db.commit()
        await self.db.refresh(author)
        return author

    async def update_author(self, author: Author) -> Author:
        """Update author"""
        await self.db.commit()
        await self.db.refresh(author)
        return author

    async def delete_author(self, author: Author) -> None:
        """Xóa author"""
        await self.db.delete(author)
        await self.db.commit()