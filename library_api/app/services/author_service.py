from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import List
from app.repositories.author_repository import AuthorRepository
from app.models.author import Author
from app.schemas.author import AuthorCreate, AuthorUpdate


class AuthorService:
    def __init__(self, db: AsyncSession):
        """
        Khởi tạo AuthorService với kết nối cơ sở dữ liệu.

        Logic:
            1. Nhận vào một phiên làm việc bất đồng bộ (AsyncSession).
            2. Tạo instance của AuthorRepository để thao tác với database.

        Args:
            db (AsyncSession): Phiên làm việc (session) dùng cho truy vấn database.
        """
        self.repository = AuthorRepository(db)  # Khởi tạo instance cho self.repository

    async def get_all_authors(self) -> List[Author]:
        """
        Lấy danh sách tất cả tác giả.

        Logic:
            1. Gọi repository để truy vấn toàn bộ dữ liệu tác giả.
            2. Trả về danh sách Author (list object).

        Returns:
            List[Author]: Danh sách tất cả tác giả trong hệ thống.
        """
        return await self.repository.get_all_authors()

    async def get_author_detail(self, author_id: int) -> Author:  # Định dạng kiểu trả về 1 object của Author
        """
        Lấy chi tiết thông tin của một tác giả theo ID.

        Logic:
            1. Gọi repository để truy vấn tác giả theo `author_id`.
            2. Nếu không tìm thấy → raise HTTPException(404).
            3. Nếu tìm thấy → trả về đối tượng Author.

        Args:
            author_id (int): ID của tác giả cần lấy.

        Returns:
            Author: Đối tượng tác giả tương ứng với ID.
        """
        author = await self.repository.get_author_by_id(author_id)

        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy author với id={author_id}"
            )

        return author

    async def create_new_author(self, author_data: AuthorCreate) -> Author:
        """
        Tạo mới một tác giả.

        Logic:
            1. Kiểm tra xem tên tác giả đã tồn tại trong hệ thống chưa.
                - Nếu trùng → raise HTTPException(400) báo lỗi "Author đã tồn tại".
            2. Nếu hợp lệ → khởi tạo đối tượng Author mới.
            3. Gọi repository để lưu tác giả mới vào cơ sở dữ liệu.
            4. Trả về đối tượng Author vừa được tạo.

        Args:
            author_data (AuthorCreate): Dữ liệu đầu vào để tạo tác giả mới
            (bao gồm name, bio, ...).

        Returns:
            Author: Đối tượng Author vừa được tạo và lưu vào database.
        """
        # 1. Kiểm tra tên đã tồn tại
        existing_author = await self.repository.get_author_by_name(author_data.name)
        if existing_author:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Author '{author_data.name}' đã tồn tại"
            )

        # 2. Tạo author mới
        new_author = Author(
            name=author_data.name,
            bio=author_data.bio
        )

        created_author = await self.repository.create_author(new_author)

        return created_author

    async def update_author(self, author_id: int, author_data: AuthorUpdate) -> Author:
        """
        Cập nhật thông tin tác giả theo ID.

        Logic:
            1. Lấy thông tin tác giả hiện tại theo `author_id`.
                - Nếu không tìm thấy → raise HTTPException(404).
            2. Nếu client gửi `name` mới:
                - Kiểm tra xem tên đó đã tồn tại trong hệ thống chưa.
                - Nếu tồn tại và thuộc về tác giả khác → raise HTTPException(400).
                - Nếu hợp lệ → cập nhật tên mới.
            3. Nếu client gửi `bio` → cập nhật tiểu sử.
            4. Lưu các thay đổi vào cơ sở dữ liệu thông qua repository.
            5. Trả về đối tượng Author đã được cập nhật.

        Args:
            author_id (int): ID của tác giả cần cập nhật.
            author_data (AuthorUpdate): Dữ liệu cập nhật từ client, có thể chỉ bao gồm một số trường.

        Returns:
            Author: Đối tượng Author sau khi cập nhật thành công.
        """
        # 1. Lấy author hiện tại
        author = await self.repository.get_author_by_id(author_id)
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy author với id={author_id}"
            )

        # 2. Nếu update name, kiểm tra trùng lặp
        if author_data.name is not None:
            existing_author = await self.repository.get_author_by_name(author_data.name)

            # Kiểm tra: tên đã tồn tại VÀ thuộc về author khác
            if existing_author and existing_author.id != author_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Author '{author_data.name}' đã tồn tại"
                )

            author.name = author_data.name

        # 3. Update bio nếu có
        if author_data.bio is not None:
            author.bio = author_data.bio

        # 4. Lưu vào DB
        updated_author = await self.repository.update_author(author)
        return updated_author

    async def delete_author(self, author_id: int) -> None:
        """
        Xóa author

        Note: Nếu author có books liên kết, có thể cần kiểm tra trước
        """
        author = await self.repository.get_author_by_id(author_id)
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy author với id={author_id}"
            )

        await self.repository.delete_author(author)
