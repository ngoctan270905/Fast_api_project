from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import List, Optional

# GET request Reponse Schema
class AuthorInBook(BaseModel):
    """Schema hiển thị Author trong Book"""
    id: int
    name: str

    class Config:
        from_attributes = True

# GET request Reponse Schema
class CategoryInBook(BaseModel):
    """Schema hiển thị Category trong Book"""
    id: int
    name: str

    class Config:
        from_attributes = True

# POST request Schema (validate input Json)
class BookCreate(BaseModel):
    """Schema để tạo sách mới"""
    title: str = Field(..., max_length=200, description="Tên sách")
    category_id: int = Field(..., description="ID của category")
    published_date: date = Field(..., description="Ngày xuất bản")
    is_available: bool = Field(default=True, description="Sách có sẵn không")
    author_ids: List[int] = Field(..., min_length=1, description="Danh sách ID tác giả (ít nhất 1)")

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title không được để trống")
        return v.strip()

    @field_validator("published_date")
    @classmethod
    def date_not_future(cls, v: date) -> date:
        from datetime import date as dt_date
        if v > dt_date.today():
            raise ValueError("published_date không được trong tương lai")
        return v

    @field_validator("author_ids")
    @classmethod
    def author_ids_unique(cls, v: List[int]) -> List[int]:
        if len(v) != len(set(v)):
            raise ValueError("author_ids không được trùng lặp")
        return v

# PUT / PATCH request Schema (validate input Json)
class BookUpdate(BaseModel):
    """Schema để update sách"""
    title: Optional[str] = Field(None, max_length=200)
    category_id: Optional[int] = None
    published_date: Optional[date] = None
    is_available: Optional[bool] = None
    author_ids: Optional[List[int]] = Field(None, min_length=1)

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("title không được để trống")
            return v.strip()
        return v

    @field_validator("published_date")
    @classmethod
    def date_not_future(cls, v: Optional[date]) -> Optional[date]:
        if v is not None:
            from datetime import date as dt_date
            if v > dt_date.today():
                raise ValueError("published_date không được trong tương lai")
        return v

    @field_validator("author_ids")
    @classmethod
    def author_ids_unique(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        if v is not None and len(v) != len(set(v)):
            raise ValueError("author_ids không được trùng lặp")
        return v

# GET request reponse Schema
class BookResponse(BaseModel):
    """Schema response khi lấy thông tin sách (có category và authors)"""
    id: int
    title: str
    category_id: int
    published_date: date
    is_available: bool
    cover_image_url: Optional[str] = None
    category: Optional[CategoryInBook] = None
    authors: List[AuthorInBook] = []

    class Config:
        from_attributes = True

# GET request reponse Schema
class BookListResponse(BaseModel):
    """Schema response khi lấy danh sách sách"""
    total: int
    page: int
    page_size: int
    books: List[BookResponse]