from typing import List, Tuple
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status
from app.repositories.book_repository import BookRepository
from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate


class BookService:

    # Hàm khởi tạo
    def __init__(self, db: AsyncSession):
        self.repository = BookRepository(db)

    # Hàm lấy danh sách book
    async def get_books_list(self,
            available: bool = None,
            search: str = None,
            page: int = 1,
            page_size: int = 10
    ) -> Tuple[List[Book], int, int]: # set type hint để nhập kiểu dữ liệu trả về là tuple

        if page < 1: # nếu số trang < 1 tự động gán = 1, còn k thì gán tự động
            page = 1
        if page_size < 1: # nếu page_size ( số sách trong trang ) < 1 tự động bán = 10, ... )
            page_size = 10
        if page_size > 100: # nếu page_size ( số sách trong trang ) > 100 tự động bán = 100, ... )
            page_size = 100

        # Tính skip
        skip = (page - 1) * page_size

        # Gọi method trong reponsitory để lấy danh sách book
        books = await self.repository.get_all_books(
            available=available,
            search=search,
            skip=skip,
            limit=page_size
        )

        # Gọi method trong reponsitory để tính tổng book
        total = await self.repository.count_books(
            available=available,
            search=search
        )

        return books, total, page


    async def get_book_detail(self, book_id: int) -> Book:
        """
        Lấy chi tiết 1 cuốn sách (ASYNC)
        Raise 404 nếu không tìm thấy
        """
        book = await self.repository.get_book_by_id(book_id)

        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy sách với id={book_id}"
            )

        return book

    # ============================================
    # CREATE BOOK
    # ============================================

    async def create_new_book(self, book_data: BookCreate) -> Book:
        """
        Tạo sách mới (ASYNC)

        Logic nghiệp vụ:
        1. Validate category_id có tồn tại
        2. Validate tất cả author_ids có tồn tại
        3. Tạo Book object
        4. Gán authors vào book
        5. Lưu vào DB

        Raises:
            HTTPException 404: Nếu category hoặc author không tồn tại
        """
        # 1. Kiểm tra category có tồn tại (ASYNC)
        category = await self.repository.get_category_by_id(book_data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy category với id={book_data.category_id}"
            )

        # 2. Kiểm tra tất cả authors có tồn tại (ASYNC)
        authors = await self.repository.get_authors_by_ids(book_data.author_ids)

        # So sánh số lượng: nếu thiếu author => raise error
        if len(authors) != len(book_data.author_ids):
            found_ids = {a.id for a in authors}
            requested_ids = set(book_data.author_ids)
            missing_ids = requested_ids - found_ids
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy authors với ids: {list(missing_ids)}"
            )

        # 3. Tạo Book object
        new_book = Book(
            title=book_data.title,
            category_id=book_data.category_id,
            published_date=book_data.published_date,
            is_available=book_data.is_available
        )

        # 4. Gán authors vào book (many-to-many relationship)
        new_book.authors = authors

        # 5. Lưu vào DB (ASYNC)
        created_book = await self.repository.create_book(new_book)

        return created_book

    # ============================================
    # UPDATE BOOK
    # ============================================

    async def update_book(self, book_id: int, book_data: BookUpdate) -> Book:
        """
        Update thông tin sách (ASYNC)

        Logic:
        1. Kiểm tra book có tồn tại
        2. Validate category_id nếu có update
        3. Validate author_ids nếu có update
        4. Update các field
        5. Lưu vào DB
        """
        # 1. Lấy book hiện tại (ASYNC)
        book = await self.repository.get_book_by_id(book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy sách với id={book_id}"
            )

        # 2. Validate category_id nếu có update (ASYNC)
        if book_data.category_id is not None:
            category = await self.repository.get_category_by_id(book_data.category_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy category với id={book_data.category_id}"
                )
            book.category_id = book_data.category_id

        # 3. Validate author_ids nếu có update (ASYNC)
        if book_data.author_ids is not None:
            authors = await self.repository.get_authors_by_ids(book_data.author_ids)
            if len(authors) != len(book_data.author_ids):
                found_ids = {a.id for a in authors}
                requested_ids = set(book_data.author_ids)
                missing_ids = requested_ids - found_ids
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy authors với ids: {list(missing_ids)}"
                )
            book.authors = authors

        # 4. Update các field khác
        if book_data.title is not None:
            book.title = book_data.title
        if book_data.published_date is not None:
            book.published_date = book_data.published_date
        if book_data.is_available is not None:
            book.is_available = book_data.is_available

        # 5. Lưu vào DB (ASYNC)
        updated_book = await self.repository.update_book(book)

        return updated_book

    async def update_book_cover_image_url(self, book_id: int, image_url: str) -> Book:
        """
        Update the cover image URL for a book (ASYNC)
        """
        book = await self.repository.get_book_by_id(book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy sách với id={book_id}"
            )
        
        updated_book = await self.repository.update_book_cover_image_url(book_id, image_url)
        return updated_book

    # ============================================
    # DELETE BOOK
    # ============================================

    async def delete_book(self, book_id: int) -> None:
        """Xóa sách (ASYNC)"""
        book = await self.repository.get_book_by_id(book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy sách với id={book_id}"
            )

        await self.repository.delete_book(book)