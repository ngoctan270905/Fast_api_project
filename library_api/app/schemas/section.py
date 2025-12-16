from pydantic import BaseModel, Field
from .utils import ObjectIdStr
from typing import List, Optional
from .question import QuestionDetail


# Schema CRETE SECTION ======================================================
class SectionCreate(BaseModel):
    title: str

class SectionCreateResponse(BaseModel):
    id: ObjectIdStr = Field(..., alias="_id", serialization_alias="id")
    exam_paper_id: ObjectIdStr
    title: str
    order: int


# Schema READ SECTION ========================================================
class SectionDetailResponse(BaseModel):
    id: ObjectIdStr = Field(..., alias="_id", serialization_alias="id")
    exam_paper_id: ObjectIdStr = Field(..., exclude=True)
    title: str
    order: int


# Schema UPDATE SECTION ======================================================
class SectionUpdate(BaseModel):
    title: Optional[str] = None

class SectionUpdateResponse(BaseModel):
    id: ObjectIdStr = Field(..., alias="_id", serialization_alias="id")
    exam_paper_id: ObjectIdStr
    title: str
    order: int


# Schema DETAIL SECTION kèm QUESTION =========================================
class SectionDetail(BaseModel):
    id: ObjectIdStr = Field(..., alias="_id", serialization_alias="id")
    exam_paper_id: ObjectIdStr = Field(..., exclude=True)
    title: str
    order: int
    questions: List[QuestionDetail] = Field(default=[])





