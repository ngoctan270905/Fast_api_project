from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from app.core.dependencies import get_current_user
from app.repositories.exam_paper_repository import ExamPaperRepository
from app.schemas.question import QuestionResponse, QuestionCreate
from app.schemas.response import ResponseModel
from app.schemas.section import SectionCreate, SectionResponse, SectionUpdate
from app.services.exam_service import ExamService
from app.schemas.exam import ExamListResponse, ExamCreate, ExamUpdate, ExamDetailResponse
from app.api.deps import get_exam_service, get_exam_paper_repository, get_section_repository, get_question_repository, \
    get_section_service, get_question_service
from app.services.question_service import QuestionService
from app.services.section_service import SectionService

router = APIRouter()

# @router.post("/{exam_paper_id}/sections", response_model=ResponseModel[SectionResponse], summary="Thêm mới section")
# async def create_section(section_data:SectionCreate, exam_paper_id: str, section_service: SectionService = Depends(get_section_service),
#                          user: dict = Depends(get_current_user)):
#     new_section = await section_service.create_section(section_data, exam_paper_id)
#     return ResponseModel(data=new_section, message="Thêm phần trong đề thành công")

# PUT sửa section
@router.put("/{section_id}", response_model=ResponseModel[SectionResponse], summary="Chỉnh sửa phần")
async def update_section(section_data:SectionUpdate,section_id:str,
                         section_service: SectionService = Depends(get_section_service), user: dict = Depends(get_current_user)):
    updated = await section_service.update_section(section_id, section_data)
    return ResponseModel(data=updated, message="Sửa phần trong đề thành công")

@router.delete("/{section_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa phần")
async def update_section(section_id:str,
                         section_service: SectionService = Depends(get_section_service), user: dict = Depends(get_current_user)):
    deleted = await section_service.delete_section(section_id)
    return deleted

# POST thêm câu hỏi
@router.post("/{section_id}/questions", response_model=ResponseModel[QuestionResponse], summary="Thêm mới câu hỏi")
async def create_question(section_id:str, question_data: QuestionCreate,
                          question_service: QuestionService = Depends(get_question_service),
                          user: dict = Depends(get_current_user)):
    new_question = await question_service.create_question(question_data, section_id)
    return ResponseModel(data=new_question, message="Thêm câu hỏi thành công")
