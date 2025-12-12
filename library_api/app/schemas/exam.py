from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .utils import ObjectIdStr
from .exam_paper import ExamPaperDetail


class ExamBase(BaseModel):
    name: str = Field(..., description="Tên bài kiểm tra")
    grade: int = Field(..., ge=1, le=12, description="Khối lớp từ 1-12")
    exam_type: str = Field(..., description="Loại đề: giữa kỳ, cuối kỳ, 15 phút...")
    exam_number: int = Field(..., ge=1, description="Tổng bao nhiêu đề")
    description: str = Field(..., description="Mô tả đề thi")


class ExamCreate(ExamBase):
    """Schema cho tạo mới bài kiểm tra"""
    # created_by: str = Field(..., description="User ID người tạo")
    pass


class ExamUpdate(BaseModel):
    """Schema cho cập nhật đề thi"""
    grade: Optional[int] = Field(None, ge=1, le=12)
    exam_type: Optional[str] = None
    exam_number: Optional[int] = Field(None, ge=1)
    description: Optional[str] = None


class ExamResponse(BaseModel):
    """Schema cho response trả về"""
    id: Optional[ObjectIdStr] = Field(default=None, alias="_id")
    name: str = Field(..., description="Tên bài kiểm tra")
    grade: int = Field(..., ge=1, le=12, description="Khối lớp từ 1-12")
    exam_type: str = Field(..., description="Loại đề: giữa kỳ, cuối kỳ, 15 phút...")
    exam_number: int = Field(..., ge=1, description="Tổng bao nhiêu đề")
    description: str = Field(..., description="Mô tả đề thi")
    created_by: ObjectIdStr
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = Field(None, exclude=True)


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