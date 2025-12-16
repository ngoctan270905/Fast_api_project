from enum import Enum
from fastapi import APIRouter, Depends, status, HTTPException, Query
from typing import List, Optional
from app.core.dependencies import get_current_user
from app.schemas.response import ResponseModel
from app.services.exam_service import ExamService
from app.schemas.exam import ExamListResponse, ExamCreate, ExamUpdate, ExamDetailResponse, ExamCreateResponse, ExamUpdateResponse
from app.api.deps import get_exam_service
from app.utils.enums import ExamSortType

router = APIRouter()


# GET lấy danh sách kì thi =============================================================================================
@router.get("/", response_model=ResponseModel[List[ExamListResponse]], summary="Danh sách bài kiểm tra")
async def list_exams(exam_service: ExamService = Depends(get_exam_service),
                     grade: Optional[int] = Query(None, ge=1, le=12, description="Tìm theo khối"),
                     sort_by: Optional[ExamSortType] = Query(None, description="Sắp xếp theo")):

    exams = await exam_service.get_all_exams(grade=grade, sort_by=sort_by)
    if not exams:
        msg = (
            f"Không có bản ghi nào thuộc khối {grade}"
            if grade is not None
            else "Không có bài kiểm tra nào"
        )
    else:
        msg = "Lấy danh sách bài kiểm tra thành công"
    return ResponseModel(data=exams, message=msg)



# POST tạo exam ========================================================================================================
@router.post("/",response_model=ResponseModel[ExamCreateResponse],
                      status_code=status.HTTP_201_CREATED,
                      summary="Tạo bài kiểm tra mới")

async def create_exam(exam_data: ExamCreate,
                      exam_service: ExamService = Depends(get_exam_service),
                      user: dict = Depends(get_current_user) ):

    new_exam = await exam_service.create_exam(exam_data, user["id"])
    return ResponseModel(data=new_exam, message="Tạo bài kiểm tra mới thành công")



# GET xem chi tiết exam ================================================================================================
@router.get("/{exam_id}", response_model=ResponseModel[ExamDetailResponse], summary="Xem chi tiết bài kiểm tra")
async def get_exam_detail(exam_id:str,  exam_service:ExamService = Depends(get_exam_service)):
    exam = await exam_service.get_exam_by_id(exam_id)
    return ResponseModel(data=exam, message="Lấy thông tin bài kiểm tra thành công")



# PUT tạo exam =========================================================================================================
@router.put("/{exam_id}",
             response_model=ResponseModel[ExamUpdateResponse],
             summary="Cập nhật bài kiểm tra" )

async def update_exam(exam_id:str,exam_data: ExamUpdate, exam_service: ExamService = Depends(get_exam_service)):
    updated_exam = await exam_service.update_exam(exam_data=exam_data, exam_id=exam_id)
    return ResponseModel(data=updated_exam, message="Cập nhật bài kiểm tra thành công")







