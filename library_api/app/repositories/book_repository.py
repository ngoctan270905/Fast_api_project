from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
from sqlalchemy.orm import selectinload

from app.models.book import Book
from app.models.author import Author
from app.models.category import Category


class BookRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Hàm xử lí db lấy danh sách book
    async def get_all_books(self,
            available: Optional[bool] = None, # có sẵn
            search: Optional[str] = None, # tìm kiếm
            skip: int = 0,
            limit: int = 10
    ) -> List[Book]:

        # Sử dụng selectinload để eager load relationships (tránh N+1 query)
        # Tạo query với eager loading
        query = select(Book).options(
            selectinload(Book.category),  # Load category
            selectinload(Book.authors)  # Load authors
        )

        # Filter theo available
        if available is not None:
            query = query.where(Book.is_available == available)

        # Search theo title (không phân biệt hoa thường)
        if search:
            query = query.where(Book.title.ilike(f"%{search}%"))

        # Pagination
        query = query.offset(skip).limit(limit)

        # Execute async và trả về list
        result = await self.db.execute(query)
        books = result.scalars().all()
        return list(books)

    # hàm đếm tổng số sách
    async def count_books(
            self,
            available: Optional[bool] = None,
            search: Optional[str] = None
    ) -> int:

        query = select(func.count(Book.id))

        if available is not None:
            query = query.where(Book.is_available == available)

        if search:
            query = query.where(Book.title.ilike(f"%{search}%"))

        result = await self.db.execute(query)
        total = result.scalar_one()
        return total

    # Lấy sách theo id
    async def get_book_by_id(self, book_id: int) -> Optional[Book]:
        query = select(Book).options(
            selectinload(Book.category),
            selectinload(Book.authors)
        ).where(Book.id == book_id)

        result = await self.db.execute(query)
        book = result.scalar_one_or_none()
        return book

    # ============================================
    # CREATE OPERATIONS
    # ============================================

    async def create_book(self, book: Book) -> Book:
        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)  # Refresh để có ID

        #Query lại với eager loading để load relationships
        query = select(Book).options(
            selectinload(Book.category),
            selectinload(Book.authors)
        ).where(Book.id == book.id)

        result = await self.db.execute(query)
        book_with_relations = result.scalar_one()

        return book_with_relations

    # ============================================
    # UPDATE OPERATIONS
    # ============================================

    async def update_book(self, book: Book) -> Book:
        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)  # Refresh để có data mới nhất

        # ✅ Query lại với eager loading để load relationships
        query = select(Book).options(
            selectinload(Book.category),
            selectinload(Book.authors)
        ).where(Book.id == book.id)

        result = await self.db.execute(query)
        book_with_relations = result.scalar_one()

        return book_with_relations

    async def update_book_cover_image_url(self, book_id: int, image_url: str) -> Optional[Book]:
        book = await self.get_book_by_id(book_id)
        if book:
            book.cover_image_url = image_url
            self.db.add(book)
            await self.db.commit()
            await self.db.refresh(book)
            return book
        return None

    # ============================================
    # DELETE OPERATIONS
    # ============================================

    async def delete_book(self, book: Book) -> None:
        """Xóa sách khỏi DB (ASYNC)"""
        await self.db.delete(book)
        await self.db.commit()

    # ============================================
    # HELPER METHODS (validate foreign keys)
    # ============================================

    async def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Kiểm tra category có tồn tại không (ASYNC)"""
        result = await self.db.get(Category, category_id)
        return result

    async def get_authors_by_ids(self, author_ids: List[int]) -> List[Author]:
        """Lấy danh sách authors theo IDs (ASYNC)"""
        query = select(Author).where(Author.id.in_(author_ids))
        result = await self.db.execute(query)
        authors = result.scalars().all()
        return list(authors)
