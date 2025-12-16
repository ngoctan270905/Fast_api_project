from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .utils import ObjectIdStr
from .exam_paper import ExamPaperDetail

class ExamType(str, Enum):
    MIDTERM = "giữa kỳ"
    FINAL = "cuối kỳ"
    FIFTEEN_MIN = "1 Tiết"

class ExamCreate(BaseModel):
    """Tạo mới bài thi"""
    name: str = Field(..., description="Tên bài kiểm tra")
    grade: int = Field(..., ge=1, le=12, description="Khối lớp từ 1-12")
    exam_type: ExamType = Field(..., description="Loại đề")
    exam_number: int = Field(..., ge=1, description="Tổng bao nhiêu đề")
    description: str = Field(..., description="Mô tả đề thi")

class ExamCreateResponse(BaseModel):
    """Thông tin tạo mới"""
    id: Optional[ObjectIdStr] = Field(default=None, alias="_id", serialization_alias="id")
    name: str = Field(..., description="Tên bài kiểm tra")
    grade: int = Field(..., ge=1, le=12, description="Khối lớp từ 1-12")
    exam_type: ExamType = Field(..., description="Loại đề")
    exam_number: int = Field(..., ge=1, description="Tổng bao nhiêu đề")
    description: str = Field(..., description="Mô tả đề thi")
    created_at: datetime


class ExamUpdate(BaseModel):
    """Cập nhật bài thi"""
    name: Optional[str] = Field(None, description="Tên bài kiểm tra")
    grade: Optional[int] = Field(None, ge=1, le=12, description="Khối lớp từ 1-12")
    exam_type: Optional[ExamType] = Field(None, description="Loại đề")
    exam_number: Optional[int] = Field(None, ge=1, description="Tổng bao nhiêu đề")
    description: Optional[str] = Field(None, description="Mô tả đề thi")

class ExamUpdateResponse(BaseModel):
    """Thông tin cập nhật"""
    id: Optional[ObjectIdStr] = Field(default=None, alias="_id", serialization_alias="id")
    name: str = Field(..., description="Tên bài kiểm tra")
    grade: int = Field(..., ge=1, le=12, description="Khối lớp từ 1-12")
    exam_type: ExamType = Field(..., description="Loại đề")
    exam_number: int = Field(..., ge=1, description="Tổng bao nhiêu đề")
    description: str = Field(..., description="Mô tả đề thi")
    updated_at: datetime


# Schem trả về danh sách bài kiểm tra
class ExamListResponse(BaseModel):
    """Hiển thị danh sách bài kiểm tra"""
    id: Optional[ObjectIdStr] = Field(default=None, alias="_id", serialization_alias="id")
    name: str = Field(..., description="Tên bài kiểm tra")
    grade: int = Field(..., ge=1, le=12, description="Khối lớp từ 1-12")
    created_at: datetime

class ExamDetailResponse(BaseModel):
    """Schema cho response trả về chi tiết của đề thi"""
    id: Optional[ObjectIdStr] = Field(default=None, alias="_id")
    name: str = Field(..., description="Tên bài kiểm tra")
    grade: int = Field(..., ge=1, le=12, description="Khối lớp từ 1-12")
    exam_type: str = Field(..., description="Loại đề: giữa kỳ, cuối kỳ, 15 phút...")
    exam_number: int = Field(..., ge=1, description="Tổng bao nhiêu đề")
    description: str = Field(..., description="Mô tả đề thi")
    created_by: ObjectIdStr
    created_at: datetime
    updated_at: datetime = Field(..., exclude=True)
    deleted_at: Optional[datetime] = Field(None, exclude=True)
    exam_papers: List[ExamPaperDetail] = Field(default=[])