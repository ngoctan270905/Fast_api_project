from enum import Enum
from pydantic import BaseModel, Field, computed_field
from typing import Optional, List
from datetime import datetime
from .utils import ObjectIdStr
from .exam_paper import ExamPaperDetail


class ExamType(str, Enum):
    MIDTERM = "Giữa kỳ"
    FINAL = "Cuối kỳ"
    FIFTEEN_MIN = "1 Tiết"

# ============================================================================================
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


# ===============================================================================================
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


# =================================================================================================
class ExamListResponse(BaseModel):
    """Hiển thị danh sách bài kiểm tra"""
    id: ObjectIdStr = Field(..., alias="_id", serialization_alias="id")
    name: str = Field(..., description="Tên bài kiểm tra")
    grade: int = Field(..., ge=1, le=12, description="Khối lớp từ 1-12")
    created_at: datetime


# =================================================================================================
class ExamDetailResponse(BaseModel):
    """Schema cho response trả về chi tiết của đề thi"""
    id: Optional[ObjectIdStr] = Field(default=None, alias="_id", serialization_alias="id")
    grade: int = Field(..., ge=1, le=12, description="Khối lớp từ 1-12", exclude=True)
    exam_type: ExamType = Field(..., description="Loại đề", exclude=True)
    exam_number: int = Field(..., ge=1, description="Tổng bao nhiêu đề", exclude=True)
    description: str = Field(..., description="Mô tả đề thi", exclude=True)
    created_at: datetime = Field(..., exclude=True)
    exam_papers: List[ExamPaperDetail] = Field(default=[])

    @computed_field
    def exam_info(self) -> str:
        return (f"Khối: {self.grade}  Loại đề: {self.exam_type.value}  "
                f"Số đề: {self.exam_number}  Mô tả: {self.description}  "
                f"Thời gian tạo: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}")