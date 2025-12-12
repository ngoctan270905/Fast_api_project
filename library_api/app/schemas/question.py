from pydantic import BaseModel, Field
from typing import List, Optional
from .utils import ObjectIdStr

class AnswerItem(BaseModel):
    label: str
    value: str

class QuestionBase(BaseModel):
    section_id: ObjectIdStr
    order: int
    score_value: float
    question_text: str
    answers: Optional[List[AnswerItem]] = None


class QuestionResponse(QuestionBase):
    id: ObjectIdStr


class QuestionDetail(BaseModel):
    id: ObjectIdStr = Field(..., alias="_id")
    section_id: ObjectIdStr = Field(..., exclude=True)
    score_value: float
    question_text: str
    order: int
    answers: Optional[List[AnswerItem]] = None

