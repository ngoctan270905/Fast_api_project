from pydantic import BaseModel, Field
from .utils import ObjectIdStr
from typing import List, Optional
from .question import QuestionDetail

class SectionBase(BaseModel):
    exam_paper_id: ObjectIdStr
    title: str
    order: int

class SectionCreate(BaseModel):
    title: str
    order: Optional[int] = None

class SectionUpdate(BaseModel):
    title: Optional[str] = None
    order: Optional[int] = Field(default=None, nullable=True)

class SectionResponse(BaseModel):
    id: ObjectIdStr = Field(..., alias="_id")
    exam_paper_id: ObjectIdStr
    title: str
    order: int

class SectionDetail(BaseModel):
    id: ObjectIdStr = Field(..., alias="_id")
    exam_paper_id: ObjectIdStr = Field(..., exclude=True)
    title: str
    order: int
    questions: List[QuestionDetail] = Field(default=[])





