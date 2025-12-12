from typing import Optional, List

from pydantic import BaseModel, Field
from datetime import datetime
from .utils import ObjectIdStr
from .section import SectionDetail

class ExamPaperBase(BaseModel):
    exam_id: ObjectIdStr
    paper_number: int
    title: str

class ExamPaperResponse(ExamPaperBase):
    id: Optional[ObjectIdStr] = Field(default=None, alias="_id")
    created_at: datetime
    updated_at: datetime

class ExamPaperDetail(BaseModel):
    id: Optional[ObjectIdStr] = Field(default=None, alias="_id")
    exam_id: ObjectIdStr = Field(..., exclude=True)
    paper_number: int
    title: str
    sections: List[SectionDetail] = Field(default=[])


