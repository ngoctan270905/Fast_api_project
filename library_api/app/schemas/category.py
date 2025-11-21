from sqlmodel import SQLModel, Field
from typing import Optional, List

class CategoryCreate(SQLModel):
    name: str

class CategoryUpdate(SQLModel):
    name: Optional[str] = None

class CategoryResponse(SQLModel):
    id: int
    name: str

    class Config:
        from_attributes = True
