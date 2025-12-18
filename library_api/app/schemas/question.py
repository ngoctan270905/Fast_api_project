from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from .utils import ObjectIdStr

# Validate type câu hỏi
class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    SHORT_ANSWER = "SHORT_ANSWER"
    ESSAY = "ESSAY"

# Trắc nghiệm
class OptionItem(BaseModel):
    key: str = Field(..., example="A")
    value: str = Field(..., example="x = 2")


# Dữ liệu thêm mới ======================================================
class QuestionCreate(BaseModel):
    question_type: QuestionType
    question_text: str
    images: Optional[str] = None
    order: int
    score: float
    options: Optional[List[OptionItem]] = None

# Dữ liệu Create trả về
class QuestionCreateResponse(BaseModel):
    id: ObjectIdStr = Field(alias="_id", serialization_alias="id")
    section_id: ObjectIdStr
    question_type: QuestionType
    question_text: str
    images: Optional[str] = None
    order: int
    score: float
    options: Optional[List[OptionItem]] = None


# Dữ liệu update =========================================================
class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    order: Optional[int] = None
    score: Optional[float] = None
    options: Optional[List[OptionItem]] = None

# Dữ liệu Update trả về
class QuestionUpdateResponse(BaseModel):
    id: ObjectIdStr = Field(alias="_id", serialization_alias="id")
    section_id: ObjectIdStr
    question_type: QuestionType
    question_text: str
    images: Optional[List[str]] = None
    order: int
    score: float
    options: Optional[List[OptionItem]] = None


# Dữ liệu Read Question ===================================================
class QuestionReadResponse(BaseModel):
    id: ObjectIdStr = Field(alias="_id", serialization_alias="id")
    section_id: ObjectIdStr
    question_type: QuestionType
    question_text: str
    images: Optional[List[str]] = None
    order: int
    score: float
    options: Optional[List[OptionItem]] = None


# Dữ liệu Trả về
class QuestionResponse(BaseModel):
    id: ObjectIdStr = Field(alias="_id")
    section_id: ObjectIdStr
    question_type: QuestionType
    question_text: str
    images: Optional[str] = None
    order: int
    score: float
    options: Optional[List[OptionItem]] = None


# Chi tiết trong Exam
class QuestionDetail(BaseModel):
    id: ObjectIdStr = Field(..., alias="_id", serialization_alias="id")

    question_type: QuestionType
    question_text: str
    order: int
    score: float
    options: Optional[List[OptionItem]] = None




