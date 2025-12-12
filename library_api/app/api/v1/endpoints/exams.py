from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from app.core.dependencies import get_current_user
from app.repositories.exam_paper_repository import ExamPaperRepository
from app.schemas.response import ResponseModel
from app.schemas.section import SectionCreate, SectionResponse, SectionUpdate
from app.services.exam_service import ExamService
from app.schemas.exam import ExamResponse, ExamCreate, ExamUpdate, ExamDetailResponse
from app.api.deps import get_exam_service, get_exam_paper_repository, get_section_repository, get_question_repository, \
    get_section_service
from app.services.section_service import SectionService

router = APIRouter()

# GET lấy danh sách kì thi
@router.get("/", response_model=ResponseModel[List[ExamResponse]], summary="Danh sách bài kiểm tra")
async def list_exams(exam_service: ExamService = Depends(get_exam_service), user: dict = Depends(get_current_user) ):

    exams = await exam_service.get_all_exams()
    return ResponseModel(data=exams, message="Lấy danh sách bài kiểm tra thành công")

# POST tạo exam
@router.post("/", response_model=ResponseModel[ExamResponse], status_code=status.HTTP_201_CREATED
             , summary="Tạo bài kiểm tra mới")
async def create_exam(exam_data: ExamCreate,
                      exam_service: ExamService = Depends(get_exam_service),
                      user: dict = Depends(get_current_user) ):

    new_exam = await exam_service.create_exam(exam_data, user["id"])
    return ResponseModel(data=new_exam, message="Tạo bài kiểm tra mới thành công")

# GET xem chi tiết exam
@router.get("/{exam_id}", response_model=ResponseModel[ExamDetailResponse], summary="Xem chi tiết bài kiểm tra")
async def get_exam_detail(exam_id: str, exam_service: ExamService = Depends(get_exam_service), user: dict = Depends(get_current_user)):
    exam = await exam_service.get_exam_by_id(exam_id)
    return ResponseModel(data=exam, message="Lấy thông tin bài kiểm tra thành công")







