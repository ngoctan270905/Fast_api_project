from pydantic import BaseModel
from typing import Optional

# base chứa tất cả
class AuthorBase(BaseModel):
    name: str
    bio: Optional[str] = None

# reponse ( kế thừa model )
class AuthorCreate(AuthorBase):
    pass

# reponse update ( Nếu client ko gửi thì None giữ như cũ )
class AuthorUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None

# reponse read ( hiển thị dữ liệu cho client )
class AuthorResponse(AuthorBase):
    id: int

    class Config:
        from_attributes = True  # Cho phép convert từ SQLModel → Pydantic